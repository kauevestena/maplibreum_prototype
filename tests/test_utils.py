from maplibreum.utils import get_id

from maplibreum.utils import IDGenerator

def test_get_id():
    IDGenerator.reset()
    # ID should be prefixed with the passed string and end with a counter
    id1 = get_id("maplibreum_")
    assert id1 == "maplibreum_0"

    id2 = get_id("maplibreum_")
    assert id2 == "maplibreum_1"

    id3 = get_id("layer_")
    assert id3 == "layer_0"

    id4 = get_id("maplibreum_")
    assert id4 == "maplibreum_2"

    id5 = get_id()
    assert id5 == "0"
