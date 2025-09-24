"""Testing helpers for MapLibre example parity tests."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

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


def _inject_banner(html: str, banner: str) -> str:
    """Insert a banner immediately after the opening ``<body>`` tag."""

    if not html.strip():
        return f"<body>\n{banner}</body>"

    lower_html = html.lower()
    body_index = lower_html.find("<body")
    if body_index == -1:
        return banner + html

    tag_end = lower_html.find(">", body_index)
    if tag_end == -1:
        return banner + html

    insertion_point = tag_end + 1
    return html[:insertion_point] + "\n" + banner + html[insertion_point:]


def _load_original_html(path_value: Optional[str]) -> Optional[str]:
    """Return the contents of the scraped HTML page if it exists."""

    if not path_value:
        return None

    candidate = Path(path_value)
    if not candidate.is_absolute():
        candidate = _REPO_ROOT / candidate

    try:
        return candidate.read_text(encoding="utf-8") if candidate.exists() else None
    except OSError:
        return None


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

        html_output = _inject_banner(html, banner)

        original_html = _load_original_html(metadata.get("file_path"))
        if original_html is not None:
            write_payload = _inject_banner(original_html, banner)
        else:
            write_payload = html_output

        output_file.write_text(write_payload, encoding="utf-8")
        return html_output

    monkeypatch.setattr(Map, "render", _wrapped_render, raising=False)
