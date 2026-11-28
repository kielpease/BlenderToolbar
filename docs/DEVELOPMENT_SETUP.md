# Continue development on another computer

The repository carries the approved 0.1.17 add-on and a snapshot of the current
**toolbar layout only**. No Blender `userpref.blend`, `startup.blend`, scene,
personal file path, or third-party add-on is included in the preset.

## Restore the current toolbar

1. Clone or pull this repository.
2. Install and enable the ZIP in [stable/](../stable/). Use Blender 5.2.5 LTS to
   match the version verified on the work laptop. The declared target remains
   5.2.4 LTS, whose exact runtime check is still outstanding.
3. Find Blender's user configuration directory. In Blender's Python Console,
   `bpy.utils.user_resource("CONFIG")` prints the location. For a standard
   Windows Blender 5.2 profile it is
   `%APPDATA%\Blender Foundation\Blender\5.2\config`.
4. Close Blender. Back up any existing `blender_toolbar/layout.json` in that
   directory. Create the `blender_toolbar` subfolder if necessary.
5. Copy [development-layout.json](../presets/development-layout.json) into that
   subfolder and name the copy **layout.json**.
6. Reopen Blender with BlenderToolbar enabled. Switch an empty area to Text
   Editor and use **Use as Toolbar**, or open an existing workspace that already
   contains a designated toolbar area. The saved JSON loads automatically.
7. Arrange the toolbar where you want it. Save the `.blend` workspace or use
   **File > Defaults > Save Startup File** for future normal launches. That
   command also saves the current scene as the startup scene.
8. With multiple viewports, click or navigate in your intended viewport before
   using a toolbar command. Install and enable your separate Spline Maker
   extension if you want Draw Spline; the toolbar does not bundle it.

The JSON restores commands, IDs, order, icons, labels, separators, Popup flags,
color, height and font size. It does not restore Blender themes, keymaps,
workspace geometry, actual materials, render settings, or other add-ons.
Those belong to Blender's profile or scene and were intentionally left out of Git.

## Update the shared preset

Use **Save Toolbar** in Setup, then copy the resulting `layout.json` from the
user configuration folder over `presets/development-layout.json`. Review the
JSON diff before committing it. Keep scene files and raw preferences out of Git.
The preset is a snapshot; editing it in the checkout does not update an already
running Blender session. Repeat the copy/restart steps to apply a newer snapshot.

Schema 3 requires build 0.1.17 or newer. Versions 1/2 migrate when loaded, but
older add-ons do not understand version 3; keep an older-layout backup before
downgrading. Full Import/Export buttons remain future work.

## Current validation and next builds

Five pure layout tests and the isolated Blender lifecycle/selection/targeting
checks pass. Interactive 5.2.5 checks covered perspective viewport selection,
Spline Maker activation/cancellation, and lock Undo/Redo. Exhaustive multiple
window, scaling, overflow, and modal-history checks remain open.

Next builds should improve icon legibility and consistency: distinct command
shapes, native icon alignment where supported, clearer tooltips for icon-only
buttons, light/dark theme contrast, and high-DPI readability. The current GPU
icons are prototype vector strokes rather than a completed icon system.
