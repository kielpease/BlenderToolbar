# Architecture proposal

Status: Text Editor host prototype underway. The remaining feature design is
awaiting review. Target: Blender 5.2.4 LTS. See [API research](BLENDER_API_RESEARCH.md).

## UI host

The approved Phase 1 direction is a horizontal toolbar hosted in a designated
Text Editor area in stock Blender. Users activate toolbar mode in that area
and can restore normal editing there. Other Text Editor areas retain their
normal behavior. Blender's Editor Type picker continues to show Text Editor.

Prototype supported drawing and input hooks for the designated area. Verify
area resizing, horizontal overflow, UI scaling, and multiple windows. Check
that input outside toolbar mode continues to reach the Text Editor.
Viewport-dependent actions need an explicit target because clicks originate
in the Text Editor host.

The prototype uses a tagged empty Text datablock as the host marker. Blender
saves the area's datablock selection with the workspace, so reopening the UI
restores toolbar mode without matching area coordinates. The marker is visible
in the Text Editor's datablock selector. Selecting it in a second area or
duplicating an area that carries it can also activate toolbar mode there.
The prototype draws one Add Cube button in the main region and intercepts
clicks within its bounds. Other events reach native input handling. Editing
the marker text disables toolbar mode.

## Modules and dependency direction

| Module | Responsibility |
| --- | --- |
| core | Canonical layout model, ordering, validation, default definitions |
| actions | Resolve action types and Blender operators; validate and invoke |
| ui | Render buttons; present menus, dialogs, and layout editing controls |
| preferences | Adapt Blender properties and user settings to core data |
| storage | JSON serialization, schema versions, migrations, file operations |
| integrations | Optional capability providers and external action adapters |
| icons | Future icon lookup and preview resource lifecycle |
| registration | Coordinate Blender resources and cleanup |

Core has no dependency on Blender. Storage depends on core. Blender-facing
modules depend on core contracts; they must not create circular imports.
Registration composes the modules. UI delegates editing to configuration
services and delegates execution to actions.

## Configuration contract to review

Use one canonical ordered layout model and a schema-versioned JSON envelope.
The following is an illustrative contract, not a shipped schema or default:

```json
{
  "schema_version": 1,
  "layout": {
    "id": "main",
    "name": "Main Toolbar",
    "buttons": [
      {
        "id": "add-cube",
        "label": "Cube",
        "icon": {"kind": "builtin", "name": "MESH_CUBE"},
        "action": {
          "kind": "operator",
          "operator": "mesh.primitive_cube_add",
          "properties": {},
          "execution": "INVOKE_DEFAULT",
          "context": "VIEW_3D_WINDOW"
        }
      }
    ]
  }
}
```

Array position defines order; IDs remain stable when labels or order change.
Add/delete/edit/reorder operate on the same model and validate before commit.
Do not keep independently mutable JSON and Blender-property copies: the proposed
core model is authoritative, with Blender properties as editing adapters.
Menus reference declarative child actions. Dialog actions reference registered
providers or an operator's invoke behavior; imported layouts cannot define Python
classes or arbitrary executable code. Exact menu/dialog fields remain for review.

Validate structural types, unique IDs, action kinds, property shapes, allowed
context policies, and bounded nesting/file size. Check operator properties
against RNA when available. Unknown future schema versions must be rejected
clearly without changing the active configuration. A missing optional provider
must preserve the saved definition and render an unavailable action.

## Action execution and context

Use Blender operator identifiers, not executable Python strings. Resolve and
check availability at runtime; evaluate poll in the intended execution context.
For viewport-dependent actions, define how the user identifies a target viewport
and how the dispatcher resolves its WINDOW region on each click. Use a
consistent temporary override where needed.
The Add Cube prototype selects a viewport in the same window by horizontal
alignment with the click and distance from the toolbar. The intended policy
is to use the last interacted viewport. The 0.1.2 startup watcher was removed
in 0.1.3 after a reported startup crash. Verify a replacement interactively
before shipping it.
Do not silently switch areas, modes, selections, or choose an unrelated window.
Disable unsupported actions with an explanation and handle poll failure again
at execution because context can change after drawing.

Preserve invoke versus execute semantics, especially for modal tools and dialogs.
Actions that require another editor need an explicit future context policy;
they are not automatically supported by a viewport toolbar. Avoid wrapping every
action in a generic undo operation; respect the called operator's behavior.

## Persistence and sharing

Propose user-wide layouts in a writable Blender user configuration location,
not in the installed add-on folder or implicitly in .blend files. Preferences
would store UI choices and the selected layout identity. Exact storage ownership
and autosave behavior need review before implementation. Blender's startup file
stores the workspace and area geometry. The add-on saves the toolbar settings
and needs a reliable way to identify and restore the designated host area after
startup or a workspace load. If the designation cannot be resolved, leave the
workspace as loaded and let the user designate a host again.

Imports should parse and validate a candidate before applying it. Default to an
explicit replace operation with confirmation when an existing layout would be
lost; merge behavior is deferred. Export portable configuration only, using
atomic file replacement. Retain the active layout on parse/write failures.
Custom icon paths must not cause automatic file loading during import; future
asset sharing needs its own portable reference and path-validation policy.

## Optional integrations and icons

The base toolbar must work without external add-ons. Integrations expose availability
and action descriptors through optional adapters. Missing/disabled providers
must not break startup or delete buttons. No hard dependency on V-Ray or
BlenderSpline; neither integration is part of v0.1.

Start with Blender's built-in icons. Future custom icons use a managed preview
collection and a fallback when an asset is missing. Free previews on unregister.

## Lifecycle and packaging

The prototype registers the host toggle and drawing hooks. Registration
installs classes before UI hooks and removes hooks
before their dependencies. Track owned callbacks, keymaps, handlers, and previews;
clean up partially completed registration and support repeated enable/disable.

The initial scaffold uses traditional bl_info metadata. Decide whether to ship
an Extensions manifest before distribution, including license, maintainer,
minimum version, and any required permissions. Do not invent license approval
or claim this scaffold is a built/validated extension. The target test version
is 5.2.4 even though metadata declares the 5.2 API baseline.

## Architecture review checklist

- Approve the Text Editor prototype scope, host restoration strategy, and
  drawing and input lifecycle.
- Approve the module boundaries and configuration identity/ordering rules.
- Settle menu/dialog descriptors and operator context/availability policies.
- Settle persistence ownership, autosave, and import replacement behavior.
- Confirm v0.1 acceptance scope and later integration/icon phases.
- Determine how to distribute and license the add-on before release packaging.

Approval permits implementation; it does not establish runtime compatibility.
