from __future__ import annotations

import time

import otter as ot


def main() -> None:
    df = ot.DataFrame({"x": list(range(10_000)), "y": list(range(10_000))})
    plan = df.lazy().with_column("z", ot.col("y") + 1).filter(ot.col("x") >= 5_000).select("x", "z")
    start = time.perf_counter()
    out = plan.collect()
    print({"rows": out.height, "seconds": time.perf_counter() - start})


if __name__ == "__main__":
    main()
