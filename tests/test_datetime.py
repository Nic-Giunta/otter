from __future__ import annotations

import datetime as dt

import otter as ot


def test_datetime_helpers() -> None:
    s = ot.Series([dt.date(2024, 1, 2), None])
    assert s.dt_year().to_list() == [2024, ot.NULL]
    assert s.dt_month().to_list() == [1, ot.NULL]
    assert s.dt_day().to_list() == [2, ot.NULL]
    assert s.dt.year().to_list() == [2024, ot.NULL]
