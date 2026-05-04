# Query Optimizer

## Logical plans

LazyFrame stores operations as a logical plan. The plan is independent of a physical backend.

## Expression simplification

Current expressions preserve structure. Future simplification may fold literals and remove redundant predicates.

## Projection pushdown

The architecture allows future projection pushdown so only required columns are materialized. The initial optimizer focuses on no-op removal and filter combination.

## Filter combination

Adjacent expression filters are combined into a single logical AND expression.

## Future predicate pushdown

CSV, Parquet, SQL, and Arrow sources can eventually receive predicates before full materialization.

## Future join optimization

Join reordering, key statistics, and algorithm selection can be added once plan metadata and cost models exist.
