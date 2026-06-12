import pytest
import math
from maplibreum.animation import haversine_distance, calculate_bearing, interpolate_along_line

def test_haversine_distance_zero():
    # Same point should have zero distance
    point = (0.0, 0.0)
    assert haversine_distance(point, point) == 0.0

def test_haversine_distance_poles():
    # North pole to South pole is approx 20,000 km
    north_pole = (0.0, 90.0)
    south_pole = (0.0, -90.0)
    # Expected: pi * R = 3.14159... * 6371000
    expected = math.pi * 6371000
    assert pytest.approx(haversine_distance(north_pole, south_pole), rel=1e-4) == expected

def test_haversine_distance_known():
    # London to New York (approx 5570 km)
    london = (-0.1278, 51.5074)
    new_york = (-74.0060, 40.7128)
    distance = haversine_distance(london, new_york)
    # 5570 km = 5,570,000 meters
    assert 5500000 < distance < 5600000

def test_haversine_distance_symmetry():
    a = (12.34, 56.78)
    b = (90.12, 34.56)
    assert haversine_distance(a, b) == haversine_distance(b, a)

def test_calculate_bearing_cardinal():
    start = (0.0, 0.0)
    north = (0.0, 10.0)
    east = (10.0, 0.0)
    south = (0.0, -10.0)
    west = (-10.0, 0.0)

    assert calculate_bearing(start, north) == 0.0
    assert calculate_bearing(start, east) == 90.0
    assert calculate_bearing(start, south) == 180.0
    assert calculate_bearing(start, west) == 270.0

def test_interpolate_along_line_simple():
    coords = [(0.0, 0.0), (10.0, 0.0)]
    steps = 10
    arc = interpolate_along_line(coords, steps)

    assert len(arc) == steps + 1
    assert arc[0] == (0.0, 0.0)
    assert arc[-1] == (10.0, 0.0)
    # Midpoint should be approx (5, 0)
    assert pytest.approx(arc[5][0]) == 5.0
    assert pytest.approx(arc[5][1]) == 0.0

def test_interpolate_along_line_single_point():
    coords = [(0.0, 0.0)]
    arc = interpolate_along_line(coords, 10)
    assert arc == coords

def test_interpolate_along_line_zero_distance():
    coords = [(0.0, 0.0), (0.0, 0.0)]
    arc = interpolate_along_line(coords, 10)
    assert arc == coords
