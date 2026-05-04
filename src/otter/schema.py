"""Schema representation for Otter dataframes."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass

from .dtypes import DType, infer_dtype
from .errors import DuplicateColumnError, SchemaError


@dataclass(frozen=True, slots=True)
class Field:
    """A named column and its logical dtype."""

    name: str
    dtype: DType
    nullable: bool = True


class Schema:
    """Ordered dataframe schema."""

    def __init__(self, fields: Iterable[Field] | Mapping[str, DType]) -> None:
        if isinstance(fields, Mapping):
            field_list = [Field(name, dtype) for name, dtype in fields.items()]
        else:
            field_list = list(fields)
        names = [field.name for field in field_list]
        if len(names) != len(set(names)):
            duplicates = sorted({name for name in names if names.count(name) > 1})
            raise DuplicateColumnError(f"Duplicate column names are not allowed: {duplicates}.")
        self._fields: OrderedDict[str, Field] = OrderedDict((field.name, field) for field in field_list)

    @classmethod
    def infer(cls, data: Mapping[str, list[object]]) -> Schema:
        """Infer a schema from column-oriented data."""

        return cls(Field(name, infer_dtype(values)) for name, values in data.items())

    def __iter__(self) -> Iterator[Field]:
        return iter(self._fields.values())

    def __len__(self) -> int:
        return len(self._fields)

    def __contains__(self, name: object) -> bool:
        return name in self._fields

    def __getitem__(self, name: str) -> Field:
        try:
            return self._fields[name]
        except KeyError as exc:
            raise SchemaError(f"Field {name!r} does not exist in the schema.") from exc

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Schema) and list(self._fields.values()) == list(other._fields.values())

    def __repr__(self) -> str:
        inner = ", ".join(f"{field.name}: {field.dtype}" for field in self)
        return f"Schema({inner})"

    @property
    def names(self) -> list[str]:
        """Return column names in order."""

        return list(self._fields.keys())

    @property
    def dtypes(self) -> dict[str, DType]:
        """Return an ordered mapping of column names to dtypes."""

        return {name: field.dtype for name, field in self._fields.items()}

    def to_dict(self) -> dict[str, str]:
        """Return a serializable schema dictionary."""

        return {name: str(field.dtype) for name, field in self._fields.items()}

    def validate_columns(self, columns: Iterable[str]) -> None:
        """Validate that column names match the schema exactly."""

        actual = list(columns)
        expected = self.names
        if actual != expected:
            raise SchemaError(
                f"Columns do not match schema. Expected {expected!r}, got {actual!r}."
            )
