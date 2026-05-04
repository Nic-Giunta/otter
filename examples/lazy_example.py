from __future__ import annotations

import otter as ot


df = ot.DataFrame({"name": ["Ada", "Grace", "Linus"], "age": [36, 85, 54]})
plan = df.lazy().with_column("age2", ot.col("age") + 2).filter(ot.col("age") >= 40).select("name", "age2")
print(plan.explain())
print(plan.collect().to_rows())
