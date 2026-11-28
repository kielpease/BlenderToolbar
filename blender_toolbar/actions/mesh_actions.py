"""Dispatch supported mesh actions in the toolbar's window."""

import bpy

from dataclasses import dataclass, field

from ..integrations.spline_maker import unavailable_reason
from .viewports import resolve_viewport


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
    properties_context: str | None = None
    provider: str | None = None
    native_icon: str = "MESH_CUBE"
    undo_step: bool = False


_TOOLS = {"space_type": "VIEW_3D"}
ACTIONS = {
    "ADD_CUBE": Action(0, "Add Cube", "Add a cube at the 3D cursor", "mesh.primitive_cube_add", undo_step=True),
    "EXTRUDE": Action(1, "Extrude Region Tool", "Activate the Extrude Region gizmo", "wm.tool_set_by_id",
                      "EXTRUDE", "EDIT_MESH", properties={**_TOOLS, "name": "builtin.extrude_region"}),
    "ADD_UV_SPHERE": Action(2, "Add UV Sphere", "Add a sphere at the 3D cursor", "mesh.primitive_uv_sphere_add", undo_step=True),
    "ADD_CYLINDER": Action(3, "Add Cylinder", "Add a cylinder at the 3D cursor", "mesh.primitive_cylinder_add", undo_step=True),
    "ADD_PLANE": Action(4, "Add Plane", "Add a plane at the 3D cursor", "mesh.primitive_plane_add", undo_step=True),
    "MOVE_TOOL": Action(5, "Translate", "Activate the Move gizmo", "wm.tool_set_by_id",
                        "MOVE", properties={**_TOOLS, "name": "builtin.move"}, native_icon="TRANSFORM_MOVE"),
    "ROTATE_TOOL": Action(6, "Rotate Tool", "Activate the Rotate gizmo", "wm.tool_set_by_id",
                          "ROTATE", properties={**_TOOLS, "name": "builtin.rotate"}, native_icon="TRANSFORM_ROTATE"),
    "SCALE_TOOL": Action(7, "Scale Tool", "Activate the Scale gizmo", "wm.tool_set_by_id",
                         "SCALE", properties={**_TOOLS, "name": "builtin.scale"}, native_icon="TRANSFORM_SCALE"),
    "BEVEL": Action(8, "Bevel", "Interactively bevel selected edges in Mesh Edit Mode", "mesh.bevel",
                    "EXTRUDE", "EDIT_MESH", "INVOKE_DEFAULT"),
    "INSET": Action(9, "Inset Faces", "Interactively inset selected faces in Mesh Edit Mode", "mesh.inset",
                    "EXTRUDE", "EDIT_MESH", "INVOKE_DEFAULT"),
    "ADD_SPLINE": Action(10, "Draw Spline", "Draw with the optional Spline Maker tool", "spline_maker.draw_spline",
                         "SPLINE", execution="INVOKE_DEFAULT", provider="spline_maker", native_icon="CURVE_BEZCURVE"),
    "CONVERT_MESH": Action(11, "Convert to Mesh", "Convert selected objects to mesh in Object Mode", "object.convert",
                           "MESH", "OBJECT", properties={"target": "MESH"}, native_icon="OUTLINER_OB_MESH", undo_step=True),
    "MATERIALS": Action(12, "Materials", "Open the full Material Properties in a floating window", "",
                        "MATERIAL", properties_context="MATERIAL", native_icon="MATERIAL"),
    "RENDER_SETTINGS": Action(13, "Render Settings", "Open the full Render Properties in a floating window", "",
                              "RENDER", properties_context="RENDER", native_icon="RENDER_STILL"),
    "VIEWPORT": Action(14, "3D Viewport Window", "Open an interactive floating 3D Viewport", "",
                       "CUBE", properties_context="VIEW_3D", native_icon="VIEW3D"),
    "UNDO": Action(15, "Undo", "Undo the last Blender operation", "ed.undo", "UNDO", native_icon="LOOP_BACK"),
    "REDO": Action(16, "Redo", "Redo the last undone Blender operation", "ed.redo", "REDO", native_icon="LOOP_FORWARDS"),
    "RENAME_SELECTED": Action(17, "Rename Selected", "Rename the selected editable objects", "blender_toolbar.rename_selected",
                              "RENAME", "OBJECT", "INVOKE_DEFAULT", native_icon="GREASEPENCIL"),
    "LOCK_TRANSLATION": Action(18, "Lock Translation", "Lock X, Y and Z location for selected editable objects",
                               "blender_toolbar.set_location_lock", "LOCK", "OBJECT", properties={"locked": True}, native_icon="LOCKED", undo_step=True),
    "UNLOCK_TRANSLATION": Action(19, "Unlock Translation", "Unlock X, Y and Z location for selected editable objects",
                                 "blender_toolbar.set_location_lock", "UNLOCK", "OBJECT", properties={"locked": False}, native_icon="UNLOCKED", undo_step=True),
}
ACTION_ITEMS = tuple(
    (identifier, action.label, action.description, action.number)
    for identifier, action in ACTIONS.items()
)


