from __future__ import annotations

import pytest

import otter as ot


def test_range_index_and_explicit_index() -> None:
    index = ot.RangeIndex(3)
    assert index.to_list() == [0, 1, 2]
    df = ot.DataFrame({"id": [10, 20], "x": [1, 2]}).set_index("id")
    assert df.index.to_list() == [10, 20]
    assert df.reset_index().columns == ["id", "x"]


def test_index_length_validation() -> None:
    with pytest.raises(ot.ShapeError):
        ot.DataFrame({"a": [1]}, index=ot.Index([1, 2]))
