"""Prototype a saved, opt-in toolbar area using a Text Editor host."""

from contextlib import ExitStack

import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from ..actions.mesh_actions import run_action
from ..preferences.buttons import (
    CLASSES, configured_buttons, current_layout, get_preferences, initialize,
    load_saved_layout, save_layout,
)
from .setup import BLENDERTOOLBAR_OT_choose_action, BLENDERTOOLBAR_OT_edit_buttons, draw_setup


_MARKER = "blender_toolbar_host"
_resources = None
_BUTTON_LABEL = "Add Cube"
_hover = {}
_BACKGROUND = (0.13, 0.13, 0.13, 1)


def is_toolbar(space):
    """Return whether the space displays a toolbar marker saved with the file."""
    if space is None or space.type != "TEXT_EDITOR":
        return False
    text = space.text
    return (
        text is not None
        and text.get(_MARKER) == 1
        and len(text.lines) == 1
        and not text.lines[0].body
    )


class BLENDERTOOLBAR_OT_toggle_host(bpy.types.Operator):
    """Switch an empty Text Editor area into or out of toolbar mode."""

    bl_idname = "blender_toolbar.toggle_host"
    bl_label = "Toggle Toolbar Mode"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (
            space is not None
            and space.type == "TEXT_EDITOR"
            and (space.text is None or is_toolbar(space))
        )

    def execute(self, context):
        space = context.space_data
        if is_toolbar(space):
            space.text = None
        else:
            marker = bpy.data.texts.new("BlenderToolbar Host")
            marker[_MARKER] = 1
            space.text = marker
        context.area.tag_redraw()
        return {"FINISHED"}


def _draw_header(self, context):
    if is_toolbar(context.space_data):
        self.layout.operator("blender_toolbar.toggle_host", text="Exit Toolbar Mode")
        self.layout.operator("blender_toolbar.setup")
    elif context.space_data.text is None:
        self.layout.operator("blender_toolbar.toggle_host", text="Use as Toolbar")


