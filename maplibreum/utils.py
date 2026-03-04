class IDGenerator:
    _counters = {}

    @classmethod
    def get_id(cls, prefix=""):
        if prefix not in cls._counters:
            cls._counters[prefix] = 0
        current_id = f"{prefix}{cls._counters[prefix]}"
        cls._counters[prefix] += 1
        return current_id

    @classmethod
    def reset(cls):
        cls._counters = {}

def get_id(prefix=""):
    return IDGenerator.get_id(prefix)

def get_geojson_dict(data):
    """
    Normalizes a variety of data types into a GeoJSON dictionary.

    Supports:
    - Dictionary (returned as-is)
    - Any object with a `__geo_interface__` property (e.g. geopandas.GeoDataFrame)
    - JSON strings

    Parameters
    ----------
    data : dict, str, or object with __geo_interface__
        The input data to normalize.

    Returns
    -------
    dict
        A GeoJSON dictionary representation of the data.
    """
    import json

    if isinstance(data, dict):
        return data

    if hasattr(data, "__geo_interface__"):
        geo_interface = data.__geo_interface__
        if isinstance(geo_interface, dict):
            return geo_interface
        # Some objects might return a JSON string from __geo_interface__
        if isinstance(geo_interface, str):
            try:
                return json.loads(geo_interface)
            except json.JSONDecodeError:
                pass

    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            # It's likely a URL or file path; return it as-is for maplibre's source data
            return data

    raise ValueError(
        f"Cannot convert object of type {type(data)} to a GeoJSON dictionary. "
        "Expected a dictionary, a valid JSON string, a URL/path, or an object implementing __geo_interface__."
    )
