from pathlib import Path

from maplibreum import Map, layers, sources


UPLOAD_JS = """
const fileInput = document.createElement('input');
fileInput.type = 'file';
fileInput.accept = 'application/geo+json,application/vnd.geo+json,.geojson';
fileInput.id = 'uploaded-geojson-file';
fileInput.style.position = 'absolute';
fileInput.style.top = '0';
fileInput.style.left = '0';
const container = map.getContainer();
container.appendChild(fileInput);
fileInput.addEventListener('change', (evt) => {
    const file = evt.target.files[0];
    if (!file) {
        return;
    }
    const reader = new FileReader();
    reader.onload = (event) => {
        const geoJSONcontent = JSON.parse(event.target.result);
        map.addSource('uploaded-source', { type: 'geojson', data: geoJSONcontent });
        map.addLayer({
            id: 'uploaded-polygons',
            type: 'fill',
            source: 'uploaded-source',
            paint: {
                'fill-color': '#888888',
                'fill-outline-color': 'red',
                'fill-opacity': 0.4,
            },
            filter: ['==', '$type', 'Polygon'],
        });
    };
    reader.readAsText(file, 'UTF-8');
});
"""


EXPERIMENTAL_JS = """
const button = document.createElement('button');
button.id = 'viewbutton';
button.textContent = 'View local GeoJSON file';
button.style.position = 'absolute';
button.style.top = '0';
button.style.left = '0';
map.getContainer().appendChild(button);
async function buttonClickHandler() {
    const [fileHandle] = await window.showOpenFilePicker({
        multiple: false,
        types: [
            {
                description: 'GeoJSON',
                accept: { 'application/geo+json': ['.geojson'] },
            },
        ],
        startIn: 'downloads',
    });
    const file = await fileHandle.getFile();
    const contents = await file.text();
    map.addSource('uploaded-source', { type: 'geojson', data: JSON.parse(contents) });
    map.addLayer({
        id: 'uploaded-polygons',
        type: 'fill',
        source: 'uploaded-source',
        paint: {
            'fill-color': '#888888',
            'fill-outline-color': 'red',
            'fill-opacity': 0.4,
        },
        filter: ['==', '$type', 'Polygon'],
    });
}
if ('showOpenFilePicker' in window) {
    button.addEventListener('click', buttonClickHandler);
} else {
    button.textContent = 'Your browser does not support File System Access API';
}
"""


def test_view_local_geojson():
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-8.3226655, 53.7654751],
        zoom=8,
    )

    m.add_on_load_js(UPLOAD_JS)

    html = m.render()

    assert "uploaded-geojson-file" in html
    assert "FileReader" in html
    assert "map.addSource('uploaded-source'" in html
    assert "['==','$type','Polygon']" in html.replace(" ", "").replace("\n", "")


def test_view_local_geojson_experimental():
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-8.3226655, 53.7654751],
        zoom=8,
    )

    m.add_on_load_js(EXPERIMENTAL_JS)

    html = m.render()

    assert "showOpenFilePicker" in html
    assert "buttonClickHandler" in html
    assert "map.addSource('uploaded-source'" in html
    assert "Your browser does not support File System Access API" in html


def test_view_local_geojson_with_python_api():
    geojson_path = Path(__file__).parent / "data/sample.geojson"
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-8.3226655, 53.7654751],
        zoom=8,
    )
    source = sources.GeoJSONSource.from_file(geojson_path)
    m.add_source("local-geojson-source", source)
    layer = layers.FillLayer(
        id="local-geojson-layer",
        source="local-geojson-source",
        paint={"fill-color": "red", "fill-opacity": 0.5},
    )
    m.add_layer(layer)
    html = m.render()
    assert '{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-8.5,53.5],[-8.0,53.5],[-8.0,54.0],[-8.5,54.0],[-8.5,53.5]]]}}]}' in html.replace(
        " ", ""
    ).replace(
        "\\n", ""
    )
