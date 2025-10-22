# Protocol helpers

MapLibre supports custom URL schemes for loading tiles and other resources. The
:mod:`maplibreum.protocols` module provides small dataclasses and
:class:`maplibreum.core.Map` helpers that make it easy to prepare runtime
configuration without writing raw JavaScript snippets.

## PMTiles

`pmtiles` archives bundle vector or raster tiles into a single file that is
served over HTTP. To use them with MapLibre you need to load the PMTiles runtime
script, register the protocol, and preload any archives that your map style
references. The helper API automates each of those steps.

```python
from maplibreum import Map
from maplibreum.protocols import PMTilesProtocol, PMTilesSource

archive_url = "https://pmtiles.io/protomaps(vector)ODbL_firenze.pmtiles"

m = Map(map_style={
    "version": 8,
    "sources": {
        "example_source": {
            "type": "vector",
            "url": f"pmtiles://{archive_url}",
        }
    },
    "layers": [...],
})

protocol = PMTilesProtocol(name="pmtiles", credentials="include")
m.add_pmtiles_protocol(protocol)
m.add_pmtiles_source(PMTilesSource(archive_url=archive_url, protocol=protocol.name))
```

The calls above ensure that:

* the `https://unpkg.com/pmtiles@3.2.0/dist/pmtiles.js` runtime is added to the
  page exactly once,
* `maplibregl.addProtocol('pmtiles', …)` is executed before the map
  initialises, and
* the referenced archive is wrapped in a `pmtiles.PMTiles` instance and added to
  the registered protocol.

### Dataclass reference

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class PMTilesProtocol:
    name: str = "pmtiles"
    script_url: str = "https://unpkg.com/pmtiles@3.2.0/dist/pmtiles.js"
    credentials: Optional[str] = None

@dataclass(frozen=True)
class PMTilesSource:
    archive_url: str
    protocol: str = "pmtiles"
    credentials: Optional[str] = None
```

* ``credentials`` accepts any value that would be passed to
  ``fetch(..., {credentials: ...})`` – for example ``"include"`` when working
  with cookies.
* ``PMTilesSource.style_url`` returns the ``pmtiles://`` URL for a given
  archive. You can pass it directly into MapLibre source definitions when
  building styles dynamically.

You do not need to call :meth:`Map.add_pmtiles_protocol` explicitly when every
archive uses the default protocol. Registering a source automatically creates a
protocol with the default script and any provided credentials.

```python
m.add_pmtiles_source(PMTilesSource(archive_url=archive_url))
```

This is convenient when you are working with stock ``pmtiles://`` URLs inside a
static style dictionary.
