"""Edit the prototype button list from a popup in the toolbar area."""

import bpy

from ..actions.mesh_actions import ACTION_ITEMS, ACTIONS
from ..preferences.buttons import MAX_BUTTONS, append_button, get_preferences, initialize, layout_error


class BLENDERTOOLBAR_OT_edit_buttons(bpy.types.Operator):
    bl_idname = "blender_toolbar.edit_buttons"
    bl_label = "Edit Toolbar Buttons"
    bl_options = {"INTERNAL"}

    operation: bpy.props.EnumProperty(items=(
        ("ADD", "Add", ""),
        ("SEPARATOR", "Add Separator", ""),
        ("REMOVE", "Remove", ""),
        ("UP", "Move Left", ""),
        ("DOWN", "Move Right", ""),
    ))
    index: bpy.props.IntProperty(default=-1)

    def execute(self, context):
        preferences = get_preferences(context)
        if preferences is None:
            return {"CANCELLED"}
        initialize(preferences)
        buttons = preferences.buttons
        if self.operation in {"ADD", "SEPARATOR"}:
            if len(buttons) >= MAX_BUTTONS:
                return {"CANCELLED"}
            append_button(preferences)
            if self.operation == "SEPARATOR":
                buttons[-1].kind = "SEPARATOR"
                buttons[-1].icon = "NONE"
        elif not 0 <= self.index < len(buttons):
            return {"CANCELLED"}
        elif self.operation == "REMOVE":
            buttons.remove(self.index)
        else:
            destination = self.index + (-1 if self.operation == "UP" else 1)
            if not 0 <= destination < len(buttons):
                return {"CANCELLED"}
            buttons.move(self.index, destination)
        if context.area is not None:
            context.area.tag_redraw()
        return {"FINISHED"}


class BLENDERTOOLBAR_OT_choose_action(bpy.types.Operator):
    """Search supported Blender actions for one toolbar button."""

    bl_idname = "blender_toolbar.choose_action"
    bl_label = "Search Toolbar Actions"
    bl_options = {"INTERNAL"}
    bl_property = "action"

    button_id: bpy.props.StringProperty()
    action: bpy.props.EnumProperty(items=ACTION_ITEMS, default="ADD_CUBE")

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        preferences = get_preferences(context)
        if preferences is None:
            return {"CANCELLED"}
        for button in preferences.buttons:
            if button.button_id == self.button_id:
                button.action = self.action
                if ACTIONS[self.action].properties_context:
                    button.popup = True
                if context.area is not None:
                    context.area.tag_redraw()
                return {"FINISHED"}
        self.report({"WARNING"}, "The toolbar button was removed")
        return {"CANCELLED"}


def draw_setup(layout, preferences):
    """Draw the live settings."""
    columns = layout.row()
    columns.label(text="Label")
    columns.label(text="Action")
    columns.label(text="Icon")
    columns.label(text="Popup")
    if layout_error():
        layout.label(text=f"Layout could not load: {layout_error()}", icon="ERROR")
    for index, button in enumerate(preferences.buttons):
        row = layout.row(align=True)
        row.prop(button, "label", text="")
        picker = row.row(align=True)
        picker.enabled = button.kind == "BUTTON"
        picker.operator_context = "INVOKE_DEFAULT"
        choose = picker.operator("blender_toolbar.choose_action", text="Separator / Group" if button.kind == "SEPARATOR" else ACTIONS[button.action].label, icon="VIEWZOOM")
        choose.button_id = button.button_id
        choose.action = button.action
        icon = row.row(align=True)
        icon.enabled = button.kind == "BUTTON"
        icon.prop(button, "icon", text="")
        popup = row.row(align=True)
        popup.enabled = button.kind == "BUTTON" and ACTIONS[button.action].properties_context is None
        popup.prop(button, "popup", text="Popup")
        for operation, icon, enabled in (
            ("UP", "TRIA_UP", index > 0),
            ("DOWN", "TRIA_DOWN", index < len(preferences.buttons) - 1),
            ("REMOVE", "X", True),
        ):
            control = row.row(align=True)
            control.enabled = enabled
            edit = control.operator("blender_toolbar.edit_buttons", text="", icon=icon)
            edit.operation = operation
            edit.index = index
    row = layout.row()
    row.enabled = len(preferences.buttons) < MAX_BUTTONS
    row.operator("blender_toolbar.edit_buttons", text="Add Button", icon="ADD").operation = "ADD"
    row.operator("blender_toolbar.edit_buttons", text="Add Separator", icon="REMOVE").operation = "SEPARATOR"
    layout.label(text="Name a separator to label a group. Click a viewport before using its commands.")
    layout.label(text="Popup: command launcher. Materials / Render / Viewport: full floating editors.")
    colors = layout.row()
    colors.prop(preferences, "button_color")
    sizes = layout.row()
    sizes.prop(preferences, "button_height")
    sizes.prop(preferences, "font_size")
