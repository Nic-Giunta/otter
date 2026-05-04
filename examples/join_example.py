from __future__ import annotations

import otter as ot


left = ot.DataFrame({"id": [1, 2], "name": ["Ada", "Grace"]})
right = ot.DataFrame({"id": [2, 3], "score": [99, 80]})
print(left.join(right, on="id", how="left").to_rows())
