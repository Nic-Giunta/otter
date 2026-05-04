from __future__ import annotations

import pytest

import otter as ot


def test_error_message_style() -> None:
    df = ot.DataFrame({"country": ["US"], "sales": [10]})
    with pytest.raises(ot.ColumnNotFoundError) as excinfo:
        df["revenue"]
    message = str(excinfo.value)
    assert "Column 'revenue' does not exist." in message
    assert "Available columns:" in message
    assert "Suggested fix:" in message
