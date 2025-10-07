import uuid
from typing import List, Optional


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
            lines.append(f"let {self.handle_name} = requestAnimationFrame({self.name});")
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