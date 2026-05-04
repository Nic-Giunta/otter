from __future__ import annotations

import pytest

import otter as ot


def test_rolling_and_expanding_windows() -> None:
    s = ot.Series([1, 2, 3, 4])
    assert s.rolling(2).sum().to_list() == [ot.NULL, 3, 5, 7]
    assert s.rolling(2).mean().to_list() == [ot.NULL, 1.5, 2.5, 3.5]
    assert s.rolling(2).min().to_list() == [ot.NULL, 1, 2, 3]
    assert s.rolling(2).max().to_list() == [ot.NULL, 2, 3, 4]
    assert s.expanding().sum().to_list() == [1, 3, 6, 10]
    assert s.expanding().mean().to_list() == [1, 1.5, 2, 2.5]
    with pytest.raises(ot.WindowError):
        s.rolling(0)
