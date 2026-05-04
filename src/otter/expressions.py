"""Expression system for eager evaluation and lazy planning."""

from __future__ import annotations

import operator
from dataclasses import dataclass
from typing import Any, Callable

from .errors import ExpressionError
from .series import Series


@dataclass(frozen=True)
class Expr:
    """A dataframe expression that can be evaluated against a DataFrame."""

    kind: str
    value: Any = None
    left: Expr | None = None
    right: Expr | None = None
    func: Callable[..., Any] | None = None
    alias_name: str | None = None

    def __add__(self, other: Any) -> Expr:
        return _binary(self, other, "+", operator.add)

    def __radd__(self, other: Any) -> Expr:
        return _binary(_ensure_expr(other), self, "+", operator.add)

    def __sub__(self, other: Any) -> Expr:
        return _binary(self, other, "-", operator.sub)

    def __rsub__(self, other: Any) -> Expr:
        return _binary(_ensure_expr(other), self, "-", operator.sub)

    def __mul__(self, other: Any) -> Expr:
        return _binary(self, other, "*", operator.mul)

    def __rmul__(self, other: Any) -> Expr:
        return _binary(_ensure_expr(other), self, "*", operator.mul)

    def __truediv__(self, other: Any) -> Expr:
        return _binary(self, other, "/", operator.truediv)

    def __rtruediv__(self, other: Any) -> Expr:
        return _binary(_ensure_expr(other), self, "/", operator.truediv)

    def __floordiv__(self, other: Any) -> Expr:
        return _binary(self, other, "//", operator.floordiv)

    def __mod__(self, other: Any) -> Expr:
        return _binary(self, other, "%", operator.mod)

    def __pow__(self, other: Any) -> Expr:
        return _binary(self, other, "**", operator.pow)

    def __eq__(self, other: object) -> Expr:  # type: ignore[override]
        return _binary(self, other, "==", operator.eq)

    def __ne__(self, other: object) -> Expr:  # type: ignore[override]
        return _binary(self, other, "!=", operator.ne)

    def __gt__(self, other: Any) -> Expr:
        return _binary(self, other, ">", operator.gt)

    def __ge__(self, other: Any) -> Expr:
        return _binary(self, other, ">=", operator.ge)

    def __lt__(self, other: Any) -> Expr:
        return _binary(self, other, "<", operator.lt)

    def __le__(self, other: Any) -> Expr:
        return _binary(self, other, "<=", operator.le)

    def __and__(self, other: Any) -> Expr:
        return and_(self, _ensure_expr(other))

    def __or__(self, other: Any) -> Expr:
        return or_(self, _ensure_expr(other))

    def __invert__(self) -> Expr:
        return not_(self)

    def alias(self, name: str) -> Expr:
        """Return this expression with an output alias."""

        return Expr(self.kind, self.value, self.left, self.right, self.func, alias_name=name)

    def evaluate(self, df: Any) -> Series:
        """Evaluate this expression against a dataframe."""

        from .dataframe import DataFrame

        if not isinstance(df, DataFrame):
            raise ExpressionError("Expressions can only be evaluated against an Otter DataFrame.")
        if self.kind == "col":
            return df[str(self.value)]
        if self.kind == "lit":
            return Series([self.value] * df.height, name=self.alias_name)
        if self.kind == "binary":
            if self.left is None or self.right is None or self.func is None:
                raise ExpressionError("Binary expression is incomplete.")
            left_series = self.left.evaluate(df)
            right_series = self.right.evaluate(df)
            if self.value in {"==", "!=", ">", ">=", "<", "<="}:
                result = getattr(left_series, _COMPARE_METHODS[str(self.value)])(right_series)
            else:
                result = getattr(left_series, _ARITH_METHODS[str(self.value)])(right_series)
            return result.rename(self.alias_name)
        if self.kind == "boolean":
            if self.left is None or self.right is None or self.func is None:
                raise ExpressionError("Boolean expression is incomplete.")
            return self.func(self.left.evaluate(df), self.right.evaluate(df)).rename(self.alias_name)
        if self.kind == "not":
            if self.left is None:
                raise ExpressionError("Not expression is incomplete.")
            return (~self.left.evaluate(df)).rename(self.alias_name)
        raise ExpressionError(f"Unknown expression kind {self.kind!r}.")

    def output_name(self) -> str | None:
        """Return the expression output name when known."""

        if self.alias_name is not None:
            return self.alias_name
        if self.kind == "col":
            return str(self.value)
        return None

    def __repr__(self) -> str:
        if self.kind in {"col", "lit"}:
            text = f"{self.kind}({self.value!r})"
        elif self.kind == "not":
            text = f"not_({self.left!r})"
        else:
            text = f"({self.left!r} {self.value} {self.right!r})"
        if self.alias_name:
            text += f".alias({self.alias_name!r})"
        return text


_COMPARE_METHODS = {
    "==": "__eq__",
    "!=": "__ne__",
    ">": "__gt__",
    ">=": "__ge__",
    "<": "__lt__",
    "<=": "__le__",
}
_ARITH_METHODS = {
    "+": "__add__",
    "-": "__sub__",
    "*": "__mul__",
    "/": "__truediv__",
    "//": "__floordiv__",
    "%": "__mod__",
    "**": "__pow__",
}


def col(name: str) -> Expr:
    """Return a column expression."""

    return Expr("col", name)


def lit(value: Any) -> Expr:
    """Return a literal expression."""

    return Expr("lit", value)


def and_(*expressions: Expr) -> Expr:
    """Combine boolean expressions with logical AND."""

    if not expressions:
        raise ExpressionError("and_() requires at least one expression.")
    expr = expressions[0]
    for next_expr in expressions[1:]:
        expr = Expr("boolean", "AND", expr, next_expr, lambda a, b: a & b)
    return expr


def or_(*expressions: Expr) -> Expr:
    """Combine boolean expressions with logical OR."""

    if not expressions:
        raise ExpressionError("or_() requires at least one expression.")
    expr = expressions[0]
    for next_expr in expressions[1:]:
        expr = Expr("boolean", "OR", expr, next_expr, lambda a, b: a | b)
    return expr


def not_(expression: Expr) -> Expr:
    """Negate a boolean expression."""

    return Expr("not", "NOT", left=expression)


def _ensure_expr(value: Any) -> Expr:
    return value if isinstance(value, Expr) else lit(value)


def _binary(left: Expr, right: Any, symbol: str, func: Callable[[Any, Any], Any]) -> Expr:
    return Expr("binary", symbol, left, _ensure_expr(right), func)
