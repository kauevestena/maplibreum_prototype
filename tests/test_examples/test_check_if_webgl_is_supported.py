"""Test for check-if-webgl-is-supported MapLibre example."""
from maplibreum.core import Map


def test_check_if_webgl_is_supported():
    """Test recreating the 'check-if-webgl-is-supported' MapLibre example."""
    # JavaScript to check for WebGL support and conditionally initialize the map
    js_code = """
    const originalMap = maplibregl.Map;
    maplibregl.Map = function (options) {
        if (isWebglSupported()) {
            return new originalMap(options);
        } else {
            alert('Your browser does not support WebGL');
            return null;
        }
    };

    function isWebglSupported() {
        if (window.WebGLRenderingContext) {
            const canvas = document.createElement('canvas');
            try {
                const context = canvas.getContext('webgl2') || canvas.getContext('webgl');
                if (context && typeof context.getParameter == 'function') {
                    return true;
                }
            } catch (e) {
                // WebGL is supported, but disabled
            }
            return false;
        }
        // WebGL not supported
        return false;
    }
    """

    # Create a map instance and inject the custom JavaScript
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-74.5, 40],
        zoom=2,
        extra_js=js_code,
    )

    # Render the HTML
    html = m.render()

    # Verify that the custom JavaScript is included in the rendered HTML
    assert "const originalMap = maplibregl.Map;" in html
    assert "function isWebglSupported()" in html
    assert "alert('Your browser does not support WebGL');" in html
    assert "new originalMap(options);" in html
    assert "https://demotiles.maplibre.org/style.json" in html