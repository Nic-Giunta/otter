from __future__ import annotations

import time

import otter as ot


def main() -> None:
    left = ot.DataFrame({"id": list(range(10_000)), "x": list(range(10_000))})
    right = ot.DataFrame({"id": list(range(5_000, 15_000)), "y": list(range(10_000))})
    start = time.perf_counter()
    out = left.join(right, on="id", how="inner")
    print({"rows": out.height, "seconds": time.perf_counter() - start})


if __name__ == "__main__":
    main()
