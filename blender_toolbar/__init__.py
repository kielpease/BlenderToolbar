"""BlenderToolbar add-on entry points."""

bl_info = {
    "name": "BlenderToolbar",
    "description": "Horizontal toolbar prototype for a Text Editor area",
    "version": (0, 1, 14),
    "blender": (5, 2, 0),
    "category": "Interface",
    "warning": "Development prototype",
}


def register():
    """Enable the add-on."""
    from . import registration

    registration.register()


def unregister():
    """Disable the add-on."""
    from . import registration

    registration.unregister()
