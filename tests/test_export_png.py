"""Regression tests for export_png's shell-argument sanitization.

Migrated from the root-level ad hoc script test_export_png.py, which was
never collected by pytest (outside testpaths=["tests"]) and never ran in CI.
"""

import os
from unittest.mock import patch

import pytest

from maplibreum.core import Map


def test_export_png_sanitizes_inputs():
    m = Map()

    with patch("subprocess.run") as mock_run, patch("maplibreum.core.os.remove"):
        m.export_png("--output-dir=./test", width="1024", height="768")

        cmd = mock_run.call_args[0][0]

        assert cmd[0] == "npx"
        assert cmd[1] == "--yes"
        assert cmd[2] == "--"
        assert cmd[3] == "@maplibre/maplibre-gl-export"
        assert cmd[4] == "--input"
        # cmd[5] is the tmp file name
        assert cmd[6] == "--output"

        # The output path must be resolved to an absolute path so a value
        # like "--output-dir=./test" can't be smuggled in as an extra flag.
        assert cmd[7] == os.path.abspath("--output-dir=./test")

        assert cmd[8] == "--width"
        assert cmd[9] == "1024"
        assert cmd[10] == "--height"
        assert cmd[11] == "768"


def test_export_png_fails_on_bad_ints():
    m = Map()

    with patch("subprocess.run"), patch("maplibreum.core.os.remove"):
        with pytest.raises(ValueError):
            m.export_png("test.png", width="1024; rm -rf /", height="768")
