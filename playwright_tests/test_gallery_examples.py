"""Manual Playwright checks for rendered MapLibreum examples.

These tests exercise the generated HTML in ``development/maplibre_examples/reproduced_pages``
with a real browser. They are intentionally excluded from the default pytest run
(``pyproject.toml`` limits automated discovery to the ``tests`` package) so they can
be executed on demand when browser-level validation is required.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import pytest

pytest.importorskip("pytest_playwright")
pytest.importorskip("playwright")

_STATUS_PATH = Path("development/maplibre_examples/status.json")
_REPRODUCED_DIR = Path("development/maplibre_examples/reproduced_pages")


def _load_example_cases() -> Iterable[Tuple[str, Path, Dict[str, Any]]]:
    if not _STATUS_PATH.exists():
        return []
    with _STATUS_PATH.open("r", encoding="utf-8") as handle:
        status = json.load(handle)

    for slug, wrapper in status.items():
        if isinstance(wrapper, dict) and slug not in wrapper:
            # New clean structure - wrapper is directly the metadata
            metadata = wrapper
        else:
            # Legacy structure with duplicate keys
            inner_key, inner_value = next(iter(wrapper.items()))
            # Normalise legacy entries that accidentally duplicated the slug key.
            metadata = inner_value if inner_key == slug else wrapper[inner_key]
        if not metadata.get("script"):
            continue
        yield slug, _REPRODUCED_DIR / f"{slug}.html", metadata


@pytest.mark.browser
@pytest.mark.manual
@pytest.mark.parametrize(
    "slug, html_path, metadata",
    list(_load_example_cases()),
    ids=lambda case: case[0] if isinstance(case, tuple) else case,
)
def test_rendered_example_loads(
    page, slug: str, html_path: Path, metadata: Dict[str, Any]
):
    """Confirm the generated HTML boots MapLibre GL and exposes style metadata."""

    if not html_path.exists():
        pytest.skip(
            f"Reproduced page for {slug!r} not found. Re-run pytest tests/test_examples to regenerate."
        )

    page.goto(html_path.resolve().as_uri())

    # Wait until MapLibre injects its canvas into the DOM.
    page.wait_for_selector(".maplibregl-canvas", timeout=60_000)

    # Wait for at least one tracked map instance to finish loading.
    page.wait_for_function(
        "() => window.maplibreumMapsLoaded && Object.values(window.maplibreumMapsLoaded).some(Boolean)",
        timeout=60_000,
    )

    style_summary = page.evaluate(
        """
        () => {
            const maps = window.maplibreumMaps || {};
            const first = Object.values(maps)[0];
            if (!first) {
                return {layers: 0, sources: 0};
            }
            const style = first.getStyle();
            return {
                layers: Array.isArray(style.layers) ? style.layers.length : 0,
                sources: style.sources ? Object.keys(style.sources).length : 0,
            };
        }
        """
    )

    assert (
        style_summary["layers"] > 0
    ), "Expected the MapLibre style to expose at least one layer"
    assert (
        style_summary["sources"] > 0
    ), "Expected the MapLibre style to expose at least one source"

    banner_link = page.locator(".maplibreum-example-banner a")
    if metadata.get("url"):
        banner_link.wait_for()
        assert metadata["url"] in banner_link.get_attribute(
            "href"
        ), "Original example URL missing"
    else:
        assert banner_link.count() == 0
