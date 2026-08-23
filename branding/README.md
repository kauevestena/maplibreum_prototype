# MapLibreum branding

Original artwork for the MapLibreum project — no assets, paths, or artwork are
reused from MapLibre or Folium; this is a new mark designed to sit visually
between the two projects MapLibreum bridges.

## Concept

- **Silhouette** — a rounded map-pin/marker, the universal "location" shape,
  redrawn with our own proportions and curves.
- **Inner motif** — an abstract two-peak mountain range cut into the pin in a
  light tone, doubling as a stylized "M" for MapLibreum and nodding to
  MapLibre's terrain-rendering roots.
- **Accent** — a small light-cyan dot above the peak, a "you are here"
  marker/compass touch.
- **Wordmark** — lowercase `maplibreum`, matching the PyPI package name, in a
  bold geometric sans-serif.

## Palette

| Hex | Use |
| --- | --- |
| `#2C5C99` | Pin gradient start (deep MapLibre blue) |
| `#38A5DE` | Pin gradient end (bright sky blue) |
| `#F4FAFF` | Mountain cutout (light mode) |
| `#8FE0FF` | Accent dot |
| `#1B2A41` | Wordmark (light backgrounds) |
| `#F2F6FA` | Wordmark (dark backgrounds) |

The palette stays within MapLibre's blue family deliberately — no green — so
the mark reads as "MapLibre-adjacent" without borrowing Folium's leaf motif.

## Files

| File | Purpose |
| --- | --- |
| `icon.svg` | Mark only (pin + mountains), square artboard. Source for favicons/social previews. |
| `icon.png` | Raster export of `icon.svg` (512×555), for contexts that don't support SVG. |
| `logo.svg` | Horizontal lockup (icon + wordmark) for light backgrounds. |
| `logo-dark.svg` | Horizontal lockup for dark backgrounds (light wordmark, punched-out mountain motif). |
| `favicon.svg` | Simplified, flat-color version of the icon, optimized for legibility at tiny sizes. |
| `favicon.ico` | Multi-resolution favicon (16/32/48/64/256 px), generated from `favicon.svg`. |
| `favicon-16x16.png`, `favicon-32x32.png` | Individual favicon raster sizes. |

`favicon.ico` and the PNG rasters were generated from the SVG sources with
`cairosvg` + `Pillow`; regenerate them after editing `favicon.svg` with:

```bash
python3 - <<'PY'
import cairosvg
from PIL import Image
import io

png = cairosvg.svg2png(url="favicon.svg", output_width=256, output_height=256)
Image.open(io.BytesIO(png)).convert("RGBA").save(
    "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (256, 256)]
)
for size in (16, 32):
    cairosvg.svg2png(url="favicon.svg", output_width=size, output_height=size,
                      write_to=f"favicon-{size}x{size}.png")
PY
```

## Usage guidelines

- Prefer the SVG files wherever possible — they stay crisp at any size.
- Keep clear space around the mark roughly equal to the width of one
  mountain peak; don't crowd it against other logos or text.
- Don't recolor the pin gradient, stretch it non-uniformly, or drop the
  mountain cutout.
- `logo-dark.svg` is meant for near-black backgrounds (e.g. `#0d1117`,
  GitHub's dark theme); on other dark tones the punched-out mountain may not
  blend as intended.
