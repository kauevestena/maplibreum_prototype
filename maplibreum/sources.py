class Source:
    def __init__(self, type, **kwargs):
        self.type = type
        self.options = kwargs

    @property
    def __dict__(self):
        return {"type": self.type, **self.options}


class RasterSource(Source):
    def __init__(self, tiles, tileSize=256, **kwargs):
        super().__init__("raster", tiles=tiles, tileSize=tileSize, **kwargs)


class RasterDemSource(Source):
    def __init__(self, url, tileSize=256, **kwargs):
        super().__init__("raster-dem", url=url, tileSize=tileSize, **kwargs)
