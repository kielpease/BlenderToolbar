"""Register explicit resources in order and release them in reverse order."""

from contextlib import ExitStack

import bpy

from .actions import selection, viewports
from .preferences.buttons import CLASSES as PREFERENCE_CLASSES, load_saved_layout
from .ui import popups, setup, text_host

_resources = None
_CLASSES = (*PREFERENCE_CLASSES, *selection.CLASSES, *popups.CLASSES,
            setup.BLENDERTOOLBAR_OT_edit_buttons, setup.BLENDERTOOLBAR_OT_choose_action,
            text_host.BLENDERTOOLBAR_OT_toggle_host, text_host.BLENDERTOOLBAR_OT_click_button,
            text_host.BLENDERTOOLBAR_OT_setup, text_host.BLENDERTOOLBAR_OT_hover_button,
            viewports.BLENDERTOOLBAR_OT_remember_viewport)


def register():
    """Install classes, drawing hooks, pass-through input observers, and load cleanup."""
    global _resources
    if _resources is not None:
        return
    load_saved_layout()
    with ExitStack() as resources:
        for cls in _CLASSES:
            bpy.utils.register_class(cls)
            resources.callback(bpy.utils.unregister_class, cls)
        bpy.types.TEXT_HT_header.append(text_host._draw_header)
        resources.callback(bpy.types.TEXT_HT_header.remove, text_host._draw_header)
        handle = bpy.types.SpaceTextEditor.draw_handler_add(text_host._draw_toolbar, (), 'WINDOW', 'POST_PIXEL')
        resources.callback(bpy.types.SpaceTextEditor.draw_handler_remove, handle, 'WINDOW')
        keyconfig = bpy.context.window_manager.keyconfigs.addon
        if keyconfig is not None:
            keymap = keyconfig.keymaps.new(name='Text', space_type='TEXT_EDITOR')
            for operator, event_type, value in (
                (text_host.BLENDERTOOLBAR_OT_click_button, 'LEFTMOUSE', 'PRESS'),
                (text_host.BLENDERTOOLBAR_OT_setup, 'RIGHTMOUSE', 'PRESS'),
                (text_host.BLENDERTOOLBAR_OT_hover_button, 'MOUSEMOVE', 'ANY'),
            ):
                item = keymap.keymap_items.new(operator.bl_idname, event_type, value, head=True)
                resources.callback(keymap.keymap_items.remove, item)
            keymap = keyconfig.keymaps.new(name='3D View', space_type='VIEW_3D', region_type='WINDOW')
            for event_type, value in (
                ('LEFTMOUSE', 'PRESS'), ('MIDDLEMOUSE', 'PRESS'), ('RIGHTMOUSE', 'PRESS'),
                ('WHEELUPMOUSE', 'PRESS'), ('WHEELDOWNMOUSE', 'PRESS'),
                ('TRACKPADPAN', 'ANY'), ('TRACKPADZOOM', 'ANY'), ('NDOF_MOTION', 'ANY'),
            ):
                item = keymap.keymap_items.new(viewports.BLENDERTOOLBAR_OT_remember_viewport.bl_idname,
                                              event_type, value, any=True, head=True)
                resources.callback(keymap.keymap_items.remove, item)
        bpy.app.handlers.load_post.append(viewports.clear_targets)
        resources.callback(bpy.app.handlers.load_post.remove, viewports.clear_targets)
        resources.callback(viewports.clear_targets)
        resources.callback(text_host._hover.clear)
        _resources = resources.pop_all()


def unregister():
    """Remove owned resources and cached viewport pointers, including partial registrations."""
    global _resources
    if _resources is not None:
        resources, _resources = _resources, None
        resources.close()
