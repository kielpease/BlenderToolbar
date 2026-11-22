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
