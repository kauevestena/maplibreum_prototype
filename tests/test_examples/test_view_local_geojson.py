from maplibreum import Map
from maplibreum.layers import FillLayer
from maplibreum.sources import GeoJSONSource


EMPTY_FEATURE_COLLECTION = {"type": "FeatureCollection", "features": []}


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
        map.getSource('uploaded-source').setData(geoJSONcontent);
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
    map.getSource('uploaded-source').setData(JSON.parse(contents));
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

    m.add_source(
        "uploaded-source",
        GeoJSONSource(data=EMPTY_FEATURE_COLLECTION),
    )
    m.add_layer(
        FillLayer(
            id="uploaded-polygons",
            source="uploaded-source",
            paint={
                "fill-color": "#888888",
                "fill-outline-color": "red",
                "fill-opacity": 0.4,
            },
            filter=["==", "$type", "Polygon"],
        )
    )
    m.add_on_load_js(UPLOAD_JS)

    html = m.render()

    assert "uploaded-geojson-file" in html
    assert "FileReader" in html
    assert any(source["name"] == "uploaded-source" for source in m.sources)
    assert any(layer["definition"]["id"] == "uploaded-polygons" for layer in m.layers)
    assert "map.getSource('uploaded-source').setData" in html
    assert '["==","$type","Polygon"]' in html.replace(" ", "").replace("\n", "")


def test_view_local_geojson_experimental():
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-8.3226655, 53.7654751],
        zoom=8,
    )

    m.add_source(
        "uploaded-source",
        GeoJSONSource(data=EMPTY_FEATURE_COLLECTION),
    )
    m.add_layer(
        FillLayer(
            id="uploaded-polygons",
            source="uploaded-source",
            paint={
                "fill-color": "#888888",
                "fill-outline-color": "red",
                "fill-opacity": 0.4,
            },
            filter=["==", "$type", "Polygon"],
        )
    )
    m.add_on_load_js(EXPERIMENTAL_JS)

    html = m.render()

    assert "showOpenFilePicker" in html
    assert "buttonClickHandler" in html
    assert any(source["name"] == "uploaded-source" for source in m.sources)
    assert any(layer["definition"]["id"] == "uploaded-polygons" for layer in m.layers)
    assert "map.getSource('uploaded-source').setData" in html
    assert '["==","$type","Polygon"]' in html.replace(" ", "").replace("\n", "")
    assert "Your browser does not support File System Access API" in html
