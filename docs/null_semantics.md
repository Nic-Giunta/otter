# Null Semantics

## NULL

`ot.NULL` is Otter's logical null sentinel. Its representation is `NULL`, and using it as a boolean raises `NullValueError`.

## None and NaN

Python `None` and floating `NaN` normalize to `NULL` where appropriate.

## Arithmetic

Arithmetic involving null values propagates `NULL`.

## Comparison

Comparisons involving null values produce `NULL`. Filtering rejects null masks and asks users to fill or remove nulls first.

## Aggregation

Aggregations skip null values by default. Passing `skip_nulls=False` causes nulls to propagate.

## Sorting

Sorting places nulls last.

## GroupBy

Null grouping keys are represented explicitly and retained as group keys.

## Joins

Null join keys do not match other null join keys. This avoids accidental matches from missing data.

## Reshaping

Pivot and explode preserve missing values as `NULL`.

## CSV mapping

Empty strings and common null tokens are read as `NULL`. Writing materializes `NULL` as empty external values through the CSV writer.

## JSON mapping

JSON `null` maps to `NULL`; `NULL` writes as JSON `null`.

## SQL mapping

SQL `NULL` maps to `NULL` through DB-API values.

## Pandas mapping

Pandas null-like values normalize to `NULL` on import and become `None` on export.

## Arrow and Parquet mapping

Arrow nulls normalize to `NULL`. Parquet mapping follows PyArrow table conversion.
