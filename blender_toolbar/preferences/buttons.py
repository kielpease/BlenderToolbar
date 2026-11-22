"""Store the user's ordered toolbar buttons in Blender preferences."""

from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import bpy

from ..actions.mesh_actions import ACTION_ITEMS
from ..storage.layout import read_layout, write_layout


_PACKAGE = __package__.rsplit(".", 1)[0]
MAX_BUTTONS = 12
ICON_ITEMS = (
    ("AUTO", "Match Action", "Show the icon for the selected action", 0),
    ("NONE", "None", "Show the label only", 1),
    ("CUBE", "Cube", "Show a cube icon", 2),
    ("EXTRUDE", "Extrude", "Show an upward arrow", 3),
)
_ACTION_LABELS = {identifier: label for identifier, label, _, _ in ACTION_ITEMS}
_ACTION_ICONS = {"ADD_CUBE": "CUBE", "EXTRUDE": "EXTRUDE"}
_SETTINGS = ("button_height", "font_size", "button_color")
_saved = None
_restored = False
_load_error = None


class BLENDERTOOLBAR_PG_button(bpy.types.PropertyGroup):
    button_id: bpy.props.StringProperty()
    label: bpy.props.StringProperty(name="Label", description="Leave blank for an icon-only button", maxlen=32)
    action: bpy.props.EnumProperty(name="Action", items=ACTION_ITEMS, default="ADD_CUBE")
    icon: bpy.props.EnumProperty(name="Icon", items=ICON_ITEMS, default="AUTO")


class BLENDERTOOLBAR_AP_preferences(bpy.types.AddonPreferences):
    bl_idname = _PACKAGE

    buttons: bpy.props.CollectionProperty(type=BLENDERTOOLBAR_PG_button)
    initialized: bpy.props.BoolProperty()
    button_height: bpy.props.IntProperty(name="Button Height", default=24, min=16, max=64)
    font_size: bpy.props.IntProperty(name="Font Size", default=11, min=8, max=24)
    button_color: bpy.props.FloatVectorProperty(
        name="Button Background", subtype="COLOR_GAMMA", size=3,
        min=0.0, max=1.0, default=(0.29, 0.29, 0.29),
    )


CLASSES = (BLENDERTOOLBAR_PG_button, BLENDERTOOLBAR_AP_preferences)


def get_preferences(context):
    """Look up the active add-on's preferences."""
    addon = context.preferences.addons.get(_PACKAGE)
    return addon.preferences if addon else None


def configured_buttons(context):
    """Read the configured labels and actions, with one button for a fresh installation."""
    preferences = current_layout(context)
    if preferences is None or not preferences.initialized:
        return (("", "ADD_CUBE", "CUBE"),)
    entries = []
    for button in preferences.buttons:
        label = button.label.strip()
        action = button.action
        icon = button.icon
        if icon == "AUTO" or (icon == "NONE" and not label):
            icon = _ACTION_ICONS[action]
        entries.append((label, action, icon))
    return tuple(entries)


def append_button(preferences):
    """Append a button with a stable identity."""
    button = preferences.buttons.add()
    button.button_id = uuid4().hex


def initialize(preferences):
    """Materialize the default layout when the setup dialog is first opened."""
    global _restored
    if _saved is not None and not _restored:
        for key in _SETTINGS:
            setattr(preferences, key, getattr(_saved, key))
        preferences.buttons.clear()
        for saved_button in _saved.buttons:
            button = preferences.buttons.add()
            for key, value in vars(saved_button).items():
                setattr(button, key, value)
        preferences.initialized = True
    _restored = True
    if not preferences.initialized:
        append_button(preferences)
        preferences.initialized = True


def _layout_path():
    return Path(bpy.utils.user_resource("CONFIG")) / "blender_toolbar" / "layout.json"


def current_layout(context):
    """Read the cached disk layout until Setup opens for editing."""
    return _saved if _saved is not None and not _restored else get_preferences(context)


def load_saved_layout():
    """Read and validate the disk layout once per add-on registration."""
    global _saved, _restored, _load_error
    _saved = _load_error = None
    _restored = False
    try:
        data = read_layout(_layout_path())
        if data is None:
            return
        for key, minimum, maximum in (("button_height", 16, 64), ("font_size", 8, 24)):
            if type(data[key]) is not int or not minimum <= data[key] <= maximum:
                raise ValueError(f"Invalid {key}")
        color = data["button_color"]
        if not isinstance(color, list) or len(color) != 3 or not all(
            type(channel) in (float, int) and 0 <= channel <= 1 for channel in color
        ):
            raise ValueError("Invalid button color")
        buttons = data["buttons"]
        if not isinstance(buttons, list) or len(buttons) > MAX_BUTTONS:
            raise ValueError("Invalid button list")
        entries = []
        ids = set()
        for button in buttons:
            if not isinstance(button, dict):
                raise ValueError("Invalid button entry")
            fields = {key: button[key] for key in ("button_id", "label", "action", "icon")}
            if not all(isinstance(value, str) for value in fields.values()):
                raise ValueError("Invalid button field")
            if (not fields["button_id"] or fields["button_id"] in ids
                    or len(fields["label"]) > 32
                    or fields["action"] not in _ACTION_LABELS
                    or fields["icon"] not in {item[0] for item in ICON_ITEMS}):
                raise ValueError("Invalid button settings")
            ids.add(fields["button_id"])
            entries.append(SimpleNamespace(**fields))
        _saved = SimpleNamespace(
            initialized=True, buttons=entries, **{key: data[key] for key in _SETTINGS}
        )
    except (OSError, KeyError, ValueError) as error:
        _load_error = str(error)


def layout_error():
    """Return a startup read error for display in Setup."""
    return _load_error


def save_layout(preferences):
    """Save the toolbar separately from Blender's installed add-on preferences."""
    if _load_error is not None:
        raise ValueError(f"Move the unreadable layout file before saving: {_layout_path()}")
    initialize(preferences)
    data = {
        "version": 1,
        "button_height": preferences.button_height,
        "font_size": preferences.font_size,
        "button_color": list(preferences.button_color),
        "buttons": [
            {key: getattr(button, key) for key in ("button_id", "label", "action", "icon")}
            for button in preferences.buttons
        ],
    }
    write_layout(_layout_path(), data)
