"""DataFrame implementation for Otter."""

from __future__ import annotations

import random
from collections import OrderedDict
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from .dtypes import DType, is_numeric_dtype
from .errors import ColumnNotFoundError, DTypeError, DuplicateColumnError, SchemaError, ShapeError
from .expressions import Expr
from .index import Index, RangeIndex
from .nulls import NULL, is_null, materialize_null, normalize_null
from .schema import Field, Schema
from .series import Series, _validate_mask


class DataFrame:
    """An ordered, immutable-by-default dataframe."""

    def __init__(self, data: Mapping[str, Iterable[Any]] | Sequence[Mapping[str, Any]], *, index: Index | None = None) -> None:
        columns, row_count_hint = _normalize_input(data)
        names = list(columns.keys())
        if len(names) != len(set(names)):
            raise DuplicateColumnError("Duplicate column names are not allowed.")
        lengths = {name: len(values) for name, values in columns.items()}
        if lengths and len(set(lengths.values())) != 1:
            details = ", ".join(f"{name}={length}" for name, length in lengths.items())
            raise ShapeError(f"All columns must have the same length. Received lengths: {details}.")
        self._data: OrderedDict[str, Series] = OrderedDict(
            (name, values if isinstance(values, Series) else Series(values, name=name))
            for name, values in columns.items()
        )
        for name, series in list(self._data.items()):
            if series.name != name:
                self._data[name] = series.rename(name)
        height = next(iter(lengths.values()), None)
        if height is None:
            height = row_count_hint if row_count_hint is not None else (len(index) if index is not None else 0)
        self._index = index.copy() if index is not None else RangeIndex(height)
        self._index.validate_length(height)
        self._schema = Schema(Field(name, series.dtype) for name, series in self._data.items())

    def __repr__(self) -> str:
        preview = self.head(5).to_rows(null_as_none=False)
        return f"DataFrame({preview!r}, shape={self.shape})"

    def __len__(self) -> int:
        return self.height

    def __getitem__(self, item: str | Sequence[str]) -> Series | DataFrame:
        if isinstance(item, str):
            self._require_column(item)
            return self._data[item].copy()
        return self.select(*list(item))

    @property
    def shape(self) -> tuple[int, int]:
        """Return ``(height, width)``."""

        return (self.height, self.width)

    @property
    def height(self) -> int:
        """Return the number of rows."""

        if not self._data:
            return len(self._index)
        return len(next(iter(self._data.values())))

    @property
    def width(self) -> int:
        """Return the number of columns."""

        return len(self._data)

    @property
    def columns(self) -> list[str]:
        """Return ordered column names."""

        return list(self._data.keys())

    @property
    def schema(self) -> Schema:
        """Return the dataframe schema."""

        return self._schema

    @property
    def index(self) -> Index:
        """Return the explicit row index."""

        return self._index.copy()

    def select(self, *columns: str | Expr) -> DataFrame:
        """Return a dataframe with selected columns or evaluated expressions."""

        if not columns:
            return DataFrame({}, index=self._index)
        out: OrderedDict[str, Iterable[Any]] = OrderedDict()
        for item in columns:
            if isinstance(item, Expr):
                series = item.evaluate(self)
                name = item.output_name() or series.name or repr(item)
                if name in out:
                    raise DuplicateColumnError(f"Selection would create duplicate column {name!r}.")
                out[name] = series.rename(name)
            else:
                _validate_column_name(item)
                self._require_column(item)
                out[item] = self._data[item]
        return DataFrame(out, index=self._index)

    def drop(self, *columns: str) -> DataFrame:
        """Return a dataframe without the selected columns."""

        for column in columns:
            self._require_column(column)
        return DataFrame(OrderedDict((name, series) for name, series in self._data.items() if name not in columns), index=self._index)

    def rename(self, mapping: Mapping[str, str]) -> DataFrame:
        """Return a dataframe with renamed columns."""

        if not isinstance(mapping, Mapping):
            raise SchemaError(
                f"rename() expects a mapping of old names to new names, got {type(mapping).__name__}."
            )
        for source in mapping:
            _validate_column_name(source)
            _validate_column_name(mapping[source])
            self._require_column(source)
        names = [mapping.get(name, name) for name in self.columns]
        if len(names) != len(set(names)):
            raise DuplicateColumnError(f"Rename would create duplicate columns: {names!r}.")
        return DataFrame(OrderedDict((mapping.get(name, name), series.rename(mapping.get(name, name))) for name, series in self._data.items()), index=self._index)

    def with_column(self, name: str, values: Series | Expr | Iterable[Any] | Any) -> DataFrame:
        """Return a dataframe with one added or replaced column."""

        _validate_column_name(name)
        series = self._coerce_column(values, name)
        data = OrderedDict((column, value) for column, value in self._data.items())
        data[name] = series.rename(name)
        return DataFrame(data, index=self._index_for_new_columns(data.values()))

    def with_columns(self, mapping: Mapping[str, Series | Expr | Iterable[Any] | Any]) -> DataFrame:
        """Return a dataframe with multiple added or replaced columns."""

        if not isinstance(mapping, Mapping):
            raise SchemaError(
                f"with_columns() expects a mapping of names to values, got {type(mapping).__name__}."
            )
        coerced: OrderedDict[str, Series] = OrderedDict()
        for name, values in mapping.items():
            _validate_column_name(name)
            coerced[name] = self._coerce_column(values, name)
        data = OrderedDict((column, value) for column, value in self._data.items())
        for name, series in coerced.items():
            data[name] = series.rename(name)
        return DataFrame(data, index=self._index_for_new_columns(data.values()))

    def assign(self, **columns: Series | Expr | Iterable[Any] | Any) -> DataFrame:
        """Return a dataframe with keyword-assigned columns."""

        return self.with_columns(columns)

    def filter(self, mask: Series | Expr | Sequence[bool]) -> DataFrame:
        """Return rows selected by a boolean mask."""

        if isinstance(mask, Expr):
            mask = mask.evaluate(self)
        booleans = _validate_mask(mask, self.height)
        positions = [position for position, keep in enumerate(booleans) if keep]
        return self._take_positions(positions)

    def where(self, mask: Series | Expr | Sequence[bool]) -> DataFrame:
        """Return rows where the mask is true."""

        return self.filter(mask)

    def sort(
        self,
        by: str | Sequence[str],
        *,
        reverse: bool = False,
        ascending: bool | None = None,
        nulls_last: bool = True,
    ) -> DataFrame:
        """Return rows sorted by one or more columns."""

        if ascending is not None:
            reverse = not ascending
        columns = [by] if isinstance(by, str) else list(by)
        for column in columns:
            _validate_column_name(column)
            self._require_column(column)
        null_positions = [
            idx for idx in range(self.height) if any(is_null(self._data[column][idx]) for column in columns)
        ]
        null_position_set = set(null_positions)
        value_positions = [idx for idx in range(self.height) if idx not in null_position_set]
        try:
            sorted_values = sorted(
                value_positions,
                key=lambda idx: tuple(self._data[column][idx] for column in columns),
                reverse=reverse,
            )
        except TypeError as exc:
            raise DTypeError(
                f"sort() could not compare values in columns {columns!r}.\n\n"
                "Suggested fix:\nCast mixed-type columns to a common dtype before sorting."
            ) from exc
        positions = [*sorted_values, *null_positions] if nulls_last else [*null_positions, *sorted_values]
        return self._take_positions(positions)

    def cast(self, mapping: Mapping[str, DType], *, strict: bool = True) -> DataFrame:
        """Return a dataframe with selected columns cast to requested dtypes."""

        data = OrderedDict((name, series) for name, series in self._data.items())
        for name, dtype in mapping.items():
            self._require_column(name)
            data[name] = self._data[name].cast(dtype, strict=strict)
        return DataFrame(data, index=self._index)

    def fill_null(self, value: Any | Mapping[str, Any]) -> DataFrame:
        """Return a dataframe with nulls filled."""

        if isinstance(value, Mapping):
            data = OrderedDict(
                (name, series.fill_null(value[name]) if name in value else series)
                for name, series in self._data.items()
            )
        else:
            data = OrderedDict((name, series.fill_null(value)) for name, series in self._data.items())
        return DataFrame(data, index=self._index)

    def drop_nulls(self, subset: Sequence[str] | None = None) -> DataFrame:
        """Return rows without nulls in the selected subset."""

        columns = list(subset) if subset is not None else self.columns
        for column in columns:
            self._require_column(column)
        positions = [idx for idx in range(self.height) if all(not is_null(self._data[column][idx]) for column in columns)]
        return self._take_positions(positions)

    def unique(self) -> DataFrame:
        """Return unique rows in first-seen order."""

        rows = self.to_rows(null_as_none=False)
        seen: list[dict[str, Any]] = []
        positions: list[int] = []
        for position, row in enumerate(rows):
            if row not in seen:
                seen.append(row)
                positions.append(position)
        return self._take_positions(positions)

    def value_counts(self, column: str | Sequence[str]) -> DataFrame:
        """Return counts for one or more columns."""

        columns = [column] if isinstance(column, str) else list(column)
        for name in columns:
            self._require_column(name)
        counts: OrderedDict[tuple[Any, ...], int] = OrderedDict()
        for idx in range(self.height):
            key = tuple(self._data[name][idx] for name in columns)
            counts[key] = counts.get(key, 0) + 1
        out: OrderedDict[str, list[Any]] = OrderedDict((name, []) for name in columns)
        out["count"] = []
        for key, count in counts.items():
            for name, value in zip(columns, key, strict=True):
                out[name].append(value)
            out["count"].append(count)
        return DataFrame(out)

    def describe(self) -> DataFrame:
        """Return summary statistics for numeric columns."""

        stats = ["count", "mean", "std", "min", "median", "max"]
        out: OrderedDict[str, list[Any]] = OrderedDict({"statistic": stats})
        for name, series in self._data.items():
            if is_numeric_dtype(series.dtype):
                out[name] = [series.count(), series.mean(), series.std(), series.min(), series.median(), series.max()]
        return DataFrame(out)

    def to_dict(self, *, null_as_none: bool = False) -> dict[str, list[Any]]:
        """Return a column-oriented dictionary."""

        return {name: series.to_list(null_as_none=null_as_none) for name, series in self._data.items()}

    def to_rows(self, *, null_as_none: bool = False) -> list[dict[str, Any]]:
        """Return row-oriented dictionaries."""

        rows: list[dict[str, Any]] = []
        for idx in range(self.height):
            row: dict[str, Any] = {}
            for name, series in self._data.items():
                value = series[idx]
                row[name] = materialize_null(value) if null_as_none else value
            rows.append(row)
        return rows

    def head(self, n: int = 5) -> DataFrame:
        """Return the first *n* rows."""

        return self._take_positions(list(range(max(0, min(n, self.height)))))

    def tail(self, n: int = 5) -> DataFrame:
        """Return the last *n* rows."""

        n = max(0, min(n, self.height))
        return self._take_positions(list(range(self.height - n, self.height)))

    def copy(self) -> DataFrame:
        """Return a copy of this dataframe."""

        return DataFrame(OrderedDict((name, series.copy()) for name, series in self._data.items()), index=self._index)

    def sample(self, n: int | None = None, *, fraction: float | None = None, seed: int | None = None) -> DataFrame:
        """Return a random row sample."""

        if n is None:
            if fraction is None:
                n = 1
            else:
                n = round(self.height * fraction)
        if n < 0 or n > self.height:
            raise ShapeError(f"Sample size must be between 0 and {self.height}.")
        rng = random.Random(seed)
        return self._take_positions(rng.sample(range(self.height), n))

    def group_by(self, *columns: str) -> Any:
        """Return a group-by object."""

        from .groupby import GroupBy

        return GroupBy(self, list(columns))

    def join(
        self,
        other: DataFrame,
        *,
        on: str | Sequence[str] | None = None,
        how: str = "inner",
        suffix: str = "_right",
    ) -> DataFrame:
        """Join this dataframe with another dataframe."""

        from .joins import join

        return join(self, other, on=on, how=how, suffix=suffix)

    def concat(self, others: Sequence[DataFrame]) -> DataFrame:
        """Concatenate this dataframe with other dataframes."""

        from .reshape import concat

        return concat([self, *others])

    def pivot(self, *, index: str, columns: str, values: str) -> DataFrame:
        """Pivot long data into a wide dataframe."""

        from .reshape import pivot

        return pivot(self, index=index, columns=columns, values=values)

    def melt(self, *, id_vars: Sequence[str], value_vars: Sequence[str], var_name: str = "variable", value_name: str = "value") -> DataFrame:
        """Unpivot columns into rows."""

        from .reshape import melt

        return melt(self, id_vars=id_vars, value_vars=value_vars, var_name=var_name, value_name=value_name)

    def explode(self, column: str) -> DataFrame:
        """Explode list values in a column."""

        from .reshape import explode

        return explode(self, column)

    def stack(self) -> DataFrame:
        """Stack columns into row, variable, and value columns."""

        from .reshape import stack

        return stack(self)

    def unstack(self, *, row: str = "row", variable: str = "variable", value: str = "value") -> DataFrame:
        """Unstack the simplified representation produced by stack()."""

        from .reshape import unstack

        return unstack(self, row=row, variable=variable, value=value)

    def lazy(self) -> Any:
        """Return a lazy dataframe wrapper."""

        from .lazy import LazyFrame

        return LazyFrame(self)

    def reset_index(self, *, name: str | None = None) -> DataFrame:
        """Return a dataframe with the explicit index materialized as a column."""

        output_name = name or self._index.name or "index"
        if output_name in self.columns:
            raise DuplicateColumnError(f"Column {output_name!r} already exists.")
        data: OrderedDict[str, Iterable[Any]] = OrderedDict()
        data[output_name] = self._index.to_list()
        for column_name, series in self._data.items():
            data[column_name] = series
        return DataFrame(data)

    def set_index(self, column: str) -> DataFrame:
        """Return a dataframe whose explicit index is taken from *column*."""

        self._require_column(column)
        data = OrderedDict((name, series) for name, series in self._data.items() if name != column)
        return DataFrame(data, index=Index(self._data[column].to_list(), name=column))

    def to_pandas(self) -> Any:
        """Convert to a pandas DataFrame. Pandas is optional."""

        from .interop import to_pandas

        return to_pandas(self)

    def to_arrow(self) -> Any:
        """Convert to a PyArrow Table. PyArrow is optional."""

        from .interop import to_arrow

        return to_arrow(self)

    def to_numpy(self) -> Any:
        """Convert to a NumPy array. NumPy is optional."""

        from .interop import to_numpy

        return to_numpy(self)

    def _take_positions(self, positions: Sequence[int]) -> DataFrame:
        data = OrderedDict((name, Series._from_data([series[position] for position in positions], name=name, dtype=series.dtype)) for name, series in self._data.items())
        index = Index([self._index[position] for position in positions], name=self._index.name)
        return DataFrame(data, index=index)

    def _require_column(self, column: str) -> None:
        if column not in self._data:
            raise ColumnNotFoundError(column, self.columns)

    def _coerce_column(self, values: Series | Expr | Iterable[Any] | Any, name: str) -> Series:
        if isinstance(values, Expr):
            series = values.evaluate(self)
        elif isinstance(values, Series):
            series = values
        elif _is_non_string_iterable(values):
            series = Series(values, name=name)
        else:
            series = Series([values] * self.height, name=name)
        if len(series) != self.height:
            if self.width == 0 and self.height == 0:
                return series.rename(name)
            raise ShapeError(
                f"Column {name!r} length {len(series)} does not match dataframe height {self.height}."
            )
        return series.rename(name)

    def _index_for_new_columns(self, columns: Iterable[Series]) -> Index | None:
        if self.width == 0 and self.height == 0 and any(len(column) > 0 for column in columns):
            return None
        return self._index


