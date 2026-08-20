"""Every name in maplibreum.__all__ must actually be importable from the
top-level package.

Regression test for LayerControl: it was implemented in core.py and listed
in core.__all__ (and used in README examples) but never re-exported from
maplibreum/__init__.py, so `from maplibreum import LayerControl` raised
ImportError.
"""

import maplibreum


def test_all_dunder_all_names_are_importable():
    missing = [name for name in maplibreum.__all__ if not hasattr(maplibreum, name)]
    assert not missing, f"names in __all__ but not importable: {missing}"


def test_layer_control_is_exported():
    from maplibreum import LayerControl

    assert LayerControl is maplibreum.core.LayerControl
