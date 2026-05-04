"""Optional interoperability with pandas, Arrow, and NumPy."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Sequence
from typing import Any

from .errors import BackendError, InteropError
from .nulls import normalize_null


def from_pandas(obj: Any) -> Any:
    """Create an Otter dataframe from a pandas DataFrame."""

    try:
        import pandas as pd  # type: ignore[import-not-found]
    except ImportError as exc:
        raise BackendError(
            "from_pandas() requires pandas, which is an optional dependency.\n\n"
            "Suggested fix:\nInstall Otter with the 'pandas' extra."
        ) from exc
    if not isinstance(obj, pd.DataFrame):
        raise InteropError("from_pandas() expects a pandas DataFrame.")
    from .dataframe import DataFrame

    return DataFrame(OrderedDict((str(column), [normalize_null(value) for value in obj[column].tolist()]) for column in obj.columns))


def to_pandas(df: Any) -> Any:
    """Convert an Otter dataframe to a pandas DataFrame."""

    try:
        import pandas as pd  # type: ignore[import-not-found]
    except ImportError as exc:
        raise BackendError(
            "DataFrame.to_pandas() requires pandas, which is an optional dependency.\n\n"
            "Suggested fix:\nInstall Otter with the 'pandas' extra."
        ) from exc
    return pd.DataFrame(df.to_dict(null_as_none=True))


def from_arrow(table: Any) -> Any:
    """Create an Otter dataframe from a PyArrow Table."""

    try:
        import pyarrow as pa  # type: ignore[import-not-found]
    except ImportError as exc:
        raise BackendError(
            "from_arrow() requires PyArrow, which is an optional dependency.\n\n"
            "Suggested fix:\nInstall Otter with the 'arrow' extra."
        ) from exc
    if not isinstance(table, pa.Table):
        raise InteropError("from_arrow() expects a pyarrow.Table.")
    from .dataframe import DataFrame

    return DataFrame([{str(key): normalize_null(value) for key, value in row.items()} for row in table.to_pylist()])


def to_arrow(df: Any) -> Any:
    """Convert an Otter dataframe to a PyArrow Table."""

    try:
        import pyarrow as pa  # type: ignore[import-not-found]
    except ImportError as exc:
        raise BackendError(
            "DataFrame.to_arrow() requires PyArrow, which is an optional dependency.\n\n"
            "Suggested fix:\nInstall Otter with the 'arrow' extra."
        ) from exc
    return pa.Table.from_pydict(df.to_dict(null_as_none=True))


def from_numpy(array: Any, *, columns: Sequence[str] | None = None) -> Any:
    """Create an Otter dataframe from a 2D NumPy array."""

    try:
        import numpy as np  # type: ignore[import-not-found]
    except ImportError as exc:
        raise BackendError(
            "from_numpy() requires NumPy, which is an optional dependency.\n\n"
            "Suggested fix:\nInstall Otter with the 'numpy' extra."
        ) from exc
    if not isinstance(array, np.ndarray):
        raise InteropError("from_numpy() expects a numpy.ndarray.")
    if array.ndim != 2:
        raise InteropError("from_numpy() expects a two-dimensional array.")
    width = int(array.shape[1])
    names = list(columns) if columns is not None else [f"column_{idx}" for idx in range(width)]
    if len(names) != width:
        raise InteropError(f"Expected {width} column names, got {len(names)}.")
    from .dataframe import DataFrame

    return DataFrame(OrderedDict((name, [normalize_null(value.item() if hasattr(value, "item") else value) for value in array[:, idx]]) for idx, name in enumerate(names)))


def to_numpy(df: Any) -> Any:
    """Convert an Otter dataframe to a NumPy array."""

    try:
        import numpy as np  # type: ignore[import-not-found]
    except ImportError as exc:
        raise BackendError(
            "DataFrame.to_numpy() requires NumPy, which is an optional dependency.\n\n"
            "Suggested fix:\nInstall Otter with the 'numpy' extra."
        ) from exc
    return np.array([[row[column] for column in df.columns] for row in df.to_rows(null_as_none=True)], dtype=object)
