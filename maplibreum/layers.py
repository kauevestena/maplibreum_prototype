class Layer:
    def __init__(self, id, type, source, **kwargs):
        self.id = id
        self.type = type
        self.source = source
        self.options = kwargs

    def to_dict(self):
        return {"id": self.id, "type": self.type, "source": self.source, **self.options}


class RasterLayer(Layer):
    def __init__(self, id, source, **kwargs):
        super().__init__(id, "raster", source, **kwargs)


class HillshadeLayer(Layer):
    def __init__(self, id, source, **kwargs):
        super().__init__(id, "hillshade", source, **kwargs)
