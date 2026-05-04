from __future__ import annotations

import otter as ot


def test_series_string_helpers() -> None:
    s = ot.Series(["Ada", None, "Grace"], name="name")
    assert s.str_len().to_list() == [3, ot.NULL, 5]
    assert s.str_lower().to_list() == ["ada", ot.NULL, "grace"]
    assert s.str_upper().to_list() == ["ADA", ot.NULL, "GRACE"]
    assert s.str_contains("a").to_list() == [True, ot.NULL, True]
    assert s.str_startswith("A").to_list() == [True, ot.NULL, False]
    assert s.str_endswith("e").to_list() == [False, ot.NULL, True]
    assert s.str_replace("a", "A").to_list() == ["AdA", ot.NULL, "GrAce"]
    assert s.str.lower().to_list()[0] == "ada"
