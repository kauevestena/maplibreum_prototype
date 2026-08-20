#!/usr/bin/env python3
"""
MapLibre Examples Side-by-Side Comparison Generator.

Generates HTML pages in `development/maplibre_examples/side-by-side/` that display:
- Left half: Original MapLibre GL JS (JavaScript code above, rendered reference map below)
- Right half: MapLibreum Python implementation (Python code above, reproduced map below)
Also generates an interactive index.html gallery dashboard.
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
BASE_DIR = Path(__file__).resolve().parent
STATUS_FILE = BASE_DIR / "status.json"
PAGES_DIR = BASE_DIR / "pages"
REPRODUCED_DIR = BASE_DIR / "reproduced_pages"
OUTPUT_DIR = BASE_DIR / "side-by-side"


TITLE_REPLACEMENTS = {
    "3d": "3D",
    "wms": "WMS",
    "cog": "COG",
    "pmtiles": "PMTiles",
    "geojson": "GeoJSON",
    "svg": "SVG",
    "html": "HTML",
    "rest": "REST",
    "deckgl": "Deck.gl",
    "threejs": "Three.js",
    "babylonjs": "Babylon.js",
    "webgl": "WebGL",
    "mlt": "MLT",
    "api": "API",
}


def format_title(slug: str) -> str:
    """Format a slug into a clean human-readable title."""
    parts = slug.split("-")
    formatted_parts = []
    for part in parts:
        lower = part.lower()
        if lower in TITLE_REPLACEMENTS:
            formatted_parts.append(TITLE_REPLACEMENTS[lower])
        else:
            formatted_parts.append(part.capitalize())
    return " ".join(formatted_parts)


def read_text_safe(path: Path) -> Optional[str]:
    """Safely read text from a file if it exists."""
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except Exception as err:
            print(f"Warning: Failed to read {path}: {err}", file=sys.stderr)
    return None


def get_side_by_side_html(
    slug: str,
    title: str,
    status_info: Dict[str, Any],
    all_slugs: List[str],
    current_index: int,
    js_code: str,
    py_code: Optional[str],
    has_reproduced: bool,
    script_rel_path: Optional[str],
) -> str:
    """Generate the side-by-side comparison HTML for a single example."""
    prev_slug = all_slugs[current_index - 1] if current_index > 0 else None
    next_slug = all_slugs[current_index + 1] if current_index < len(all_slugs) - 1 else None

    # Upstream standalone reference url
    original_map_url = f"https://maplibre.org/maplibre-gl-js/docs/examples/{slug}.html"
    upstream_doc_url = status_info.get("url", f"https://maplibre.org/maplibre-gl-js/docs/examples/{slug}/")

    # Options for dropdown
    options_html = []
    for s in all_slugs:
        selected = ' selected="selected"' if s == slug else ""
        options_html.append(f'<option value="{s}.html"{selected}>{format_title(s)}</option>')
    dropdown_options = "\n          ".join(options_html)

    # Status badges
    is_implemented = py_code is not None and has_reproduced
    parity_badge = (
        '<span class="badge badge-success"><span class="badge-dot"></span> Parity Implemented</span>'
        if is_implemented
        else '<span class="badge badge-warning"><span class="badge-dot"></span> Parity Pending</span>'
    )

    # Left Top: JS Code
    escaped_js = html.escape(js_code.strip()) if js_code else "// No JavaScript source available"

    # Right Top: Python Code
    if py_code:
        escaped_py = html.escape(py_code.strip())
        py_code_display = f'<pre class="line-numbers"><code class="language-python">{escaped_py}</code></pre>'
        py_path_badge = (
            f'<span class="code-path-badge" title="Source script">{script_rel_path or "tests/test_examples"}</span>'
        )
    else:
        py_path_badge = '<span class="code-path-badge status-pending">Pending Implementation</span>'
        py_code_display = f"""<div class="pending-code-card">
  <div class="pending-icon">⏳</div>
  <h3>Python Implementation Needed</h3>
  <p>This example has not been implemented in <code>maplibreum</code> yet.</p>
  <p>To implement, create <code>tests/test_examples/test_{slug.replace('-', '_')}.py</code> and run pytest.</p>
