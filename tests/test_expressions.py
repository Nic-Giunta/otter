from __future__ import annotations

import otter as ot


def test_expressions_evaluate_arithmetic_comparison_boolean_alias() -> None:
    df = ot.DataFrame({"age": [17, 18, 40], "name": ["A", "B", "C"]})
    expr = ((ot.col("age") + 1) >= 19).alias("ok")
    assert expr.evaluate(df).to_list() == [False, True, True]
    filtered = df.filter(ot.and_(ot.col("age") >= 18, ot.not_(ot.col("age") > 39)))
    assert filtered.to_dict()["name"] == ["B"]
    assert df.filter(ot.or_(ot.col("age") < 18, ot.col("age") > 39)).height == 2
    assert "col('age')" in repr(ot.col("age"))
