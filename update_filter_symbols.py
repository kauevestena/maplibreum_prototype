import textwrap
content = open('tests/test_examples/test_filter_layer_symbols_using_global_state.py').read()
if "test_filter_layer_symbols_using_global_state_with_python_api" not in content:
    with open('tests/test_examples/test_filter_layer_symbols_using_global_state.py', 'w') as f:
        f.write(content + """

def test_filter_layer_symbols_using_global_state_with_python_api() -> None:
    \"\"\"Toggle symbol visibility based on a select element and global state using Python API.\"\"\"

    map_instance = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[9.0679, 45.8822],
        zoom=9,
    )

    map_instance.add_source(
        "railways_and_lifts",
        {
            "type": "geojson",
            "data": "https://maplibre.org/maplibre-gl-js/docs/assets/funicolares-and-funivias-como.json",
        },
    )

    filter_expression = [
        "case",
        ["==", ["to-string", ["global-state", "type"]], ""],
        True,
        ["==", ["get", "type"], ["global-state", "type"]],
    ]

    map_instance.add_layer(
        {
            "id": "railways_and_lifts_labels",
            "type": "symbol",
            "layout": {
                "text-field": "{name}",
                "text-font": ["Open Sans Semibold"],
                "text-offset": [0, 1],
                "text-anchor": "top",
            },
            "paint": {
                "text-color": "#000000",
                "text-halo-color": "#ffffff",
                "text-halo-width": 2,
            },
            "filter": filter_expression,
        },
        source="railways_and_lifts",
    )
    map_instance.add_layer(
        {
            "id": "railways_and_lifts_points",
            "type": "circle",
            "paint": {
                "circle-radius": 5,
                "circle-color": "#000000",
            },
            "filter": filter_expression,
        },
        source="railways_and_lifts",
    )

    control_js = textwrap.dedent(
        \"\"\"
        class GlobalStateFilterControl {
            onAdd(map) {
                this._map = map;
                this._container = document.createElement('div');
                this._container.className = 'maplibregl-ctrl maplibreum-type-filter';
                this._container.style.backgroundColor = '#fff';
                this._container.style.padding = '10px';
                this._container.style.borderRadius = '4px';
                this._container.style.boxShadow = '0 1px 4px rgba(0, 0, 0, 0.25)';
                this._container.style.font = "13px/18px 'Helvetica Neue', Arial, sans-serif";

                var label = document.createElement('label');
                label.textContent = 'Filter by type';
                label.style.display = 'block';
                label.style.marginBottom = '5px';
                this._container.appendChild(label);

                var select = document.createElement('select');
                select.name = 'type';
                ['All', 'lift', 'railway'].forEach(function(optionValue, index) {
                    var option = document.createElement('option');
                    option.value = index === 0 ? '' : optionValue;
                    option.textContent = index === 0 ? 'All' : optionValue.replace('-', ' ');
                    if (index === 0) {
                        option.selected = true;
                    }
                    select.appendChild(option);
                });
                this._container.appendChild(select);

                map.setGlobalStateProperty('type', select.value);
                select.addEventListener('change', function(event) {
                    map.setGlobalStateProperty('type', event.target.value);
                });

                return this._container;
            }
            onRemove() {
                this._container.parentNode.removeChild(this._container);
                this._map = undefined;
            }
        }
        map.addControl(new GlobalStateFilterControl(), 'top-left');
        \"\"\"
    ).strip()
    map_instance.add_on_load_js(control_js)

    html = map_instance.render()
    assert "GlobalStateFilterControl" in html
    assert "setGlobalStateProperty" in html
""")
