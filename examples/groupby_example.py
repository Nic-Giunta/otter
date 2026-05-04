from __future__ import annotations

import otter as ot


df = ot.DataFrame({"country": ["US", "US", "FR"], "revenue": [10, 20, 7]})
print(df.group_by("country").agg({"revenue": "sum"}).to_rows())
