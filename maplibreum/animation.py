import uuid
import math
from typing import List, Optional, Tuple


def calculate_bearing(start: Tuple[float, float], end: Tuple[float, float]) -> float:
    """Calculate the bearing between two points in degrees.

    Args:
        start: (longitude, latitude) of start point
        end: (longitude, latitude) of end point

    Returns:
        Bearing in degrees (0-360)
    """
    lon1, lat1 = math.radians(start[0]), math.radians(start[1])
    lon2, lat2 = math.radians(end[0]), math.radians(end[1])

    dLon = lon2 - lon1
    y = math.sin(dLon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(
        dLon
    )

    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360) % 360


def haversine_distance(
    coord1: Tuple[float, float], coord2: Tuple[float, float]
) -> float:
    """Calculate great circle distance between two points in kilometers.

    Args:
        coord1: (longitude, latitude) of first point
        coord2: (longitude, latitude) of second point

    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth radius in kilometers
    lon1, lat1 = math.radians(coord1[0]), math.radians(coord1[1])
    lon2, lat2 = math.radians(coord2[0]), math.radians(coord2[1])

    dLat = lat2 - lat1
    dLon = lon2 - lon1

    a = (
        math.sin(dLat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dLon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def interpolate_along_line(
    coordinates: List[Tuple[float, float]], steps: int = 500
) -> List[Tuple[float, float]]:
    """Create an arc (interpolated points) along a LineString.

    Args:
        coordinates: List of (longitude, latitude) tuples defining the line
        steps: Number of interpolation steps

    Returns:
        List of interpolated coordinates
    """
    if len(coordinates) < 2:
        return coordinates

    # Calculate total distance
    total_distance = 0
    for i in range(len(coordinates) - 1):
        total_distance += haversine_distance(coordinates[i], coordinates[i + 1])

    if total_distance == 0:
        return coordinates

    # Generate interpolated points
    arc = []
    distance_per_step = total_distance / steps

    current_segment = 0
    accumulated_distance = 0
    segment_start = coordinates[0]
    segment_end = coordinates[1]
    segment_distance = haversine_distance(segment_start, segment_end)

    for step in range(steps + 1):
        target_distance = step * distance_per_step

        # Find the right segment
        while (
            accumulated_distance + segment_distance < target_distance
            and current_segment < len(coordinates) - 2
        ):
            accumulated_distance += segment_distance
            current_segment += 1
            segment_start = coordinates[current_segment]
            segment_end = coordinates[current_segment + 1]
            segment_distance = haversine_distance(segment_start, segment_end)

        # Interpolate within the segment
        if segment_distance > 0:
            ratio = (target_distance - accumulated_distance) / segment_distance
            ratio = max(0, min(1, ratio))  # Clamp to [0, 1]

            lon = segment_start[0] + ratio * (segment_end[0] - segment_start[0])
            lat = segment_start[1] + ratio * (segment_end[1] - segment_start[1])
            arc.append((lon, lat))
        else:
            arc.append(segment_start)

    return arc


class RouteAnimation:
    """Helper for animating a point along a route with Python API.

    This class eliminates the need for Turf.js by implementing route
    interpolation and bearing calculation in Python.
    """

    def __init__(
        self,
        route_coordinates: List[Tuple[float, float]],
        steps: int = 500,
        route_source_id: str = "route",
        point_source_id: str = "point",
        replay_button_id: str = "replay",
    ):
        """Initialize a RouteAnimation.

        Args:
            route_coordinates: List of (lon, lat) tuples defining the route
            steps: Number of animation steps
            route_source_id: ID of the GeoJSON source for the route line
            point_source_id: ID of the GeoJSON source for the animated point
            replay_button_id: ID of the replay button element
        """
        self.route_coordinates = route_coordinates
        self.steps = steps
        self.route_source_id = route_source_id
        self.point_source_id = point_source_id
        self.replay_button_id = replay_button_id

        # Pre-calculate the interpolated arc
        self.arc = interpolate_along_line(route_coordinates, steps)

    def to_js(self) -> str:
        """Generate JavaScript code for the route animation.

        Returns:
            JavaScript code string
        """
        import json

        # Convert arc to JavaScript array format
        arc_js = json.dumps(self.arc)

        js_code = f"""
