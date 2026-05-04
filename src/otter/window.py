"""Window operations for Otter series."""

from __future__ import annotations

from typing import Any

from .compute import aggregate
from .errors import WindowError
from .nulls import NULL
from .series import Series


class Rolling:
    """Rolling fixed-size window over a series."""

    def __init__(self, series: Series, window: int) -> None:
        if window <= 0:
            raise WindowError("Rolling window size must be a positive integer.")
        self.series = series
        self.window = window

    def _apply(self, op: str) -> Series:
        out: list[Any] = []
        values = self.series.to_list()
        for index in range(len(values)):
            if index + 1 < self.window:
                out.append(NULL)
            else:
                out.append(aggregate(values[index + 1 - self.window : index + 1], op))
        return Series(out, name=self.series.name)

    def sum(self) -> Series:
        """Return rolling sums."""

        return self._apply("sum")

    def mean(self) -> Series:
        """Return rolling means."""

        return self._apply("mean")

    def min(self) -> Series:
        """Return rolling minima."""

        return self._apply("min")

    def max(self) -> Series:
        """Return rolling maxima."""

        return self._apply("max")


class Expanding:
    """Expanding window over a series."""

    def __init__(self, series: Series) -> None:
        self.series = series

    def _apply(self, op: str) -> Series:
        values = self.series.to_list()
        return Series([aggregate(values[: index + 1], op) for index in range(len(values))], name=self.series.name)

    def sum(self) -> Series:
        """Return expanding sums."""

        return self._apply("sum")

    def mean(self) -> Series:
        """Return expanding means."""

        return self._apply("mean")
