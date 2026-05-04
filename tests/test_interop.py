from __future__ import annotations

import pytest

import otter as ot


def test_pandas_optional_interop_behavior() -> None:
    pd = pytest.importorskip("pandas")
    df = ot.from_pandas(pd.DataFrame({"a": [1, None]}))
    assert df.to_dict()["a"][0] == 1.0 or df.to_dict()["a"][0] == 1
    assert df.to_pandas().shape == (2, 1)


def test_arrow_optional_interop_behavior() -> None:
    pa = pytest.importorskip("pyarrow")
    table = pa.Table.from_pydict({"a": [1, None]})
    df = ot.from_arrow(table)
    assert df.to_dict() == {"a": [1, ot.NULL]}
    assert df.to_arrow().num_rows == 2


def test_numpy_optional_interop_behavior() -> None:
    np = pytest.importorskip("numpy")
    array = np.array([[1, 2], [3, 4]])
    df = ot.from_numpy(array, columns=["a", "b"])
    assert df.to_dict() == {"a": [1, 3], "b": [2, 4]}
    assert df.to_numpy().shape == (2, 2)
