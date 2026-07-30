"""Manual Playwright checks for rendered MapLibreum examples.

These tests exercise the generated HTML in ``development/maplibre_examples/reproduced_pages``
with a real browser. They are intentionally excluded from the default pytest run
(``pyproject.toml`` limits automated discovery to the ``tests`` package) so they can
be executed on demand when browser-level validation is required.
"""

from __future__ import annotations

import json
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import pytest

pytest.importorskip("pytest_playwright")
pytest.importorskip("playwright")

_STATUS_PATH = Path("development/maplibre_examples/status.json")
_REPRODUCED_DIR = Path("development/maplibre_examples/reproduced_pages")
_SCREENSHOT_DIR = Path(
    os.environ.get("MAPLIBREUM_SCREENSHOT_DIR", "playwright-report/screenshots")
)


class _QuietRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        """Keep the pytest output focused on browser diagnostics."""


@pytest.fixture(scope="session")
def gallery_base_url():
    """Serve generated pages over HTTP so browser CORS rules match real use."""

    handler = partial(_QuietRequestHandler, directory=str(Path.cwd()))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _load_example_cases() -> Iterable[Tuple[str, Path, Dict[str, Any]]]:
    if not _STATUS_PATH.exists():
        return []
    with _STATUS_PATH.open("r", encoding="utf-8") as handle:
        status = json.load(handle)

    cases = []
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
        cases.append((slug, _REPRODUCED_DIR / f"{slug}.html", metadata))

    requested_slug = os.environ.get("MAPLIBREUM_GALLERY_SLUG")
    if requested_slug:
        cases = [case for case in cases if case[0] == requested_slug]
        if not cases:
            raise ValueError(f"Unknown or unimplemented gallery slug: {requested_slug}")

    shard_total = int(os.environ.get("MAPLIBREUM_GALLERY_SHARD_TOTAL", "1"))
    shard_index = int(os.environ.get("MAPLIBREUM_GALLERY_SHARD_INDEX", "0"))
    if shard_total < 1 or not 0 <= shard_index < shard_total:
        raise ValueError("Invalid MapLibreum gallery shard configuration")

    yield from cases[shard_index::shard_total]


@pytest.mark.browser
@pytest.mark.manual
@pytest.mark.parametrize(
    "slug, html_path, metadata",
    list(_load_example_cases()),
    ids=lambda case: case[0] if isinstance(case, tuple) else case,
)
def test_rendered_example_loads(
    page,
    gallery_base_url: str,
    slug: str,
    html_path: Path,
    metadata: Dict[str, Any],
):
    """Confirm the generated HTML boots MapLibre GL and exposes style metadata."""

    if not html_path.exists():
        pytest.fail(
            f"Reproduced page for {slug!r} not found. "
            "Re-run pytest tests/test_examples to regenerate."
        )

    page_errors = []
    console_errors = []
    failed_requests = []
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    page.on(
        "console",
        lambda message: (
            console_errors.append(message.text) if message.type == "error" else None
        ),
    )
    page.on(
        "requestfailed",
        lambda request: failed_requests.append(
            f"{request.url}: {request.failure or 'request failed'}"
        ),
    )

    page.goto(
        f"{gallery_base_url}/{html_path.as_posix()}",
        wait_until="domcontentloaded",
    )

    try:
        # Wait until MapLibre injects its canvas into the DOM.
        page.wait_for_selector(".maplibregl-canvas", timeout=60_000)

        # Every map in multi-map examples must expose a populated style.
        page.wait_for_function(
            """
            () => {
                const maps = window.maplibreumMaps || {};
                const ids = Object.keys(maps);
                return ids.length > 0 && ids.every((id) => {
                    const map = maps[id];
                    const style = map.getStyle();
                    return map.getCanvas()
                        && Array.isArray(style.layers)
                        && style.layers.length > 0
                        && style.sources
                        && Object.keys(style.sources).length > 0;
                });
            }
            """,
            timeout=60_000,
        )
    except Exception as error:
        diagnostics = {
            "page_errors": page_errors,
            "console_errors": console_errors,
            "failed_requests": failed_requests,
            "url": page.url,
        }
        pytest.fail(f"{error}\nBrowser diagnostics:\n{json.dumps(diagnostics, indent=2)}")
    finally:
        _SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        page.screenshot(
            path=str(_SCREENSHOT_DIR / f"{slug}.png"),
            full_page=True,
        )

    style_summary = page.evaluate(
        """
        () => {
            const maps = window.maplibreumMaps || {};
            return {
                version: maplibregl.version,
                maps: Object.values(maps).map((map) => {
                    const style = map.getStyle();
                    return {
                        layers: Array.isArray(style.layers) ? style.layers.length : 0,
                        sources: style.sources ? Object.keys(style.sources).length : 0,
                        canvasWidth: map.getCanvas().width,
                        canvasHeight: map.getCanvas().height,
                    };
                }),
            };
        }
        """
    )

    assert style_summary["version"].split(".", 1)[0] == "6"
    assert style_summary["maps"], "Expected at least one tracked MapLibre map"
    for map_summary in style_summary["maps"]:
        assert map_summary["layers"] > 0
        assert map_summary["sources"] > 0
        assert map_summary["canvasWidth"] > 0
        assert map_summary["canvasHeight"] > 0

    assert not page_errors, f"Unhandled page errors: {page_errors}"
    assert not console_errors, f"Browser console errors: {console_errors}"
    assert not failed_requests, f"Failed browser requests: {failed_requests}"

    banner_link = page.locator(".maplibreum-example-banner a")
    if metadata.get("url"):
        banner_link.wait_for()
        assert metadata["url"] in banner_link.get_attribute(
            "href"
        ), "Original example URL missing"
    else:
        assert banner_link.count() == 0
