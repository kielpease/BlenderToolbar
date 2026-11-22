"""Prototype a saved, opt-in toolbar area using a Text Editor host."""

from contextlib import ExitStack

import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from ..actions.add_cube import add_cube


_MARKER = "blender_toolbar_host"
_resources = None
_BUTTON_LABEL = "Add Cube"


def is_toolbar(space):
    """Return whether the space displays a toolbar marker saved with the file."""
    if space is None or space.type != "TEXT_EDITOR":
        return False
    text = space.text
    return (
        text is not None
        and text.get(_MARKER) == 1
        and len(text.lines) == 1
        and not text.lines[0].body
    )


class BLENDERTOOLBAR_OT_toggle_host(bpy.types.Operator):
    """Switch an empty Text Editor area into or out of toolbar mode."""

    bl_idname = "blender_toolbar.toggle_host"
    bl_label = "Toggle Toolbar Mode"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (
            space is not None
            and space.type == "TEXT_EDITOR"
            and (space.text is None or is_toolbar(space))
        )

    def execute(self, context):
        space = context.space_data
        if is_toolbar(space):
            space.text = None
        else:
            marker = bpy.data.texts.new("BlenderToolbar Host")
            marker[_MARKER] = 1
            space.text = marker
        context.area.tag_redraw()
        return {"FINISHED"}


def _draw_header(self, context):
    if is_toolbar(context.space_data):
        self.layout.operator("blender_toolbar.toggle_host", text="Exit Toolbar Mode")
    elif context.space_data.text is None:
        self.layout.operator("blender_toolbar.toggle_host", text="Use as Toolbar")


def _button_bounds(context):
    scale = context.preferences.system.ui_scale or 1.0
    width = min(100 * scale, context.region.width - 12 * scale)
    height = min(24 * scale, context.region.height - 8 * scale)
    if width < 72 * scale or height < 16 * scale:
        return None
    left = 6 * scale
    bottom = (context.region.height - height) / 2
    return left, bottom, left + width, bottom + height


class BLENDERTOOLBAR_OT_click_button(bpy.types.Operator):
    """Dispatch a click inside the prototype button."""

    bl_idname = "blender_toolbar.click_button"
    bl_label = _BUTTON_LABEL
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        return (
            context.region is not None
            and context.region.type == "WINDOW"
            and is_toolbar(context.space_data)
        )

    def invoke(self, context, event):
        bounds = _button_bounds(context)
        if bounds is None:
            return {"PASS_THROUGH"}
        left, bottom, right, top = bounds
        if not (left <= event.mouse_region_x < right and bottom <= event.mouse_region_y < top):
            return {"PASS_THROUGH"}
        error = add_cube(context, event.mouse_x)
        if error is not None:
            self.report({"WARNING"}, error)
        return {"FINISHED"}


def _draw_rectangle(shader, bounds, color):
    left, bottom, right, top = bounds
    vertices = ((left, bottom), (right, bottom), (left, top), (right, top))
    shader.uniform_float("color", color)
    batch_for_shader(shader, "TRI_STRIP", {"pos": vertices}).draw(shader)


def _draw_toolbar():
    context = bpy.context
    if not is_toolbar(context.space_data):
        return
    shader = gpu.shader.from_builtin("UNIFORM_COLOR")
    shader.bind()
    _draw_rectangle(shader, (0, 0, context.region.width, context.region.height), (0.13, 0.13, 0.13, 1))
    bounds = _button_bounds(context)
    if bounds is None:
        return
    _draw_rectangle(shader, bounds, (0.29, 0.29, 0.29, 1))
    left, bottom, right, top = bounds
    font = 0
    blf.size(font, 13 * (context.preferences.system.ui_scale or 1.0))
    blf.color(font, 0.9, 0.9, 0.9, 1.0)
    width, height = blf.dimensions(font, _BUTTON_LABEL)
    blf.position(font, (left + right - width) / 2, (bottom + top - height) / 2, 0)
    blf.draw(font, _BUTTON_LABEL)


def register():
    """Install the opt-in header control and area drawing hook."""
    global _resources
    if _resources is not None:
        return
    with ExitStack() as resources:
        for cls in (BLENDERTOOLBAR_OT_toggle_host, BLENDERTOOLBAR_OT_click_button):
            bpy.utils.register_class(cls)
            resources.callback(bpy.utils.unregister_class, cls)
        bpy.types.TEXT_HT_header.append(_draw_header)
        resources.callback(bpy.types.TEXT_HT_header.remove, _draw_header)
        handle = bpy.types.SpaceTextEditor.draw_handler_add(
            _draw_toolbar, (), "WINDOW", "POST_PIXEL"
        )
        resources.callback(bpy.types.SpaceTextEditor.draw_handler_remove, handle, "WINDOW")
        keyconfig = bpy.context.window_manager.keyconfigs.addon
        if keyconfig is not None:
            keymap = keyconfig.keymaps.new(name="Text", space_type="TEXT_EDITOR")
            item = keymap.keymap_items.new(
                BLENDERTOOLBAR_OT_click_button.bl_idname, "LEFTMOUSE", "PRESS", head=True
            )
            resources.callback(keymap.keymap_items.remove, item)
        _resources = resources.pop_all()


def unregister():
    """Remove the drawing hook and header control in reverse order."""
    global _resources
    if _resources is not None:
        resources, _resources = _resources, None
        resources.close()
