# Reshaping

## concat

`concat()` vertically combines dataframes with identical ordered columns.

## pivot

`pivot()` converts long data to wide data. Duplicate index/column pairs raise `ReshapeError`.

## melt

`melt()` unpivots selected value variables into `variable` and `value` columns.

## explode

`explode()` expands list values into multiple rows and uses `NULL` for empty lists.

## stack

`stack()` returns a simplified row/variable/value representation.

## unstack

`unstack()` is the simplified inverse for data produced by `stack()`.
