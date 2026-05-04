"""Group-by implementation for Otter."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Mapping, Sequence
from typing import Any

from .compute import aggregate
from .errors import GroupByError

_ALLOWED_AGGS = {"sum", "mean", "median", "min", "max", "count", "std", "var"}


class GroupBy:
    """Group rows by one or more key columns and aggregate value columns."""

    def __init__(self, df: Any, keys: Sequence[str]) -> None:
        if not keys:
            raise GroupByError("group_by() requires at least one key column.")
        self.df = df
        self.keys = list(keys)
        for key in self.keys:
            if key not in df.columns:
                from .errors import ColumnNotFoundError

                raise ColumnNotFoundError(key, df.columns)

    def agg(self, aggregations: Mapping[str, str | Sequence[str]]) -> Any:
        """Aggregate grouped rows using named operations."""

        from .dataframe import DataFrame

        if not isinstance(aggregations, Mapping):
            raise GroupByError(
                f"agg() expects a mapping of column names to aggregation names, got {type(aggregations).__name__}."
            )
        normalized_specs: list[tuple[str, str]] = []
        for column, agg_spec in aggregations.items():
            if column not in self.df.columns:
                from .errors import ColumnNotFoundError

                raise ColumnNotFoundError(column, self.df.columns)
            specs = [agg_spec] if isinstance(agg_spec, str) else list(agg_spec)
            for spec in specs:
                if spec not in _ALLOWED_AGGS:
                    raise GroupByError(
                        f"Aggregation {spec!r} is not supported.\n\n"
                        "Suggested fix:\nUse one of: sum, mean, median, min, max, count, std, var."
                    )
                normalized_specs.append((column, spec))
        normalized: list[tuple[str, str, str]] = []
        planned_names: set[str] = set(self.keys)
        for column, spec in normalized_specs:
            out_name = column if len(normalized_specs) == 1 and spec != "count" else f"{column}_{spec}"
            if out_name in planned_names:
                out_name = f"{out_name}_value"
            while out_name in planned_names:
                out_name = f"{out_name}_value"
            planned_names.add(out_name)
            normalized.append((column, spec, out_name))
        groups: OrderedDict[tuple[Any, ...], list[int]] = OrderedDict()
        key_columns = [self.df._data[key] for key in self.keys]
        for row_idx in range(self.df.height):
            key = tuple(column[row_idx] for column in key_columns)
            groups.setdefault(key, []).append(row_idx)
        out: OrderedDict[str, list[Any]] = OrderedDict((key, []) for key in self.keys)
        for _, _, out_name in normalized:
            out[out_name] = []
        for key, positions in groups.items():
            for name, value in zip(self.keys, key, strict=True):
                out[name].append(value)
            for column, spec, out_name in normalized:
                source = self.df._data[column]
                values = [source[idx] for idx in positions]
                out[out_name].append(aggregate(values, spec))
        return DataFrame(out)
