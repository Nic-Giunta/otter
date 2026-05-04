"""Dtype objects, inference, and casting for Otter."""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from decimal import Decimal as _Decimal
from collections.abc import Iterable
from typing import Any

from .errors import CastError
from .nulls import NULL, is_null, normalize_null


@dataclass(frozen=True, slots=True)
class DType:
    """A logical Otter dtype."""

    name: str
    nullable: bool = True

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


Int8 = DType("Int8")
Int16 = DType("Int16")
Int32 = DType("Int32")
Int64 = DType("Int64")
UInt8 = DType("UInt8")
UInt16 = DType("UInt16")
UInt32 = DType("UInt32")
UInt64 = DType("UInt64")
Float32 = DType("Float32")
Float64 = DType("Float64")
Boolean = DType("Boolean")
String = DType("String")
Date = DType("Date")
Datetime = DType("Datetime")
Time = DType("Time")
Duration = DType("Duration")
Decimal = DType("Decimal")
Categorical = DType("Categorical")
List = DType("List")
Struct = DType("Struct")
Null = DType("Null")
Object = DType("Object")

_INTEGER_DTYPES = {Int8, Int16, Int32, Int64, UInt8, UInt16, UInt32, UInt64}
_FLOAT_DTYPES = {Float32, Float64}
_NUMERIC_DTYPES = _INTEGER_DTYPES | _FLOAT_DTYPES | {Decimal}
_STRING_DTYPES = {String, Categorical}
_TEMPORAL_DTYPES = {Date, Datetime, Time, Duration}
_ALL_DTYPES = {
    Int8,
    Int16,
    Int32,
    Int64,
    UInt8,
    UInt16,
    UInt32,
    UInt64,
    Float32,
    Float64,
    Boolean,
    String,
    Date,
    Datetime,
    Time,
    Duration,
    Decimal,
    Categorical,
    List,
    Struct,
    Null,
    Object,
}

_INT_RANGES: dict[DType, tuple[int, int]] = {
    Int8: (-(2**7), 2**7 - 1),
    Int16: (-(2**15), 2**15 - 1),
    Int32: (-(2**31), 2**31 - 1),
    Int64: (-(2**63), 2**63 - 1),
    UInt8: (0, 2**8 - 1),
    UInt16: (0, 2**16 - 1),
    UInt32: (0, 2**32 - 1),
    UInt64: (0, 2**64 - 1),
}


def _non_null(values: Iterable[Any]) -> list[Any]:
    return [normalize_null(value) for value in values if not is_null(value)]


def infer_dtype(values: Iterable[Any]) -> DType:
    """Infer a conservative logical dtype for a sequence of values."""

    observed = _non_null(values)
    if not observed:
        return Null
    if all(isinstance(value, bool) for value in observed):
        return Boolean
    if all(isinstance(value, int) and not isinstance(value, bool) for value in observed):
        return Int64
    if all(
        (isinstance(value, int) and not isinstance(value, bool)) or isinstance(value, float)
        for value in observed
    ):
        return Float64
    if all(isinstance(value, str) for value in observed):
        return String
    if all(isinstance(value, _dt.datetime) for value in observed):
        return Datetime
    if all(isinstance(value, _dt.date) and not isinstance(value, _dt.datetime) for value in observed):
        return Date
    if all(isinstance(value, _dt.time) for value in observed):
        return Time
    if all(isinstance(value, _dt.timedelta) for value in observed):
        return Duration
    if all(isinstance(value, _Decimal) for value in observed):
        return Decimal
    if all(isinstance(value, list) for value in observed):
        return List
    if all(isinstance(value, dict) for value in observed):
        return Struct
    return Object


def _parse_date(value: str) -> _dt.date:
    try:
        return _dt.date.fromisoformat(value)
    except ValueError as exc:
        raise CastError(f"Value {value!r} cannot be cast to Date.") from exc


def _parse_datetime(value: str) -> _dt.datetime:
    try:
        return _dt.datetime.fromisoformat(value)
    except ValueError as exc:
        raise CastError(f"Value {value!r} cannot be cast to Datetime.") from exc


def _parse_time(value: str) -> _dt.time:
    try:
        return _dt.time.fromisoformat(value)
    except ValueError as exc:
        raise CastError(f"Value {value!r} cannot be cast to Time.") from exc


def can_cast(from_dtype: DType, to_dtype: DType, *, strict: bool = True) -> bool:
    """Return whether values of *from_dtype* can be cast to *to_dtype*."""

    if from_dtype == to_dtype or from_dtype == Null or to_dtype == Object:
        return True
    if to_dtype == String:
        return not strict or from_dtype in {String, Categorical}
    if from_dtype in _INTEGER_DTYPES and to_dtype in _INTEGER_DTYPES:
        return not strict or to_dtype == Int64 or to_dtype == UInt64
    if from_dtype in _INTEGER_DTYPES and to_dtype in _FLOAT_DTYPES:
        return True
    if from_dtype in _FLOAT_DTYPES and to_dtype in _FLOAT_DTYPES:
        return True
    if from_dtype == Boolean and to_dtype == Boolean:
        return True
    if not strict and to_dtype in _ALL_DTYPES:
        return True
    return False


