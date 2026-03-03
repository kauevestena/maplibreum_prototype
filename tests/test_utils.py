from maplibreum.utils import IDGenerator, get_id

def test_get_id_no_prefix():
    IDGenerator.reset()
    assert get_id() == "0"
    assert get_id() == "1"
    assert get_id() == "2"

def test_get_id_with_prefix():
    IDGenerator.reset()
    assert get_id("prefix_") == "prefix_0"
    assert get_id("prefix_") == "prefix_1"
    assert get_id("prefix_") == "prefix_2"

def test_get_id_mixed_prefixes():
    IDGenerator.reset()
    assert get_id("a_") == "a_0"
    assert get_id("b_") == "b_0"
    assert get_id("a_") == "a_1"
    assert get_id("b_") == "b_1"

def test_id_generator_reset():
    IDGenerator.reset()
    assert get_id("test_") == "test_0"
    IDGenerator.reset()
    assert get_id("test_") == "test_0"