</div>"""

    # Right Bottom: Reproduced Map
    if has_reproduced:
        reproduced_iframe = f'<iframe id="right-map-frame" src="../reproduced_pages/{slug}.html" title="Reproduced MapLibreum Map"></iframe>'
        right_open_link = f'<a href="../reproduced_pages/{slug}.html" target="_blank" rel="noopener" class="pane-btn" title="Open MapLibreum output in new tab">Open Standalone ↗</a>'
    else:
        reproduced_iframe = f"""<div class="pending-map-card">
  <div class="pending-icon">🗺️</div>
  <h3>Reproduced Output Missing</h3>
  <p>Run the test suite to generate <code>development/maplibre_examples/reproduced_pages/{slug}.html</code>.</p>
</div>"""
        right_open_link = '<span class="pane-btn disabled">Standalone Unavailable</span>'

    prev_button = (
        f'<a href="{prev_slug}.html" class="nav-btn" title="Previous: {format_title(prev_slug)}">← Prev</a>'
        if prev_slug
        else '<span class="nav-btn disabled">← Prev</span>'
    )
    next_button = (
        f'<a href="{next_slug}.html" class="nav-btn" title="Next: {format_title(next_slug)}">Next →</a>'
        if next_slug
        else '<span class="nav-btn disabled">Next →</span>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} - MapLibre vs MapLibreum Side-by-Side</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.css" />
  <style>
    :root {{
      --bg-dark: #0f172a;
      --bg-surface: #1e293b;
      --bg-surface-alt: #334155;
      --border-color: #334155;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent-blue: #38bdf8;
      --accent-green: #4ade80;
      --accent-amber: #fbbf24;
      --accent-purple: #c084fc;
      --header-height: 56px;
      --pane-header-height: 38px;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg-dark);
      color: var(--text-main);
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}

    /* Global Navigation Header */
    header.app-header {{
      height: var(--header-height);
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      gap: 12px;
      flex-shrink: 0;
      z-index: 10;
    }}

    .header-left, .header-center, .header-right {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .back-link {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      background: var(--bg-surface-alt);
      color: var(--text-main);
      text-decoration: none;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 500;
      transition: all 0.2s ease;
    }}

    .back-link:hover {{
      background: #475569;
      color: #fff;
      transform: translateY(-1px);
    }}

    .example-title {{
      font-size: 16px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 10px;
      white-space: nowrap;
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 3px 8px;
      border-radius: 9999px;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.02em;
    }}

    .badge-dot {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
    }}

    .badge-success {{
      background: rgba(74, 222, 128, 0.15);
      color: var(--accent-green);
      border: 1px solid rgba(74, 222, 128, 0.3);
    }}
    .badge-success .badge-dot {{
      background: var(--accent-green);
      box-shadow: 0 0 6px var(--accent-green);
    }}

    .badge-warning {{
      background: rgba(251, 191, 36, 0.15);
      color: var(--accent-amber);
      border: 1px solid rgba(251, 191, 36, 0.3);
    }}
    .badge-warning .badge-dot {{
      background: var(--accent-amber);
      box-shadow: 0 0 6px var(--accent-amber);
    }}

    .example-select {{
      background: var(--bg-dark);
      color: var(--text-main);
      border: 1px solid var(--border-color);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      outline: none;
      max-width: 320px;
    }}

    .example-select:focus {{
      border-color: var(--accent-blue);
      box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
    }}

    .nav-btn {{
      display: inline-flex;
      align-items: center;
      padding: 6px 12px;
      background: var(--bg-surface-alt);
      color: var(--text-main);
      text-decoration: none;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 500;
      transition: all 0.2s ease;
    }}

    .nav-btn:hover:not(.disabled) {{
      background: #475569;
      color: #fff;
    }}

    .nav-btn.disabled {{
      opacity: 0.4;
      cursor: not-allowed;
    }}

    .view-mode-buttons {{
      display: flex;
      background: var(--bg-dark);
      padding: 2px;
      border-radius: 6px;
      border: 1px solid var(--border-color);
    }}

    .mode-btn {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 4px 10px;
      font-size: 12px;
      font-weight: 600;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .mode-btn.active, .mode-btn:hover {{
      background: var(--bg-surface-alt);
      color: #fff;
    }}

    /* Main 2x2 Grid Workspace */
    main.workspace {{
      flex: 1;
      display: grid;
      grid-template-columns: 1fr 1fr;
      overflow: hidden;
      position: relative;
    }}

    /* Left and Right Main Columns */
    .comparison-column {{
      display: grid;
      grid-template-rows: 1fr 1fr;
      height: calc(100vh - var(--header-height));
      overflow: hidden;
      border-right: 1px solid var(--border-color);
    }}

    .comparison-column:last-child {{
      border-right: none;
    }}

    /* Pane Container */
    .pane {{
      display: flex;
      flex-direction: column;
      overflow: hidden;
      background: var(--bg-dark);
      position: relative;
    }}

    .pane-top {{
      border-bottom: 1px solid var(--border-color);
    }}

    /* Pane Header */
    .pane-header {{
      height: var(--pane-header-height);
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 12px;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-main);
      user-select: none;
      flex-shrink: 0;
    }}

    .pane-title {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .pane-icon {{
      font-size: 14px;
    }}

    .pane-actions {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .pane-btn {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      background: var(--bg-surface-alt);
      border: 1px solid transparent;
      color: var(--text-main);
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 500;
      text-decoration: none;
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .pane-btn:hover:not(.disabled) {{
      background: #475569;
      border-color: #64748b;
      color: #fff;
    }}

    .pane-btn.disabled {{
      opacity: 0.5;
      cursor: not-allowed;
    }}

    .code-path-badge {{
      font-family: 'Fira Code', monospace;
      font-size: 11px;
      color: var(--accent-blue);
      background: rgba(56, 189, 248, 0.1);
      padding: 2px 6px;
      border-radius: 4px;
      max-width: 260px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}

    .code-path-badge.status-pending {{
      color: var(--accent-amber);
      background: rgba(251, 191, 36, 0.1);
    }}

    /* Code Container */
    .code-viewport {{
      flex: 1;
      overflow: auto;
      background: #141b2d;
      position: relative;
    }}

    .code-viewport pre {{
      margin: 0 !important;
      padding: 14px 14px !important;
      border-radius: 0 !important;
      background: transparent !important;
      font-family: 'Fira Code', monospace !important;
      font-size: 12.5px !important;
      line-height: 1.55 !important;
    }}

    .code-viewport code {{
      font-family: 'Fira Code', monospace !important;
    }}

    /* Map Container & Iframes */
    .map-viewport {{
      flex: 1;
      position: relative;
      background: #020617;
      overflow: hidden;
    }}

    .map-viewport iframe {{
      width: 100%;
      height: 100%;
      border: none;
      display: block;
      background: #0b0f19;
    }}

    /* Pending Placeholders */
    .pending-code-card, .pending-map-card {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      padding: 32px;
      text-align: center;
      color: var(--text-muted);
      background: #141b2d;
    }}

    .pending-icon {{
      font-size: 36px;
      margin-bottom: 12px;
    }}

    .pending-code-card h3, .pending-map-card h3 {{
      color: #fff;
      font-size: 15px;
      margin-bottom: 8px;
    }}

    .pending-code-card p, .pending-map-card p {{
      font-size: 13px;
      max-width: 380px;
      line-height: 1.5;
      margin-bottom: 6px;
    }}

    .pending-code-card code {{
      background: var(--bg-surface-alt);
      color: var(--accent-amber);
      padding: 2px 6px;
      border-radius: 4px;
      font-family: 'Fira Code', monospace;
      font-size: 12px;
    }}

    /* Toast Notification */
    #toast {{
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: var(--accent-green);
      color: #0f172a;
      font-weight: 600;
      font-size: 13px;
      padding: 8px 16px;
      border-radius: 6px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      opacity: 0;
      transform: translateY(10px);
      transition: all 0.2s ease;
      pointer-events: none;
      z-index: 100;
    }}

    #toast.show {{
      opacity: 1;
      transform: translateY(0);
    }}

    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
      width: 8px;
      height: 8px;
    }}
    ::-webkit-scrollbar-track {{
      background: var(--bg-dark);
    }}
    ::-webkit-scrollbar-thumb {{
      background: var(--bg-surface-alt);
      border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: #475569;
    }}

    /* Responsive adjustments */
    @media (max-width: 1024px) {{
      main.workspace {{
        grid-template-columns: 1fr;
        overflow-y: auto;
      }}
      .comparison-column {{
        height: auto;
        min-height: 900px;
        border-right: none;
        border-bottom: 2px solid var(--border-color);
      }}
      body {{
        overflow-y: auto;
      }}
    }}
  </style>
</head>
<body>

  <!-- Application Header -->
  <header class="app-header">
    <div class="header-left">
      <a href="index.html" class="back-link">← All Examples</a>
      <div class="example-title">
        <span>{title}</span>
        {parity_badge}
      </div>
    </div>

    <div class="header-center">
      <select class="example-select" onchange="if (this.value) window.location.href = this.value">
        {dropdown_options}
      </select>
    </div>

    <div class="header-right">
      <div class="view-mode-buttons">
        <button class="mode-btn active" onclick="setViewMode('split')" id="btn-split">50/50</button>
        <button class="mode-btn" onclick="setViewMode('code-focus')" id="btn-code">Code</button>
        <button class="mode-btn" onclick="setViewMode('map-focus')" id="btn-map">Maps</button>
      </div>
      {prev_button}
      {next_button}
    </div>
  </header>

  <!-- Side-by-Side 2x2 Workspace -->
  <main class="workspace" id="workspace">

    <!-- LEFT COLUMN: Original MapLibre GL JS -->
    <section class="comparison-column" id="left-column">
      
      <!-- Top Left: Native JavaScript Code -->
      <div class="pane pane-top" id="left-top-pane">
        <div class="pane-header">
          <div class="pane-title">
            <span class="pane-icon">📜</span>
            <span>Native MapLibre GL JS (JavaScript)</span>
          </div>
          <div class="pane-actions">
            <a href="{upstream_doc_url}" target="_blank" rel="noopener" class="pane-btn" title="View official MapLibre documentation">Docs ↗</a>
            <button class="pane-btn" onclick="copyCode('js-code-block')">Copy JS</button>
          </div>
        </div>
        <div class="code-viewport">
          <pre class="line-numbers"><code class="language-javascript" id="js-code-block">{escaped_js}</code></pre>
        </div>
      </div>

      <!-- Bottom Left: Original Reference Map -->
      <div class="pane pane-bottom" id="left-bottom-pane">
        <div class="pane-header">
          <div class="pane-title">
            <span class="pane-icon">🗺️</span>
            <span>Original Reference Map</span>
          </div>
          <div class="pane-actions">
            <a href="{original_map_url}" target="_blank" rel="noopener" class="pane-btn" title="Open original standalone example">Open Standalone ↗</a>
            <button class="pane-btn" onclick="reloadIframe('left-map-frame')">Reload ⟳</button>
          </div>
        </div>
        <div class="map-viewport">
          <iframe id="left-map-frame" src="{original_map_url}" title="Original MapLibre Example"></iframe>
        </div>
      </div>

    </section>

    <!-- RIGHT COLUMN: MapLibreum Reproduced (Python) -->
    <section class="comparison-column" id="right-column">

      <!-- Top Right: Python Implementation Code -->
      <div class="pane pane-top" id="right-top-pane">
        <div class="pane-header">
          <div class="pane-title">
            <span class="pane-icon">🐍</span>
            <span>MapLibreum (Python)</span>
            {py_path_badge}
          </div>
          <div class="pane-actions">
            <button class="pane-btn" onclick="copyCode('py-code-block')">Copy Python</button>
          </div>
        </div>
        <div class="code-viewport" id="py-code-block">
          {py_code_display}
        </div>
      </div>

      <!-- Bottom Right: MapLibreum Reproduced Map -->
      <div class="pane pane-bottom" id="right-bottom-pane">
        <div class="pane-header">
          <div class="pane-title">
            <span class="pane-icon">⚡</span>
            <span>MapLibreum Generated Map</span>
          </div>
          <div class="pane-actions">
            {right_open_link}
            <button class="pane-btn" onclick="reloadIframe('right-map-frame')">Reload ⟳</button>
          </div>
        </div>
        <div class="map-viewport">
          {reproduced_iframe}
        </div>
      </div>

    </section>

  </main>

  <div id="toast">Copied to clipboard!</div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.js"></script>
  <script>
    function copyCode(containerId) {{
      const el = document.getElementById(containerId);
      if (!el) return;
      const code = el.innerText;
      navigator.clipboard.writeText(code).then(() => {{
        showToast('Code copied to clipboard!');
      }}).catch(() => {{
        showToast('Failed to copy');
      }});
    }}

    function reloadIframe(iframeId) {{
      const frame = document.getElementById(iframeId);
      if (frame && frame.src) {{
        frame.src = frame.src;
        showToast('Map reloaded');
      }}
    }}

    function showToast(msg) {{
      const toast = document.getElementById('toast');
      toast.textContent = msg;
      toast.classList.add('show');
      setTimeout(() => {{
        toast.classList.remove('show');
      }}, 2000);
    }}

    function setViewMode(mode) {{
      document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
      const leftCol = document.getElementById('left-column');
      const rightCol = document.getElementById('right-column');

      if (mode === 'split') {{
        document.getElementById('btn-split').classList.add('active');
        leftCol.style.gridTemplateRows = '1fr 1fr';
        rightCol.style.gridTemplateRows = '1fr 1fr';
      }} else if (mode === 'code-focus') {{
        document.getElementById('btn-code').classList.add('active');
        leftCol.style.gridTemplateRows = '3fr 1fr';
        rightCol.style.gridTemplateRows = '3fr 1fr';
      }} else if (mode === 'map-focus') {{
        document.getElementById('btn-map').classList.add('active');
        leftCol.style.gridTemplateRows = '1fr 3fr';
        rightCol.style.gridTemplateRows = '1fr 3fr';
      }}
    }}
  </script>
</body>
</html>
"""


