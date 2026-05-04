"""String helper functions for Otter."""

from __future__ import annotations

from .series import Series


def str_len(series: Series) -> Series:
    """Return string lengths."""

    return series.str_len()


def str_lower(series: Series) -> Series:
    """Return lowercase strings."""

    return series.str_lower()


def str_upper(series: Series) -> Series:
    """Return uppercase strings."""

    return series.str_upper()


def str_contains(series: Series, pattern: str) -> Series:
    """Return whether strings contain a pattern."""

    return series.str_contains(pattern)
