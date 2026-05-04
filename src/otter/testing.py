"""Testing utilities for Otter users and maintainers."""

from __future__ import annotations

from typing import Any


def assert_series_equal(left: Any, right: Any) -> None:
    """Assert that two series are equal in values, name, and dtype."""

    assert left.name == right.name
    assert left.dtype == right.dtype
    assert left.to_list() == right.to_list()


def assert_frame_equal(left: Any, right: Any) -> None:
    """Assert that two dataframes are equal in columns, schema, and values."""

    assert left.columns == right.columns
    assert left.schema == right.schema
    assert left.to_dict() == right.to_dict()


def assert_schema_equal(left: Any, right: Any) -> None:
    """Assert that two schemas are equal."""

    assert left == right
