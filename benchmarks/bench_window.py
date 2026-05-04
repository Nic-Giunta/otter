from __future__ import annotations

import time

import otter as ot


def main() -> None:
    s = ot.Series(range(20_000), name="x")
    start = time.perf_counter()
    out = s.rolling(10).mean()
    print({"rows": len(out), "seconds": time.perf_counter() - start})


if __name__ == "__main__":
    main()
