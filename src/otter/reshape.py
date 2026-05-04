"""Reshaping operations for Otter dataframes."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Sequence
from typing import Any

from .errors import ColumnNotFoundError, DuplicateColumnError, ReshapeError
from .nulls import NULL, is_null


def concat(frames: Sequence[Any]) -> Any:
    """Concatenate dataframes vertically."""

    from .dataframe import DataFrame

    if not frames:
        return DataFrame({})
    columns = frames[0].columns
    for frame in frames:
        if frame.columns != columns:
            raise ReshapeError(
                f"concat() requires identical ordered columns. Expected {columns!r}, got {frame.columns!r}."
            )
    out: OrderedDict[str, list[Any]] = OrderedDict((column, []) for column in columns)
    for frame in frames:
        for column in columns:
            out[column].extend(frame._data[column].to_list())
    return DataFrame(out)


def pivot(df: Any, *, index: str, columns: str, values: str) -> Any:
    """Pivot long data into wide form."""

    from .dataframe import DataFrame

    for name in (index, columns, values):
        if name not in df.columns:
            raise ColumnNotFoundError(name, df.columns)
    index_values: list[Any] = []
    column_values: list[Any] = []
    cells: dict[tuple[Any, Any], Any] = {}
    for row in range(df.height):
        idx_value = df._data[index][row]
        col_value = df._data[columns][row]
        key = (idx_value, col_value)
        if key in cells:
            raise ReshapeError("pivot() found duplicate index/column pairs. Aggregate before pivoting.")
        cells[key] = df._data[values][row]
        if idx_value not in index_values:
            index_values.append(idx_value)
        if col_value not in column_values:
            column_values.append(col_value)
    out: OrderedDict[str, list[Any]] = OrderedDict([(index, index_values)])
    for col_value in column_values:
        name = str(col_value)
        if name in out:
            raise DuplicateColumnError(f"Pivot would create duplicate column {name!r}.")
        out[name] = [cells.get((idx_value, col_value), NULL) for idx_value in index_values]
    return DataFrame(out)


def melt(
    df: Any,
    *,
    id_vars: Sequence[str],
    value_vars: Sequence[str],
    var_name: str = "variable",
    value_name: str = "value",
) -> Any:
    """Unpivot selected columns into variable/value rows."""

    from .dataframe import DataFrame

    for name in [*id_vars, *value_vars]:
        if name not in df.columns:
            raise ColumnNotFoundError(name, df.columns)
    if var_name in id_vars or value_name in id_vars or var_name == value_name:
        raise DuplicateColumnError("Melt output column names must not collide with id variables.")
    out: OrderedDict[str, list[Any]] = OrderedDict((name, []) for name in id_vars)
    out[var_name] = []
    out[value_name] = []
    for row in range(df.height):
        for value_column in value_vars:
            for id_column in id_vars:
                out[id_column].append(df._data[id_column][row])
            out[var_name].append(value_column)
            out[value_name].append(df._data[value_column][row])
    return DataFrame(out)


def explode(df: Any, column: str) -> Any:
    """Explode list values into multiple rows."""

    from .dataframe import DataFrame

    if column not in df.columns:
        raise ColumnNotFoundError(column, df.columns)
    out: OrderedDict[str, list[Any]] = OrderedDict((name, []) for name in df.columns)
    for row in range(df.height):
        value = df._data[column][row]
        items = [NULL] if is_null(value) else value
        if not isinstance(items, list):
            raise ReshapeError(f"Column {column!r} contains non-list value {value!r} at row {row}.")
        if not items:
            items = [NULL]
        for item in items:
            for name in df.columns:
                out[name].append(item if name == column else df._data[name][row])
    return DataFrame(out)


def stack(df: Any) -> Any:
    """Return a simple stacked representation with row, variable, and value columns."""

    from .dataframe import DataFrame

    out: dict[str, list[Any]] = {"row": [], "variable": [], "value": []}
    for row in range(df.height):
        for column in df.columns:
            out["row"].append(row)
            out["variable"].append(column)
            out["value"].append(df._data[column][row])
    return DataFrame(out)


def unstack(df: Any, *, row: str = "row", variable: str = "variable", value: str = "value") -> Any:
    """Unstack the simplified output produced by stack()."""

    return pivot(df, index=row, columns=variable, values=value)
