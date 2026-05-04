from __future__ import annotations

import sqlite3

import pytest

import otter as ot


def test_csv_roundtrip(tmp_path) -> None:  # type: ignore[no-untyped-def]
    df = ot.DataFrame({"a": [1, None], "b": ["x", "y"]})
    path = tmp_path / "data.csv"
    ot.write_csv(df, path)
    out = ot.read_csv(path)
    assert out.to_dict() == {"a": [1, ot.NULL], "b": ["x", "y"]}


def test_json_roundtrip(tmp_path) -> None:  # type: ignore[no-untyped-def]
    df = ot.DataFrame({"a": [1, None], "b": ["x", "y"]})
    path = tmp_path / "data.json"
    ot.write_json(df, path)
    out = ot.read_json(path)
    assert out.to_dict() == {"a": [1, ot.NULL], "b": ["x", "y"]}


def test_parquet_optional_behavior(tmp_path) -> None:  # type: ignore[no-untyped-def]
    path = tmp_path / "data.parquet"
    try:
        import pyarrow  # noqa: F401
    except ImportError:
        with pytest.raises(ot.BackendError):
            ot.write_parquet(ot.DataFrame({"a": [1]}), path)
    else:
        df = ot.DataFrame({"a": [1]})
        ot.write_parquet(df, path)
        assert ot.read_parquet(path).to_dict() == df.to_dict()


def test_sql_read() -> None:
    connection = sqlite3.connect(":memory:")
    connection.execute("create table items (id integer, name text)")
    connection.execute("insert into items values (1, 'Ada')")
    out = ot.read_sql("select * from items", connection)
    assert out.to_dict() == {"id": [1], "name": ["Ada"]}
