"""Explicit row indexes for Otter."""

from __future__ import annotations

import builtins
from collections.abc import Iterable, Iterator
from typing import Any

from .errors import IndexError, ShapeError


class Index:
    """Explicit row labels with no implicit alignment semantics."""

    def __init__(self, values: Iterable[Any], *, name: str | None = None) -> None:
        if name is not None and not isinstance(name, str):
            raise IndexError(f"Index name must be a string or None, got {type(name).__name__}.")
        self._values = list(values)
        self.name = name

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._values)

    def __getitem__(self, item: int | slice) -> Any | Index:
        if isinstance(item, slice):
            return Index(self._values[item], name=self.name)
        if isinstance(item, bool) or not isinstance(item, int):
            raise IndexError(f"Index positions must be integers or slices, got {type(item).__name__}.")
        try:
            return self._values[item]
        except builtins.IndexError as exc:
            raise IndexError(f"Index position {item} is out of bounds for length {len(self)}.") from exc

    def __repr__(self) -> str:
        return f"Index({self._values!r}, name={self.name!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Index) and self._values == other._values and self.name == other.name

    def to_list(self) -> list[Any]:
        """Return row labels as a list."""

        return list(self._values)

    def copy(self) -> Index:
        """Return a copy of this index."""

        return Index(self._values, name=self.name)

    def validate_length(self, expected: int) -> None:
        """Validate this index length."""

        if len(self) != expected:
            raise ShapeError(f"Index length {len(self)} does not match dataframe height {expected}.")


class RangeIndex(Index):
    """A compact explicit range index."""

    def __init__(self, start: int = 0, stop: int | None = None, step: int = 1, *, name: str | None = None) -> None:
        if stop is None:
            start, stop = 0, start
        if step == 0:
            raise IndexError("RangeIndex step must not be zero.")
        self.start = start
        self.stop = stop
        self.step = step
        super().__init__(range(start, stop, step), name=name)

    def __repr__(self) -> str:
        return f"RangeIndex(start={self.start}, stop={self.stop}, step={self.step}, name={self.name!r})"

    def copy(self) -> RangeIndex:
        """Return a copy of this RangeIndex."""

        return RangeIndex(self.start, self.stop, self.step, name=self.name)
