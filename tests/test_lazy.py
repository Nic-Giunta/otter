from __future__ import annotations

import otter as ot


def test_lazy_select_filter_with_column_collect_explain() -> None:
    df = ot.DataFrame({"name": ["Ada", "Grace", "Linus"], "age": [36, 85, 54]})
    out = df.lazy().with_column("age2", ot.col("age") + 2).filter(ot.col("age") >= 40).select("name", "age2").collect()
    assert out.to_dict() == {"name": ["Grace", "Linus"], "age2": [87, 56]}
    explain = df.lazy().select("name").filter(ot.col("age") >= 40).explain()
    assert "Optimized Logical Plan" in explain
    assert "filter" in explain


def test_lazy_groupby_join_and_rename_drop() -> None:
    df = ot.DataFrame({"id": [1, 2], "g": ["a", "a"], "x": [1, 2]})
    grouped = df.lazy().group_by("g").agg({"x": "sum"}).collect()
    assert grouped.to_dict()["x"] == [3]
    joined = df.lazy().drop().rename({}).join(ot.DataFrame({"id": [2], "y": [3]}), on="id", how="inner").collect()
    assert joined.to_dict()["y"] == [3]
