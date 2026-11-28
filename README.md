# BlenderToolbar

A customizable horizontal toolbar for Blender, hosted in a designated Text
Editor area. The approved stable prototype is **0.1.17**.

Target runtime: **Blender 5.2.4 LTS**. The current build was runtime-tested on
**Blender 5.2.5 LTS**, build `5f2fd03c4701`; exact 5.2.4 verification remains open.

## Install

Download [BlenderToolbar-prototype-0.1.17.zip](stable/BlenderToolbar-prototype-0.1.17.zip)
and install it through Blender Preferences > Add-ons > Install from Disk, then
enable **BlenderToolbar**. This is a traditional Python add-on ZIP, not a Blender
Extensions archive. The [stable folder](stable/) contains one approved build.
Packaging/license decisions for a broader public release remain open.

Switch an empty area to **Text Editor**, then click **Use as Toolbar** in its
header. Resize or move that area with Blender's normal workspace controls.
**Exit Toolbar Mode** restores ordinary text editing in the area. Save the
workspace in a `.blend` file, or use **File > Defaults > Save Startup File** to
make its arrangement your startup layout. Saving a startup file also saves the
current scene as the startup scene.

## Toolbar controls

Click the three-dot button or right-click the toolbar to open Setup. Add,
remove, rename and reorder buttons, and click an Action to search supported
commands. A blank Label gives a compact icon-only button. **Save Toolbar**
saves the layout independently of the installed add-on; reinstalling preserves
it. Setup edits are live; Save Toolbar persists them for the next session.
Button Background, Button Height and Font Size control the row.

**Add Separator** creates a movable divider. Give it a Label to mark a group,
or leave it blank for a plain line. Up to 32 entries are supported; groups are
labels and dividers, not collapsible containers.

Supported commands include:

- Add Cube, UV Sphere, Cylinder and Plane.
- Translate, Rotate and Scale gizmos; Extrude Region, Bevel and Inset in Mesh Edit Mode.
- Undo, Redo, Rename Selected, and lock/unlock all three selected-object translation axes.
- Convert selected objects to mesh in Object Mode, including already-mesh selections.
- Full floating Material Properties, Render Properties, and 3D Viewport windows.
- Draw Spline through the optional, already-enabled Spline Maker extension.

Rename uses one name for a single selected editable object, or Name_001,
Name_002, etc. for multiple objects. Translation locks preserve rotation and
scale lock flags. Conversion requires the active object to be part of the
editable selection and leaves unselected objects unchanged.

A button's **Popup** checkbox opens a small command launcher before running.
Editor actions always open a full floating Blender editor, whose settings are
live Blender edits. Materials requires an active object. Popup launchers do
not expose every target operator's parameters.

With multiple viewports, **click or navigate in the desired viewport first**.
Commands, including Draw Spline, use the last interacted viewport in that
window. A single viewport works immediately. Targets reset after loading a
file; missing targets produce a prompt to select a viewport. No modal startup
watcher is used. The add-on never installs or enables external add-ons, and
missing Spline Maker preserves its button with an availability explanation.

## Continue development on another computer

The current toolbar preset is saved as
[presets/development-layout.json](presets/development-layout.json). It contains
button order, stable IDs, labels, icons, Popup choices, separators, color, height
and font size. Follow [Development setup](docs/DEVELOPMENT_SETUP.md) to restore
it on another computer. Blender startup workspaces and full preferences are
not committed to this repository.

The add-on reads `blender_toolbar/layout.json` inside Blender's user
configuration folder when enabled. Layout schema **3** adds entry kinds;
versions 1 and 2 migrate without changing existing IDs or order. Invalid or
future versions are rejected before replacing a saved layout. To downgrade to
an older add-on, restore a layout backup supported by that version. Open Blender
instances do not automatically refresh a file saved by another instance.

## Development and verification

Read [AGENTS.md](AGENTS.md), [Architecture](docs/ARCHITECTURE.md),
[API research](docs/BLENDER_API_RESEARCH.md) and [Roadmap](docs/ROADMAP.md).
The requested button, popup, separator, selection and targeting features have
scoped approval; unrelated architecture and public-release decisions remain open.

Build an iteration ZIP using Python's standard library:

```powershell
python scripts/build_addon.py
```

Builds go into the ignored `dist/` folder. The script syntax-checks the package
and creates a reproducible archive containing only add-on Python sources.
Promote a build into `stable/` only after explicit approval.

Pure tests:

```powershell
python -m unittest discover -s tests -v
```

Blender runtime checks (use an installed Blender executable):

```powershell
blender --background --factory-startup --python-exit-code 1 --python tests/blender_runtime.py
```

Runtime checks use an isolated factory scene and write generated files to
`dist/`. The [roadmap](docs/ROADMAP.md) records tested behavior and remaining
coverage; see the [changelog](docs/CHANGELOG.md) for stable 0.1.17. Improved icon
clarity and consistency are a priority for the next builds.
