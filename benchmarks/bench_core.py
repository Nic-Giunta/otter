from __future__ import annotations

import time

import otter as ot


def main() -> None:
    start = time.perf_counter()
    df = ot.DataFrame({"x": list(range(10_000)), "y": list(range(10_000))})
    filtered = df.filter(df["x"] >= 5_000)
    filtered = filtered.with_column("z", filtered["y"] + 1)
    elapsed = time.perf_counter() - start
    print({"rows": filtered.height, "seconds": elapsed})


if __name__ == "__main__":
    main()
