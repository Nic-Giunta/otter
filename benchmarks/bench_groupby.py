from __future__ import annotations

import time

import otter as ot


def main() -> None:
    df = ot.DataFrame({"g": [idx % 100 for idx in range(20_000)], "x": list(range(20_000))})
    start = time.perf_counter()
    out = df.group_by("g").agg({"x": "sum"})
    print({"groups": out.height, "seconds": time.perf_counter() - start})


if __name__ == "__main__":
    main()