class BLENDERTOOLBAR_OT_setup(bpy.types.Operator):
    bl_idname = "blender_toolbar.setup"
    bl_label = "BlenderToolbar Setup"

    @classmethod
    def poll(cls, context):
        return is_toolbar(context.space_data) and get_preferences(context) is not None

    def invoke(self, context, event):
        initialize(get_preferences(context))
        return context.window_manager.invoke_props_dialog(
            self, width=560, confirm_text="Save Toolbar"
        )

    def draw(self, context):
        draw_setup(self.layout, get_preferences(context))

    def execute(self, context):
        try:
            save_layout(get_preferences(context))
        except (OSError, ValueError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        return {"FINISHED"}


def _button_bounds(context):
    scale = context.preferences.system.ui_scale or 1.0
    region_height = context.region.height
    preferences = current_layout(context)
    button_height = preferences.button_height if preferences else 24
    height = min(button_height * scale, region_height - 8 * scale)
    if context.region.width < 38 * scale or height < 16 * scale:
        return
    bottom = (region_height - height) / 2
    yield None, "", "SETUP", (6 * scale, bottom, 32 * scale, bottom + height)
    left = 44 * scale
    for label, action, icon in configured_buttons(context):
        width = max((100 if label else 28) * scale, height)
        if left + width > context.region.width - 6 * scale:
            break
        yield action, label, icon, (left, bottom, left + width, bottom + height)
        left += width + 6 * scale


class BLENDERTOOLBAR_OT_click_button(bpy.types.Operator):
    """Dispatch a click inside the prototype button."""

    bl_idname = "blender_toolbar.click_button"
    bl_label = _BUTTON_LABEL
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        return (
            context.region is not None
            and context.region.type == "WINDOW"
            and is_toolbar(context.space_data)
        )

    def invoke(self, context, event):
        for action, _, _, (left, bottom, right, top) in _button_bounds(context):
            if left <= event.mouse_region_x < right and bottom <= event.mouse_region_y < top:
                if action is None:
                    result = bpy.ops.blender_toolbar.setup("INVOKE_DEFAULT")
                    return {"CANCELLED"} if "CANCELLED" in result else {"FINISHED"}
                error = run_action(context, event.mouse_x, action)
                if error is not None:
                    self.report({"WARNING"}, error)
                return {"FINISHED"}
        return {"PASS_THROUGH"}


class BLENDERTOOLBAR_OT_hover_button(bpy.types.Operator):
    bl_idname = "blender_toolbar.hover_button"
    bl_label = "Highlight Toolbar Button"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        return BLENDERTOOLBAR_OT_click_button.poll(context)

    def invoke(self, context, event):
        key = context.window.as_pointer()
        area = context.area.as_pointer()
        x, y = event.mouse_region_x, event.mouse_region_y
        index = next(
            (index for index, (_, _, _, (left, bottom, right, top)) in enumerate(_button_bounds(context))
             if left <= x < right and bottom <= y < top),
            None,
        )
        state = (area, index)
        if _hover.get(key) != state:
            _hover[key] = state
            context.area.tag_redraw()
        if index is not None:
            context.window.cursor_set("DEFAULT")
        return {"PASS_THROUGH"}


def _draw_rectangle(shader, bounds, color):
    left, bottom, right, top = bounds
    vertices = ((left, bottom), (right, bottom), (left, top), (right, top))
    shader.uniform_float("color", color)
    batch_for_shader(shader, "TRI_STRIP", {"pos": vertices}).draw(shader)


_ICON_LINES = {
    "CUBE": (
        ((0, 0.25), (0.5, 0), (1, 0.25), (1, 0.75), (0.5, 1), (0, 0.75), (0, 0.25)),
        ((0, 0.75), (0.5, 0.5), (1, 0.75)),
        ((0.5, 0.5), (0.5, 0)),
    ),
    "EXTRUDE": (
        ((0.5, 0.17), (0.5, 1)),
        ((0.16, 0.66), (0.5, 1), (0.84, 0.66)),
        ((0.08, 0), (0.92, 0)),
    ),
}


def _foreground(color):
    luminance = sum(channel * weight for channel, weight in zip(color, (0.2126, 0.7152, 0.0722)))
    value = 0.08 if luminance > 0.55 else 0.95
    return value, value, value, 1


def _draw_icon(shader, icon, left, center_y, size, color):
    if icon == "SETUP":
        center_x = left + size / 2
        radius = size * 0.12
        for offset in (-0.34, 0, 0.34):
            y = center_y + offset * size
            _draw_rectangle(shader, (center_x - radius, y - radius, center_x + radius, y + radius), color)
        return
    shader.uniform_float("color", color)
    for line in _ICON_LINES[icon]:
        points = [(left + x * size, center_y + (y - 0.5) * size) for x, y in line]
        batch_for_shader(shader, "LINE_STRIP", {"pos": points}).draw(shader)


def _draw_toolbar():
    context = bpy.context
    if not is_toolbar(context.space_data):
        return
    shader = gpu.shader.from_builtin("UNIFORM_COLOR")
    shader.bind()
    _draw_rectangle(shader, (0, 0, context.region.width, context.region.height), _BACKGROUND)
    preferences = current_layout(context)
    button_color = tuple(preferences.button_color) if preferences else (0.29, 0.29, 0.29)
    font = 0
    scale = context.preferences.system.ui_scale or 1.0
    font_size = preferences.font_size if preferences else 11
    hovered = _hover.get(context.window.as_pointer())
    area = context.area.as_pointer()
    for index, (_, label, icon, bounds) in enumerate(_button_bounds(context)):
        is_hovered = hovered == (area, index)
        color = _BACKGROUND[:3]
        if icon != "SETUP":
            color = tuple(channel * 0.8 + 0.2 for channel in button_color) if is_hovered else button_color
            _draw_rectangle(shader, bounds, (*color, 1))
        foreground = _foreground(color)
        left, bottom, right, top = bounds
        blf.size(font, min(font_size * scale, (top - bottom) * 0.8))
        icon_size = (top - bottom) * 0.5
        if not label:
            _draw_icon(shader, icon, (left + right - icon_size) / 2, (bottom + top) / 2, icon_size, foreground)
            continue
        if icon != "NONE":
            _draw_icon(shader, icon, left + 6, (bottom + top) / 2, icon_size, foreground)
            left += icon_size + 10
        while len(label) > 1 and blf.dimensions(font, label)[0] > (right - left) * 0.85:
            label = label[:-2].rstrip() + "…" if len(label) > 2 else "…"
        width, height = blf.dimensions(font, label)
        blf.position(font, (left + right - width) / 2, (bottom + top - height) / 2, 0)
        blf.color(font, *foreground)
        blf.draw(font, label)


def register():
    """Install the opt-in header control and area drawing hook."""
    global _resources
    if _resources is not None:
        return
    load_saved_layout()
    with ExitStack() as resources:
        for cls in (*CLASSES, BLENDERTOOLBAR_OT_toggle_host, BLENDERTOOLBAR_OT_click_button,
                    BLENDERTOOLBAR_OT_setup, BLENDERTOOLBAR_OT_edit_buttons,
                    BLENDERTOOLBAR_OT_hover_button, BLENDERTOOLBAR_OT_choose_action):
            bpy.utils.register_class(cls)
            resources.callback(bpy.utils.unregister_class, cls)
        bpy.types.TEXT_HT_header.append(_draw_header)
        resources.callback(bpy.types.TEXT_HT_header.remove, _draw_header)
        handle = bpy.types.SpaceTextEditor.draw_handler_add(
            _draw_toolbar, (), "WINDOW", "POST_PIXEL"
        )
        resources.callback(bpy.types.SpaceTextEditor.draw_handler_remove, handle, "WINDOW")
        keyconfig = bpy.context.window_manager.keyconfigs.addon
        if keyconfig is not None:
            keymap = keyconfig.keymaps.new(name="Text", space_type="TEXT_EDITOR")
            for operator, event_type, value in (
                (BLENDERTOOLBAR_OT_click_button, "LEFTMOUSE", "PRESS"),
                (BLENDERTOOLBAR_OT_setup, "RIGHTMOUSE", "RELEASE"),
                (BLENDERTOOLBAR_OT_hover_button, "MOUSEMOVE", "ANY"),
            ):
                item = keymap.keymap_items.new(operator.bl_idname, event_type, value, head=True)
                resources.callback(keymap.keymap_items.remove, item)
        resources.callback(_hover.clear)
        _resources = resources.pop_all()


def unregister():
    """Remove the drawing hook and header control in reverse order."""
    global _resources
    if _resources is not None:
        resources, _resources = _resources, None
        resources.close()
