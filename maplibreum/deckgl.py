"""Deck.GL integration for maplibreum."""

import json
from textwrap import dedent

from .datasources import RESTDataSource


def to_js_literal(value):
    """Converts a Python object to a JavaScript literal."""
    if isinstance(value, str) and (
        value.strip().startswith("d =>")
        or value.strip().startswith("function")
        or value.strip().startswith("info =>")
    ):
        return value
    return json.dumps(value)


class DeckGLLayer:
    """Represents a custom layer for rendering data using Deck.GL."""

    def __init__(
        self,
        id: str,
        data: str or dict or RESTDataSource,
        layer_type: str = "ScatterplotLayer",
        **kwargs,
    ):
        self.id = id
        self.data = data
        self.layer_type = layer_type
        self.kwargs = kwargs

    @property
    def scripts(self) -> list[str]:
        """Returns the list of Deck.GL scripts required for the layer."""
        return ["https://unpkg.com/deck.gl@8.9.33/dist.min.js"]

    def add_to(self, before_layer_id: str = None) -> str:
        """Generates the JavaScript code to add the Deck.GL layer to the map.
        Args:
            before_layer_id (str, optional): The ID of an existing layer to insert the new layer before.
        Returns:
            str: The JavaScript code to add the layer.
        """
        if isinstance(self.data, RESTDataSource):
            data_promise = self.data.to_js()
            data_accessor = self.kwargs.pop("data_accessor", "")
            if data_accessor:
                data_promise += f".then(data => data{data_accessor})"
        else:
            data_promise = f"Promise.resolve({json.dumps(self.data)})"

        props = {"id": f"{self.id}-layer", "data": "data"}
        props.update(self.kwargs)

        props_str_parts = []
        for key, value in props.items():
            key_camel = "".join(word.capitalize() for word in key.split("_"))
            key_camel = key_camel[0].lower() + key_camel[1:]
            if value == "data":
                props_str_parts.append(f"                                    {key_camel}: data")
            else:
                props_str_parts.append(
                    f"                                    {key_camel}: {to_js_literal(value)}"
                )

        props_str = ",\\n".join(props_str_parts)

        js_code = dedent(f"""
            const customLayer = {{
                id: '{self.id}',
                type: 'custom',
                renderingMode: '3d',
                onAdd: function(map, gl) {{
                    const dataPromise = {data_promise};
                    dataPromise.then(data => {{
                        this.deck = new deck.Deck({{
                            gl,
                            map,
                            initialViewState: map.getFreeCameraOptions(),
                            layers: [
                                new deck.{self.layer_type}({{
{props_str}
                                }})
                            ]
                        }});
                    }});
                }},
                render: function(gl, matrix) {{
                    if (this.deck) {{
                        this.deck.setProps({{
                            viewState: map.getFreeCameraOptions(),
                        }});
                    }}
                }}
            }};
            map.addLayer(customLayer, '{before_layer_id if before_layer_id else ""}');
        """)
        return js_code
