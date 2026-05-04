"""Datetime helper functions for Otter."""

from __future__ import annotations

from .series import Series


def dt_year(series: Series) -> Series:
    """Return year values."""

    return series.dt_year()


def dt_month(series: Series) -> Series:
    """Return month values."""

    return series.dt_month()


def dt_day(series: Series) -> Series:
    """Return day values."""

    return series.dt_day()
