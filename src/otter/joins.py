"""Join algorithms for Otter dataframes."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Sequence
from typing import Any

from .errors import ColumnNotFoundError, JoinError
from .nulls import NULL, is_null


def join(left: Any, right: Any, *, on: str | Sequence[str] | None = None, how: str = "inner", suffix: str = "_right") -> Any:
    """Join two dataframes."""

    from .dataframe import DataFrame

    how = how.lower()
    if how not in {"inner", "left", "right", "outer", "cross", "semi", "anti"}:
        raise JoinError("Join how must be one of: inner, left, right, outer, cross, semi, anti.")
    if how == "cross":
        keys: list[str] = []
    else:
        if on is None:
            raise JoinError("Join key 'on' is required unless how='cross'.")
        keys = [on] if isinstance(on, str) else list(on)
        for key in keys:
            if key not in left.columns:
                raise ColumnNotFoundError(key, left.columns)
            if key not in right.columns:
                raise ColumnNotFoundError(key, right.columns)
    if how in {"semi", "anti"}:
        matched_left = _matched_left_positions(left, right, keys)
        keep = matched_left if how == "semi" else [idx for idx in range(left.height) if idx not in set(matched_left)]
        return left._take_positions(keep)
    pairs: list[tuple[int | None, int | None]]
    if how == "cross":
        pairs = [(i, j) for i in range(left.height) for j in range(right.height)]
    else:
        pairs = _join_pairs(left, right, keys, how)
    right_output = [column for column in right.columns if column not in keys]
    output_names = _output_names(left.columns, right_output, suffix)
    out: OrderedDict[str, list[Any]] = OrderedDict((name, []) for name in output_names)
    for left_idx, right_idx in pairs:
        for column in left.columns:
            if left_idx is None and column in keys and right_idx is not None:
                out[column].append(right[column][right_idx])
            else:
                out[column].append(NULL if left_idx is None else left[column][left_idx])
        for column in right_output:
            name = column if column not in left.columns else f"{column}{suffix}"
            out[name].append(NULL if right_idx is None else right[column][right_idx])
    return DataFrame(out)


def _key(df: Any, row: int, keys: Sequence[str]) -> tuple[Any, ...] | None:
    values = tuple(df[key][row] for key in keys)
    if any(is_null(value) for value in values):
        return None
    return values


def _right_index(right: Any, keys: Sequence[str]) -> OrderedDict[tuple[Any, ...], list[int]]:
    index: OrderedDict[tuple[Any, ...], list[int]] = OrderedDict()
    for row in range(right.height):
        key = _key(right, row, keys)
        if key is not None:
            index.setdefault(key, []).append(row)
    return index


def _join_pairs(left: Any, right: Any, keys: Sequence[str], how: str) -> list[tuple[int | None, int | None]]:
    index = _right_index(right, keys)
    pairs: list[tuple[int | None, int | None]] = []
    matched_right: set[int] = set()
    for left_idx in range(left.height):
        key = _key(left, left_idx, keys)
        matches = index.get(key, []) if key is not None else []
        if matches:
            for right_idx in matches:
                pairs.append((left_idx, right_idx))
                matched_right.add(right_idx)
        elif how in {"left", "outer"}:
            pairs.append((left_idx, None))
    if how in {"right", "outer"}:
        for right_idx in range(right.height):
            if right_idx not in matched_right:
                pairs.append((None, right_idx))
    return pairs


def _matched_left_positions(left: Any, right: Any, keys: Sequence[str]) -> list[int]:
    index = _right_index(right, keys)
    return [left_idx for left_idx in range(left.height) if _key(left, left_idx, keys) in index]


def _output_names(left_columns: Sequence[str], right_columns: Sequence[str], suffix: str) -> list[str]:
    names = list(left_columns)
    for column in right_columns:
        name = column if column not in names else f"{column}{suffix}"
        if name in names:
            raise JoinError(f"Join output would contain duplicate column {name!r}.")
        names.append(name)
    return names
