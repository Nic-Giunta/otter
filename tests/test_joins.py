from __future__ import annotations

import otter as ot


def test_joins_inner_left_right_outer() -> None:
    left = ot.DataFrame({"id": [1, 2], "x": ["a", "b"]})
    right = ot.DataFrame({"id": [2, 3], "y": ["c", "d"]})
    assert left.join(right, on="id", how="inner").to_dict() == {"id": [2], "x": ["b"], "y": ["c"]}
    assert left.join(right, on="id", how="left").to_dict()["y"] == [ot.NULL, "c"]
    assert left.join(right, on="id", how="right").to_dict()["id"] == [2, 3]
    assert left.join(right, on="id", how="outer").height == 3


def test_join_multi_key_suffix_semi_anti_cross() -> None:
    left = ot.DataFrame({"k1": [1, 1, 2], "k2": ["a", "b", "a"], "v": [10, 20, 30]})
    right = ot.DataFrame({"k1": [1], "k2": ["a"], "v": [99]})
    out = left.join(right, on=["k1", "k2"], how="inner")
    assert out.columns == ["k1", "k2", "v", "v_right"]
    assert left.join(right, on=["k1", "k2"], how="semi").height == 1
    assert left.join(right, on=["k1", "k2"], how="anti").height == 2
    assert left.join(right, how="cross").height == 3