def cast_value(value: Any, dtype: DType, *, strict: bool = True) -> Any:
    """Cast one value to *dtype*, preserving logical nulls."""

    if not isinstance(dtype, DType):
        raise CastError(
            f"Target dtype must be an Otter DType, got {type(dtype).__name__}.\n\n"
            "Suggested fix:\nUse a dtype object such as otter.Int64 or otter.String."
        )
    value = normalize_null(value)
    if value is NULL:
        return NULL
    try:
        if dtype == Object:
            return value
        if dtype == Null:
            raise CastError(f"Non-null value {value!r} cannot be cast to Null.")
        if dtype == String or dtype == Categorical:
            if strict and not isinstance(value, str):
                raise CastError(f"Value {value!r} cannot be safely cast to String with strict=True.")
            return str(value)
        if dtype == Boolean:
            if isinstance(value, bool):
                return value
            if not strict and isinstance(value, str) and value.lower() in {"true", "false"}:
                return value.lower() == "true"
            raise CastError(f"Value {value!r} cannot be cast to Boolean.")
        if dtype in _INTEGER_DTYPES:
            if isinstance(value, bool):
                raise CastError(f"Boolean value {value!r} cannot be cast to {dtype}.")
            if isinstance(value, int):
                result = value
            elif not strict and isinstance(value, float) and value.is_integer():
                result = int(value)
            elif not strict and isinstance(value, str):
                result = int(value)
            else:
                raise CastError(f"Value {value!r} cannot be safely cast to {dtype}.")
            lower, upper = _INT_RANGES[dtype]
            if not lower <= result <= upper:
                raise CastError(f"Value {value!r} is outside the valid range for {dtype}.")
            return result
        if dtype in _FLOAT_DTYPES:
            if isinstance(value, bool):
                raise CastError(f"Boolean value {value!r} cannot be cast to {dtype}.")
            if isinstance(value, (int, float)):
                return float(value)
            if not strict and isinstance(value, str):
                return float(value)
            raise CastError(f"Value {value!r} cannot be safely cast to {dtype}.")
        if dtype == Decimal:
            return _Decimal(str(value))
        if dtype == Date:
            if isinstance(value, _dt.date) and not isinstance(value, _dt.datetime):
                return value
            if not strict and isinstance(value, str):
                return _parse_date(value)
            raise CastError(f"Value {value!r} cannot be cast to Date.")
        if dtype == Datetime:
            if isinstance(value, _dt.datetime):
                return value
            if not strict and isinstance(value, str):
                return _parse_datetime(value)
            raise CastError(f"Value {value!r} cannot be cast to Datetime.")
        if dtype == Time:
            if isinstance(value, _dt.time):
                return value
            if not strict and isinstance(value, str):
                return _parse_time(value)
            raise CastError(f"Value {value!r} cannot be cast to Time.")
        if dtype == Duration:
            if isinstance(value, _dt.timedelta):
                return value
            raise CastError(f"Value {value!r} cannot be cast to Duration.")
        if dtype == List:
            if isinstance(value, list):
                return value
            raise CastError(f"Value {value!r} cannot be cast to List.")
        if dtype == Struct:
            if isinstance(value, dict):
                return value
            raise CastError(f"Value {value!r} cannot be cast to Struct.")
    except CastError as exc:
        raise _enrich_cast_error(value, dtype, strict, str(exc)) from exc
    except (ValueError, TypeError) as exc:
        raise _enrich_cast_error(value, dtype, strict, f"Underlying conversion failed: {exc}.") from exc
    raise _enrich_cast_error(value, dtype, strict, f"Unsupported dtype {dtype!r}.")


def cast_values(values: Iterable[Any], dtype: DType, *, strict: bool = True) -> list[Any]:
    """Cast a sequence of values to *dtype*."""

    return [cast_value(value, dtype, strict=strict) for value in values]


def common_supertype(left: DType, right: DType) -> DType:
    """Return a conservative common dtype for two dtypes."""

    if left == right:
        return left
    if left == Null:
        return right
    if right == Null:
        return left
    if left in _NUMERIC_DTYPES and right in _NUMERIC_DTYPES:
        if left == Decimal or right == Decimal:
            return Decimal
        if left in _FLOAT_DTYPES or right in _FLOAT_DTYPES:
            return Float64
        return Int64
    if left in _TEMPORAL_DTYPES and right in _TEMPORAL_DTYPES and left == right:
        return left
    if left in _STRING_DTYPES and right in _STRING_DTYPES:
        return String
    return Object


def is_numeric_dtype(dtype: DType) -> bool:
    """Return True for numeric dtypes."""

    return dtype in _NUMERIC_DTYPES


def is_string_dtype(dtype: DType) -> bool:
    """Return True for string-like dtypes."""

    return dtype in _STRING_DTYPES


def is_temporal_dtype(dtype: DType) -> bool:
    """Return True for temporal dtypes."""

    return dtype in _TEMPORAL_DTYPES


def _enrich_cast_error(value: Any, dtype: DType, strict: bool, reason: str) -> CastError:
    source_dtype = infer_dtype([value])
    mode = "strict=True" if strict else "strict=False"
    return CastError(
        f"Cannot cast value {value!r} from inferred dtype {source_dtype} to target dtype {dtype} "
        f"with {mode}.\n\nReason:\n{reason}\n\n"
        "Suggested fix:\nClean or replace invalid values, choose a compatible dtype, or use "
        "strict=False only when Otter documents the coercion you want."
    )
