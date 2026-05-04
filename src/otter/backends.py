"""Backend abstraction for Otter."""

from __future__ import annotations

from typing import Any, Protocol


class Backend(Protocol):
    """Execution backend protocol."""

    name: str

    def dataframe_from_mapping(self, data: dict[str, list[Any]]) -> Any:
        """Create a dataframe from a mapping."""


class PythonBackend:
    """Pure Python backend used by the core package."""

    name = "python"

    def dataframe_from_mapping(self, data: dict[str, list[Any]]) -> Any:
        """Create a dataframe from a Python mapping."""

        from .dataframe import DataFrame

        return DataFrame(data)


DEFAULT_BACKEND = PythonBackend()
