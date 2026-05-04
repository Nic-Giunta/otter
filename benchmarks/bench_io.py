from __future__ import annotations

import time
from pathlib import Path

import otter as ot


def main() -> None:
    df = ot.DataFrame({"x": list(range(5_000)), "y": ["value"] * 5_000})
    path = Path("bench_otter.csv")
    start = time.perf_counter()
    ot.write_csv(df, path)
    out = ot.read_csv(path)
    path.unlink(missing_ok=True)
    print({"rows": out.height, "seconds": time.perf_counter() - start})


if __name__ == "__main__":
    main()
