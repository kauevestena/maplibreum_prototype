from .utils import get_id
from typing import Any, Dict, Optional


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

    def __init__(
        self, data: Dict[str, Any], options: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize a TimeDimension."""
        self.data = data
        self.options = options or {}
        self.name = get_id("timedimension_")

    def add_to(self, map_instance: Any) -> "TimeDimension":
        """Add this time dimension data to a map instance."""
        map_instance.add_time_dimension(self.data, self.options)
        return self
