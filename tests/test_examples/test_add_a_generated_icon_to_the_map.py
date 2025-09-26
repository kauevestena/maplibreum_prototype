"""Test for add-a-generated-icon-to-the-map MapLibre example."""

import pytest
from maplibreum.core import Map


def test_add_a_generated_icon_to_the_map():
    """Test recreating the 'add-a-generated-icon-to-the-map' MapLibre example.

    Original JavaScript:
    ```
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://demotiles.maplibre.org/style.json'
    });

    map.on('load', () => {
        const width = 64; // The image will be 64 pixels square
        const bytesPerPixel = 4; // Each pixel is represented by 4 bytes: red, green, blue, and alpha.
        const data = new Uint8Array(width * width * bytesPerPixel);

        for (let x = 0; x < width; x++) {
            for (let y = 0; y < width; y++) {
                const offset = (y * width + x) * bytesPerPixel;
                data[offset + 0] = (y / width) * 255; // red
                data[offset + 1] = (x / width) * 255; // green
                data[offset + 2] = 128; // blue
                data[offset + 3] = 255; // alpha
            }
        }

        map.addImage('gradient', {width, height: width, data});

        map.addSource('point', {
            'type': 'geojson',
            'data': {
                'type': 'FeatureCollection',
                'features': [
                    {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [0, 0]
                        }
                    }
                ]
            }
        });
        map.addLayer({
            'id': 'points',
            'type': 'symbol',
            'source': 'point',
            'layout': {
                'icon-image': 'gradient'
            }
        });
    });
    ```
    """
    # Create map with the same configuration as the original example
    m = Map(map_style="https://demotiles.maplibre.org/style.json")

    # Generate image data similar to the original example
    width = 64
    bytes_per_pixel = 4
    data = []

    for x in range(width):
        for y in range(width):
            offset = (y * width + x) * bytes_per_pixel
            data.extend(
                [
                    int((y / width) * 255),  # red
                    int((x / width) * 255),  # green
                    128,  # blue
                    255,  # alpha
                ]
            )

    # Add the generated image to the map
    m.add_image("gradient", data={"width": width, "height": width, "data": data})

    # Add a GeoJSON source with a point
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [0, 0]}}
        ],
    }

    # Add the source and layer
    m.add_source("point", geojson_data)
    m.add_symbol_layer("points", "point", layout={"icon-image": "gradient"})

    # Verify the components were added correctly
    assert len(m.images) == 1
    assert m.images[0]["id"] == "gradient"
    assert m.images[0]["data"]["width"] == 64
    assert m.images[0]["data"]["height"] == 64
    assert len(m.images[0]["data"]["data"]) == width * width * bytes_per_pixel

    assert any(source["name"] == "point" for source in m.sources)
    assert len(m.layers) == 1
    assert m.layers[0]["id"] == "points"
    assert m.layers[0]["definition"]["type"] == "symbol"
    assert m.layers[0]["definition"]["layout"]["icon-image"] == "gradient"

    # Verify the HTML renders correctly
    html = m.render()
    assert "demotiles.maplibre.org/style.json" in html
    assert "gradient" in html
