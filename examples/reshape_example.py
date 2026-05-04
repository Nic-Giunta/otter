from __future__ import annotations

import otter as ot


df = ot.DataFrame({"country": ["US", "US"], "year": [2023, 2024], "revenue": [10, 12]})
print(df.pivot(index="country", columns="year", values="revenue").to_rows())
print(df.melt(id_vars=["country"], value_vars=["year", "revenue"]).to_rows())