// Route animation setup
const routeArc = {arc_js};
const routeSteps = {self.steps};
let routeCounter = 0;

// Update route source with interpolated arc
const routeSource = map.getSource('{self.route_source_id}');
if (routeSource) {{
    const routeData = routeSource._data;
    if (routeData && routeData.features && routeData.features[0]) {{
        routeData.features[0].geometry.coordinates = routeArc;
        routeSource.setData(routeData);
    }}
}}

// Calculate bearing between two points
function calculateBearing(start, end) {{
    const toRad = (deg) => deg * Math.PI / 180;
    const toDeg = (rad) => rad * 180 / Math.PI;
    
    const lon1 = toRad(start[0]);
    const lat1 = toRad(start[1]);
    const lon2 = toRad(end[0]);
    const lat2 = toRad(end[1]);
    
    const dLon = lon2 - lon1;
    const y = Math.sin(dLon) * Math.cos(lat2);
    const x = Math.cos(lat1) * Math.sin(lat2) - 
              Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);
    
    const bearing = toDeg(Math.atan2(y, x));
    return (bearing + 360) % 360;
}}

// Animation function
function animateRoute(timestamp) {{
    const pointSource = map.getSource('{self.point_source_id}');
    if (!pointSource) return;
    
    const pointData = pointSource._data;
    if (!pointData || !pointData.features || !pointData.features[0]) return;
    
    // Update point position
    pointData.features[0].geometry.coordinates = routeArc[routeCounter];
    
    // Calculate and update bearing
    const currentIdx = routeCounter >= routeSteps ? routeCounter - 1 : routeCounter;
    const nextIdx = routeCounter >= routeSteps ? routeCounter : routeCounter + 1;
    const bearing = calculateBearing(routeArc[currentIdx], routeArc[nextIdx]);
    pointData.features[0].properties.bearing = bearing;
    
    pointSource.setData(pointData);
    
    if (routeCounter < routeSteps) {{
        requestAnimationFrame(animateRoute);
    }}
    routeCounter = routeCounter + 1;
}}

// Replay button handler
const replayButton = document.getElementById('{self.replay_button_id}');
if (replayButton) {{
    replayButton.addEventListener('click', () => {{
        const pointSource = map.getSource('{self.point_source_id}');
        if (pointSource) {{
            const pointData = pointSource._data;
            if (pointData && pointData.features && pointData.features[0]) {{
                pointData.features[0].geometry.coordinates = routeArc[0];
                pointSource.setData(pointData);
                routeCounter = 0;
                animateRoute(0);
            }}
        }}
    }});
}}

