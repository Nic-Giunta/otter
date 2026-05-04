"""Reusable compute helpers for Otter."""

from __future__ import annotations

import operator
import statistics
from collections.abc import Callable, Iterable
from typing import Any

from .dtypes import DType, Float64, Int64, is_numeric_dtype
from .errors import AggregationError, CastError
from .nulls import NULL, is_null, normalize_null

BinaryFunc = Callable[[Any, Any], Any]


def apply_binary(left: Any, right: Any, func: BinaryFunc) -> Any:
    """Apply a null-propagating binary operation."""

    left = normalize_null(left)
    right = normalize_null(right)
    if is_null(left) or is_null(right):
        return NULL
    return func(left, right)


def apply_comparison(left: Any, right: Any, func: BinaryFunc) -> Any:
    """Apply a null-aware comparison. Null comparisons produce NULL."""

    left = normalize_null(left)
    right = normalize_null(right)
    if is_null(left) or is_null(right):
        return NULL
    return bool(func(left, right))


def arithmetic_values(left: list[Any], right: list[Any], func: BinaryFunc) -> list[Any]:
    """Apply a binary arithmetic function to two columns."""

    if len(left) != len(right):
        raise ValueError("Cannot compute with columns of different lengths.")
    return [apply_binary(a, b, func) for a, b in zip(left, right, strict=True)]


def comparison_values(left: list[Any], right: list[Any], func: BinaryFunc) -> list[Any]:
    """Apply a binary comparison function to two columns."""

    if len(left) != len(right):
        raise ValueError("Cannot compare columns of different lengths.")
    return [apply_comparison(a, b, func) for a, b in zip(left, right, strict=True)]


def non_null_values(values: Iterable[Any]) -> list[Any]:
    """Return normalized non-null values."""

    return [normalize_null(value) for value in values if not is_null(value)]


def aggregate(values: Iterable[Any], op: str, *, skip_nulls: bool = True) -> Any:
    """Aggregate values with consistent null semantics."""

    normalized = [normalize_null(value) for value in values]
    data = non_null_values(normalized) if skip_nulls else normalized
    if any(is_null(value) for value in data):
        return NULL
    if op == "count":
        return len(data)
    if not data:
        return NULL
    if op == "sum":
        return sum(data)
    if op == "mean":
        return sum(data) / len(data)
    if op == "median":
        return statistics.median(data)
    if op == "min":
        return min(data)
    if op == "max":
        return max(data)
    if op == "var":
        return statistics.variance(data) if len(data) > 1 else 0.0
    if op == "std":
        return statistics.stdev(data) if len(data) > 1 else 0.0
    raise AggregationError(
        f"Aggregation {op!r} is not supported.\n\n"
        "Suggested fix:\nUse one of: sum, mean, median, min, max, count, std, var."
    )


def quantile(values: Iterable[Any], q: float, *, skip_nulls: bool = True) -> Any:
    """Compute a nearest-rank quantile with linear interpolation."""

    if not 0 <= q <= 1:
        raise AggregationError("Quantile must be between 0 and 1 inclusive.")
    data = sorted(non_null_values(values) if skip_nulls else list(values))
    if any(is_null(value) for value in data):
        return NULL
    if not data:
        return NULL
    if len(data) == 1:
        return data[0]
    pos = (len(data) - 1) * q
    lower = int(pos)
    upper = min(lower + 1, len(data) - 1)
    weight = pos - lower
    return data[lower] * (1 - weight) + data[upper] * weight


def sort_key(value: Any) -> tuple[int, Any]:
    """Sort null values last while keeping non-null ordering natural."""

    value = normalize_null(value)
    return (1, None) if is_null(value) else (0, value)


def result_numeric_dtype(left: DType, right: DType, op: str) -> DType:
    """Infer a numeric result dtype for simple arithmetic."""

    if op == "/":
        return Float64
    if is_numeric_dtype(left) and is_numeric_dtype(right):
        if left == Float64 or right == Float64:
            return Float64
        return Int64
    return Float64


ARITHMETIC_OPERATORS: dict[str, BinaryFunc] = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "//": operator.floordiv,
    "%": operator.mod,
    "**": operator.pow,
}

COMPARISON_OPERATORS: dict[str, BinaryFunc] = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}


def safe_cast_column(values: Iterable[Any], caster: Callable[[Any], Any]) -> list[Any]:
    """Cast a column and normalize errors into CastError."""

    result: list[Any] = []
    for value in values:
        try:
            result.append(caster(value))
        except Exception as exc:  # noqa: BLE001
            raise CastError(f"Value {value!r} could not be cast safely.") from exc
    return result
