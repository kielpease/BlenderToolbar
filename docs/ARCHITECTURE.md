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


## Scoped popup and Spline Maker implementation (0.1.16)

The user requested per-button popups, Spline Maker drawing, conversion to mesh,
and Materials / Render Settings on 2026-11-27, and explicitly chose the full
Properties editor in separate floating windows. This authorizes those specific
capabilities; the remaining architecture review items above remain open.

- Operator commands retain the same-window, position-based viewport target.
  A per-button `popup` flag opens a transient command launcher; dismissing it
  does not run the command. Its Run button rechecks the original viewport and
  operator poll, including mode and selection, before execution.
- Materials and Render Settings duplicate the selected viewport into a new
  Blender window and configure only that new area as Properties, on the
  MATERIAL or RENDER tab. A 3D Viewport Window action is also available. These
  windows are normal interactive Blender editors, owned and closed by Blender.
  No existing area is temporarily converted or restored, and no timers or
  persistent window references are installed by the add-on.
- Draw Spline invokes `spline_maker.draw_spline` lazily. The adapter checks for
  the registered operator, imports no extension, and never enables it. Missing
  Spline Maker preserves the button and reports the unavailable capability.
- Convert to Mesh uses `object.convert(target='MESH')` in Object Mode and the
  target viewport. It respects Blender's operator undo and selection behavior.
- Pure core validation defines layout version 2, adding the boolean `popup`.
  Version 1 migrates in memory with Popup disabled, preserving IDs and order;
  Save Toolbar atomically writes version 2. Unsupported versions and malformed
  candidates are rejected before replacing the file. Downgrading to 0.1.15
  requires restoring a version-1 backup; older builds reject version 2.
- The GPU toolbar uses portable curve/mesh/material/camera vector strokes owned
  by icons/. The command popup uses Blender's native curve icon, matching
  Spline Maker's Add menu; no extension asset or preview ID is persisted.


## Scoped grouping, selection commands, and targeting (0.1.17)

On 2026-11-27 the user requested separators/grouping, undo/redo, transform tools,
selected-object rename and translation locks, selected conversion, and repair
of Draw Spline targeting the camera view instead of the last selected viewport.
That request authorizes this scope; unrelated architecture gates remain open.

Layout version 3 adds `kind` (BUTTON or SEPARATOR) to the existing ordered
entries. A separator's optional label is a group heading. Its saved action/icon
fields remain inert, and it is never dispatched as an action. Versions 1/2
migrate to BUTTON entries without changing identities, labels, actions or order.
The maximum is 32 entries; collapsible/nested groups remain deferred.

Viewport targeting is owned by actions/viewports.py. A short pass-through
operator observes mouse clicks, wheel and trackpad/3D-mouse navigation through
a supported View3D keymap. It records only integer window/screen/area pointers.
Resolution matches the current screen and window on every click, using the sole
viewport only when unambiguous. Multiple views without a valid remembered target
require explicit viewport interaction. File-load and unregister cleanup clear
the cache. There is no modal observer, startup operator invocation, draw-based
state mutation, or startup timer. Keyboard-only navigation without a click or
tracked navigation event does not change the remembered target.

registration.py now owns explicit class ordering, header and draw hooks,
keymaps, the persistent load cleanup handler, and reverse/partial cleanup.
Selection operators own rename and lock changes. Only selected editable objects
are changed, in Object Mode. Convert delegates selected-object conversion to
Blender and rejects an active object outside the editable selection.

Undo/Redo invoke Blender history without adding a new step. Synchronous data
edits called from the toolbar's mouse handler need explicit undo recording in
Blender 5.2.5; the nested operator's UNDO flag alone did not create a step in
interactive verification. The action descriptor opts known synchronous edits
into a single named undo_push after success. Modal actions, dialogs, tool
activation, editor windows, and history commands retain their native behavior.
No blanket undo wrapper is applied to every action.
