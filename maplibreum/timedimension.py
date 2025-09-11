import uuid


class TimeDimension:
    """Wrapper for timestamped GeoJSON data enabling simple playback.

    Parameters
    ----------
    data: dict
        GeoJSON ``FeatureCollection`` with features carrying a ``time``
        property.
    options: dict, optional
        Additional options for playback, such as ``interval`` in
        milliseconds.
    """

    def __init__(self, data, options=None):
        self.data = data
        self.options = options or {}
        self.name = f"timedimension_{uuid.uuid4().hex}"

    def add_to(self, map_instance):
        """Add this time dimension data to a map instance."""
        map_instance.add_time_dimension(self.data, self.options)
        return self
