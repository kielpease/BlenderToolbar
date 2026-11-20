# Architecture proposal

Status: awaiting review. This document defines intended boundaries, not existing
features. Target: Blender 5.2.4 LTS. See [API research](BLENDER_API_RESEARCH.md).

## UI host

Propose a horizontal row appended to the existing 3D Viewport header through a
supported draw hook. Keep the renderer separate from that hook so another
supported host can be considered without changing the configuration model.
Retain Blender's existing header. Do not promise a standalone editor, separate
dockable toolbar region, arbitrary height, or Maya-style shelves from Python.

Header space is shared and limited. Narrow regions, horizontal scrolling,
overflow menus, scaling, and interaction with other add-ons require a small
Blender prototype after approval. A sidebar can host configuration controls but
does not itself satisfy the horizontal-toolbar goal. A custom GPU overlay would
require separate input/layout/accessibility work and is deferred.

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
The proposed default is the originating viewport's WINDOW region. Resolve the
region on each click and use a consistent temporary override where needed.
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
and autosave behavior need review before implementation.

Imports should parse and validate a candidate before applying it. Default to an
explicit replace operation with confirmation when an existing layout would be
lost; merge behavior is deferred. Export portable configuration only, using
atomic file replacement. Retain the active layout on parse/write failures.
Custom icon paths must not cause automatic file loading during import; future
asset sharing needs its own portable reference and path-validation policy.

## Optional integrations and icons

The base toolbar must work with stock Blender. Integrations expose availability
and action descriptors through optional adapters. Missing/disabled providers
must not break startup or delete buttons. No hard dependency on V-Ray or
BlenderSpline; neither integration is part of v0.1.

Start with Blender's built-in icons. Future custom icons use a managed preview
collection and a fallback when an asset is missing. Free previews on unregister.

## Lifecycle and packaging

The current register/unregister entry points are intentionally inert. Later,
registration will install properties/classes before UI hooks and remove hooks
before their dependencies. Track owned callbacks, keymaps, handlers, and previews;
clean up partially completed registration and support repeated enable/disable.

The initial scaffold uses traditional bl_info metadata. Decide whether to ship
an Extensions manifest before distribution, including license, maintainer,
minimum version, and any required permissions. Do not invent license approval
or claim this scaffold is a built/validated extension. The target test version
is 5.2.4 even though metadata declares the 5.2 API baseline.

## Architecture review checklist

- Approve the viewport header host and post-approval overflow prototype scope.
- Approve the module boundaries and configuration identity/ordering rules.
- Settle menu/dialog descriptors and operator context/availability policies.
- Settle persistence ownership, autosave, and import replacement behavior.
- Confirm v0.1 acceptance scope and later integration/icon phases.
- Choose distribution format and licensing before release packaging.

Approval permits implementation; it does not establish runtime compatibility.
