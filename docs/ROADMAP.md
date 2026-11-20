# Development roadmap

All phases after the current scaffold require architecture approval before
behavior is implemented. Versions below are milestones, not released software.

## Phase 0 — Architecture and scaffold (current)

- Inspect the repository and investigate the official Blender 5.2 Python API.
- Establish documentation, module boundaries, and inert package entry points.
- Review the UI host, configuration contract, persistence, context, and packaging.

Exit: architecture explicitly approved. Scaffold creation alone does not close
this gate. No toolbar behavior belongs in this phase.

## Phase 1 — v0.1: Toolbar Foundation

- Prototype the approved native horizontal host in Blender 5.2.4.
- Establish configuration model/validation and built-in icon defaults.
- Implement registration/cleanup and built-in operator actions with poll/context
  handling, including invoke versus execute behavior.
- Render ordered buttons and provide basic add, delete, edit, and reorder controls.
- Establish simple popup menu and property-dialog paths.
- Persist the approved user layout using the agreed storage ownership.

Acceptance: stock Blender displays a configurable horizontal toolbar; edits and
order survive restart; valid actions run in the intended context; unavailable
actions explain why; menus/dialogs behave correctly, including cancellation.
Repeated enable/disable leaves no callbacks/classes behind. Validate narrow
viewports, multiple windows, and representative modes on Blender 5.2.4.
Record the host prototype outcome before expanding UI work.

## Phase 2 — v0.2: Portable layouts

- Finalize/version the public JSON contract and export/import user layouts.
- Add transactional validation, atomic writes, and clear import errors.
- Define migrations, unsupported-version rejection, and replacement semantics.

Acceptance: export/import round trips preserve IDs, order, and action properties;
invalid files leave the active layout intact. Missing providers retain their
definitions. Shared files contain no arbitrary Python execution mechanism.

## Phase 3 — v0.3: Custom icons and usability

- Add portable custom icon references and managed preview resources.
- Improve overflow, labeling, tooltips, and layout editing based on usage.

Acceptance: missing assets fall back safely; previews are released on disable;
layout sharing and UI scaling remain usable. No generated preview IDs are saved.

## Phase 4 — v0.4: Optional integrations

- Formalize adapter capabilities and document integration registration.
- Add specific integrations only when their APIs and user requirements are known.

Acceptance: clean stock-Blender startup and unchanged base functionality with
every external add-on absent. Providers can disappear without losing layouts.
V-Ray and BlenderSpline remain optional; no specific adapter is promised.

## Phase 5 — Release hardening

- Complete distribution format, license, manifest/metadata, and installation docs.
- Exercise upgrades, storage failures, lifecycle recovery, and compatibility.
- Publish a validation record naming the exact Blender build and known limits.

Acceptance: a reproducible package installs and passes the documented manual
matrix on Blender 5.2.4 LTS. Broader Blender support requires separate evidence.
