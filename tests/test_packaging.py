"""Packaging checks for the installed memberful distribution."""

from importlib.resources import files


def test_py_typed_marker_is_present():
    """PEP 561: without py.typed, type checkers treat memberful as untyped."""
    assert files('memberful').joinpath('py.typed').is_file()
