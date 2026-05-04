from __future__ import annotations

from pathlib import Path

import otter as ot


path = Path("people.csv")
df = ot.DataFrame({"name": ["Ada", "Grace"], "age": [36, 85]})
ot.write_csv(df, path)
print(ot.read_csv(path).to_rows())
path.unlink(missing_ok=True)
