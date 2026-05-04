"""Internal typing aliases for Otter."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any, TypeAlias

Scalar: TypeAlias = Any
ColumnName: TypeAlias = str
Row: TypeAlias = dict[str, Any]
DataMapping: TypeAlias = Mapping[str, Iterable[Any]]
ColumnSelection: TypeAlias = str | Sequence[str]
