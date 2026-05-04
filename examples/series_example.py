from __future__ import annotations

import otter as ot


s = ot.Series([1, 2, None, 4], name="numbers")
print(s.fill_null(0).to_list())
print(s.drop_nulls().mean())
