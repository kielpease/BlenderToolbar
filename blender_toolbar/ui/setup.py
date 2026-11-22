"""Edit the prototype button list from a popup in the toolbar area."""

import bpy

from ..preferences.buttons import MAX_BUTTONS, append_button, get_preferences, initialize, layout_error


class BLENDERTOOLBAR_OT_edit_buttons(bpy.types.Operator):
    bl_idname = "blender_toolbar.edit_buttons"
    bl_label = "Edit Toolbar Buttons"
    bl_options = {"INTERNAL"}

    operation: bpy.props.EnumProperty(items=(
        ("ADD", "Add", ""),
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
        if self.operation == "ADD":
            if len(buttons) >= MAX_BUTTONS:
                return {"CANCELLED"}
            append_button(preferences)
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


def draw_setup(layout, preferences):
    """Draw the live settings."""
    columns = layout.row()
    columns.label(text="Label")
    columns.label(text="Action")
    columns.label(text="Icon")
    if layout_error():
        layout.label(text=f"Layout could not load: {layout_error()}", icon="ERROR")
    for index, button in enumerate(preferences.buttons):
        row = layout.row(align=True)
        row.prop(button, "label", text="")
        row.prop(button, "action", text="")
        row.prop(button, "icon", text="")
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
    colors = layout.row()
    colors.prop(preferences, "button_color")
    sizes = layout.row()
    sizes.prop(preferences, "button_height")
    sizes.prop(preferences, "font_size")
