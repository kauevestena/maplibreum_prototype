"""Testing helpers for MapLibre example parity tests."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

import pytest

from maplibreum.core import Map

_STATUS_PATH = Path("misc/maplibre_examples/status.json")
_OUTPUT_DIR = Path("misc/maplibre_examples/reproduced_pages")


def _slug_from_request_path(path: Path) -> str:
    name = path.name
    if name.startswith("test_"):
        name = name[len("test_") :]
    if name.endswith(".py"):
        name = name[: -len(".py")]
    return name.replace("_", "-")


@lru_cache(maxsize=None)
def _status_lookup() -> Dict[str, Dict[str, Any]]:
    if not _STATUS_PATH.exists():
        return {}
    with _STATUS_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _get_metadata(slug: str) -> Dict[str, Any]:
    record = _status_lookup().get(slug, {})
    if not record:
        return {}
    inner_key, inner_value = next(iter(record.items()))
    if inner_key != slug:
        return inner_value
    return inner_value


@pytest.fixture(autouse=True)
def capture_reproduction_page(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
    """Wrap Map.render to emit a documentation page for each gallery example."""

    slug = _slug_from_request_path(Path(str(request.node.fspath)))
    metadata = _get_metadata(slug)
    gallery_url = metadata.get("url")
    title_text = metadata.get("title") or slug.replace("-", " ").title()
    test_filename = Path(str(request.node.fspath)).name

    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = _OUTPUT_DIR / f"{slug}.html"

    original_render = Map.render

    def _wrapped_render(self, *args, **kwargs):  # type: ignore[override]
        html = original_render(self, *args, **kwargs)
        header_lines = [
            "<div class=\"maplibreum-example-banner\">",
            f"  <h1>{title_text}</h1>",
        ]
        if gallery_url:
            header_lines.append(
                "  <p>Original MapLibre example: "
                f"<a href=\"{gallery_url}\" target=\"_blank\" rel=\"noopener\">{gallery_url}</a></p>"
            )
        header_lines.append(
            f"  <p>Generated from {test_filename} by the automated test suite.</p>"
        )
        header_lines.append("</div>")
        banner = "\n".join(header_lines) + "\n"

        if "<body>" in html:
            prefix, remainder = html.split("<body>", 1)
            html_output = f"{prefix}<body>\n{banner}{remainder}"
        else:
            html_output = f"<body>\n{banner}</body>" if not html.strip() else banner + html

        output_file.write_text(html_output, encoding="utf-8")
        return html_output

    monkeypatch.setattr(Map, "render", _wrapped_render, raising=False)
