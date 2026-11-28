"""Interactive command popups; execution policy belongs to actions."""

import bpy

from ..actions.mesh_actions import ACTION_ITEMS, ACTIONS, run_in_viewport


class BLENDERTOOLBAR_OT_run_popup_action(bpy.types.Operator):
    bl_idname = "blender_toolbar.run_popup_action"
    bl_label = "Run Toolbar Action"
    bl_options = {"INTERNAL"}

    action: bpy.props.EnumProperty(items=ACTION_ITEMS)
    viewport_id: bpy.props.StringProperty()

    def execute(self, context):
        error = run_in_viewport(context, self.viewport_id, self.action, record_undo=True)
        if error:
            self.report({'WARNING'}, error)
            return {'CANCELLED'}
        return {'FINISHED'}


class BLENDERTOOLBAR_OT_action_popup(bpy.types.Operator):
    bl_idname = "blender_toolbar.action_popup"
    bl_label = "Toolbar Action"
    bl_options = {"INTERNAL"}

    action: bpy.props.EnumProperty(items=ACTION_ITEMS)
    viewport_id: bpy.props.StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)

    def draw(self, context):
        entry = ACTIONS[self.action]
        self.layout.label(text=entry.label, icon=entry.native_icon)
        self.layout.label(text=entry.description)
        self.layout.operator_context = 'EXEC_DEFAULT'
        command = self.layout.operator('blender_toolbar.run_popup_action', text=entry.label,
                                       icon=entry.native_icon)
        command.action = self.action
        command.viewport_id = self.viewport_id

    def execute(self, context):
        return {'FINISHED'}


CLASSES = (BLENDERTOOLBAR_OT_run_popup_action, BLENDERTOOLBAR_OT_action_popup)
