"""Logical null handling for Otter."""

from __future__ import annotations

import math
from decimal import Decimal
from typing import Any, TypeGuard

from .errors import NullValueError


class NullValue:
    """Singleton logical null value used by Otter."""

    __slots__ = ()

    def __repr__(self) -> str:
        return "NULL"

    def __str__(self) -> str:
        return "NULL"

    def __bool__(self) -> bool:
        raise NullValueError(
            "NULL cannot be used as a boolean.\n\n"
            "Suggested fix:\nUse is_null(), not_null(), fill_null(), or an explicit comparison."
        )

    def __reduce__(self) -> str:
        return "NULL"


NULL = NullValue()


def is_null(value: Any) -> bool:
    """Return True when *value* is Otter NULL, None, or a floating NaN."""

    if value is NULL or value is None:
        return True
    if isinstance(value, float):
        return math.isnan(value)
    if isinstance(value, Decimal):
        return value.is_nan()
    return False


def not_null(value: Any) -> bool:
    """Return True when *value* is not logically null."""

    return not is_null(value)


def is_null_value(value: Any) -> TypeGuard[NullValue]:
    """Return True if *value* is the Otter NULL singleton."""

    return value is NULL


def normalize_null(value: Any) -> Any:
    """Normalize Python null-like values to the Otter NULL singleton."""

    return NULL if is_null(value) else value


def coalesce(*values: Any) -> Any:
    """Return the first non-null value, or NULL when all values are null."""

    for value in values:
        normalized = normalize_null(value)
        if not is_null(normalized):
            return normalized
    return NULL


def materialize_null(value: Any) -> Any:
    """Convert Otter NULL to None for external formats."""

    return None if is_null(value) else value
