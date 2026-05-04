from __future__ import annotations

import time

import otter as ot


def main() -> None:
    df = ot.DataFrame({"id": list(range(1_000)), "a": list(range(1_000)), "b": list(range(1_000))})
    start = time.perf_counter()
    out = df.melt(id_vars=["id"], value_vars=["a", "b"])
    print({"rows": out.height, "seconds": time.perf_counter() - start})


if __name__ == "__main__":
    main()
