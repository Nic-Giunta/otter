"""Custom exceptions for Otter."""

from __future__ import annotations

from collections.abc import Sequence


class OtterError(Exception):
    """Base class for all public Otter exceptions."""


class SchemaError(OtterError):
    """Raised when a schema is invalid or data does not match a schema."""


class ColumnNotFoundError(OtterError):
    """Raised when a requested column does not exist."""

    def __init__(self, column: str, available: Sequence[str] | None = None) -> None:
        message = f"Column '{column}' does not exist."
        if available:
            message += "\n\nAvailable columns:\n" + "\n".join(f"- {name}" for name in available)
        message += "\n\nSuggested fix:\nCheck the column name or inspect df.columns."
        super().__init__(message)


class DuplicateColumnError(OtterError):
    """Raised when an operation would create duplicate column names."""


class DTypeError(OtterError):
    """Raised when dtype inference or validation fails."""


class CastError(DTypeError):
    """Raised when a value cannot be safely cast to the requested dtype."""


class NullValueError(OtterError):
    """Raised when a null value is used in an invalid context."""


class ShapeError(OtterError):
    """Raised when lengths or shapes are incompatible."""


class RowSelectionError(OtterError):
    """Raised when row selection masks or positions are invalid."""


class JoinError(OtterError):
    """Raised when a join request is invalid."""


class GroupByError(OtterError):
    """Raised when a group-by request is invalid."""


class ExpressionError(OtterError):
    """Raised when an expression cannot be built or evaluated."""


class LazyExecutionError(OtterError):
    """Raised when lazy execution fails."""


class BackendError(OtterError):
    """Raised when an optional backend is unavailable or fails."""


class DataSourceError(OtterError):
    """Raised when external data cannot be read or written."""


class IndexError(OtterError):
    """Raised when explicit row index operations are invalid."""


class ReshapeError(OtterError):
    """Raised when reshaping data fails."""


class WindowError(OtterError):
    """Raised when a window operation is invalid."""


class AggregationError(OtterError):
    """Raised when an aggregation cannot be performed."""


class InteropError(OtterError):
    """Raised when conversion to or from another library fails."""
