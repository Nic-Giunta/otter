# API Design

## DataFrame API

The DataFrame API is column-oriented and immutable-by-default. Selection, filtering, assignment, casting, reshaping, joining, and grouping return new dataframes.

## Series API

Series supports element-wise arithmetic, comparisons, null-aware aggregations, string helpers, datetime helpers, and window operations.

## Index API

Indexes are explicit row labels. They are not used for hidden alignment.

## GroupBy API

`df.group_by("key").agg({"value": "sum"})` supports one or more key columns and deterministic output order.

## Join API

`join()` supports inner, left, right, outer, cross, semi, and anti joins. Duplicate non-key columns are suffixed.

## Reshape API

`concat`, `pivot`, `melt`, `explode`, `stack`, and `unstack` cover common reshape workflows.

## Window API

`Series.rolling(window)` supports rolling sum, mean, min, and max. `Series.expanding()` supports expanding sum and mean.

## Expression API

`col()` and `lit()` create expression trees. Arithmetic, comparison, and boolean combinators evaluate against a DataFrame and are used by LazyFrame.

## LazyFrame API

LazyFrame records operations and executes on `collect()`. `explain()` prints logical and optimized plans.

## I/O API

CSV and JSON are standard-library implementations. Parquet uses optional PyArrow. SQL uses DB-API cursor behavior where practical.

## Interoperability API

Pandas, Arrow, and NumPy conversions are optional and raise clear `BackendError` messages if dependencies are unavailable.
