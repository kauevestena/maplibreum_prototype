import uuid

class ImageOverlay:
    """Overlay a georeferenced image on the map."""

    def __init__(
        self,
        image,
        bounds=None,
        coordinates=None,
        opacity=1.0,
        attribution=None,
        name=None,
    ):
        """Create an ImageOverlay.

        Parameters
        ----------
        image : str
            URL or local path to the image.
        bounds : list, optional
            Bounds of the image as ``[west, south, east, north]`` or
            ``[[west, south], [east, north]]``.
        coordinates : list, optional
            Four corner coordinates of the image specified as
            ``[[west, north], [east, north], [east, south], [west, south]]``.
            If provided, ``bounds`` is ignored.
        opacity : float, optional
            Opacity of the raster layer, defaults to ``1.0``.
        attribution : str, optional
            Attribution text for the source.
        name : str, optional
            Layer identifier. If omitted, a unique one is generated.
        """

        self.image = image
        self.attribution = attribution
        self.opacity = opacity
        self.name = name or get_id("imageoverlay_")

        if coordinates is not None:
            self.coordinates = coordinates
        elif bounds is not None:
            if len(bounds) == 2 and all(len(b) == 2 for b in bounds):
                west, south = bounds[0]
                east, north = bounds[1]
            else:
                west, south, east, north = bounds
            self.coordinates = [
                [west, north],
                [east, north],
                [east, south],
                [west, south],
            ]
        else:
            raise ValueError("Either coordinates or bounds must be provided")

    def add_to(self, map_instance):
        """Add the image overlay to a map instance.

        Parameters
        ----------
        map_instance : maplibreum.Map
            The map instance to which the image overlay will be added.

        Returns
        -------
        self
        """
        source = {
            "type": "image",
            "url": self.image,
            "coordinates": self.coordinates,
        }
        if self.attribution:
            source["attribution"] = self.attribution

        layer = {"id": self.name, "type": "raster", "source": self.name}
        if self.opacity is not None:
            layer["paint"] = {"raster-opacity": self.opacity}

        map_instance.add_layer(layer, source=source)
        return self


class VideoOverlay:
    """Overlay a georeferenced video on the map."""

    def __init__(
        self,
        videos,
        bounds=None,
        coordinates=None,
        opacity=1.0,
        attribution=None,
        name=None,
    ):
        """Create a VideoOverlay.

        Parameters
        ----------
        videos : str or list
            URL or local path to the video, or a list of URLs for different
            formats.
        bounds : list, optional
            Bounds of the video as ``[west, south, east, north]`` or
            ``[[west, south], [east, north]]``.
        coordinates : list, optional
            Four corner coordinates of the video specified as
            ``[[west, north], [east, north], [east, south], [west, south]]``.
            If provided, ``bounds`` is ignored.
        opacity : float, optional
            Opacity of the raster layer, defaults to ``1.0``.
        attribution : str, optional
            Attribution text for the source.
        name : str, optional
            Layer identifier. If omitted, a unique one is generated.
        """

        if isinstance(videos, str):
            self.urls = [videos]
        else:
            self.urls = list(videos)
        self.attribution = attribution
        self.opacity = opacity
        self.name = name or get_id("videooverlay_")

        if coordinates is not None:
            self.coordinates = coordinates
        elif bounds is not None:
            if len(bounds) == 2 and all(len(b) == 2 for b in bounds):
                west, south = bounds[0]
                east, north = bounds[1]
            else:
                west, south, east, north = bounds
            self.coordinates = [
                [west, north],
                [east, north],
                [east, south],
                [west, south],
            ]
        else:
            raise ValueError("Either coordinates or bounds must be provided")

    def add_to(self, map_instance):
        """Add the video overlay to a map instance.

        Parameters
        ----------
        map_instance : maplibreum.Map
            The map instance to which the video overlay will be added.

        Returns
        -------
        self
        """
        source = {
            "type": "video",
            "urls": self.urls,
            "coordinates": self.coordinates,
        }
        if self.attribution:
            source["attribution"] = self.attribution

        layer = {"id": self.name, "type": "raster", "source": self.name}
        if self.opacity is not None:
            layer["paint"] = {"raster-opacity": self.opacity}

        map_instance.add_layer(layer, source=source)
        return self
