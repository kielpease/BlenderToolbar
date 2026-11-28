"""Selection commands with Blender-native undo and explicit Object Mode checks."""

import bpy


def selected_editable(context) -> list:
    """Return selected objects whose properties can be changed in this view layer."""
    return list(context.selected_editable_objects)


class BLENDERTOOLBAR_OT_set_location_lock(bpy.types.Operator):
    bl_idname = 'blender_toolbar.set_location_lock'
    bl_label = 'Set Selected Translation Locks'
    bl_options = {'REGISTER', 'UNDO'}

    locked: bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and bool(selected_editable(context))

    def execute(self, context):
        objects = selected_editable(context)
        for obj in objects:
            obj.lock_location = (self.locked,) * 3
        self.report({'INFO'}, f"{'Locked' if self.locked else 'Unlocked'} translation on {len(objects)} object(s)")
        return {'FINISHED'}


class BLENDERTOOLBAR_OT_rename_selected(bpy.types.Operator):
    bl_idname = 'blender_toolbar.rename_selected'
    bl_label = 'Rename Selected Objects'
    bl_options = {'REGISTER', 'UNDO'}

    base_name: bpy.props.StringProperty(name='Name', maxlen=63)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and bool(selected_editable(context))

    def invoke(self, context, event):
        objects = selected_editable(context)
        active = context.active_object
        self.base_name = active.name if active in objects else objects[0].name
        return context.window_manager.invoke_props_dialog(self, width=360, confirm_text='Rename')

    def draw(self, context):
        self.layout.prop(self, 'base_name')
        count = len(selected_editable(context))
        if count > 1:
            self.layout.label(text=f'{count} objects: Name_001, Name_002, ...')

    def execute(self, context):
        name = self.base_name.strip()
        if not name:
            self.report({'WARNING'}, 'Enter a non-empty name')
            return {'CANCELLED'}
        objects = selected_editable(context)
        if not objects:
            self.report({'WARNING'}, 'No editable objects are selected')
            return {'CANCELLED'}
        active = context.active_object
        objects.sort(key=lambda obj: (obj != active, obj.name))
        for index, obj in enumerate(objects, 1):
            obj.name = name if len(objects) == 1 else f'{name}_{index:03}'
        return {'FINISHED'}


CLASSES = (BLENDERTOOLBAR_OT_set_location_lock, BLENDERTOOLBAR_OT_rename_selected)
