# API Reference

## Classes

### `DataFrame`

Construct from a mapping of column names to iterables or from records:

```python
df = ot.DataFrame({"name": ["Ada"], "age": [36]})
```

Important attributes and methods: `shape`, `height`, `width`, `columns`, `schema`, `index`, `to_dict()`, `to_rows()`, `head()`, `tail()`, `copy()`, `select()`, `filter()`, `where()`, `with_column()`, `with_columns()`, `assign()`, `drop()`, `rename()`, `sort()`, `cast()`, `fill_null()`, `drop_nulls()`, `unique()`, `value_counts()`, `describe()`, `sample()`, `group_by()`, `join()`, `concat()`, `pivot()`, `melt()`, `explode()`, `stack()`, `unstack()`, `lazy()`, `to_pandas()`, `to_arrow()`, and `to_numpy()`.

### `Series`

A one-dimensional column:

```python
s = ot.Series([1, 2, None], name="numbers")
```

Methods include `to_list()`, `to_dict()`, `cast()`, `sum()`, `mean()`, `min()`, `max()`, `count()`, `median()`, `std()`, `var()`, `quantile()`, `fill_null()`, `drop_nulls()`, `unique()`, `value_counts()`, `sort()`, `is_null()`, `not_null()`, string helpers, datetime helpers, and rolling/expanding windows. String helpers require string values except for nulls; datetime helpers require `date` or `datetime` values except for nulls.

### `LazyFrame`

Created with `df.lazy()`. Supports `select()`, `filter()`, `with_column()`, `with_columns()`, `drop()`, `rename()`, `sort()`, `group_by()`, `join()`, `collect()`, and `explain()`.

### `Index` and `RangeIndex`

Represent explicit row labels with no implicit alignment semantics.

### `Schema` and `Field`

Represent ordered column names, dtypes, and nullability.

## Functions

I/O: `read_csv`, `write_csv`, `read_json`, `write_json`, `read_parquet`, `write_parquet`, `read_sql`.

Reshaping: `concat`, `pivot`, `melt`, `explode`, `stack`, `unstack`.

Interop: `from_pandas`, `from_arrow`, `from_numpy` and corresponding dataframe methods.

Expressions: `col`, `lit`, `and_`, `or_`, `not_`.

Testing: `assert_frame_equal`, `assert_series_equal`, `assert_schema_equal`.

## Expected behavior

Dataframe operations are non-mutating. Duplicate columns are rejected. Column lengths must match. Nulls normalize to `NULL`. Unsafe casts raise `CastError` unless `strict=False` is explicitly passed.
