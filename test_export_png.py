import sys
from unittest.mock import patch, MagicMock
from maplibreum.core import Map
import os

def test_export_png_sanitizes_inputs():
    m = Map()

    with patch('subprocess.run') as mock_run:
        with patch('maplibreum.core.os.remove') as mock_remove:
            m.export_png("--output-dir=./test", width="1024", height="768")

            cmd = mock_run.call_args[0][0]
            print(f"Executed command: {cmd}")

            assert cmd[0] == "npx"
            assert cmd[1] == "--yes"
            assert cmd[2] == "--"
            assert cmd[3] == "@maplibre/maplibre-gl-export"
            assert cmd[4] == "--input"
            # cmd[5] is the tmp name
            assert cmd[6] == "--output"

            # The filepath should be absolute, so it shouldn't start with "--output-dir" directly anymore
            assert cmd[7] == os.path.abspath("--output-dir=./test")

            assert cmd[8] == "--width"
            assert cmd[9] == "1024"
            assert cmd[10] == "--height"
            assert cmd[11] == "768"

            print("Successfully sanitized standard inputs")

def test_export_png_fails_on_bad_ints():
    m = Map()

    with patch('subprocess.run') as mock_run:
        with patch('maplibreum.core.os.remove') as mock_remove:
            try:
                m.export_png("test.png", width="1024; rm -rf /", height="768")
                print("Failed: Should have raised ValueError")
                sys.exit(1)
            except ValueError:
                print("Successfully caught bad int for width")

if __name__ == "__main__":
    test_export_png_sanitizes_inputs()
    test_export_png_fails_on_bad_ints()
    print("All tests passed.")
