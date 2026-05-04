from __future__ import annotations

import pytest

import otter as ot


def test_testing_helpers() -> None:
    ot.assert_series_equal(ot.Series([1], name="a"), ot.Series([1], name="a"))
    ot.assert_frame_equal(ot.DataFrame({"a": [1]}), ot.DataFrame({"a": [1]}))
    ot.assert_schema_equal(ot.Schema({"a": ot.Int64}), ot.Schema({"a": ot.Int64}))
    with pytest.raises(AssertionError):
        ot.assert_frame_equal(ot.DataFrame({"a": [1]}), ot.DataFrame({"a": [2]}))
