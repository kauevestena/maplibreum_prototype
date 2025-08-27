import pytest

from maplibreum.expressions import get, interpolate, var, validate


def test_get_expression():
    expr = get("fillColor", ["properties"])
    assert expr == ["get", "fillColor", ["properties"]]
    assert validate(expr)


def test_interpolate_and_validation():
    expr = interpolate(
        "linear",
        var("heatmap-density"),
        [(0, "blue"), (1, "red")],
    )
    assert expr[0] == "interpolate"
    assert validate(expr)

    with pytest.raises(ValueError):
        validate("not an expression")
