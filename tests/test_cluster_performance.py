import random
import time

from maplibreum.cluster import cluster_features


def test_supercluster_performance():
    features = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    random.uniform(-180, 180),
                    random.uniform(-90, 90),
                ],
            },
            "properties": {},
        }
        for _ in range(100_000)
    ]
    start = time.perf_counter()
    index = cluster_features(features, radius=40, max_zoom=16)
    index.get_clusters([-180, -90, 180, 90], 0)
    duration = time.perf_counter() - start
    assert duration < 5.0
