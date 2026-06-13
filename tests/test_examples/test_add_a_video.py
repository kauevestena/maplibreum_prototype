"""Test for add-a-video MapLibre example."""

import textwrap

import pytest

from maplibreum import Map


def test_add_a_video():
    """Test video overlay using improved Python API (Phase 2 improvement).

    This version eliminates JavaScript injection by:
    1. Using VideoOverlay class instead of manual source/layer setup
    2. Auto-generating playback controls
    3. Providing clean Python configuration
    """
    from maplibreum.sources import VideoOverlay

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-122.514426, 37.562984],
        zoom=17,
        bearing=-96,
    )

    # Define video corners
    coordinates = [
        [-122.51596391201019, 37.56238816766053],
        [-122.51467645168304, 37.56410183312965],
        [-122.51309394836426, 37.563391708549425],
        [-122.51423120498657, 37.56161849366671],
    ]

    # Create video overlay with Python API
    video_overlay = VideoOverlay(
        source_id="drone-video",
        layer_id="drone-video-layer",
        urls=[
            "https://static-assets.mapbox.com/mapbox-gl-js/drone.mp4",
            "https://static-assets.mapbox.com/mapbox-gl-js/drone.webm",
        ],
        coordinates=coordinates,
        autoplay=True,
        loop=True,
        click_to_toggle=True,
    )

    # Add source
    m.add_source(video_overlay.source_id, video_overlay.get_source_config())

    # Add layer
    m.add_layer(video_overlay.get_layer_config())

    # Add controls JavaScript
    m.add_on_load_js(video_overlay.to_js())

    # Generate HTML
    html = m.render()

    # Verify Python API usage
    assert '"center": [-122.514426, 37.562984]' in html
    assert '"zoom": 17' in html

    # Verify video source ID is present
    assert "drone-video" in html

    # Verify layer is present
    assert "drone-video-layer" in html

    # Verify video URLs
    assert "drone.mp4" in html
    assert "drone.webm" in html

    # Verify toggle controls are present
    assert "videoSource" in html
    assert "play()" in html
    assert "pause()" in html
    assert "map.on('click'" in html or 'map.on("click"' in html
