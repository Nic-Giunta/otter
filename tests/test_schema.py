from __future__ import annotations

import pytest

import otter as ot


def test_schema_validation_and_equality() -> None:
    schema = ot.Schema([ot.Field("a", ot.Int64)])
    schema.validate_columns(["a"])
    ot.assert_schema_equal(schema, ot.Schema({"a": ot.Int64}))
    with pytest.raises(ot.SchemaError):
        schema.validate_columns(["b"])


def test_duplicate_schema_rejected() -> None:
    with pytest.raises(ot.DuplicateColumnError):
        ot.Schema([ot.Field("a", ot.Int64), ot.Field("a", ot.String)])
