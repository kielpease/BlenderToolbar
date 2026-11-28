# Development roadmap

The Text Editor host prototype is underway. Remaining behavior requires
architecture approval. Versions below are milestones, not released software.

## Phase 0 — Architecture and scaffold

- Inspect the repository and investigate the official Blender 5.2 Python API.
- Establish documentation, module boundaries, and inert package entry points.
- Review the UI host, configuration contract, persistence, context, and packaging.

Exit: architecture explicitly approved. Scaffold creation alone does not close
this gate. No toolbar behavior belongs in this phase.

## Phase 1 — v0.1: Toolbar Foundation

- [x] Choose a designated Text Editor area as the toolbar host in stock Blender.
- [ ] Approve the remaining architecture decisions for v0.1, including
  operator context across editors and configuration and storage.
- [ ] Prototype opt-in toolbar mode in stock Blender 5.2.4 LTS. Check area
  resizing, overflow, UI scaling, and multiple windows. Verify other Text Editor
  areas continue to work normally. Record the exact build and findings before
  expanding UI work.

  Background verification on Blender 5.2.4 LTS (cd5dc428cce1) passed opt-in,
  preservation of another editor's text, saved UI reload, exit, and a repeat
  registration cycle. A user test also confirmed that Blender restored the
  toolbar in the top area automatically after saving the startup workspace and
  relaunching. Input, resizing, overflow, scaling, and multi-window checks remain.
  The user also confirmed that clicking Add Cube in prototype 0.1.1 creates a
  cube in Blender.
  The user confirmed 0.1.3 works after 0.1.2 crashed at startup. Version 0.1.3
  restores position-based viewport targeting. Last-interacted targeting remains
  open and needs an interactive startup check before another prototype build.
- [ ] Define the canonical ordered layout, stable button IDs, built-in icon
  defaults, and validation rules. Check model and validation behavior outside Blender.
- [ ] Implement ordered registration and reverse cleanup for classes and UI hooks.
  Verify that repeated enable/disable and a partial registration failure leave
  no classes or callbacks behind.
- [ ] Implement built-in operator resolution, RNA property validation, and
  availability feedback. Check poll in the intended viewport context, recheck
  on click, and preserve invoke versus execute behavior.
- [ ] Render buttons in layout order and add controls to add, delete, edit, and
  reorder them. Validate edits before applying them and preserve button IDs
  across label changes and reordering.
- [ ] Add simple popup menus and operator property dialogs using the approved
  action descriptors. Verify confirmation and cancellation in Blender.
- [ ] Save and load the user layout using the approved storage and autosave
  policy. Verify that toolbar mode, button edits, and order survive a restart
  with the workspace saved via Save Startup File.
- [ ] Run the v0.1 acceptance checks in stock Blender 5.2.4 LTS across
  representative modes, narrow viewports, and multiple windows. Record the
  exact build, results, and any known limitations.

Acceptance: a designated Text Editor area displays a resizable horizontal
toolbar. Toolbar mode, button edits, and order survive restart. Valid actions run in the
intended context; unavailable
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

Acceptance: clean startup in stock Blender and working toolbar functionality with
every external add-on absent. Providers can disappear without losing layouts.
V-Ray and BlenderSpline remain optional; no specific adapter is promised.

## Phase 5 — Release hardening

- Complete distribution format, license, manifest/metadata, and installation docs.
- Exercise upgrades, storage failures, lifecycle recovery, and compatibility.
- Publish a validation record naming the exact Blender build and known limits.

Acceptance: a reproducible package installs and passes the documented manual
matrix on Blender 5.2.4 LTS. Broader Blender support requires separate evidence.


## Local 0.1.16 development verification (2026-11-27)

Scoped approval covers the requested Popup control, Spline Maker drawing,
Convert to Mesh, and full floating Materials / Render Settings editors.
The work-laptop build was installed and checked in Blender 5.2.5 LTS
(5f2fd03c4701); this does not close the broader 5.2.4 acceptance matrix.

Passed: syntax; four pure Python migration/validation/atomic-write regression
tests outside Blender; three enable/disable cycles; saved host restoration;
version-1 layout migration preserving IDs; Popup flag round-trip; selected
curve conversion to mesh; missing Spline Maker operator feedback; installed
source matching the build; isolated interactive Spline Maker invocation and
cleanup; command popup invocation without immediate action execution. Full Material and Render Properties windows were
also observed interactively from their toolbar buttons.

Still open: full multi-window/mode/scaling/overflow coverage, interactive
confirmation and dismissal of every action, lifecycle while a command popup
is open, and exact target Blender 5.2.4 verification. Transient command popups
are launchers; they do not expose every target operator's parameters.


## Local 0.1.17 verification (2026-11-27)

Scoped work: movable separators with optional group labels; Undo/Redo; transform
gizmos; selected editable-object rename and location lock/unlock; last-interacted
viewport targeting; selected-object conversion checks. Tested on Blender 5.2.5
LTS (5f2fd03c4701), preserving the user's current top-toolbar workspace.

Passed: five pure layout regression tests (v1/v2 migration, separator and Popup
round trips, invalid candidate rejection, atomic-write failure preservation);
background lifecycle repetition, simulated partial-registration cleanup, owned
keymap/handler removal, two-view targeting and stale target rejection, selected
multi-object locks/rename, curve and mesh conversion with an unselected curve
unchanged, Object/Edit Mode checks, and saved host restoration/cache reset.
Interactive input verified actual pass-through selection, perspective-view
Spline Maker targeting and cancellation, and one-step lock Undo/Redo. The installed
source matches the built ZIP. Tests are in tests/test_layout.py and
tests/blender_runtime.py; generated scenes and local install ZIPs remain ignored.

Still open: exact 5.2.4 testing; exhaustive multi-window/keyboard-only targeting;
all modal-action/undo combinations; overflow and scaling coverage. Group headers
are separators with labels, not collapsible or nested containers.


## Approved stable promotion and next-build priority (2026-11-27)

The user approved 0.1.17 as the single stable prototype and requested a portable
snapshot of the current toolbar layout for another development computer.
`presets/development-layout.json` is the approved JSON snapshot. Raw preferences,
startup workspaces and scenes remain outside Git. See DEVELOPMENT_SETUP.md.

**Priority for the next builds: better icons.** Improve distinctness and visual
consistency across undo/redo, transform, spline, mesh, material/render and lock
commands. Check icon-only tooltips, light/dark contrast and high-DPI scaling.
Investigate supported native icon rendering before expanding custom assets.
This icon work is planned, not implemented or runtime-verified.

Stable promotion does not close the remaining architecture, packaging/license,
5.2.4, multi-window, scaling/overflow or modal-history acceptance items above.
