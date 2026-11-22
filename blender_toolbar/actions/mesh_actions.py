"""Dispatch supported mesh actions in the toolbar's window."""

import bpy

ACTION_ITEMS = (
    ("ADD_CUBE", "Add Cube", "Add a cube at the 3D cursor", 0),
    ("EXTRUDE", "Extrude", "Activate the Extrude Region gizmo in Mesh Edit Mode", 1),
)


def run_action(context, window_x, action):
    """Run a configured action or return an explanation for an unavailable action."""
    target = _fallback_viewport(context, window_x)
    if target is None:
        return "Open a 3D Viewport in this window to use the toolbar"
    viewport, region = target
    with context.temp_override(area=viewport, region=region):
        if action == "EXTRUDE":
            if context.mode != "EDIT_MESH":
                return "Extrude requires Mesh Edit Mode"
            operator = bpy.ops.wm.tool_set_by_id
            properties = {"name": "builtin.extrude_region", "space_type": "VIEW_3D"}
            label = "Extrude"
        elif action == "ADD_CUBE":
            operator = bpy.ops.mesh.primitive_cube_add
            properties = {}
            label = "Add Cube"
        else:
            return "This toolbar action is unavailable"
        if not operator.poll():
            return f"{label} is unavailable in the target viewport"
        if "FINISHED" not in operator("EXEC_DEFAULT", **properties):
            return f"{label} did not complete"
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
