# Query Optimizer

## Logical plans

LazyFrame stores operations as a logical plan. The plan is independent of a physical backend.

## Expression simplification

Current expressions preserve structure. Future simplification may fold literals and remove redundant predicates.

## Projection pushdown

The architecture allows future projection pushdown so only required columns are materialized. The initial optimizer focuses on no-op removal and filter combination.

## Filter combination

Adjacent expression filters are combined into a single ordered logical AND expression. The ordered form preserves Otter's filter behavior: rows rejected by an earlier predicate do not make later nulls invalid, while nulls in earlier predicates still raise the same filtering error as eager execution.

## Future predicate pushdown

CSV, Parquet, SQL, and Arrow sources can eventually receive predicates before full materialization.

## Future join optimization

Join reordering, key statistics, and algorithm selection can be added once plan metadata and cost models exist.
