"""Remember explicit viewport interaction without a modal watcher or timer."""

import bpy
from bpy.app.handlers import persistent

# Store integers only. Resolve them against the current screen before every action.
_targets: dict[int, tuple[int, int]] = {}


@persistent
def clear_targets(_unused=None) -> None:
    """Forget targets when files load and when the add-on is disabled."""
    _targets.clear()


def remember_viewport(context) -> None:
    """Remember the viewport receiving a click or navigation event in this window."""
    _targets[context.window.as_pointer()] = (
        context.screen.as_pointer(), context.area.as_pointer(),
    )


def resolve_viewport(context):
    """Return the last interacted viewport, or the sole viewport; never guess among several."""
    viewports = [area for area in context.screen.areas if area.type == 'VIEW_3D']
    target = _targets.get(context.window.as_pointer())
    viewport = next((area for area in viewports if target == (
        context.screen.as_pointer(), area.as_pointer())), None)
    if viewport is None and len(viewports) == 1:
        viewport = viewports[0]
    if viewport is None:
        return None, 'Click or navigate in the 3D Viewport you want to use, then click the toolbar'
    region = next((region for region in viewport.regions if region.type == 'WINDOW'), None)
    if region is None:
        return None, 'The target viewport has no window region'
    return (viewport, region), None


class BLENDERTOOLBAR_OT_remember_viewport(bpy.types.Operator):
    """Observe viewport input and let Blender continue processing the same event."""

    bl_idname = 'blender_toolbar.remember_viewport'
    bl_label = 'Remember Toolbar Viewport'
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return (context.window is not None and context.area is not None
                and context.area.type == 'VIEW_3D' and context.region is not None
                and context.region.type == 'WINDOW')

    def invoke(self, context, event):
        remember_viewport(context)
        return {'PASS_THROUGH'}
