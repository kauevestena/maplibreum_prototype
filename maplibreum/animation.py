"""Utilities for describing MapLibre animations using Python objects."""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Union


def _normalize_lines(block: Optional[Union[str, Sequence[str]]]) -> List[str]:
    """Convert input into a flat list of JavaScript source lines."""

    if block is None:
        return []
    if isinstance(block, str):
        return [line for line in block.splitlines()]
    result: List[str] = []
    for line in block:
        if not isinstance(line, str):
            raise TypeError("Animation code blocks must be strings")
        result.extend(line.splitlines())
    return result


def _indent_block(lines: Iterable[str], prefix: str = "    ") -> str:
    body = "\n".join(lines).strip()
    if not body:
        return ""
    return textwrap.indent(body, prefix)


@dataclass
class AnimationLoop:
    """Describe a ``requestAnimationFrame`` loop.

    Parameters
    ----------
    name:
        Name of the JavaScript function implementing the loop.
    body:
        Statements executed on each frame. Either a string or sequence of
        strings.
    variables:
        Mapping of variable names to initial values declared with ``let``.
    setup:
        Additional statements executed once before the animation starts.
    auto_schedule:
        When ``True`` the loop automatically schedules the next frame using
        ``requestAnimationFrame`` at the end of ``body``.
    start_immediately:
        When ``True`` the animation starts right away once registered.
    handle_name:
        Optional variable that stores the ``requestAnimationFrame`` handle.
    visibility_reset:
        Statements executed whenever the page visibility changes, useful for
        resuming animations gracefully.
    """

    name: str
    body: Union[str, Sequence[str]]
    variables: Dict[str, str] = field(default_factory=dict)
    setup: Union[str, Sequence[str], None] = None
    auto_schedule: bool = True
    start_immediately: bool = True
    handle_name: Optional[str] = None
    visibility_reset: Union[str, Sequence[str], None] = None

    def to_js(self) -> str:
        handle = self.handle_name or f"{self.name}Handle"
        parts: List[str] = []

        for var, value in self.variables.items():
            parts.append(f"let {var} = {value};")

        declare_handle = (self.auto_schedule or self.start_immediately) and (
            handle not in self.variables
        )
        if declare_handle:
            parts.append(f"let {handle};")

        parts.extend(_normalize_lines(self.setup))

        body_lines = _normalize_lines(self.body)
        if self.auto_schedule:
            body_lines.append(f"{handle} = requestAnimationFrame({self.name});")
        function_block = _indent_block(body_lines)
        parts.append(f"function {self.name}(timestamp){{\n{function_block}\n}}")

        if self.start_immediately:
            parts.append(f"{handle} = requestAnimationFrame({self.name});")

        reset_lines = _normalize_lines(self.visibility_reset)
        if reset_lines:
            reset_block = _indent_block(reset_lines)
            parts.append(
                "document.addEventListener('visibilitychange', function(){\n"
                f"{reset_block}\n" "});"
            )

        return "\n".join(filter(None, parts))


@dataclass
class TemporalInterval:
    """Represent a ``setInterval`` loop."""

    callback: Union[str, Sequence[str]]
    interval: int
    name: Optional[str] = None
    run_immediately: bool = False

    def to_js(self) -> str:
        body_lines = _normalize_lines(self.callback)
        body_block = _indent_block(body_lines)
        function = f"function(){{\n{body_block}\n}}"

        if self.name:
            declaration = f"var {self.name} = setInterval({function}, {self.interval});"
        else:
            declaration = f"setInterval({function}, {self.interval});"

        if self.run_immediately:
            immediate = f"(function(){{\n{body_block}\n}})();"
            return immediate + "\n" + declaration
        return declaration


__all__ = ["AnimationLoop", "TemporalInterval"]
