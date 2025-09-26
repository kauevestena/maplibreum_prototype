"""Test for add-a-video MapLibre example."""

import textwrap

import pytest

from maplibreum import Map


def test_add_a_video():
    """Replicate the video overlay example with satellite basemap."""

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-122.514426, 37.562984],
        zoom=17,
        bearing=-96,
        map_options={"minZoom": 14},
    )

    # Background layer to match the dark backdrop used in the original example
    background_layer = {
        "id": "background",
        "type": "background",
        "paint": {"background-color": "rgb(4,7,14)"},
    }
    m.add_layer(background_layer)

    # Satellite raster source from MapTiler (placeholder key as in the example)
    satellite_source = {
        "type": "raster",
        "url": "https://api.maptiler.com/tiles/satellite/tiles.json?key=get_your_own_OpIi9ZULNHzrESv6T2vL",
        "tileSize": 256,
    }
    m.add_source("satellite", satellite_source)
    m.add_layer({"id": "satellite", "type": "raster", "source": "satellite"})

    # Video source covering the Golden Gate drone footage footprint
    video_coordinates = [
        [-122.51596391201019, 37.56238816766053],
        [-122.51467645168304, 37.56410183312965],
        [-122.51309394836426, 37.563391708549425],
        [-122.51423120498657, 37.56161849366671],
    ]
    video_source = {
        "type": "video",
        "urls": [
            "https://static-assets.mapbox.com/mapbox-gl-js/drone.mp4",
            "https://static-assets.mapbox.com/mapbox-gl-js/drone.webm",
        ],
        "coordinates": video_coordinates,
    }
    m.add_source("video", video_source)
    m.add_layer({"id": "video", "type": "raster", "source": "video"})

    # Track playback state and wire up the click interaction
    m.add_on_load_js("window._maplibreumVideoPlaying = true;")

    toggle_js = textwrap.dedent(
        """
        var videoSource = map.getSource('video');
        if (!videoSource) { return; }
        if (window._maplibreumVideoPlaying) {
            videoSource.pause();
            window._maplibreumVideoPlaying = false;
        } else {
            videoSource.play();
            window._maplibreumVideoPlaying = true;
        }
        """
    ).strip()
    binding_id = m.add_event_listener("click", js=toggle_js, event_id="toggle-video")

    # Verify core map configuration
    assert m.center == [-122.514426, 37.562984]
    assert m.zoom == 17
    assert m.bearing == -96
    assert m.additional_map_options["minZoom"] == 14

    # Ensure the satellite and video sources are registered
    source_lookup = {source["name"]: source["definition"] for source in m.sources}
    assert "satellite" in source_lookup
    assert "video" in source_lookup

    assert source_lookup["satellite"]["type"] == "raster"
    assert "tiles" not in source_lookup["satellite"]  # URL-based TileJSON source
    assert "tiles.json" in source_lookup["satellite"]["url"]

    video_def = source_lookup["video"]
    assert video_def["type"] == "video"
    assert video_def["urls"] == [
        "https://static-assets.mapbox.com/mapbox-gl-js/drone.mp4",
        "https://static-assets.mapbox.com/mapbox-gl-js/drone.webm",
    ]
    assert video_def["coordinates"] == video_coordinates

    # Confirm layers are queued with the expected ordering
    layer_ids = [layer["id"] for layer in m.layers]
    assert layer_ids[:3] == ["background", "satellite", "video"]

    background_def = next(layer["definition"] for layer in m.layers if layer["id"] == "background")
    assert background_def["type"] == "background"
    assert background_def["paint"]["background-color"] == "rgb(4,7,14)"

    video_layer_def = next(layer["definition"] for layer in m.layers if layer["id"] == "video")
    assert video_layer_def["type"] == "raster"
    assert video_layer_def["source"] == "video"

    # Validate the click handler wiring
    assert binding_id == "toggle-video"
    binding = next(evt for evt in m.event_bindings if evt.id == "toggle-video")
    assert "videoSource" in binding.js
    assert "pause" in binding.js
    assert "play" in binding.js

    # Render HTML and ensure critical strings are embedded
    html = m._repr_html_()
    assert "drone.mp4" in html
    assert "drone.webm" in html
    assert "videoSource" in html  # Check that the toggle JS is present
    assert "videoSource.pause()" in html
    assert "videoSource.play()" in html
    assert "background-color" in html
    assert "tiles.json" in html


if __name__ == "__main__":
    pytest.main([__file__])
