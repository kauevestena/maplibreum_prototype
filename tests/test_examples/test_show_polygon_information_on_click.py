import json
from maplibreum import Map
from maplibreum.sources import GeoJSONSource

def test_show_polygon_information_on_click():
    """
    Test the 'show-polygon-information-on-click' example.
    """
    # Create a map
    map_ = Map(
        center=[-100.04, 38.907],
        zoom=3,
        map_style="https://demotiles.maplibre.org/style.json",
    )

    # Add a GeoJSON source for the states
    map_.add_source(
        "states",
        GeoJSONSource(data="https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_110m_admin_1_states_provinces_shp.geojson")
    )

    # Add a layer showing the state polygons
    map_.add_layer(
        {
            "id": "states-layer",
            "type": "fill",
            "source": "states",
            "paint": {
                "fill-color": "rgba(200, 100, 240, 0.4)",
                "fill-outline-color": "rgba(200, 100, 240, 1)",
            },
        }
    )

    # Add a click event listener to the states layer to show a popup
    map_.add_event_listener(
        "click",
        layer_id="states-layer",
        js="""
        new maplibregl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(e.features[0].properties.name)
            .addTo(map);
        """,
    )

    # Add mouseenter and mouseleave event listeners to change the cursor
    map_.add_event_listener(
        "mouseenter",
        layer_id="states-layer",
        js="map.getCanvas().style.cursor = 'pointer';",
    )
    map_.add_event_listener(
        "mouseleave",
        layer_id="states-layer",
        js="map.getCanvas().style.cursor = '';",
    )

    # Get the map's HTML representation
    html = map_.render()

    # Verify that the necessary JavaScript snippets are in the HTML
    assert "new maplibregl.Popup()" in html
    assert "e.features[0].properties.name" in html
    assert "map.getCanvas().style.cursor = 'pointer';" in html
    assert "map.getCanvas().style.cursor = '';" in html