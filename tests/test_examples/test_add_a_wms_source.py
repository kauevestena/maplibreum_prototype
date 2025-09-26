"""Test for add-a-wms-source MapLibre example."""

import pytest
from maplibreum.core import Map


def test_add_a_wms_source():
    """Test recreating the 'add-a-wms-source' MapLibre example.
    
    Original JavaScript:
    ```
    const map = new maplibregl.Map({
        container: 'map',
        style: {
            version: 8,
            sources: {
                'wms-test-source': {
                    type: 'raster',
                    // use the tiles option to specify a WMS tile source URL
                    // https://maplibre.org/maplibre-style-spec/sources/
                    tiles: [
                        'https://ows.terrestris.de/osm/service?service=WMS&request=GetMap&version=1.1.1&layers=TOPO-WMS%2COSM-Overlay-WMS&styles=&format=image%2Fpng&transparent=true&info_format=text%2Fhtml&tiled=false&srs=EPSG:3857&bbox={bbox-epsg-3857}&width=256&height=256'
                    ],
                    tileSize: 256
                }
            },
            layers: [{
                id: 'wms-test-layer',
                type: 'raster',
                source: 'wms-test-source',
                paint: {}
            }]
        },
        zoom: 8,
        center: [-74.5447, 40.6892]
    });
    ```
    """
    # Create map with the same configuration as the original example
    m = Map(
        zoom=8,
        center=[-74.5447, 40.6892]
    )
    
    # Add WMS layer using the built-in method
    m.add_wms_layer(
        base_url='https://ows.terrestris.de/osm/service',
        layers='TOPO-WMS,OSM-Overlay-WMS',
        name='wms-test-layer',
        styles='',
        version='1.1.1',
        format='image/png',
        transparent=True
    )
    
    # Verify the components were added correctly
    assert m.center == [-74.5447, 40.6892]
    assert m.zoom == 8
    
    # The add_wms_layer method should have created a source and layer
    assert len(m.sources) == 1
    assert len(m.layers) == 1
    
    # Check the layer configuration
    layer = m.layers[0]
    assert layer['id'] == 'wms-test-layer'
    assert layer['definition']['type'] == 'raster'
    
    # Check the source configuration
    source_name = layer['definition']['source']
    source_def = None
    for source in m.sources:
        if source['name'] == source_name:
            source_def = source['definition']
            break
    
    assert source_def is not None
    assert source_def['type'] == 'raster'
    assert 'tiles' in source_def
    
    # The tiles URL should contain the WMS parameters
    tiles_url = source_def['tiles'][0]
    assert 'service=WMS' in tiles_url
    assert 'request=GetMap' in tiles_url
    assert 'version=1.1.1' in tiles_url
    assert 'layers=TOPO-WMS%2COSM-Overlay-WMS' in tiles_url
    assert 'format=image%2Fpng' in tiles_url
    assert 'transparent=true' in tiles_url
    assert 'srs=EPSG%3A3857' in tiles_url
    assert '{bbox-epsg-3857}' in tiles_url
    assert 'width=256' in tiles_url
    assert 'height=256' in tiles_url
    
    # Verify the HTML renders correctly
    html = m.render()
    assert '-74.5447' in html
    assert '40.6892' in html
    assert 'wms-test-layer' in html