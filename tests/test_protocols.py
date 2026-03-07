from maplibreum import Map
from maplibreum.protocols import Protocol

def test_protocol_init():
    """Test basic initialization of Protocol."""
    name = "custom"
    definition = "console.log('custom protocol');"
    protocol = Protocol(name=name, definition=definition)

    assert protocol.name == name
    assert protocol.definition == definition

def test_map_add_protocol():
    """Test registering a Protocol on a Map instance."""
    m = Map()
    protocol = Protocol(name="test", definition="// test")
    m.add_protocol(protocol)

    assert protocol in m.custom_protocols

def test_protocol_rendering():
    """Test that Protocol is correctly rendered in the HTML template."""
    m = Map()
    protocol_name = "my-custom-proto"
    protocol_def = "return {data: new ArrayBuffer(0)};"
    protocol = Protocol(name=protocol_name, definition=protocol_def)
    m.add_protocol(protocol)

    html = m.render()

    assert f"maplibregl.addProtocol('{protocol_name}'" in html
    assert protocol_def in html
