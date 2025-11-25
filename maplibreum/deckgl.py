"""Deck.GL integration for maplibreum."""

from __future__ import annotations

import json
from textwrap import dedent
from typing import Any, Dict, Tuple

from .datasources import RESTDataSource


def _is_js_literal(value: Any) -> bool:
    """Return ``True`` when *value* should be embedded as raw JavaScript."""

    if not isinstance(value, str):
        return False
    stripped = value.strip()
    return "=>" in stripped or stripped.startswith("function")


def _to_camel_case(key: str) -> str:
    """Convert ``snake_case`` keys to camelCase for Deck.GL props."""

    if not key:
        return key
    parts = key.split("_")
    head, *tail = parts
    return head + "".join(segment.capitalize() for segment in tail)


class DeckGLLayer:
    """Represents a custom layer for rendering data using Deck.GL."""

    def __init__(
        self,
        id: str,
        data: str | Dict[str, Any] | RESTDataSource,
        layer_type: str = "ScatterplotLayer",
        **kwargs: Any,
    ):
        self.id = id
        self.data = data
        self.layer_type = layer_type
        self.data_accessor = kwargs.pop("data_accessor", "")
        # Store a shallow copy to avoid mutating user supplied kwargs when serialising
        self.kwargs = dict(kwargs)

    @property
    def scripts(self) -> list[str]:
        """Return the list of Deck.GL scripts required for the layer."""

        return ["https://unpkg.com/deck.gl@8.9.33/dist.min.js"]

    def _serialise_props(self) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """Split Deck.GL properties into JSON-safe and raw-JS dictionaries."""

        json_props: Dict[str, Any] = {"id": f"{self.id}-layer"}
        raw_props: Dict[str, str] = {}

        for key, value in self.kwargs.items():
            camel_key = _to_camel_case(key)
            if camel_key == "data":
                # ``data`` is injected at runtime once the promise resolves.
                continue
            if _is_js_literal(value):
                raw_props[camel_key] = value
            else:
                json_props[camel_key] = value

        return json_props, raw_props

    def serialize(self, before_layer_id: str | None = None) -> Dict[str, Any]:
        """Return a JSON-serialisable configuration for the Deck.GL overlay."""

        if isinstance(self.data, RESTDataSource):
            data_expression = self.data.to_js()
            if self.data_accessor:
                data_expression += f".then(data => data{self.data_accessor})"
            data_config = {"mode": "promise", "value": data_expression}
        else:
            data_config = {"mode": "inline", "value": self.data}

        json_props, raw_props = self._serialise_props()

        return {
            "id": self.id,
            "before": before_layer_id,
            "layerType": self.layer_type,
            "data": data_config,
            "props": {"json": json_props, "raw": raw_props},
        }

    def add_to(self, before_layer_id: str | None = None) -> str:
        """Generate JavaScript code to add the Deck.GL layer to the map."""

        config = self.serialize(before_layer_id=before_layer_id)

        if config["data"]["mode"] == "promise":
            data_promise = config["data"]["value"]
        else:
            data_promise = f"Promise.resolve({json.dumps(config['data']['value'])})"

        json_props = config["props"]["json"].copy()
        raw_props = dict(config["props"]["raw"])

        props_str_parts = ["                                    data: data"]

        for key, value in json_props.items():
            props_str_parts.append(
                f"                                    {_to_camel_case(key)}: {json.dumps(value)}"
            )

        for key, value in raw_props.items():
            props_str_parts.append(f"                                    {key}: {value}")

        props_str = ",\\n".join(props_str_parts)

        js_code = dedent(
            f"""
            const customLayer = {{
                id: '{config['id']}',
                type: 'custom',
                renderingMode: '3d',
                onAdd: function(map, gl) {{
                    const dataPromise = {data_promise};
                    dataPromise.then(data => {{
                        if (typeof deck === 'undefined') {{
                            console.error('Deck.GL library is not loaded');
                            return;
                        }}
                        this.deck = new deck.Deck({{
                            gl,
                            map,
                            initialViewState: map.getFreeCameraOptions(),
                            layers: [
                                new deck.{config['layerType']}({{
{props_str}
                                }})
                            ]
                        }});
                    }}).catch(error => {{
                        console.error('Failed to initialise Deck.GL overlay {config['id']}', error);
                    }});
                }},
                render: function(gl, matrix) {{
                    if (this.deck) {{
                        this.deck.setProps({{
                            viewState: map.getFreeCameraOptions(),
                        }});
                    }}
                }},
                onRemove: function() {{
                    if (this.deck) {{
                        this.deck.finalize();
                        this.deck = null;
                    }}
                }}
            }};
            map.addLayer(customLayer, '{config['before'] or ''}');
        """
        )
        return js_code
