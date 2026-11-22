"""Dispatch supported mesh actions in the toolbar's window."""

import bpy

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Action:
    number: int
    label: str
    description: str
    operator: str
    icon: str = "CUBE"
    mode: str | None = None
    execution: str = "EXEC_DEFAULT"
    properties: dict = field(default_factory=dict)


_TOOLS = {"space_type": "VIEW_3D"}
ACTIONS = {
    "ADD_CUBE": Action(0, "Add Cube", "Add a cube at the 3D cursor", "mesh.primitive_cube_add"),
    "EXTRUDE": Action(1, "Extrude Region Tool", "Activate the Extrude Region gizmo", "wm.tool_set_by_id",
                      "EXTRUDE", "EDIT_MESH", properties={**_TOOLS, "name": "builtin.extrude_region"}),
    "ADD_UV_SPHERE": Action(2, "Add UV Sphere", "Add a sphere at the 3D cursor", "mesh.primitive_uv_sphere_add"),
    "ADD_CYLINDER": Action(3, "Add Cylinder", "Add a cylinder at the 3D cursor", "mesh.primitive_cylinder_add"),
    "ADD_PLANE": Action(4, "Add Plane", "Add a plane at the 3D cursor", "mesh.primitive_plane_add"),
    "MOVE_TOOL": Action(5, "Move Tool", "Activate the Move gizmo", "wm.tool_set_by_id",
                        "EXTRUDE", properties={**_TOOLS, "name": "builtin.move"}),
    "ROTATE_TOOL": Action(6, "Rotate Tool", "Activate the Rotate gizmo", "wm.tool_set_by_id",
                          "EXTRUDE", properties={**_TOOLS, "name": "builtin.rotate"}),
    "SCALE_TOOL": Action(7, "Scale Tool", "Activate the Scale gizmo", "wm.tool_set_by_id",
                         "EXTRUDE", properties={**_TOOLS, "name": "builtin.scale"}),
    "BEVEL": Action(8, "Bevel", "Interactively bevel selected edges in Mesh Edit Mode", "mesh.bevel",
                    "EXTRUDE", "EDIT_MESH", "INVOKE_DEFAULT"),
    "INSET": Action(9, "Inset Faces", "Interactively inset selected faces in Mesh Edit Mode", "mesh.inset",
                    "EXTRUDE", "EDIT_MESH", "INVOKE_DEFAULT"),
}
ACTION_ITEMS = tuple(
    (identifier, action.label, action.description, action.number)
    for identifier, action in ACTIONS.items()
)


def run_action(context, window_x, action):
    """Run a configured action or return an explanation for an unavailable action."""
    entry = ACTIONS.get(action)
    if entry is None:
        return "This toolbar action is unavailable"
    target = _fallback_viewport(context, window_x)
    if target is None:
        return "Open a 3D Viewport in this window to use the toolbar"
    viewport, region = target
    with context.temp_override(area=viewport, region=region):
        if entry.mode is not None and context.mode != entry.mode:
            return f"{entry.label} requires Mesh Edit Mode"
        namespace, name = entry.operator.split(".")
        operator = getattr(getattr(bpy.ops, namespace), name)
        if not operator.poll():
            return f"{entry.label} is unavailable in the target viewport"
        try:
            result = operator(entry.execution, **entry.properties)
        except RuntimeError as error:
            return f"{entry.label}: {error}"
        if not result.intersection({"FINISHED", "RUNNING_MODAL"}):
            return f"{entry.label} did not complete"
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
