import pytest

from maplibreum.core import Map, Marker, MarkerCluster


def test_marker_cluster_source_and_layers():
    m = Map()
    cluster = MarkerCluster().add_to(m)
    # add markers via both Marker and Map.add_marker
    Marker(coordinates=[0, 0]).add_to(cluster)
    m.add_marker(coordinates=[1, 1], cluster=cluster)

    # only cluster layers should be present
    assert len(m.layers) == 3

    # verify source parameters
    source = next(s for s in m.sources if s["name"] == cluster.source_name)
    assert source["definition"]["cluster"] is True
    assert source["definition"]["clusterRadius"] == 50

    # verify cluster layers definitions
    cluster_layer = next(
        l for l in m.layers if l["definition"]["id"] == cluster.cluster_layer_id
    )
    assert cluster_layer["definition"]["filter"] == ["has", "point_count"]

    count_layer = next(
        l for l in m.layers if l["definition"]["id"] == cluster.count_layer_id
    )
    assert count_layer["definition"]["type"] == "symbol"
    assert count_layer["definition"]["filter"] == ["has", "point_count"]

    unclustered_layer = next(
        l for l in m.layers if l["definition"]["id"] == cluster.unclustered_layer_id
    )
    assert unclustered_layer["definition"]["filter"] == [
        "!",
        ["has", "point_count"],
    ]

