# Changelog

## 0.1.17 - Approved stable prototype - 2026-11-27

- Configurable actions, searchable action picker, icon-only buttons and per-button command popups.
- Full floating Materials, Render Settings and 3D Viewport editors.
- Lazy optional Spline Maker drawing integration with missing-provider feedback.
- Selected-object mesh conversion, Undo/Redo, transform gizmos, rename and translation locks.
- Movable separators and optional group labels; up to 32 entries.
- Last-interacted same-window viewport targeting without a modal startup watcher.
- Explicit ordered registration and reverse/partial cleanup.
- Layout schema 3 with v1/v2 migration, validation and atomic writes.
- Portable development toolbar JSON snapshot and cross-computer setup instructions.
- Reproducible standard-library ZIP builder.

Verified runtime: Blender 5.2.5 LTS, build `5f2fd03c4701`. Syntax, five pure
layout tests, isolated background lifecycle/selection/targeting checks, and
selected interactive checks passed. Exact target 5.2.4, exhaustive multi-window,
scaling/overflow and modal/undo coverage remain open. This is a traditional
add-on prototype; broader distribution/license decisions remain pending.

The user approved replacing the single stable 0.1.14 ZIP with 0.1.17. Improved
icons and icon-only usability are priorities for the next builds.
