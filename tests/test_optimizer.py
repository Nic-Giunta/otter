from __future__ import annotations

import otter as ot
from otter.optimizer import LogicalPlan, Operation, Optimizer


def test_optimizer_noop_removal_and_filter_combination() -> None:
    plan = LogicalPlan("test").add(Operation("drop", ())).add(Operation("rename", ({},))).add(
        Operation("filter", (ot.col("x") > 1,))
    ).add(Operation("filter", (ot.col("x") < 3,)))
    optimized = Optimizer().optimize(plan)
    assert [operation.name for operation in optimized.operations] == ["filter"]
    assert "AND" in optimized.operations[0].display()
