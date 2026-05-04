from __future__ import annotations

import pytest

import otter as ot


def test_dataframe_construction_and_properties() -> None:
    df = ot.DataFrame({"name": ["Ada", "Grace"], "age": [36, 85]})
    assert df.shape == (2, 2)
    assert df.height == 2
    assert df.width == 2
    assert df.columns == ["name", "age"]
    assert df.schema.names == ["name", "age"]
    assert df.index.to_list() == [0, 1]
    assert df.to_rows()[0]["name"] == "Ada"
    assert df.copy().to_dict() == df.to_dict()


def test_dataframe_rejects_unequal_lengths() -> None:
    with pytest.raises(ot.ShapeError):
        ot.DataFrame({"a": [1], "b": [1, 2]})


def test_dataframe_column_selection_and_multi_selection() -> None:
    df = ot.DataFrame({"name": ["Ada"], "age": [36]})
    assert df["name"].to_list() == ["Ada"]
    assert df[["name", "age"]].columns == ["name", "age"]
    assert df.select("age").to_dict() == {"age": [36]}
    with pytest.raises(ot.ColumnNotFoundError):
        df["missing"]


def test_dataframe_filter_where_sort_drop_rename() -> None:
    df = ot.DataFrame({"name": ["Ada", "Grace", "Linus"], "age": [36, 85, 54]})
    assert df.filter(df["age"] >= 40).to_dict()["name"] == ["Grace", "Linus"]
    assert df.where(ot.col("age") >= 40).height == 2
    assert df.sort("age").to_dict()["name"] == ["Ada", "Linus", "Grace"]
    assert df.drop("age").columns == ["name"]
    assert df.rename({"name": "person_name"}).columns == ["person_name", "age"]


def test_dataframe_mutating_style_methods_return_new_frames() -> None:
    df = ot.DataFrame({"age": [17, 18, None]})
    out = df.with_column("is_adult", df["age"] >= 18)
    assert df.columns == ["age"]
    assert out.columns == ["age", "is_adult"]
    assert df.with_columns({"age2": df["age"] + 2}).columns == ["age", "age2"]
    assert df.assign(age3=df["age"] + 3).columns == ["age", "age3"]


def test_dataframe_cast_fill_drop_nulls_unique_value_counts_describe_head_tail_sample() -> None:
    df = ot.DataFrame({"x": ["1", None, "2", "2"], "g": ["a", "a", "b", "b"]})
    assert df.cast({"x": ot.Int64}, strict=False)["x"].to_list() == [1, ot.NULL, 2, 2]
    assert df.fill_null({"x": "0"})["x"].to_list() == ["1", "0", "2", "2"]
    assert df.drop_nulls(["x"]).height == 3
    assert df.unique().height == 3
    assert df.value_counts("g").to_dict()["count"] == [2, 2]
    described = df.cast({"x": ot.Int64}, strict=False).describe()
    assert "x" in described.columns
    assert df.head(2).height == 2
    assert df.tail(1).to_dict()["x"] == ["2"]
    assert df.sample(2, seed=1).height == 2