def resolve_operator(entry: Action):
    """Resolve and inspect an operator lazily without importing external add-ons."""
    if entry.provider:
        reason = unavailable_reason()
        if reason:
            return None, reason
    namespace, name = entry.operator.split(".")
    operator = getattr(getattr(bpy.ops, namespace), name)
    try:
        rna = operator.get_rna_type()
    except (AttributeError, KeyError, RuntimeError):
        return None, f"{entry.label} is unavailable; its operator is not registered"
    if any(key not in rna.properties for key in entry.properties):
        return None, f"{entry.label} has unsupported operator properties"
    return operator, None


def action_error(context, entry: Action) -> str | None:
    """Check availability in the intended viewport immediately before execution."""
    if entry.properties_context:
        if entry.properties_context == "MATERIAL" and context.active_object is None:
            return "Select an object to open Material Properties"
        return None
    if entry.mode is not None and context.mode != entry.mode:
        return f"{entry.label} requires {entry.mode.replace('_', ' ').title()} Mode"
    if entry.operator == 'object.convert':
        active = context.active_object
        if active is None or active not in context.selected_editable_objects:
            return 'Select an editable active object to convert to mesh'
    operator, error = resolve_operator(entry)
    if error:
        return error
    if not operator.poll():
        return f"{entry.label} is unavailable for the current selection in the target viewport"
    return None


def open_editor(context, editor_context: str) -> str | None:
    """Duplicate the target area into a floating editor, preserving the source area."""
    if bpy.app.background:
        return "Floating editors require an interactive Blender window"
    previous = {window.as_pointer() for window in context.window_manager.windows}
    if not bpy.ops.screen.area_dupli.poll():
        return "Blender cannot open a floating editor from this area"
    result = bpy.ops.screen.area_dupli('INVOKE_DEFAULT')
    if 'FINISHED' not in result:
        return "Blender did not open the floating editor"
    window = next((window for window in context.window_manager.windows
                   if window.as_pointer() not in previous), None)
    if window is None:
        return "Blender did not expose the new editor window"
    area = window.screen.areas[0]
    area.type = 'VIEW_3D' if editor_context == 'VIEW_3D' else 'PROPERTIES'
    if editor_context != 'VIEW_3D':
        area.spaces.active.context = editor_context
    area.tag_redraw()
    return None


def execute_command(context, entry: Action, record_undo: bool):
    """Preserve one explicit undo step for synchronous edits nested in the mouse handler."""
    operator, error = resolve_operator(entry)
    if error:
        raise RuntimeError(error)
    result = operator(entry.execution, **entry.properties)
    # Blender does not add nested synchronous operators to undo history from
    # this handler. Only declared data edits get a step; modal tools, dialogs,
    # navigation, undo/redo, and editor windows keep their own native behavior.
    if (record_undo and entry.undo_step and 'FINISHED' in result
            and context.preferences.edit.use_global_undo and bpy.ops.ed.undo_push.poll()):
        bpy.ops.ed.undo_push(message=entry.label)
    return result


def run_action(context, window_x: int, action: str, popup: bool = False, record_undo: bool = False) -> str | None:
    """Run an action, open its editor, or show its command popup in the target viewport."""
    entry = ACTIONS.get(action)
    if entry is None:
        return "This toolbar action is unavailable"
    target, error = resolve_viewport(context)
    if error:
        return error
    viewport, region = target
    with context.temp_override(area=viewport, region=region):
        error = action_error(context, entry)
        if error:
            return error
        try:
            if entry.properties_context:
                return open_editor(context, entry.properties_context)
            if popup:
                result = bpy.ops.blender_toolbar.action_popup('INVOKE_DEFAULT', action=action,
                                                              viewport_id=str(viewport.as_pointer()))
            else:
                operator, error = resolve_operator(entry)
                if error:
                    return error
                result = execute_command(context, entry, record_undo)
        except (RuntimeError, TypeError, ValueError) as error:
            return f"{entry.label}: {error}"
        if not result.intersection({'FINISHED', 'RUNNING_MODAL'}):
            return f"{entry.label} did not complete"
    return None


def run_in_viewport(context, viewport_id: str, action: str, record_undo: bool = False) -> str | None:
    """Recheck a popup's original viewport without selecting a different window or area."""
    viewport = next((area for area in context.screen.areas
                     if str(area.as_pointer()) == viewport_id and area.type == 'VIEW_3D'), None)
    if viewport is None:
        return "The popup's target viewport is no longer available"
    region = next((region for region in viewport.regions if region.type == 'WINDOW'), None)
    if region is None:
        return "The target viewport has no window region"
    entry = ACTIONS.get(action)
    if entry is None or entry.properties_context:
        return "This command is unavailable"
    with context.temp_override(area=viewport, region=region):
        error = action_error(context, entry)
        if error:
            return error
        operator, error = resolve_operator(entry)
        if error:
            return error
        try:
            result = execute_command(context, entry, record_undo)
        except (RuntimeError, TypeError, ValueError) as error:
            return str(error)
        return None if result.intersection({'FINISHED', 'RUNNING_MODAL'}) else f"{entry.label} did not complete"
