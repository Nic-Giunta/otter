"""Window operations for Otter series."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from .compute import aggregate
from .errors import WindowError
from .nulls import NULL, is_null
from .series import Series


class Rolling:
    """Rolling fixed-size window over a series."""

    def __init__(self, series: Series, window: int, *, min_periods: int | None = None) -> None:
        if isinstance(window, bool) or not isinstance(window, int) or window <= 0:
            raise WindowError("Rolling window size must be a positive integer.")
        if min_periods is None:
            min_periods = window
        if isinstance(min_periods, bool) or not isinstance(min_periods, int):
            raise WindowError("Rolling min_periods must be an integer or None.")
        if min_periods < 0 or min_periods > window:
            raise WindowError("Rolling min_periods must be between 0 and the window size.")
        self.series = series
        self.window = window
        self.min_periods = min_periods

    def _apply(self, op: str) -> Series:
        out: list[Any] = []
        values = self.series.to_list()
        _validate_numeric_values(values)
        for index in range(len(values)):
            window_values = values[max(0, index + 1 - self.window) : index + 1]
            if _non_null_count(window_values) < self.min_periods:
                out.append(NULL)
            else:
                out.append(aggregate(window_values, op))
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

    def __init__(self, series: Series, *, min_periods: int = 1) -> None:
        if isinstance(min_periods, bool) or not isinstance(min_periods, int) or min_periods < 0:
            raise WindowError("Expanding min_periods must be a non-negative integer.")
        self.series = series
        self.min_periods = min_periods

    def _apply(self, op: str) -> Series:
        values = self.series.to_list()
        _validate_numeric_values(values)
        out: list[Any] = []
        for index in range(len(values)):
            window_values = values[: index + 1]
            if _non_null_count(window_values) < self.min_periods:
                out.append(NULL)
            else:
                out.append(aggregate(window_values, op))
        return Series(out, name=self.series.name)

    def sum(self) -> Series:
        """Return expanding sums."""

        return self._apply("sum")

    def mean(self) -> Series:
        """Return expanding means."""

        return self._apply("mean")


def _non_null_count(values: list[Any]) -> int:
    return sum(1 for value in values if not is_null(value))


def _validate_numeric_values(values: list[Any]) -> None:
    for position, value in enumerate(values):
        if is_null(value):
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            raise WindowError(
                f"Window operation expected numeric values or NULL, got {type(value).__name__} "
                f"at position {position}.\n\n"
                "Suggested fix:\nCast the series to a numeric dtype or select a numeric column."
            )
