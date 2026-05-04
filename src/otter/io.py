"""Input/output functions for Otter."""

from __future__ import annotations

import csv
import datetime as _dt
import json
from collections import OrderedDict
from pathlib import Path
from typing import Any

from .errors import BackendError, DataSourceError
from .nulls import NULL, normalize_null

_NULL_STRINGS = {"", "null", "NULL", "None", "NaN", "nan"}


def read_csv(path: str | Path) -> Any:
    """Read a CSV file using the Python standard library."""

    from .dataframe import DataFrame

    try:
        with Path(path).open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise DataSourceError("CSV file does not contain a header row.")
            data: OrderedDict[str, list[Any]] = OrderedDict((name, []) for name in reader.fieldnames)
            for row in reader:
                for name in data:
                    data[name].append(_parse_text_value(row.get(name)))
    except OSError as exc:
        raise DataSourceError(f"Could not read CSV file {path!s}: {exc}.") from exc
    return DataFrame(data)


def write_csv(df: Any, path: str | Path) -> None:
    """Write a dataframe to CSV using the Python standard library."""

    try:
        with Path(path).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=df.columns)
            writer.writeheader()
            for row in df.to_rows(null_as_none=True):
                writer.writerow(row)
    except OSError as exc:
        raise DataSourceError(f"Could not write CSV file {path!s}: {exc}.") from exc


def read_json(path: str | Path) -> Any:
    """Read records-oriented JSON from a file."""

    from .dataframe import DataFrame

    try:
        with Path(path).open(encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise DataSourceError(f"Could not read JSON file {path!s}: {exc}.") from exc
    if not isinstance(payload, list) or not all(isinstance(row, dict) for row in payload):
        raise DataSourceError("JSON input must be a list of objects in records orientation.")
    rows = [{str(key): normalize_null(value) for key, value in row.items()} for row in payload]
    return DataFrame(rows)


def write_json(df: Any, path: str | Path) -> None:
    """Write records-oriented JSON to a file."""

    try:
        with Path(path).open("w", encoding="utf-8") as handle:
            json.dump(df.to_rows(null_as_none=True), handle, indent=2, default=str)
    except OSError as exc:
        raise DataSourceError(f"Could not write JSON file {path!s}: {exc}.") from exc


def read_parquet(path: str | Path) -> Any:
    """Read Parquet using optional PyArrow."""

    try:
        import pyarrow.parquet as pq  # type: ignore[import-not-found]
    except ImportError as exc:
        raise BackendError(
            "read_parquet() requires the optional PyArrow dependency.\n\n"
            "Suggested fix:\nInstall Otter with the 'parquet' or 'arrow' extra."
        ) from exc
    from .interop import from_arrow

    return from_arrow(pq.read_table(path))


def write_parquet(df: Any, path: str | Path) -> None:
    """Write Parquet using optional PyArrow."""

    try:
        import pyarrow.parquet as pq  # type: ignore[import-not-found]
    except ImportError as exc:
        raise BackendError(
            "write_parquet() requires the optional PyArrow dependency.\n\n"
            "Suggested fix:\nInstall Otter with the 'parquet' or 'arrow' extra."
        ) from exc
    pq.write_table(df.to_arrow(), path)


def read_sql(query: str, connection: Any) -> Any:
    """Read SQL through a DB-API compatible connection or cursor."""

    from .dataframe import DataFrame

    try:
        cursor = connection.cursor() if hasattr(connection, "cursor") else connection
        cursor.execute(query)
        if cursor.description is None:
            raise DataSourceError("SQL query did not return a result set.")
        columns = [str(item[0]) for item in cursor.description]
        rows = cursor.fetchall()
    except Exception as exc:  # noqa: BLE001
        raise DataSourceError(f"Could not execute SQL query: {exc}.") from exc
    data: OrderedDict[str, list[Any]] = OrderedDict((name, []) for name in columns)
    for row in rows:
        for name, value in zip(columns, row, strict=True):
            data[name].append(normalize_null(value))
    return DataFrame(data)


def _parse_text_value(value: str | None) -> Any:
    if value is None or value in _NULL_STRINGS:
        return NULL
    text = value.strip()
    if text in _NULL_STRINGS:
        return NULL
    lowered = text.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        pass
    try:
        if "T" in text or " " in text:
            return _dt.datetime.fromisoformat(text)
        if len(text) == 10 and text[4] == "-" and text[7] == "-":
            return _dt.date.fromisoformat(text)
    except ValueError:
        pass
    return text
