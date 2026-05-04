from __future__ import annotations

import otter as ot


def test_groupby_aggregations() -> None:
    df = ot.DataFrame({"g": ["a", "a", "b"], "x": [1, 3, 5]})
    assert df.group_by("g").agg({"x": "sum"}).to_dict()["x"] == [4, 5]
    assert df.group_by("g").agg({"x": "mean"}).to_dict()["x"] == [2, 5]
    assert df.group_by("g").agg({"x": "median"}).to_dict()["x"] == [2.0, 5]
    assert df.group_by("g").agg({"x": "min"}).to_dict()["x"] == [1, 5]
    assert df.group_by("g").agg({"x": "max"}).to_dict()["x"] == [3, 5]
    assert df.group_by("g").agg({"x": "count"}).to_dict()["x_count"] == [2, 1]
    assert df.group_by("g").agg({"x": ["std", "var"]}).columns == ["g", "x_std", "x_var"]


def test_groupby_multiple_keys() -> None:
    df = ot.DataFrame({"a": ["x", "x", "x"], "b": [1, 1, 2], "v": [1, 2, 3]})
    out = df.group_by("a", "b").agg({"v": "sum"})
    assert out.to_dict()["v"] == [3, 3]
