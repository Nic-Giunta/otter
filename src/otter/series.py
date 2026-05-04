"""Series implementation for Otter."""

from __future__ import annotations

import datetime as _dt
import operator
from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import Any

from . import compute
from .dtypes import Boolean, DType, cast_values, infer_dtype
from .errors import RowSelectionError, ShapeError
from .nulls import NULL, is_null, materialize_null, normalize_null, not_null


class Series:
    """A one-dimensional ordered column with a logical dtype."""

    def __init__(self, values: Iterable[Any], *, name: str | None = None, dtype: DType | None = None) -> None:
        self._data = [normalize_null(value) for value in values]
        self.name = name
        self.dtype = dtype or infer_dtype(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._data)

    def __repr__(self) -> str:
        name = f", name={self.name!r}" if self.name is not None else ""
        return f"Series({self._data!r}{name}, dtype={self.dtype})"

    def __getitem__(self, item: int | slice) -> Any | Series:
        if isinstance(item, slice):
            return Series(self._data[item], name=self.name, dtype=self.dtype)
        return self._data[item]

    def __eq__(self, other: object) -> Series:  # type: ignore[override]
        return self._compare(other, "==", operator.eq)

    def __ne__(self, other: object) -> Series:  # type: ignore[override]
        return self._compare(other, "!=", operator.ne)

    def __gt__(self, other: Any) -> Series:
        return self._compare(other, ">", operator.gt)

    def __ge__(self, other: Any) -> Series:
        return self._compare(other, ">=", operator.ge)

    def __lt__(self, other: Any) -> Series:
        return self._compare(other, "<", operator.lt)

    def __le__(self, other: Any) -> Series:
        return self._compare(other, "<=", operator.le)

    def __add__(self, other: Any) -> Series:
        return self._binary(other, "+", operator.add)

    def __radd__(self, other: Any) -> Series:
        return self._binary(other, "+", operator.add, reverse=True)

    def __sub__(self, other: Any) -> Series:
        return self._binary(other, "-", operator.sub)

    def __rsub__(self, other: Any) -> Series:
        return self._binary(other, "-", operator.sub, reverse=True)

    def __mul__(self, other: Any) -> Series:
        return self._binary(other, "*", operator.mul)

    def __rmul__(self, other: Any) -> Series:
        return self._binary(other, "*", operator.mul, reverse=True)

    def __truediv__(self, other: Any) -> Series:
        return self._binary(other, "/", operator.truediv)

    def __rtruediv__(self, other: Any) -> Series:
        return self._binary(other, "/", operator.truediv, reverse=True)

    def __floordiv__(self, other: Any) -> Series:
        return self._binary(other, "//", operator.floordiv)

    def __mod__(self, other: Any) -> Series:
        return self._binary(other, "%", operator.mod)

    def __pow__(self, other: Any) -> Series:
        return self._binary(other, "**", operator.pow)

    def __and__(self, other: Any) -> Series:
        return self._boolean_binary(other, operator.and_)

    def __or__(self, other: Any) -> Series:
        return self._boolean_binary(other, operator.or_)

    def __invert__(self) -> Series:
        values = []
        for value in self._data:
            if is_null(value):
                values.append(NULL)
            elif isinstance(value, bool):
                values.append(not value)
            else:
                raise RowSelectionError("Boolean inversion requires Boolean values or NULL.")
        return Series(values, name=self.name, dtype=Boolean)

    @property
    def length(self) -> int:
        """Return the number of values."""

        return len(self)

    def copy(self) -> Series:
        """Return a copy of this series."""

        return Series(self._data, name=self.name, dtype=self.dtype)

    def rename(self, name: str | None) -> Series:
        """Return a copy with a new name."""

        return Series(self._data, name=name, dtype=self.dtype)

    def to_list(self, *, null_as_none: bool = False) -> list[Any]:
        """Return values as a list."""

        if null_as_none:
            return [materialize_null(value) for value in self._data]
        return list(self._data)

    def to_dict(self) -> dict[int, Any]:
        """Return a positional dictionary."""

        return dict(enumerate(self._data))

    def is_null(self) -> Series:
        """Return a boolean series indicating logical nulls."""

        return Series([is_null(value) for value in self._data], name=self.name, dtype=Boolean)

    def not_null(self) -> Series:
        """Return a boolean series indicating non-null values."""

        return Series([not_null(value) for value in self._data], name=self.name, dtype=Boolean)

    def fill_null(self, value: Any) -> Series:
        """Return a series where nulls are replaced by *value*."""

        replacement = normalize_null(value)
        return Series([replacement if is_null(item) else item for item in self._data], name=self.name)

    def drop_nulls(self) -> Series:
        """Return a series without null values."""

        return Series([value for value in self._data if not_null(value)], name=self.name)

    def unique(self) -> Series:
        """Return unique values in first-seen order."""

        seen: list[Any] = []
        for value in self._data:
            if not any(value == existing or (is_null(value) and is_null(existing)) for existing in seen):
                seen.append(value)
        return Series(seen, name=self.name)

    def value_counts(self) -> Any:
        """Return a dataframe with value counts for this series."""

        from .dataframe import DataFrame

        keys: list[Any] = []
        counts: list[int] = []
        for value in self._data:
            found = False
            for index, key in enumerate(keys):
                if value == key or (is_null(value) and is_null(key)):
                    counts[index] += 1
                    found = True
                    break
            if not found:
                keys.append(value)
                counts.append(1)
        value_name = self.name or "value"
        return DataFrame({value_name: keys, "count": counts})

    def sort(self, *, reverse: bool = False) -> Series:
        """Return a sorted series with nulls last."""

        return Series(sorted(self._data, key=compute.sort_key, reverse=reverse), name=self.name, dtype=self.dtype)

    def cast(self, dtype: DType, *, strict: bool = True) -> Series:
        """Return values cast to *dtype*."""

        return Series(cast_values(self._data, dtype, strict=strict), name=self.name, dtype=dtype)

    def map(self, mapping: dict[Any, Any] | Callable[[Any], Any]) -> Series:
        """Map values using a dictionary or callable."""

        if callable(mapping):
            return Series([normalize_null(mapping(value)) if not is_null(value) else NULL for value in self._data], name=self.name)
        return Series([normalize_null(mapping.get(value, NULL)) if not is_null(value) else NULL for value in self._data], name=self.name)

    def apply(self, func: Callable[[Any], Any]) -> Series:
        """Apply a callable to each non-null value."""

        return Series([normalize_null(func(value)) if not is_null(value) else NULL for value in self._data], name=self.name)

    def filter(self, mask: Series | Sequence[bool]) -> Series:
        """Return values selected by a boolean mask."""

        booleans = _validate_mask(mask, len(self))
        return Series([value for value, keep in zip(self._data, booleans, strict=True) if keep], name=self.name, dtype=self.dtype)

    def sum(self, *, skip_nulls: bool = True) -> Any:
        """Return the sum of values."""

        return compute.aggregate(self._data, "sum", skip_nulls=skip_nulls)

    def mean(self, *, skip_nulls: bool = True) -> Any:
        """Return the arithmetic mean."""

        return compute.aggregate(self._data, "mean", skip_nulls=skip_nulls)

    def min(self, *, skip_nulls: bool = True) -> Any:
        """Return the minimum value."""

        return compute.aggregate(self._data, "min", skip_nulls=skip_nulls)

    def max(self, *, skip_nulls: bool = True) -> Any:
        """Return the maximum value."""

        return compute.aggregate(self._data, "max", skip_nulls=skip_nulls)

    def count(self) -> int:
        """Return the number of non-null values."""

        return int(compute.aggregate(self._data, "count"))

    def median(self, *, skip_nulls: bool = True) -> Any:
        """Return the median value."""

        return compute.aggregate(self._data, "median", skip_nulls=skip_nulls)

    def std(self, *, skip_nulls: bool = True) -> Any:
        """Return the sample standard deviation."""

        return compute.aggregate(self._data, "std", skip_nulls=skip_nulls)

    def var(self, *, skip_nulls: bool = True) -> Any:
        """Return the sample variance."""

        return compute.aggregate(self._data, "var", skip_nulls=skip_nulls)

    def quantile(self, q: float, *, skip_nulls: bool = True) -> Any:
        """Return the requested quantile."""

        return compute.quantile(self._data, q, skip_nulls=skip_nulls)

    def str_len(self) -> Series:
        """Return string lengths, preserving nulls."""

        return self.apply(lambda value: len(str(value)))

    def str_lower(self) -> Series:
        """Return lowercase strings."""

        return self.apply(lambda value: str(value).lower())

    def str_upper(self) -> Series:
        """Return uppercase strings."""

        return self.apply(lambda value: str(value).upper())

    def str_contains(self, pattern: str) -> Series:
        """Return whether each string contains *pattern*."""

        return self.apply(lambda value: pattern in str(value)).cast(Boolean, strict=False)

    def str_startswith(self, prefix: str) -> Series:
        """Return whether each string starts with *prefix*."""

        return self.apply(lambda value: str(value).startswith(prefix)).cast(Boolean, strict=False)

    def str_endswith(self, suffix: str) -> Series:
        """Return whether each string ends with *suffix*."""

        return self.apply(lambda value: str(value).endswith(suffix)).cast(Boolean, strict=False)

    def str_replace(self, old: str, new: str) -> Series:
        """Return strings with *old* replaced by *new*."""

        return self.apply(lambda value: str(value).replace(old, new))

    def dt_year(self) -> Series:
        """Extract year from date-like values."""

        return self.apply(lambda value: _require_temporal(value).year)

    def dt_month(self) -> Series:
        """Extract month from date-like values."""

        return self.apply(lambda value: _require_temporal(value).month)

    def dt_day(self) -> Series:
        """Extract day from date-like values."""

        return self.apply(lambda value: _require_temporal(value).day)

    def rolling(self, window: int) -> Any:
        """Return a rolling window object."""

        from .window import Rolling

        return Rolling(self, window)

    def expanding(self) -> Any:
        """Return an expanding window object."""

        from .window import Expanding

        return Expanding(self)

    @property
    def str(self) -> StringNamespace:
        """Return string helper namespace."""

        return StringNamespace(self)

    @property
    def dt(self) -> DatetimeNamespace:
        """Return datetime helper namespace."""

        return DatetimeNamespace(self)

    def _binary(self, other: Any, symbol: str, func: Callable[[Any, Any], Any], *, reverse: bool = False) -> Series:
        left, right = _align_binary(self, other, reverse=reverse)
        return Series([compute.apply_binary(a, b, func) for a, b in zip(left, right, strict=True)], name=self.name)

    def _compare(self, other: Any, symbol: str, func: Callable[[Any, Any], Any]) -> Series:
        left, right = _align_binary(self, other)
        return Series([compute.apply_comparison(a, b, func) for a, b in zip(left, right, strict=True)], name=self.name, dtype=Boolean)

    def _boolean_binary(self, other: Any, func: Callable[[bool, bool], bool]) -> Series:
        left, right = _align_binary(self, other)
        out = []
        for a, b in zip(left, right, strict=True):
            if is_null(a) or is_null(b):
                out.append(NULL)
            elif isinstance(a, bool) and isinstance(b, bool):
                out.append(func(a, b))
            else:
                raise RowSelectionError("Boolean operations require Boolean values or NULL.")
        return Series(out, name=self.name, dtype=Boolean)


