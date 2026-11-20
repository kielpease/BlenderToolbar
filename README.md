# BlenderToolbar

A customizable horizontal toolbar for Blender, inspired by the workflows of
3ds Max and Maya. Target runtime: **Blender 5.2.4 LTS**.

## Status

**v0.1 — Toolbar Foundation** is the initial milestone, not a released version.
This repository currently contains documentation and an inert Python add-on
scaffold only. No toolbar, settings, operators, or persistence are implemented.
Architecture review must happen before implementation starts.

## Planned capabilities

- Configuration-driven buttons with add, delete, edit, and reorder controls.
- Built-in Blender operator actions, popup menus, and property dialogs.
- Versioned JSON layout import/export for sharing configurations.
- Custom icons in a future release.
- Optional adapters for other add-ons; no hard dependency on V-Ray or BlenderSpline.

## Proposed approach

Use native Blender UI within an existing editor, initially the 3D Viewport
header. This is a proposal for review, not an implemented or finalized UI choice.
The Python API does not expose registration of arbitrary new editor types.
See [API investigation](docs/BLENDER_API_RESEARCH.md) for evidence, alternatives,
limitations, and the validation still required on Blender 5.2.4.

## Repository layout

```text
blender_toolbar/
    __init__.py       # Inert add-on entry points and development metadata
    registration.py   # Reserved lifecycle coordination
    core/             # Blender-independent configuration and validation
    actions/          # Blender operator resolution and invocation
    ui/               # Header rendering, menus, dialogs, layout editor
    preferences/      # Blender settings and configuration adapters
    storage/          # JSON serialization, migration, import/export
    integrations/     # Optional external add-on adapters
    icons/            # Future icon resource lifecycle
docs/
    ARCHITECTURE.md
    BLENDER_API_RESEARCH.md
    ROADMAP.md
AGENTS.md
```

All reserved modules contain documentation only. The entry points intentionally
do nothing. The package uses the traditional Python add-on entry-point shape
for the development scaffold; an Extensions manifest and distribution metadata
are deferred until packaging and license choices are reviewed. This is not an
Extensions archive or a release-ready installable distribution.

## Development

Read [AGENTS.md](AGENTS.md), the [architecture proposal](docs/ARCHITECTURE.md),
and the [roadmap](docs/ROADMAP.md) before changing code. Use Blender's bundled
Python for eventual runtime checks; ordinary Python can check syntax and later
test the Blender-independent core.

Do not expect enabling this scaffold to display UI. Compatibility with the
target Blender binary remains unverified; API research alone is not runtime
testing. No third-party Python dependencies are required by the scaffold.

## Review gate

Review the UI host, configuration contract, persistence ownership, action
context policy, and packaging decisions listed in the architecture document.
Only after explicit architecture approval should v0.1 behavior be implemented.
