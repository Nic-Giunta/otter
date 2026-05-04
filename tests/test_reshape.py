from __future__ import annotations

import otter as ot
from otter.reshape import stack, unstack


def test_concat_pivot_melt_explode_stack_unstack() -> None:
    df = ot.DataFrame({"country": ["US", "US"], "year": [2023, 2024], "revenue": [10, 12]})
    assert df.concat([df]).height == 4
    pivoted = df.pivot(index="country", columns="year", values="revenue")
    assert pivoted.columns == ["country", "2023", "2024"]
    melted = ot.DataFrame({"country": ["US"], "sales": [10], "profit": [2]}).melt(
        id_vars=["country"], value_vars=["sales", "profit"]
    )
    assert melted.height == 2
    exploded = ot.DataFrame({"id": [1, 2], "items": [["a", "b"], []]}).explode("items")
    assert exploded.to_dict()["items"] == ["a", "b", ot.NULL]
    stacked = stack(ot.DataFrame({"a": [1], "b": [2]}))
    assert unstack(stacked).columns == ["row", "a", "b"]
