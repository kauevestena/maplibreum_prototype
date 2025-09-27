"""Parity test for the toggle-interactions MapLibre example."""

from __future__ import annotations

import textwrap

from maplibreum.core import Map


def test_toggle_interactions() -> None:
    """Expose checkboxes that enable or disable standard map handlers."""

    map_instance = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-77.04, 38.907],
        zoom=3,
    )

    map_instance.custom_css = textwrap.dedent(
        """
        .listing-group {
            font: 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif;
            font-weight: 600;
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1;
            border-radius: 3px;
            max-width: 20%;
            color: #fff;
        }

        .listing-group input[type='checkbox'] {
            display: none;
        }

        .listing-group input[type='checkbox'] + label {
            background-color: #3386c0;
            display: block;
            cursor: pointer;
            padding: 10px;
            border-bottom: 1px solid rgba(0, 0, 0, 0.25);
            text-transform: capitalize;
        }

        .listing-group input[type='checkbox']:first-child + label {
            border-radius: 3px 3px 0 0;
        }

        .listing-group label:last-child {
            border-radius: 0 0 3px 3px;
            border: none;
        }

        .listing-group input[type='checkbox'] + label:hover,
        .listing-group input[type='checkbox']:checked + label {
            background-color: #4ea0da;
        }

        .listing-group input[type='checkbox']:checked + label:before {
            content: '✔';
            margin-right: 5px;
        }
        """
    ).strip()

    controls_markup = "".join(
        [
            "<input type=\"checkbox\" id=\"scrollZoom\" checked=\"checked\" />",
            "<label for=\"scrollZoom\">Scroll zoom</label>",
            "<input type=\"checkbox\" id=\"boxZoom\" checked=\"checked\" />",
            "<label for=\"boxZoom\">Box zoom</label>",
            "<input type=\"checkbox\" id=\"dragRotate\" checked=\"checked\" />",
            "<label for=\"dragRotate\">Drag rotate</label>",
            "<input type=\"checkbox\" id=\"dragPan\" checked=\"checked\" />",
            "<label for=\"dragPan\">Drag pan</label>",
            "<input type=\"checkbox\" id=\"keyboard\" checked=\"checked\" />",
            "<label for=\"keyboard\">Keyboard</label>",
            "<input type=\"checkbox\" id=\"doubleClickZoom\" checked=\"checked\" />",
            "<label for=\"doubleClickZoom\">Double click zoom</label>",
            "<input type=\"checkbox\" id=\"touchZoomRotate\" checked=\"checked\" />",
            "<label for=\"touchZoomRotate\">Touch zoom rotate</label>",
        ]
    )

    toggle_js = textwrap.dedent(
        f"""
        (function() {{
            var container = document.createElement('nav');
            container.id = 'listing-group';
            container.className = 'listing-group';
            container.innerHTML = {controls_markup!r};
            document.body.appendChild(container);

            container.addEventListener('change', function(e) {{
                var handler = e.target && e.target.id;
                if (!handler || typeof map[handler] === 'undefined') {{ return; }}
                if (e.target.checked) {{
                    map[handler].enable();
                }} else {{
                    map[handler].disable();
                }}
            }});
        }})();
        """
    ).strip()

    map_instance.extra_js = toggle_js

    html = map_instance.render()
    assert "listing-group" in html
    assert "map[handler].enable()" in html
    assert "map[handler].disable()" in html