def get_gallery_index_html(
    entries: List[Dict[str, Any]],
    total_count: int,
    implemented_count: int,
    pending_count: int,
) -> str:
    """Generate the interactive gallery index.html dashboard."""
    percentage = (implemented_count / total_count * 100) if total_count > 0 else 0

    cards_html = []
    for item in entries:
        slug = item["slug"]
        title = item["title"]
        is_implemented = item["is_implemented"]
        script_rel = item.get("script_rel", "")
        js_len = item.get("js_len", 0)

        badge_html = (
            '<span class="card-badge badge-success"><span class="badge-dot"></span> Implemented</span>'
            if is_implemented
            else '<span class="card-badge badge-warning"><span class="badge-dot"></span> Pending</span>'
        )

        status_class = "implemented" if is_implemented else "pending"

        cards_html.append(f"""
      <div class="example-card {status_class}" data-slug="{slug}" data-title="{title.lower()}">
        <div class="card-header">
          <h3 class="card-title"><a href="{slug}.html">{title}</a></h3>
          {badge_html}
        </div>
        <div class="card-meta">
          <span class="meta-slug"><code>{slug}</code></span>
          <span class="meta-js-size">{js_len} chars JS</span>
        </div>
        <div class="card-script">
          {f"<code>{script_rel}</code>" if script_rel else "<span class='text-muted'>No test script mapped</span>"}
        </div>
        <div class="card-actions">
          <a href="{slug}.html" class="action-btn primary">Side-by-Side View ↗</a>
          <a href="https://maplibre.org/maplibre-gl-js/docs/examples/{slug}/" target="_blank" rel="noopener" class="action-btn secondary" title="MapLibre Docs">Docs</a>
          {f'<a href="../reproduced_pages/{slug}.html" target="_blank" rel="noopener" class="action-btn secondary" title="Direct Reproduced Map">Map</a>' if is_implemented else ''}
        </div>
      </div>""")

    all_cards = "\n".join(cards_html)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>MapLibre GL JS vs MapLibreum Parity Suite</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --bg-dark: #0b0f19;
      --bg-surface: #131b2e;
      --bg-card: #1e293b;
      --bg-card-hover: #273549;
      --border-color: #334155;
      --border-focus: #38bdf8;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent-blue: #38bdf8;
      --accent-green: #4ade80;
      --accent-amber: #fbbf24;
      --accent-purple: #c084fc;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg-dark);
      color: var(--text-main);
      min-height: 100vh;
      padding-bottom: 60px;
    }}

    /* Hero Banner */
    .hero {{
      background: linear-gradient(180deg, #131b2e 0%, #0b0f19 100%);
      border-bottom: 1px solid var(--border-color);
      padding: 48px 24px 36px;
      text-align: center;
    }}

    .hero-container {{
      max-width: 1000px;
      margin: 0 auto;
    }}

    .hero-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      background: rgba(56, 189, 248, 0.15);
      color: var(--accent-blue);
      border: 1px solid rgba(56, 189, 248, 0.3);
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 600;
      margin-bottom: 16px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .hero-title {{
      font-size: 32px;
      font-weight: 800;
      color: #fff;
      margin-bottom: 12px;
      letter-spacing: -0.02em;
    }}

    .hero-subtitle {{
      font-size: 16px;
      color: var(--text-muted);
      max-width: 680px;
      margin: 0 auto 32px;
      line-height: 1.6;
    }}

    /* Metrics Grid */
    .metrics-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      max-width: 800px;
      margin: 0 auto 28px;
    }}

    .metric-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      padding: 16px 20px;
      border-radius: 10px;
      text-align: left;
    }}

    .metric-label {{
      font-size: 12px;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      margin-bottom: 6px;
      letter-spacing: 0.03em;
    }}

    .metric-value {{
      font-size: 26px;
      font-weight: 800;
      color: #fff;
      display: flex;
      align-items: baseline;
      gap: 6px;
    }}

    .metric-value.success {{
      color: var(--accent-green);
    }}

    .metric-value.warning {{
      color: var(--accent-amber);
    }}

    /* Progress Bar */
    .progress-bar-container {{
      max-width: 800px;
      margin: 0 auto;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 9999px;
      height: 12px;
      overflow: hidden;
      padding: 2px;
    }}

    .progress-bar-fill {{
      background: linear-gradient(90deg, #38bdf8 0%, #4ade80 100%);
      height: 100%;
      border-radius: 9999px;
      transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    /* Controls & Filter Bar */
    .filter-section {{
      max-width: 1200px;
      margin: 32px auto 24px;
      padding: 0 24px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }}

    .search-box {{
      flex: 1;
      min-width: 280px;
      position: relative;
    }}

    .search-input {{
      width: 100%;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      color: var(--text-main);
      padding: 10px 16px 10px 40px;
      border-radius: 8px;
      font-size: 14px;
      outline: none;
      transition: all 0.2s;
    }}

    .search-input:focus {{
      border-color: var(--border-focus);
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
    }}

    .search-icon {{
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      font-size: 14px;
    }}

    .filter-tabs {{
      display: flex;
      gap: 8px;
      background: var(--bg-surface);
      padding: 4px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
    }}

    .filter-tab {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .filter-tab.active, .filter-tab:hover {{
      background: var(--bg-card);
      color: #fff;
    }}

    /* Examples Grid */
    .gallery-container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 24px;
    }}

    .examples-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 20px;
    }}

    .example-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.2s ease;
    }}

    .example-card:hover {{
      background: var(--bg-card-hover);
      border-color: #475569;
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
    }}

    .card-header {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 10px;
    }}

    .card-title {{
      font-size: 15px;
      font-weight: 700;
      line-height: 1.3;
    }}

    .card-title a {{
      color: #fff;
      text-decoration: none;
      transition: color 0.15s;
    }}

    .card-title a:hover {{
      color: var(--accent-blue);
    }}

    .card-badge {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 8px;
      border-radius: 9999px;
      font-size: 10.5px;
      font-weight: 600;
      white-space: nowrap;
    }}

    .badge-dot {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
    }}

    .badge-success {{
      background: rgba(74, 222, 128, 0.15);
      color: var(--accent-green);
      border: 1px solid rgba(74, 222, 128, 0.3);
    }}
    .badge-success .badge-dot {{
      background: var(--accent-green);
    }}

    .badge-warning {{
      background: rgba(251, 191, 36, 0.15);
      color: var(--accent-amber);
      border: 1px solid rgba(251, 191, 36, 0.3);
    }}
    .badge-warning .badge-dot {{
      background: var(--accent-amber);
    }}

    .card-meta {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 11.5px;
      color: var(--text-muted);
      margin-bottom: 10px;
    }}

    .meta-slug code {{
      font-family: 'Fira Code', monospace;
      color: var(--accent-blue);
      background: rgba(56, 189, 248, 0.08);
      padding: 2px 5px;
      border-radius: 4px;
    }}

    .card-script {{
      font-size: 11px;
      color: var(--text-muted);
      margin-bottom: 16px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}

    .card-script code {{
      font-family: 'Fira Code', monospace;
      color: #cbd5e1;
    }}

    .card-actions {{
      display: flex;
      align-items: center;
      gap: 8px;
      padding-top: 12px;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
    }}

    .action-btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.15s;
    }}

    .action-btn.primary {{
      flex: 1;
      background: var(--accent-blue);
      color: #0f172a;
    }}

    .action-btn.primary:hover {{
      background: #7dd3fc;
      transform: translateY(-1px);
    }}

    .action-btn.secondary {{
      background: var(--bg-surface);
      color: var(--text-muted);
      border: 1px solid var(--border-color);
    }}

    .action-btn.secondary:hover {{
      background: #334155;
      color: #fff;
    }}

    .text-muted {{
      color: var(--text-muted);
    }}

    .no-results {{
      grid-column: 1 / -1;
      text-align: center;
      padding: 60px 20px;
      color: var(--text-muted);
      font-size: 15px;
      display: none;
    }}
  </style>
