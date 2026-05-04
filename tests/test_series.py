from __future__ import annotations

import pytest

import otter as ot


def test_series_construction_indexing_slicing() -> None:
    s = ot.Series([1, None, 3], name="numbers")
    assert len(s) == 3
    assert s[0] == 1
    assert s[1] is ot.NULL
    assert s[:2].to_list() == [1, ot.NULL]


def test_series_comparisons_arithmetic_and_aggregations() -> None:
    s = ot.Series([1, 2, 3], name="n")
    assert (s + 1).to_list() == [2, 3, 4]
    assert (s >= 2).to_list() == [False, True, True]
    assert s.sum() == 6
    assert s.mean() == 2
    assert s.min() == 1
    assert s.max() == 3
    assert s.count() == 3
    assert s.median() == 2
    assert s.var() == 1
    assert s.std() == 1
    assert s.quantile(0.5) == 2


def test_series_cast_fill_drop_unique_value_counts_sort() -> None:
    s = ot.Series(["2", None, "1", "2"], name="v")
    assert s.cast(ot.Int64, strict=False).to_list() == [2, ot.NULL, 1, 2]
    assert s.fill_null("x").to_list() == ["2", "x", "1", "2"]
    assert s.drop_nulls().to_list() == ["2", "1", "2"]
    assert s.unique().to_list() == ["2", ot.NULL, "1"]
    assert s.value_counts().to_dict()["count"] == [2, 1, 1]
    assert ot.Series([2, None, 1]).sort().to_list() == [1, 2, ot.NULL]


def test_series_filter_and_invalid_mask() -> None:
    s = ot.Series([1, 2, 3])
    assert s.filter([True, False, True]).to_list() == [1, 3]
    with pytest.raises(ot.RowSelectionError):
        s.filter([True, ot.NULL, False])
