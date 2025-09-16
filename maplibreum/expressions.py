"""Utility functions for building and validating MapLibre expressions.

MapLibre expressions are represented as nested lists following the
MapLibre GL JS style specification.  This module provides small helper
functions to create these lists while ensuring they are well formed.
"""

from __future__ import annotations

from typing import Any, Iterable, List, Sequence, Tuple

Expression = List[Any]


def validate(expr: Any) -> bool:
    """Validate that *expr* is a well-formed MapLibre expression.

    Parameters
    ----------
    expr : Any
        Expression to validate.

    Returns
    -------
    bool
        ``True`` if validation succeeds.  A :class:`ValueError` is raised
        if the expression structure is invalid.
    """
    if not isinstance(expr, list):
        raise ValueError("Expression must be a list")
    if not expr:
        raise ValueError("Expression cannot be empty")
    if not isinstance(expr[0], str):
        raise ValueError("First element must be an operator string")
    for arg in expr[1:]:
        if isinstance(arg, list):
            validate(arg)
        elif isinstance(arg, (str, int, float, bool, dict, type(None))):
            continue
        else:
            raise ValueError(f"Unsupported argument type: {type(arg).__name__}")
    return True


def expression(op: str, *args: Any) -> Expression:
    """Build and validate a raw expression."""
    expr = [op, *args]
    validate(expr)
    return expr


def get(property: str, context: Any | None = None) -> Expression:
    """Return a ``get`` expression for *property* within *context*.

    Parameters
    ----------
    property : str
        Name of the property to read.
    context : Any, optional
        Optional context, such as ``["properties"]``.
    """
    if context is None:
        expr = ["get", property]
    else:
        expr = ["get", property, context]
    validate(expr)
    return expr


def var(name: str) -> Expression:
    """Return an expression referencing a variable or attribute."""
    expr = [name]
    validate(expr)
    return expr


def interpolate(
    method: str | Sequence[Any],
    input_expr: Any,
    stops: Iterable[Tuple[Any, Any]],
) -> Expression:
    """Return an ``interpolate`` expression.

    Parameters
    ----------
    method : str or sequence
        Interpolation method, e.g. ``"linear"`` or ``["linear"]``.
    input_expr : Any
        Input expression that provides the value to interpolate.
    stops : iterable of (stop, value)
        Sequence of pairs defining interpolation stops.
    """
    if isinstance(method, str):
        method = [method]
    expr: Expression = ["interpolate", list(method), input_expr]
    for stop, value in stops:
        expr.extend([stop, value])
    validate(expr)
    return expr


__all__ = ["expression", "get", "var", "interpolate", "validate"]
