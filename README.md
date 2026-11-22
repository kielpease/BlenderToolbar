# BlenderToolbar

A customizable horizontal toolbar for Blender, inspired by the workflows of
3ds Max and Maya. Target runtime: **Blender 5.2.4 LTS**.

## Status

**v0.1 — Toolbar Foundation** is the initial milestone, not a released version.
This repository contains a Text Editor host prototype. It can mark an empty
Text Editor area as the toolbar and recognize it after loading a saved
workspace. The development build lets you add, rename, remove, and reorder
buttons and assign supported Blender commands and tools.

## Planned capabilities

- Configuration-driven buttons with add, delete, edit, and reorder controls.
- Built-in Blender operator actions, popup menus, and property dialogs.
- Versioned JSON layout import/export for sharing configurations.
- Custom icons in a future release.
- Optional adapters for other add-ons; no hard dependency on V-Ray or BlenderSpline.

## Proposed approach

Use a designated Text Editor area as a resizable horizontal toolbar in stock
Blender. The Editor Type picker continues to show Text Editor. Users can save
the workspace arrangement with Save Startup File. The add-on will restore
toolbar mode and the saved buttons. See the
[architecture proposal](docs/ARCHITECTURE.md) for the decisions still open.

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

The prototype uses traditional Python add-on entry points. An Extensions
manifest and distribution metadata
are deferred until packaging and license choices are reviewed. This is not an
Extensions archive or a release-ready installable distribution.

## Development

The [stable folder](stable/) contains the single approved install ZIP.
Drag it into Blender to install. Keep iteration builds in the local
`dist/` folder and replace the stable ZIP when a newer build is approved.

Read [AGENTS.md](AGENTS.md), the [architecture proposal](docs/ARCHITECTURE.md),
and the [roadmap](docs/ROADMAP.md) before changing code. Use Blender's bundled
Python for eventual runtime checks; ordinary Python can check syntax and later
test the Blender-independent core.

Enable the development add-on, switch an area to an empty Text Editor, and
click **Use as Toolbar** in its header. The area displays **Add Cube**.
Save your workspace with **File → Defaults → Save Startup File** to carry
the designation into future sessions. Use **Exit Toolbar Mode** to clear it.
The prototype requires no third-party Python dependencies.

In development build 0.1.15, click the three-dot button on the left or
right-click the toolbar. Leave **Label** blank for a compact icon-only button.
Click the current action in any row to search the supported commands and tools.
**Save Toolbar** saves the layout to `blender_toolbar/layout.json` inside
Blender's user configuration folder and closes Setup. The add-on loads that
file automatically on enable. Reinstalling the add-on leaves the file in place.
**Button Background**, **Button Height**, and **Font Size** control the row.
In Mesh Edit Mode, the Extrude action activates Blender's Extrude Region tool.
Select geometry and drag the tool's gizmo to extrude.

## Review gate

Review the UI host, configuration contract, persistence ownership, action
context policy, and packaging decisions listed in the architecture document.
Approve the remaining architecture decisions before expanding beyond the
host prototype.