// Start animation
animateRoute(0);
"""
        return js_code


class AnimatedIcon:
    """Represents a customizable animated icon for use on a map."""

    def __init__(
        self,
        size: int = 200,
        color: str = "rgba(255, 100, 100, 1)",
        pulse_color: str = "rgba(255, 200, 200, 0.7)",
    ):
        """Initializes an AnimatedIcon.
        Args:
            size: The size of the icon in pixels.
            color: The main color of the icon.
            pulse_color: The color of the pulsing animation.
        """
        self.icon_id = f"pulsing-dot-{uuid.uuid4().hex[:6]}"
        self.size = size
        self.color = color
        self.pulse_color = pulse_color

    def add_to_map(self, map_instance) -> str:
        """Generates the JavaScript to add the animated icon to the map.
        Args:
            map_instance: The map instance to which the icon will be added.
        Returns:
            The ID of the generated icon.
        """
        js_code = f"""
            const {self.icon_id} = {{
                width: {self.size},
                height: {self.size},
                data: new Uint8Array({self.size} * {self.size} * 4),

                onAdd: function () {{
                    const canvas = document.createElement('canvas');
                    canvas.width = this.width;
                    canvas.height = this.height;
                    this.context = canvas.getContext('2d');
                }},

                render: function () {{
                    const duration = 1000;
                    const t = (performance.now() % duration) / duration;

                    const radius = ({self.size} / 2) * 0.3;
                    const outerRadius = ({self.size} / 2) * 0.7 * t + radius;
                    const context = this.context;

                    context.clearRect(0, 0, this.width, this.height);
                    context.beginPath();
                    context.arc(this.width / 2, this.height / 2, outerRadius, 0, Math.PI * 2);
                    context.fillStyle = '{self.pulse_color.replace("0.7", "' + (1 - t) + '")}';
                    context.fill();

                    context.beginPath();
                    context.arc(this.width / 2, this.height / 2, radius, 0, Math.PI * 2);
                    context.fillStyle = '{self.color}';
                    context.strokeStyle = 'white';
                    context.lineWidth = 2 + 4 * (1 - t);
                    context.fill();
                    context.stroke();

                    this.data = context.getImageData(0, 0, this.width, this.height).data;
                    map.triggerRepaint();
                    return true;
                }}
            }};
            map.addImage('{self.icon_id}', {self.icon_id}, {{ pixelRatio: 2 }});
        """
        map_instance.add_on_load_js(js_code)
        return self.icon_id


class AnimationLoop:
    """Helper for generating JavaScript animations with requestAnimationFrame."""

    def __init__(
        self,
        name: str,
        body: str or list,
        variables: Optional[dict] = None,
        setup: Optional[str or list] = None,
        handle_name: Optional[str] = None,
        visibility_reset: Optional[str or list] = None,
        auto_schedule: bool = True,
        start_immediately: bool = True,
    ):
        self.name = name
        self.body = body if isinstance(body, list) else [body]
        self.variables = variables or {}
        self.setup = setup if isinstance(setup, list) or setup is None else [setup]
        self.handle_name = handle_name
        self.visibility_reset = (
            visibility_reset
            if isinstance(visibility_reset, list) or visibility_reset is None
            else [visibility_reset]
        )
        self.auto_schedule = auto_schedule
        self.start_immediately = start_immediately

    def to_js(self) -> str:
        """Render the animation loop to a JavaScript string."""
        lines = []
        if self.variables:
            for key, value in self.variables.items():
                lines.append(f"let {key} = {value};")

        if self.setup:
            lines.extend(self.setup)

        lines.append(f"function {self.name}(timestamp) {{")
        lines.extend([f"    {line}" for line in self.body])
        if self.auto_schedule:
            lines.append(f"    requestAnimationFrame({self.name});")
        lines.append("}")

        if self.handle_name:
            lines.append(
                f"let {self.handle_name} = requestAnimationFrame({self.name});"
            )
        elif self.start_immediately:
            lines.append(f"requestAnimationFrame({self.name});")

        if self.visibility_reset:
            lines.append("document.addEventListener('visibilitychange', () => {")
            lines.append("    if (document.visibilityState === 'visible') {")
            lines.extend([f"        {line}" for line in self.visibility_reset])
            lines.append("    }")
            lines.append("});")

        return "\n".join(lines)


class TemporalInterval:
    """Helper for generating JavaScript animations with setInterval."""

    def __init__(
        self,
        callback: str or list,
        interval: int,
        name: Optional[str] = None,
        variables: Optional[dict] = None,
        setup: Optional[str or list] = None,
    ):
        self.name = name
        self.callback = callback if isinstance(callback, list) else [callback]
        self.interval = interval
        self.variables = variables or {}
        self.setup = setup if isinstance(setup, list) or setup is None else [setup]

    def to_js(self) -> str:
        """Render the temporal interval to a JavaScript string."""
        lines = []
        if self.variables:
            for key, value in self.variables.items():
                lines.append(f"let {key} = {value};")

        if self.setup:
            lines.extend(self.setup)

        callback_body = "\n".join([f"    {line.strip()}" for line in self.callback])
        func = f"function(){{\n{callback_body}\n}}"

        if self.name:
            lines.append(f"var {self.name} = setInterval({func}, {self.interval});")
        else:
            lines.append(f"setInterval({func}, {self.interval});")
        return "\n".join(lines)