</head>
<body>

  <!-- Hero Section -->
  <section class="hero">
    <div class="hero-container">
      <div class="hero-badge">MapLibre GL JS Parity Suite</div>
      <h1 class="hero-title">Side-by-Side Example Comparison</h1>
      <p class="hero-subtitle">
        Visual parity testing and interactive code viewer comparing upstream MapLibre GL JS examples with their native Python MapLibreum implementations.
      </p>

      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-label">Total Examples</div>
          <div class="metric-value">{total_count}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Implemented in Python</div>
          <div class="metric-value success">{implemented_count}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Parity Coverage</div>
          <div class="metric-value success">{percentage:.1f}%</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Pending Port</div>
          <div class="metric-value warning">{pending_count}</div>
        </div>
      </div>

      <div class="progress-bar-container" title="{percentage:.1f}% Coverage">
        <div class="progress-bar-fill" style="width: {percentage:.1f}%;"></div>
      </div>
    </div>
  </section>

  <!-- Filter & Search Controls -->
  <section class="filter-section">
    <div class="search-box">
      <span class="search-icon">🔍</span>
      <input type="text" id="searchInput" class="search-input" placeholder="Search examples by name or slug..." oninput="filterExamples()" />
    </div>

    <div class="filter-tabs">
      <button class="filter-tab active" onclick="setFilter('all', this)">All ({total_count})</button>
      <button class="filter-tab" onclick="setFilter('implemented', this)">Implemented ({implemented_count})</button>
      <button class="filter-tab" onclick="setFilter('pending', this)">Pending ({pending_count})</button>
    </div>
  </section>

  <!-- Examples Grid -->
  <main class="gallery-container">
    <div class="examples-grid" id="examplesGrid">
      {all_cards}
      <div class="no-results" id="noResults">
        No examples found matching your search query.
      </div>
    </div>
  </main>

  <script>
    let currentFilter = 'all';

    function setFilter(filter, tabEl) {{
      currentFilter = filter;
      document.querySelectorAll('.filter-tab').forEach(el => el.classList.remove('active'));
      tabEl.classList.add('active');
      filterExamples();
    }}

    function filterExamples() {{
      const query = document.getElementById('searchInput').value.toLowerCase().trim();
      const cards = document.querySelectorAll('.example-card');
      let visibleCount = 0;

      cards.forEach(card => {{
        const title = card.getAttribute('data-title') || '';
        const slug = card.getAttribute('data-slug') || '';
        const isImplemented = card.classList.contains('implemented');

        const matchesQuery = !query || title.includes(query) || slug.includes(query);
        let matchesFilter = true;

        if (currentFilter === 'implemented' && !isImplemented) matchesFilter = false;
        if (currentFilter === 'pending' && isImplemented) matchesFilter = false;

        if (matchesQuery && matchesFilter) {{
          card.style.display = 'flex';
          visibleCount++;
        }} else {{
          card.style.display = 'none';
        }}
      }});

      document.getElementById('noResults').style.display = visibleCount === 0 ? 'block' : 'none';
    }}
  </script>
