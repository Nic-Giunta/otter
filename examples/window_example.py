from __future__ import annotations

import otter as ot


s = ot.Series([1, 2, 3, 4], name="values")
print(s.rolling(2).sum().to_list())
print(s.expanding().mean().to_list())
