"""Lazy capability checks for the optional Spline Maker extension."""

import bpy


def unavailable_reason() -> str | None:
    """Return an explanation when Spline Maker is not enabled; never import or enable it."""
    try:
        bpy.ops.spline_maker.draw_spline.get_rna_type()
    except (AttributeError, KeyError, RuntimeError):
        return "Draw Spline requires the Spline Maker add-on to be installed and enabled"
    return None