</body>
</html>
"""


def main() -> None:
    """Generate all side-by-side comparison pages."""
    print("=== Generating MapLibre Examples Side-by-Side Suite ===")

    if not STATUS_FILE.exists():
        print(f"Error: Status file not found: {STATUS_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        status_data: Dict[str, Any] = json.load(f)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_slugs = sorted(status_data.keys())
    total_count = len(all_slugs)
    implemented_count = 0
    pending_count = 0

    gallery_entries: List[Dict[str, Any]] = []

    print(f"Processing {total_count} examples...")

    for idx, slug in enumerate(all_slugs):
        info = status_data[slug]
        title = format_title(slug)

        # 1. Native JavaScript code
        js_file = PAGES_DIR / f"{slug}.html"
        js_code = read_text_safe(js_file) or ""

        # 2. Python code
        script_path_str = info.get("script")
        py_code = None
        script_rel_path = None
        if script_path_str:
            script_file = REPO_ROOT / script_path_str
            py_code = read_text_safe(script_file)
            script_rel_path = script_path_str
        else:
            # Fallback check
            cand = REPO_ROOT / "tests" / "test_examples" / f"test_{slug.replace('-', '_')}.py"
            if cand.exists():
                py_code = read_text_safe(cand)
                script_rel_path = f"tests/test_examples/test_{slug.replace('-', '_')}.py"

        # 3. Reproduced Map HTML
        reproduced_file = REPRODUCED_DIR / f"{slug}.html"
        has_reproduced = reproduced_file.exists()

        is_implemented = (py_code is not None) and has_reproduced
        if is_implemented:
            implemented_count += 1
        else:
            pending_count += 1

        # Generate individual comparison page
        page_html = get_side_by_side_html(
            slug=slug,
            title=title,
            status_info=info,
            all_slugs=all_slugs,
            current_index=idx,
            js_code=js_code,
            py_code=py_code,
            has_reproduced=has_reproduced,
            script_rel_path=script_rel_path,
        )

        out_file = OUTPUT_DIR / f"{slug}.html"
        out_file.write_text(page_html, encoding="utf-8")

        gallery_entries.append(
            {
                "slug": slug,
                "title": title,
                "is_implemented": is_implemented,
                "script_rel": script_rel_path,
                "js_len": len(js_code),
            }
        )

    # Generate Gallery Index
    index_html = get_gallery_index_html(
        entries=gallery_entries,
        total_count=total_count,
        implemented_count=implemented_count,
        pending_count=pending_count,
    )
    index_file = OUTPUT_DIR / "index.html"
    index_file.write_text(index_html, encoding="utf-8")

    print(f"\nSuccessfully generated {total_count} comparison pages + index.html in:")
    print(f"  {OUTPUT_DIR}")
    print(f"Status: {implemented_count}/{total_count} implemented ({implemented_count / total_count * 100:.1f}%), {pending_count} pending.\n")


if __name__ == "__main__":
    main()
