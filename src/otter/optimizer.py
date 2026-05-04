"""Logical plan and optimizer foundations for Otter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .expressions import Expr, and_


@dataclass(frozen=True)
class Operation:
    """One logical dataframe operation."""

    name: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] | None = None

    def display(self) -> str:
        """Return a stable human-readable representation."""

        kwargs = self.kwargs or {}
        args_text = ", ".join(repr(arg) for arg in self.args)
        kwargs_text = ", ".join(f"{key}={value!r}" for key, value in kwargs.items())
        joined = ", ".join(part for part in (args_text, kwargs_text) if part)
        return f"{self.name}({joined})"


@dataclass(frozen=True)
class LogicalPlan:
    """A simple immutable logical plan."""

    source_description: str
    operations: tuple[Operation, ...] = ()

    def add(self, operation: Operation) -> LogicalPlan:
        """Return a plan with an appended operation."""

        return LogicalPlan(self.source_description, (*self.operations, operation))

    def explain(self) -> str:
        """Return a textual explanation."""

        lines = [f"SOURCE {self.source_description}"]
        lines.extend(f"  -> {operation.display()}" for operation in self.operations)
        return "\n".join(lines)


class Optimizer:
    """Basic optimizer with no-op removal and filter combination."""

    def optimize(self, plan: LogicalPlan) -> LogicalPlan:
        """Return an optimized logical plan."""

        operations = self._remove_noops(list(plan.operations))
        operations = self._combine_filters(operations)
        return LogicalPlan(plan.source_description, tuple(operations))

    def _remove_noops(self, operations: list[Operation]) -> list[Operation]:
        result: list[Operation] = []
        for operation in operations:
            if operation.name == "drop" and not operation.args:
                continue
            if operation.name == "rename" and operation.args and not operation.args[0]:
                continue
            if operation.name == "with_columns" and operation.args and not operation.args[0]:
                continue
            result.append(operation)
        return result

    def _combine_filters(self, operations: list[Operation]) -> list[Operation]:
        result: list[Operation] = []
        pending: Expr | None = None
        for operation in operations:
            if operation.name == "filter" and operation.args and isinstance(operation.args[0], Expr):
                expr = operation.args[0]
                pending = expr if pending is None else and_(pending, expr)
                continue
            if pending is not None:
                result.append(Operation("filter", (pending,)))
                pending = None
            result.append(operation)
        if pending is not None:
            result.append(Operation("filter", (pending,)))
        return result


DEFAULT_OPTIMIZER = Optimizer()
