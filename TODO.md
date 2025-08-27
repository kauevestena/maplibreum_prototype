# TODO

- [ ] MiniMap plugin for overview map
- [ ] Measure control to calculate distances and areas
- [ ] TimeDimension support for time-enabled layers
- [ ] Search control for geocoding and feature lookup
- [ ] Optimized marker clustering for large datasets
- [x] Video overlay support
- [x] Image and canvas source helpers
- [ ] Advanced popup class with templating

- [ ] Floating image overlays similar to Folium's FloatImage plugin

## Usage Examples

```python
from maplibreum.core import Map

m = Map()
m.add_image_source(
    "overlay",
    "https://example.com/overlay.png",
    [[-1, 1], [1, 1], [1, -1], [-1, -1]],
)
m.add_layer({"id": "image-layer", "type": "raster"}, source="overlay")

m.add_canvas_source(
    "canvas",
    "myCanvas",
    [[-1, 1], [1, 1], [1, -1], [-1, -1]],
    animate=True,
)
m.add_layer({"id": "canvas-layer", "type": "raster"}, source="canvas")
```
