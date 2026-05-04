from __future__ import annotations

import otter as ot


df = ot.DataFrame({"name": ["Ada", "Grace"], "age": [36, 85]})
print(df.with_column("is_adult", df["age"] >= 18).sort("age").to_rows())
