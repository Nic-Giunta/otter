from __future__ import annotations

import otter as ot

try:
    import pandas as pd
except ImportError:
    print("Install pandas to run this example.")
else:
    pd_df = pd.DataFrame({"name": ["Ada"], "age": [36]})
    df = ot.from_pandas(pd_df)
    print(df.to_rows())
    print(df.to_pandas())
