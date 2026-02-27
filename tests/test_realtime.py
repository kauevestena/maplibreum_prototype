"""Test real-time data fetching utilities."""

import pytest
from maplibreum.realtime import RandomCoordinateFetcher, LiveDataFetcher

def test_random_coordinate_fetcher_defaults():
    """Test RandomCoordinateFetcher default initialization."""
    fetcher = RandomCoordinateFetcher(source_id="drone")

    assert fetcher.source_id == "drone"
    assert fetcher.interval == 2000
    assert fetcher.fly_to is True
    assert fetcher.fly_speed == 0.5
    assert fetcher.url == "https://www.random.org/decimal-fractions/?num=2&dec=10&col=1&format=plain&rnd=new"
    assert "function(data)" in fetcher.transform_fn
    assert "rawText.split" in fetcher.transform_fn
    assert "return {" in fetcher.transform_fn

def test_random_coordinate_fetcher_custom():
    """Test RandomCoordinateFetcher with custom parameters."""
    fetcher = RandomCoordinateFetcher(
        source_id="drone",
        interval=5000,
        fly_to=False,
        fly_speed=1.0
    )

    assert fetcher.source_id == "drone"
    assert fetcher.interval == 5000
    assert fetcher.fly_to is False
    assert fetcher.fly_speed == 1.0

def test_random_coordinate_fetcher_initial_data():
    """Test RandomCoordinateFetcher initial data generation."""
    fetcher = RandomCoordinateFetcher(source_id="drone")
    initial_data = fetcher.get_initial_data()

    assert initial_data["type"] == "Feature"
    assert initial_data["geometry"]["type"] == "Point"
    assert initial_data["geometry"]["coordinates"] == [0, 0]

def test_random_coordinate_fetcher_to_js():
    """Test RandomCoordinateFetcher JavaScript generation."""
    fetcher = RandomCoordinateFetcher(source_id="drone")
    js_code = fetcher.to_js()

    # Verify key components of the generated JS
    assert "window.setInterval" in js_code
    assert fetcher.url in js_code
    assert "map.getSource('drone')" in js_code
    assert ".setData(json)" in js_code

    # Verify transform function is included
    assert "const transformData = " in js_code
    assert "rawText.split" in js_code
    assert "(Number(l) * 180) - 90" in js_code

    # Verify fly-to logic is included (default is True)
    assert "map.flyTo" in js_code
    assert "speed: 0.5" in js_code

def test_random_coordinate_fetcher_to_js_no_fly():
    """Test RandomCoordinateFetcher JavaScript generation with fly_to disabled."""
    fetcher = RandomCoordinateFetcher(source_id="drone", fly_to=False)
    js_code = fetcher.to_js()

    assert "map.flyTo" not in js_code
    assert "// Fly-to disabled" in js_code

def test_live_data_fetcher_base():
    """Test the base LiveDataFetcher class."""
    fetcher = LiveDataFetcher(
        source_id="test",
        url="http://example.com/data.json"
    )

    assert fetcher.source_id == "test"
    assert fetcher.url == "http://example.com/data.json"
    assert fetcher.transform_fn is None

    js_code = fetcher.to_js()
    assert "// No transformation applied" in js_code
