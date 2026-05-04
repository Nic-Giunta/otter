from __future__ import annotations

import otter as ot


def test_pandas_style_idioms_have_otter_equivalents() -> None:
    df = ot.DataFrame({"name": ["Ada", "Grace", "Linus"], "age": [36, 85, 54]})
    assert df[["name", "age"]].shape == (3, 2)
    assert df.filter(df["age"] >= 40).to_dict()["name"] == ["Grace", "Linus"]
    assert df.assign(is_adult=df["age"] >= 18).to_dict()["is_adult"] == [True, True, True]
