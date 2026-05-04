"""Lazy dataframe API for Otter."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .dtypes import DType
from .expressions import Expr
from .optimizer import DEFAULT_OPTIMIZER, LogicalPlan, Operation


class LazyFrame:
    """A lazy dataframe wrapper with a logical plan."""

    def __init__(self, df: Any, plan: LogicalPlan | None = None) -> None:
        self._df = df
        self._plan = plan or LogicalPlan(f"DataFrame(shape={df.shape})")

    def select(self, *columns: str | Expr) -> LazyFrame:
        """Add a select operation."""

        return self._append("select", *columns)

    def filter(self, mask: Expr | Any) -> LazyFrame:
        """Add a filter operation."""

        return self._append("filter", mask)

    def with_column(self, name: str, values: Expr | Any) -> LazyFrame:
        """Add a with_column operation."""

        return self._append("with_column", name, values)

    def with_columns(self, mapping: Mapping[str, Expr | Any]) -> LazyFrame:
        """Add a with_columns operation."""

        return self._append("with_columns", dict(mapping))

    def drop(self, *columns: str) -> LazyFrame:
        """Add a drop operation."""

        return self._append("drop", *columns)

    def rename(self, mapping: Mapping[str, str]) -> LazyFrame:
        """Add a rename operation."""

        return self._append("rename", dict(mapping))

    def sort(self, by: str | Sequence[str], *, reverse: bool = False) -> LazyFrame:
        """Add a sort operation."""

        return self._append("sort", by, reverse=reverse)

    def cast(self, mapping: Mapping[str, DType], *, strict: bool = True) -> LazyFrame:
        """Add a cast operation."""

        return self._append("cast", dict(mapping), strict=strict)

    def group_by(self, *columns: str) -> LazyGroupBy:
        """Return a lazy group-by object."""

        return LazyGroupBy(self, list(columns))

    def join(self, other: Any, *, on: str | Sequence[str] | None = None, how: str = "inner", suffix: str = "_right") -> LazyFrame:
        """Add a join operation."""

        return self._append("join", other, on=on, how=how, suffix=suffix)

    def collect(self) -> Any:
        """Optimize and execute the lazy plan eagerly."""

        plan = DEFAULT_OPTIMIZER.optimize(self._plan)
        df = self._df
        for operation in plan.operations:
            kwargs = operation.kwargs or {}
            if operation.name == "select":
                df = df.select(*operation.args)
            elif operation.name == "filter":
                df = df.filter(operation.args[0])
            elif operation.name == "with_column":
                df = df.with_column(operation.args[0], operation.args[1])
            elif operation.name == "with_columns":
                df = df.with_columns(operation.args[0])
            elif operation.name == "drop":
                df = df.drop(*operation.args)
            elif operation.name == "rename":
                df = df.rename(operation.args[0])
            elif operation.name == "sort":
                df = df.sort(operation.args[0], **kwargs)
            elif operation.name == "cast":
                df = df.cast(operation.args[0], **kwargs)
            elif operation.name == "join":
                df = df.join(operation.args[0], **kwargs)
            elif operation.name == "group_by_agg":
                df = df.group_by(*operation.args[0]).agg(operation.args[1])
        return df

    def explain(self, *, optimized: bool = True) -> str:
        """Return a textual logical plan."""

        plan = DEFAULT_OPTIMIZER.optimize(self._plan) if optimized else self._plan
        title = "Optimized Logical Plan" if optimized else "Logical Plan"
        return f"{title}\n{plan.explain()}"

    @property
    def logical_plan(self) -> LogicalPlan:
        """Return the unoptimized logical plan."""

        return self._plan

    def _append(self, name: str, *args: Any, **kwargs: Any) -> LazyFrame:
        return LazyFrame(self._df, self._plan.add(Operation(name, args, kwargs or None)))


class LazyGroupBy:
    """Lazy group-by builder."""

    def __init__(self, frame: LazyFrame, keys: list[str]) -> None:
        self._frame = frame
        self._keys = keys

    def agg(self, aggregations: Mapping[str, str | Sequence[str]]) -> LazyFrame:
        """Add group-by aggregation to the plan."""

        return self._frame._append("group_by_agg", self._keys, dict(aggregations))
