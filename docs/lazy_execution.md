# Lazy Execution

## LazyFrame design

`LazyFrame` wraps an eager dataframe and records operations in a logical plan. It does not execute transformations until `collect()`.

## Logical plans

A logical plan contains a source description and ordered operations.

## collect()

`collect()` optimizes the plan and executes operations using eager dataframe methods.

## explain()

`explain()` prints a logical or optimized logical plan.

## Optimizer passes

Current passes remove no-op operations and combine adjacent expression filters with ordered logical AND when they are expression filters. The optimizer is intentionally conservative and must preserve eager semantics.

## Expression integration

Expressions created by `col()`, `lit()`, `and_()`, `or_()`, and `not_()` can be used in eager filters and lazy plans.

## Future optimizer roadmap

Future work includes projection pushdown, predicate pushdown into data sources, expression simplification, join reordering, aggregation pushdown, and backend-specific plan lowering.
