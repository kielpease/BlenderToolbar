"""Coordinate the add-on's Blender resources."""

from .ui import text_host


def register():
    """Install the Text Editor host prototype."""
    text_host.register()


def unregister():
    """Remove the Text Editor host prototype."""
    text_host.unregister()
