"""Run with Blender --background --factory-startup --python-exit-code 1 --python tests/blender_runtime.py."""

from pathlib import Path
import sys
from unittest.mock import patch

import bpy
import addon_utils

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
module = addon_utils.enable('blender_toolbar', default_set=True)
assert module.bl_info['version'] == (0, 1, 17)
from blender_toolbar import registration
from blender_toolbar.actions import viewports
from blender_toolbar.actions.mesh_actions import ACTIONS, resolve_operator, run_action, run_in_viewport
from blender_toolbar.preferences.buttons import get_preferences, initialize
from blender_toolbar.ui.text_host import is_toolbar


def owned_keymaps():
    config = bpy.context.window_manager.keyconfigs.addon
    return [] if config is None else [item for keymap in config.keymaps
                                      for item in keymap.keymap_items
                                      if item.idname.startswith('blender_toolbar.')]


for _ in range(3):
    addon_utils.disable('blender_toolbar', default_set=True)
    assert registration._resources is None
    assert not owned_keymaps()
    assert viewports.clear_targets not in bpy.app.handlers.load_post
    addon_utils.enable('blender_toolbar', default_set=True)
    assert len([handler for handler in bpy.app.handlers.load_post if handler is viewports.clear_targets]) == 1
    if bpy.context.window_manager.keyconfigs.addon:
        assert len(owned_keymaps()) == 11

addon_utils.disable('blender_toolbar', default_set=True)
original = bpy.utils.register_class
calls = 0


def fail_registration(cls):
    global calls
    calls += 1
    if calls == 4:
        raise RuntimeError('Simulated registration failure')
    original(cls)


with patch.object(bpy.utils, 'register_class', side_effect=fail_registration):
    try:
        registration.register()
    except RuntimeError as error:
        assert 'Simulated' in str(error)
    else:
        raise AssertionError('The simulated registration failure was not raised')
assert registration._resources is None
assert not any(cls.is_registered for cls in registration._CLASSES)
addon_utils.enable('blender_toolbar', default_set=True)

context = bpy.context
window = context.window
screen = window.screen
viewport = next(area for area in screen.areas if area.type == 'VIEW_3D')
with context.temp_override(area=viewport):
    assert bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5) == {'FINISHED'}
areas = sorted((area for area in screen.areas if area.type == 'VIEW_3D'), key=lambda area: area.x)
assert len(areas) == 2
camera_view, perspective_view = areas
camera_view.spaces.active.region_3d.view_perspective = 'CAMERA'
perspective_view.spaces.active.region_3d.view_perspective = 'PERSP'
host = next(area for area in screen.areas if area.type == 'DOPESHEET_EDITOR')
host.type = 'TEXT_EDITOR'
with context.temp_override(area=host):
    assert bpy.ops.blender_toolbar.toggle_host() == {'FINISHED'}
    assert is_toolbar(host.spaces.active)
    target, error = viewports.resolve_viewport(context)
    assert target is None and 'Click' in error
region = next(region for region in perspective_view.regions if region.type == 'WINDOW')
with context.temp_override(area=perspective_view, region=region):
    assert viewports.BLENDERTOOLBAR_OT_remember_viewport.invoke(None, context, None) == {'PASS_THROUGH'}
with context.temp_override(area=host):
    target, error = viewports.resolve_viewport(context)
    assert error is None and target[0] == perspective_view
# A stale area id or another screen must never select the camera viewport instead.
viewports._targets[window.as_pointer()] = (screen.as_pointer(), 0)
with context.temp_override(area=host):
    assert viewports.resolve_viewport(context)[0] is None
with context.temp_override(area=perspective_view, region=region):
    viewports.remember_viewport(context)

for obj in context.selected_objects:
    obj.select_set(False)
selected = []
for name in ('ToolbarSelectedA', 'ToolbarSelectedB', 'ToolbarUnselected'):
    obj = bpy.data.objects.new(name, bpy.data.meshes.new(name))
    context.collection.objects.link(obj)
    if name != 'ToolbarUnselected':
        obj.select_set(True)
        selected.append(obj)
context.view_layer.objects.active = selected[0]
untouched = bpy.data.objects['ToolbarUnselected']
with context.temp_override(area=host):
    assert run_action(context, camera_view.x + 1, 'LOCK_TRANSLATION') is None
    assert all(tuple(obj.lock_location) == (True, True, True) for obj in selected)
    assert tuple(untouched.lock_location) == (False, False, False)
    assert run_action(context, camera_view.x + 1, 'UNLOCK_TRANSLATION') is None
    assert all(tuple(obj.lock_location) == (False, False, False) for obj in selected)
with context.temp_override(area=perspective_view, region=region):
    assert bpy.ops.blender_toolbar.rename_selected(base_name='ToolbarRenamed') == {'FINISHED'}
    assert {obj.name for obj in selected} == {'ToolbarRenamed_001', 'ToolbarRenamed_002'}
    assert untouched.name == 'ToolbarUnselected'
    previous = {obj.name for obj in selected}
    assert bpy.ops.blender_toolbar.rename_selected(base_name='   ') == {'CANCELLED'}
    assert previous == {obj.name for obj in selected}

for obj in context.selected_objects:
    obj.select_set(False)
for name in ('ToolbarCurveSelected', 'ToolbarCurveUntouched'):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    points = curve.splines.new('POLY').points
    points.add(1)
    points[0].co, points[1].co = (0, 0, 0, 1), (1, 0, 0, 1)
    obj = bpy.data.objects.new(name, curve)
    context.collection.objects.link(obj)
    if name == 'ToolbarCurveSelected':
        obj.select_set(True)
        context.view_layer.objects.active = obj
with context.temp_override(area=host):
    assert run_action(context, camera_view.x + 1, 'CONVERT_MESH') is None
assert bpy.data.objects['ToolbarCurveSelected'].type == 'MESH'
assert bpy.data.objects['ToolbarCurveUntouched'].type == 'CURVE'
with context.temp_override(area=host):
    assert run_action(context, 0, 'CONVERT_MESH') is None  # Selected mesh is also supported.
with context.temp_override(area=perspective_view, region=region):
    bpy.ops.object.mode_set(mode='EDIT')
with context.temp_override(area=host):
    assert 'Object Mode' in run_action(context, 0, 'CONVERT_MESH')
    assert 'Object Mode' in run_action(context, 0, 'LOCK_TRANSLATION')
with context.temp_override(area=perspective_view, region=region):
    bpy.ops.object.mode_set(mode='OBJECT')
for entry in ACTIONS.values():
    if entry.operator and not entry.provider:
        assert resolve_operator(entry)[1] is None, entry

output = ROOT / 'dist/runtime-0.1.17.blend'
output.parent.mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(output))
bpy.ops.wm.open_mainfile(filepath=str(output))
assert not viewports._targets
assert any(is_toolbar(area.spaces.active) for area in bpy.context.screen.areas)
print('RUNTIME_17_PASSED', bpy.app.version_string, 'lifecycle, partial cleanup, targeting, selection commands, conversion, modes, restoration')
