from app.utils.geometry import point_in_polygon


SQUARE = [
    {"x": 10.0, "y": 10.0},
    {"x": 110.0, "y": 10.0},
    {"x": 110.0, "y": 90.0},
    {"x": 10.0, "y": 90.0},
]


def test_point_inside_polygon():
    assert point_in_polygon(50.0, 40.0, SQUARE) is True


def test_point_outside_polygon():
    assert point_in_polygon(130.0, 40.0, SQUARE) is False


def test_point_on_polygon_boundary_counts_as_hit():
    assert point_in_polygon(10.0, 40.0, SQUARE) is True


def test_polygon_requires_three_vertices():
    assert point_in_polygon(10.0, 10.0, SQUARE[:2]) is False