class StringNamespace:
    """String helper namespace available as ``series.str``."""

    def __init__(self, series: Series) -> None:
        self._series = series

    def len(self) -> Series:
        return self._series.str_len()

    def lower(self) -> Series:
        return self._series.str_lower()

    def upper(self) -> Series:
        return self._series.str_upper()

    def contains(self, pattern: str) -> Series:
        return self._series.str_contains(pattern)

    def startswith(self, prefix: str) -> Series:
        return self._series.str_startswith(prefix)

    def endswith(self, suffix: str) -> Series:
        return self._series.str_endswith(suffix)

    def replace(self, old: str, new: str) -> Series:
        return self._series.str_replace(old, new)


class DatetimeNamespace:
    """Datetime helper namespace available as ``series.dt``."""

    def __init__(self, series: Series) -> None:
        self._series = series

    def year(self) -> Series:
        return self._series.dt_year()

    def month(self) -> Series:
        return self._series.dt_month()

    def day(self) -> Series:
        return self._series.dt_day()


def _align_binary(series: Series, other: Any, *, reverse: bool = False) -> tuple[list[Any], list[Any]]:
    if isinstance(other, Series):
        if len(series) != len(other):
            raise ShapeError("Series lengths must match for element-wise operations.")
        left = other.to_list() if reverse else series.to_list()
        right = series.to_list() if reverse else other.to_list()
        return left, right
    if reverse:
        return [other] * len(series), series.to_list()
    return series.to_list(), [other] * len(series)


def _validate_mask(mask: Series | Sequence[bool], expected_length: int) -> list[bool]:
    values = mask.to_list() if isinstance(mask, Series) else list(mask)
    if len(values) != expected_length:
        raise RowSelectionError(
            f"Boolean mask length {len(values)} does not match expected length {expected_length}."
        )
    result: list[bool] = []
    for position, value in enumerate(values):
        if is_null(value):
            raise RowSelectionError(
                f"Boolean mask contains NULL at position {position}.\n\n"
                "Suggested fix:\nUse fill_null(False) or drop nulls before filtering."
            )
        if not isinstance(value, bool):
            raise RowSelectionError(
                f"Boolean mask contains non-boolean value {value!r} at position {position}."
            )
        result.append(value)
    return result


def _require_temporal(value: Any) -> _dt.date | _dt.datetime:
    if isinstance(value, (_dt.date, _dt.datetime)):
        return value
    raise TypeError(f"Expected date or datetime value, got {type(value).__name__}.")
