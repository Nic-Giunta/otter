from __future__ import annotations

import pytest

import otter as ot


def test_dtype_inference_and_helpers() -> None:
    assert ot.infer_dtype([1, 2, None]) == ot.Int64
    assert ot.infer_dtype([1, 2.5]) == ot.Float64
    assert ot.infer_dtype([True, False]) == ot.Boolean
    assert ot.infer_dtype(["a", None]) == ot.String
    assert ot.infer_dtype([None, ot.NULL]) == ot.Null
    assert ot.is_numeric_dtype(ot.Int64)
    assert ot.is_string_dtype(ot.String)


def test_casting_and_failed_casting() -> None:
    assert ot.cast_value("42", ot.Int64, strict=False) == 42
    assert ot.cast_values([1, None], ot.Float64) == [1.0, ot.NULL]
    with pytest.raises(ot.CastError):
        ot.cast_value("42", ot.Int64)