def _normalize_input(
    data: Mapping[str, Iterable[Any]] | Sequence[Mapping[str, Any]],
) -> tuple[OrderedDict[str, list[Any] | Series], int | None]:
    if isinstance(data, Mapping):
        columns: OrderedDict[str, list[Any] | Series] = OrderedDict()
        for name, values in data.items():
            _validate_column_name(name)
            if isinstance(values, Series):
                columns[name] = values
                continue
            if not _is_non_string_iterable(values):
                raise ShapeError(
                    f"Column {name!r} must be an iterable of values, got {type(values).__name__}.\n\n"
                    "Suggested fix:\nWrap scalar values in a list or use DataFrame.assign() for broadcasting."
                )
            columns[name] = [normalize_null(value) for value in values]
        return columns, None
    if isinstance(data, (str, bytes)) or not isinstance(data, Sequence):
        raise SchemaError(
            f"DataFrame() expects a mapping of columns or a sequence of row mappings, got {type(data).__name__}."
        )
    rows = list(data)
    names: list[str] = []
    for position, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise SchemaError(
                f"Row {position} must be a mapping of column names to values, got {type(row).__name__}."
            )
        for name in row:
            _validate_column_name(name)
            if name not in names:
                names.append(name)
    return OrderedDict((name, [normalize_null(row.get(name, NULL)) for row in rows]) for name in names), len(rows)


def _is_non_string_iterable(value: Any) -> bool:
    return isinstance(value, Iterable) and not isinstance(value, (str, bytes, dict))


def _validate_column_name(name: Any) -> None:
    if not isinstance(name, str):
        raise SchemaError(
            f"Column names must be strings, got {type(name).__name__}.\n\n"
            "Suggested fix:\nUse explicit string column names such as 'customer_id'."
        )
