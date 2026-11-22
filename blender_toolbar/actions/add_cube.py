"""Run the prototype cube action in a viewport in the toolbar's window."""

import bpy

def add_cube(context, window_x):
    """Add a cube in a viewport selected by its position relative to the click."""
    target = _fallback_viewport(context, window_x)
    if target is None:
        return "Open a 3D Viewport in this window to add a cube"
    viewport, region = target
    with context.temp_override(area=viewport, region=region):
        operator = bpy.ops.mesh.primitive_cube_add
        if not operator.poll():
            return "Add Cube is unavailable in the target viewport"
        if "FINISHED" not in operator("EXEC_DEFAULT"):
            return "Add Cube did not complete"
    return None


def _fallback_viewport(context, window_x):
    def distance(area):
        horizontal = max(area.x - window_x, window_x - (area.x + area.width - 1), 0)
        vertical = max(context.area.y - (area.y + area.height), area.y - (
            context.area.y + context.area.height
        ), 0)
        return horizontal, vertical, -area.width * area.height

    viewports = (area for area in context.screen.areas if area.type == "VIEW_3D")
    viewport = min(viewports, key=distance, default=None)
    if viewport is None:
        return None
    region = next((region for region in viewport.regions if region.type == "WINDOW"), None)
    if region is None:
        return None
    return viewport, region
