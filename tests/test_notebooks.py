"""Keep the narrative notebooks executable and their maps renderable."""

import json
from pathlib import Path

import pytest

from maplibreum import Map


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples"
NOTEBOOKS = sorted(EXAMPLE_DIR.glob("[0-9][0-9]_*.ipynb"))


@pytest.mark.parametrize("notebook_path", NOTEBOOKS, ids=lambda path: path.stem)
def test_example_notebook_executes_and_renders(notebook_path, monkeypatch, tmp_path):
    """Execute code cells in order and render every map left in the namespace."""

    monkeypatch.chdir(tmp_path)
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    namespace = {"__name__": "__main__"}

    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell.get("source", []))
        code = compile(source, f"{notebook_path.name}:cell-{index}", "exec")
        exec(code, namespace)

    maps = {
        name: value for name, value in namespace.items() if isinstance(value, Map)
    }
    assert maps, f"{notebook_path.name} did not create a Map"

    for name, map_object in maps.items():
        html = map_object.render()
        assert "<!DOCTYPE html>" in html, f"{name} did not render a complete page"
        assert "maplibre-gl@6.0.0" in html, f"{name} did not pin MapLibre 6"
        assert len(html) > 10_000, f"{name} produced unexpectedly small HTML"


def test_example_notebooks_are_clean_source_files():
    """Committed notebooks should not contain stale output or execution state."""

    assert NOTEBOOKS, "No narrative example notebooks were found"
    for notebook_path in NOTEBOOKS:
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        assert notebook["nbformat"] == 4
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                assert cell.get("execution_count") is None
                assert cell.get("outputs", []) == []
