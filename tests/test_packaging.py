"""Packaging checks for the installed memberful distribution."""

from importlib.resources import files
from pathlib import Path

import pytest

import memberful


def test_py_typed_marker_is_present():
    """PEP 561: without py.typed, type checkers treat memberful as untyped."""
    assert files('memberful').joinpath('py.typed').is_file()


def test_version_comes_from_pyproject():
    """__version__ is read from package metadata, so it must match pyproject.toml (reinstall if this fails)."""
    tomllib = pytest.importorskip('tomllib')  # stdlib on 3.11+; the package itself supports 3.10
    pyproject = tomllib.loads((Path(__file__).parent.parent / 'pyproject.toml').read_text())
    assert memberful.__version__ == pyproject['project']['version']
