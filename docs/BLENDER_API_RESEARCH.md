# Blender 5.2 Python API investigation

This records the original Python add-on investigation. The current
[architecture proposal](ARCHITECTURE.md) uses a designated Text Editor area.
The [Space API](https://docs.blender.org/api/5.2/bpy.types.Space.html) documents
region draw handlers. The prototype still needs to verify area-specific drawing,
input handling, and restoration when loading the saved startup workspace.

Investigated 2026-11-20 using official, versioned 5.2 API references. Intended
runtime is Blender 5.2.4 LTS. No Blender binary was found on PATH during setup;
no runtime test or exact patch-version compatibility claim has been made.
Direct page fetches were unavailable through the research tool; the findings
below were checked against indexed excerpts of the linked official references.

## Supported UI boundaries

[Registration utilities](https://docs.blender.org/api/5.2/bpy.utils.html) list
registerable classes such as Header, Panel, Menu, and Operator, but not Space or
a new editor type. The architectural inference is that a standard Python add-on
must use an existing editor rather than register a completely new one. This
project will not depend on native Blender modifications.

[Header](https://docs.blender.org/api/5.2/bpy.types.Header.html) documents editor
and region targeting plus append, prepend, and remove draw hooks. These provide
a supported route for extending existing header UI; they do not promise an
independent dockable toolbar region.

[UILayout](https://docs.blender.org/api/5.2/bpy.types.UILayout.html) provides
native layout controls and panel popovers. Proposed use: a horizontal row of
configuration-driven buttons with menus/popovers. Actual width and overflow
behavior remain an implementation experiment after approval.

[WindowManager](https://docs.blender.org/api/5.2/bpy.types.WindowManager.html)
exposes popup_menu, invoke_popup, and invoke_props_dialog. A properties dialog
executes on confirmation; a popup can present properties without execution.
These APIs support the planned menu/dialog actions without a custom editor.

## Context and resource handling

The [operator quickstart](https://docs.blender.org/api/5.2/info_quickstart.html)
explains that operator poll can fail for the current area or mode. Built-in
operators therefore need explicit availability/context handling.
[Context.temp_override](https://docs.blender.org/api/5.2/bpy.types.Context.html)
supports temporary window/area/region overrides, whose members must be
consistent. The proposed dispatcher targets the originating viewport rather
than assuming header context is sufficient for every operator.

[Preview utilities](https://docs.blender.org/api/5.2/bpy.utils.previews.html)
support custom previews used through icon_value, with explicit collection
creation/removal. This is a future icon implementation option, not a current
feature or a reason to persist runtime icon IDs.

## Options for review

| Host | Assessment |
| --- | --- |
| Existing 3D Viewport header | Proposed first choice; native horizontal UI, shared limited width |
| Sidebar panel with a row | Useful for configuration; insufficient as the primary horizontal shelf |
| Popup/popover | Suitable secondary UI; transient rather than persistent toolbar |
| Custom GPU overlay | Deferred; would require custom input, hit testing, and layout |
| New editor type | Excluded from the supported Python architecture |

The original host recommendation above was a design judgment based on these APIs, not proof
that every desired shelf interaction is possible. After review, verify hooks,
region context, built-in operator invocation, menus, dialog cancellation,
scaling/overflow, multiple windows, and cleanup in the exact target binary.


## Floating editors and optional commands (2026-11-27)

The versioned [Screen operators](https://docs.blender.org/api/5.2/bpy.ops.screen.html)
and [Properties space](https://docs.blender.org/api/5.2/bpy.types.SpaceProperties.html)
are the reference contracts for duplicating an area into a new window and
choosing its Properties context. Fetching those versioned pages was unavailable
through the research tool; runtime investigation uses installed Blender 5.2.5
LTS (5f2fd03c4701). `screen.area_dupli` has no execute callback in this build;
calling it with EXEC_DEFAULT is invalid, so the implementation uses INVOKE_DEFAULT.
No compatibility claim for 5.2.4 follows from this 5.2.5 verification.

The [WindowManager API](https://docs.blender.org/api/5.2/bpy.types.WindowManager.html)
documents invoke_popup for transient operator UI. The launcher keeps execution
in actions/ and rechecks the original viewport on the command click. Missing
operator RNA raises KeyError in Blender 5.2.5; the lazy lookup handles that case.


## Last-interacted viewport and synchronous undo (0.1.17)

The versioned [KeyMapItems API](https://docs.blender.org/api/5.2/bpy.types.KeyMapItems.html)
documents `new(..., any=True, head=True)`. A pass-through View3D operator can
observe input without consuming the selection/navigation event. Blender 5.2.5
interactive checks confirmed that clicking the perspective view selected the
same area used by the subsequent Spline Maker modal invocation, even though the
Spline button was positioned above/below the camera view. Cancellation worked.

The [Object API](https://docs.blender.org/api/5.2/bpy.types.Object.html) and
[Object operators](https://docs.blender.org/api/5.2/bpy.ops.object.html) are the
references for location locks and selected-object conversion. Runtime checks
covered selected curves, selected meshes, preservation of an unselected curve,
Object/Edit Mode rejection, and multi-object rename/lock changes.

Interactive undo testing found that nested synchronous selection edits were
missing from history until explicitly recorded with
[ed.undo_push](https://docs.blender.org/api/5.2/bpy.ops.ed.html). One toolbar Undo
then restored all three prior lock flags, and Redo reapplied them. This finding
is verified on Blender 5.2.5 LTS (5f2fd03c4701), not on target 5.2.4.
