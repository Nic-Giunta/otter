from __future__ import annotations

import otter as ot


df = ot.DataFrame({"name": ["Ada", "Grace", "Linus"], "age": [36, 85, 54]})
print(df.filter(df["age"] >= 40).select("name", "age").to_rows())
