from __future__ import annotations

import datetime as dt

import pytest
from hypothesis import given
from hypothesis import strategies as st

import otter as ot


def test_dataframe_constructor_validation_and_empty_row_model() -> None:
    with pytest.raises(ot.SchemaError, match="expects a mapping"):
        ot.DataFrame("not rows")  # type: ignore[arg-type]
    with pytest.raises(ot.SchemaError, match="Column names must be strings"):
        ot.DataFrame({1: [1]})  # type: ignore[dict-item]
    with pytest.raises(ot.ShapeError, match="must be an iterable"):
        ot.DataFrame({"a": 1})  # type: ignore[dict-item]
    with pytest.raises(ot.SchemaError, match="Row 0 must be a mapping"):
        ot.DataFrame([1])  # type: ignore[list-item]

    empty = ot.DataFrame({})
    assert empty.shape == (0, 0)
    row_only = ot.DataFrame([{}, {}])
    assert row_only.shape == (2, 0)
    assert row_only.to_rows() == [{}, {}]

    df = ot.DataFrame({"a": [1, 2]})
    assert df.drop("a").shape == (2, 0)
    assert df.select().shape == (2, 0)


def test_series_constructor_casts_declared_dtype_and_reports_bad_positions() -> None:
    assert ot.Series([1, 2], dtype=ot.Float64).to_list() == [1.0, 2.0]
    with pytest.raises(ot.CastError, match="target dtype Int64"):
        ot.Series(["x"], dtype=ot.Int64)
    with pytest.raises(ot.RowSelectionError, match="out of bounds"):
        _ = ot.Series([1])[5]
    with pytest.raises(ot.RowSelectionError, match="integers or slices"):
        _ = ot.Series([1])[True]


def test_string_and_datetime_helpers_reject_wrong_values_clearly() -> None:
    with pytest.raises(ot.DTypeError, match="String helper expected str"):
        ot.Series(["a", 1]).str_upper()
    with pytest.raises(ot.DTypeError, match="Datetime helper expected"):
        ot.Series([dt.date(2024, 1, 1), "bad"]).dt_year()


def test_dataframe_with_columns_validates_before_result_and_sort_null_placement() -> None:
    df = ot.DataFrame({"a": [1, 2]})
    with pytest.raises(ot.ShapeError, match="length 1"):
        df.with_columns({"b": [1], "c": [1, 2]})
    assert df.columns == ["a"]

    sortable = ot.DataFrame({"a": [1, None, 3, 2]})
    assert sortable.sort("a", ascending=False)["a"].to_list() == [3, 2, 1, ot.NULL]
    assert sortable.sort("a", nulls_last=False)["a"].to_list() == [ot.NULL, 1, 2, 3]


def test_groupby_collision_and_lazy_filter_combination_preserves_null_rejection_semantics() -> None:
    grouped = ot.DataFrame({"g": ["a", "a"], "x": [1, 2]}).group_by("g").agg({"g": "count"})
    assert grouped.columns == ["g", "g_count"]
    assert grouped.to_dict()["g_count"] == [2]

    df = ot.DataFrame({"x": [0, 1], "y": [None, 2]})
    eager = df.filter(ot.col("x") > 0).filter(ot.col("y") > 0)
    lazy = df.lazy().filter(ot.col("x") > 0).filter(ot.col("y") > 0).collect()
    assert lazy.to_dict() == eager.to_dict()


def test_window_min_periods_and_numeric_validation() -> None:
    s = ot.Series([1, None, 3])
    assert s.rolling(2, min_periods=1).sum().to_list() == [1, 1, 3]
    assert s.expanding(min_periods=2).mean().to_list() == [ot.NULL, ot.NULL, 2]
    with pytest.raises(ot.AggregationError, match="requires numeric"):
        ot.Series(["a"]).sum()
    with pytest.raises(ot.WindowError, match="numeric values"):
        ot.Series(["a"]).rolling(1).sum()


def test_csv_duplicate_header_is_data_source_error(tmp_path) -> None:
    path = tmp_path / "duplicate.csv"
    path.write_text("a,a\n1,2\n", encoding="utf-8")
    with pytest.raises(ot.DataSourceError, match="duplicate column names"):
        ot.read_csv(path)

    json_path = tmp_path / "duplicate.json"
    json_path.write_text('[{"a": 1, "a": 2}]', encoding="utf-8")
    with pytest.raises(ot.DataSourceError, match="duplicate keys"):
        ot.read_json(json_path)


@given(st.lists(st.one_of(st.none(), st.integers(), st.floats(allow_nan=True, allow_infinity=False))))
def test_null_normalization_property(values: list[object]) -> None:
    series = ot.Series(values)
    assert all(value is ot.NULL for raw, value in zip(values, series, strict=True) if ot.is_null(raw))


@given(st.lists(st.integers(), max_size=20), st.lists(st.integers(), max_size=20))
def test_concat_row_count_property(left_values: list[int], right_values: list[int]) -> None:
    left = ot.DataFrame({"x": left_values})
    right = ot.DataFrame({"x": right_values})
    assert ot.concat([left, right]).height == len(left_values) + len(right_values)
