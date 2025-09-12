import uuid

from .expressions import get as expr_get


class MarkerCluster:
    """Group markers into clusters using MapLibre's built-in clustering."""

    def __init__(self, name=None, cluster_radius=50, cluster_max_zoom=14):
        self.name = name or f"markercluster_{uuid.uuid4().hex}"
        self.cluster_radius = cluster_radius
        self.cluster_max_zoom = cluster_max_zoom
        self.features = []
        self.map = None
        self.source_name = None
        self.cluster_layer_id = None
        self.count_layer_id = None
        self.unclustered_layer_id = None

    def add_marker(self, marker):
        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": marker.coordinates},
            "properties": {"color": marker.color},
        }
        self.features.append(feature)
        if self.map and self.source_name:
            for src in self.map.sources:
                if src["name"] == self.source_name:
                    src["definition"]["data"]["features"] = self.features
                    break

    def add_to(self, map_instance):
        self.map = map_instance
        self.source_name = f"{self.name}_source"
        source = {
            "type": "geojson",
            "data": {"type": "FeatureCollection", "features": self.features},
            "cluster": True,
            "clusterRadius": self.cluster_radius,
            "clusterMaxZoom": self.cluster_max_zoom,
        }
        map_instance.add_source(self.source_name, source)

        self.cluster_layer_id = f"{self.name}_clusters"
        cluster_layer = {
            "id": self.cluster_layer_id,
            "type": "circle",
            "source": self.source_name,
            "filter": ["has", "point_count"],
            "paint": {
                "circle-color": "#51bbd6",
                "circle-radius": [
                    "step",
                    expr_get("point_count"),
                    20,
                    100,
                    30,
                    750,
                    40,
                ],
            },
        }
        map_instance.add_layer(cluster_layer)

        self.count_layer_id = f"{self.name}_cluster-count"
        count_layer = {
            "id": self.count_layer_id,
            "type": "symbol",
            "source": self.source_name,
            "filter": ["has", "point_count"],
            "layout": {
                "text-field": expr_get("point_count_abbreviated"),
                "text-font": ["Arial Unicode MS Bold"],
                "text-size": 12,
            },
        }
        map_instance.add_layer(count_layer)

        self.unclustered_layer_id = f"{self.name}_unclustered"
        unclustered = {
            "id": self.unclustered_layer_id,
            "type": "circle",
            "source": self.source_name,
            "filter": ["!", ["has", "point_count"]],
            "paint": {
                "circle-color": ["coalesce", expr_get("color"), "#007cbf"],
                "circle-radius": 8,
                "circle-stroke-width": 1,
                "circle-stroke-color": "#fff",
            },
        }
        map_instance.add_layer(unclustered)

        map_instance.cluster_layers.append(
            {"source": self.source_name, "cluster_layer": self.cluster_layer_id}
        )
        return self


class ClusteredGeoJson:
    """Cluster arbitrary GeoJSON features using MapLibre's clustering."""

    def __init__(self, data, name=None, cluster_radius=50, cluster_max_zoom=14):
        self.data = data
        self.name = name or f"clustered_geojson_{uuid.uuid4().hex}"
        self.cluster_radius = cluster_radius
        self.cluster_max_zoom = cluster_max_zoom
        self.map = None
        self.source_name = None
        self.cluster_layer_id = None
        self.count_layer_id = None
        self.unclustered_layer_id = None

    def add_to(self, map_instance):
        self.map = map_instance
        self.source_name = f"{self.name}_source"
        source = {
            "type": "geojson",
            "data": self.data,
            "cluster": True,
            "clusterRadius": self.cluster_radius,
            "clusterMaxZoom": self.cluster_max_zoom,
        }
        map_instance.add_source(self.source_name, source)

        self.cluster_layer_id = f"{self.name}_clusters"
        cluster_layer = {
            "id": self.cluster_layer_id,
            "type": "circle",
            "source": self.source_name,
            "filter": ["has", "point_count"],
            "paint": {
                "circle-color": "#51bbd6",
                "circle-radius": [
                    "step",
                    expr_get("point_count"),
                    20,
                    100,
                    30,
                    750,
                    40,
                ],
            },
        }
        map_instance.add_layer(cluster_layer)

        self.count_layer_id = f"{self.name}_cluster-count"
        count_layer = {
            "id": self.count_layer_id,
            "type": "symbol",
            "source": self.source_name,
            "filter": ["has", "point_count"],
            "layout": {
                "text-field": expr_get("point_count_abbreviated"),
                "text-font": ["Arial Unicode MS Bold"],
                "text-size": 12,
            },
        }
        map_instance.add_layer(count_layer)

        self.unclustered_layer_id = f"{self.name}_unclustered"
        unclustered = {
            "id": self.unclustered_layer_id,
            "type": "circle",
            "source": self.source_name,
            "filter": ["!", ["has", "point_count"]],
            "paint": {
                "circle-color": "#007cbf",
                "circle-radius": 8,
                "circle-stroke-width": 1,
                "circle-stroke-color": "#fff",
            },
        }
        map_instance.add_layer(unclustered)

        map_instance.cluster_layers.append(
            {"source": self.source_name, "cluster_layer": self.cluster_layer_id}
        )
        return self


def cluster_features(features, radius=40, max_zoom=16):
    """Cluster features using a simple grid-based algorithm.

    This is a lightweight stand-in for ``supercluster`` suitable for testing
    and benchmarking purposes."""

    class SimpleSupercluster:
        def __init__(self, radius, max_zoom):
            self.radius = radius
            self.max_zoom = max_zoom
            self.points = []

        def load(self, features):
            self.points = [f["geometry"]["coordinates"] for f in features]

        def get_clusters(self, bbox, zoom):
            cell_x = (bbox[2] - bbox[0]) / max(self.radius, 1)
            cell_y = (bbox[3] - bbox[1]) / max(self.radius, 1)
            clusters = {}
            for lng, lat in self.points:
                gx = int((lng - bbox[0]) / cell_x)
                gy = int((lat - bbox[1]) / cell_y)
                key = (gx, gy)
                data = clusters.setdefault(key, {"count": 0, "lng": 0.0, "lat": 0.0})
                data["count"] += 1
                data["lng"] += lng
                data["lat"] += lat
            features = []
            for data in clusters.values():
                count = data["count"]
                features.append(
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [data["lng"] / count, data["lat"] / count],
                        },
                        "properties": {
                            "cluster": count > 1,
                            "point_count": count,
                        },
                    }
                )
            return features

    index = SimpleSupercluster(radius, max_zoom)
    index.load(features)
    return index
