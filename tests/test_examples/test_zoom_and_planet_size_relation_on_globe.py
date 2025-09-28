"""Test for zoom and planet size relation on globe."""

import textwrap

from maplibreum.core import Map


def test_zoom_and_planet_size_relation_on_globe():
    """Demonstrate zoom adjustment calculations for globe projection to maintain consistent visual scale."""
    
    button_css = """
    #fly {
        display: block;
        position: absolute;
        top: 20px;
        left: 50%;
        transform: translate(-50%);
        width: 50%;
        height: 40px;
        padding: 10px;
        border: none;
        border-radius: 3px;
        font-size: 12px;
        text-align: center;
        color: #fff;
        background: #ee8a65;
    }
    """.strip()

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[0, 0],
        zoom=2,
        custom_css=button_css,
    )

    # Enable globe projection
    m.enable_globe()

    # Add the zoom adjustment functionality with button
    zoom_adjustment_js = textwrap.dedent(
        """
        // Create the button
        const flyButton = document.createElement('button');
        flyButton.id = 'fly';
        flyButton.textContent = 'Go to pole or equator';
        document.body.appendChild(flyButton);

        // To stay consistent with web mercator maps, globe is automatically enlarged when map center is nearing the poles.
        // This keeps the map center visually similar to a mercator map with the same x,y and zoom.
        // However, sometimes we want to negate this effect and keep the globe size consistent even when changing latitudes.
        // This function computes what we need to add the the target zoom level when changing latitude.
        function getZoomAdjustment(oldLatitude, newLatitude) {
            return Math.log2(Math.cos(newLatitude / 180 * Math.PI) / Math.cos(oldLatitude / 180 * Math.PI));
        }

        // Switch back and forth between zooming in and out.
        let zoomIn = false;
        const zoomDelta = 1.5;

        flyButton.addEventListener('click', () => {
            // Fly to a random location by offsetting the point -74.50, 40
            // by up to 5 degrees.
            const center = [
                map.getCenter().lng,
                zoomIn ? 0 : 80,
            ];
            const mapZoom = map.getZoom();
            const delta = (zoomIn ? zoomDelta : -zoomDelta);
            // We want to change the map's globe size by some delta and change the center latitude at the same time,
            // thus we need to compensate for the globe enlarging effect described earlier.
            const zoom = map.getZoom() + delta + getZoomAdjustment(map.getCenter().lat, center[1]);
            map.flyTo({
                center,
                zoom,
                essential: true // this animation is considered essential with respect to prefers-reduced-motion
            });
            zoomIn = !zoomIn;
        });
        """
    ).strip()

    m.add_on_load_js(zoom_adjustment_js)

    html = m.render()

    # Verify the implementation
    assert '"projection": "globe"' in html
    assert "getZoomAdjustment" in html
    assert "Math.log2" in html
    assert "Math.cos" in html
    assert "map.flyTo({" in html
    assert "essential: true" in html
    assert "Go to pole or equator" in html
    assert "#ee8a65" in html