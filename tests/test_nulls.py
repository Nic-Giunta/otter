from __future__ import annotations

import math

import pytest

import otter as ot


def test_null_detection_normalization_and_coalesce() -> None:
    assert ot.is_null(None)
    assert ot.is_null(math.nan)
    assert ot.normalize_null(None) is ot.NULL
    assert ot.coalesce(None, ot.NULL, "x") == "x"
    assert repr(ot.NULL) == "NULL"


def test_null_boolean_rejected() -> None:
    with pytest.raises(ot.NullValueError):
        bool(ot.NULL)
