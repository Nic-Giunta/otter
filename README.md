# Otter

**Otter — A modern dataframe library for Python, built for clarity, correctness, performance, and extensibility.**

Otter is an independent open-source dataframe system. It provides a familiar column-oriented API, explicit copy semantics, a logical dtype system, consistent null handling, eager execution, lazy execution, expression planning, backend abstraction, standard-library I/O, optional interoperability, tests, documentation, examples, and benchmarks.

## Status

Otter is production-oriented and designed as a serious dataframe library, but this repository is the initial public implementation. The pure Python backend prioritizes correctness, maintainability, and API design before native acceleration. Performance claims should be made only through reproducible benchmarks.

## Installation

```bash
pip install otter-dataframe
pip install "otter-dataframe[dev]"
pip install "otter-dataframe[pandas,arrow,numpy,parquet,sql]"
```

For local development:

```bash
python -m pip install -e ".[dev]"
pytest --cov=otter
ruff check .
mypy src
```

## Quickstart

```python
import otter as ot

df = ot.DataFrame({
    "name": ["Ada", "Grace", "Linus"],
    "age": [36, 85, 54],
})

adults = df.filter(df["age"] >= 40).select("name", "age")
print(adults.to_rows())
```

## Core examples

```python
df.shape
df.height
df.width
df.columns
df.schema
df.index
df.head()
df.tail()
df.copy()
```

## Series examples

```python
s = ot.Series([1, 2, None], name="numbers")
s.fill_null(0).sum()
s.drop_nulls().mean()
s.is_null()
s.unique()
s.value_counts()
```

## DataFrame examples

```python
df["name"]
df[["name", "age"]]
df.select("name", "age")
df.with_column("is_adult", df["age"] >= 18)
df.with_columns({"age2": df["age"] + 2})
df.assign(is_adult=df["age"] >= 18)
df.drop("age")
df.rename({"name": "person_name"})
df.sort("age")
df.cast({"age": ot.Int64})
df.fill_null(0)
df.drop_nulls()
df.describe()
```

## LazyFrame example

```python
lazy_df = df.lazy()
result = lazy_df.select("name", "age").filter(ot.col("age") >= 40).collect()
print(lazy_df.explain())
```

## GroupBy example

```python
sales = ot.DataFrame({"country": ["US", "US", "FR"], "revenue": [10, 20, 7]})
summary = sales.group_by("country").agg({"revenue": "sum"})
```

## Join example

```python
left = ot.DataFrame({"id": [1, 2], "name": ["Ada", "Grace"]})
right = ot.DataFrame({"id": [2], "score": [99]})
joined = left.join(right, on="id", how="left")
```

## Reshape example

```python
long = ot.DataFrame({"country": ["US", "US"], "year": [2023, 2024], "revenue": [10, 12]})
wide = long.pivot(index="country", columns="year", values="revenue")
```

## I/O example

```python
ot.write_csv(df, "people.csv")
roundtrip = ot.read_csv("people.csv")
ot.write_json(df, "people.json")
```

Parquet uses optional PyArrow. SQL reads DB-API compatible cursors or connections.

## Interoperability example

```python
# pandas, Arrow, and NumPy are optional extras.
ot_df = ot.from_pandas(pd_df)
pd_df = ot_df.to_pandas()
array = ot_df.to_numpy()
```

## Design goals

- Non-mutating dataframe operations by default.
- Explicit row positions and index semantics.
- No hidden copy/view ambiguity.
- No SettingWithCopyWarning-style behavior.
- Ordered columns with duplicate names rejected.
- Conservative dtype inference and explicit casting.
- Consistent logical null semantics.
- Modular internals for compute, grouping, joins, reshaping, lazy planning, optimization, I/O, and interoperability.
- Optional heavy dependencies rather than mandatory core dependencies.

## Non-goals

- Otter is not a wrapper around Pandas.
- Otter does not copy Pandas source code or internals.
- Otter does not try to reproduce every historical Pandas behavior.
- Otter does not make unbenchmarked performance claims.

## What makes Otter different from Pandas

Otter is familiar to Pandas users, but it intentionally makes copy and mutation semantics explicit. Methods such as `with_column()`, `drop()`, `rename()`, `select()`, and `filter()` return new dataframes. Row labels are explicit and are never used for surprising implicit alignment. Duplicate columns are rejected unless an operation resolves conflicts with suffixes.

## Null semantics summary

Otter uses `ot.NULL` as the logical null. Python `None` and floating `NaN` normalize to logical null where appropriate. Null arithmetic propagates nulls. Aggregations skip nulls by default. Filtering rejects null masks with actionable errors.

## Dtype system summary

Otter exposes logical dtypes such as `Int64`, `Float64`, `Boolean`, `String`, `Date`, `Datetime`, `Decimal`, `List`, `Struct`, `Null`, and `Object`. Inference is conservative. Integer values infer as `Int64`, mixed integers and floats infer as `Float64`, all-null columns infer as `Null`, and `Object` is used only as a fallback.

## API overview

The top-level API exports `DataFrame`, `Series`, `LazyFrame`, `Index`, `RangeIndex`, `Schema`, `Field`, all dtypes, null helpers, expression helpers, custom errors, I/O functions, optional interoperability functions, and public testing helpers.

## Compatibility philosophy

Otter treats Pandas as an important comparison and migration target, not as an implementation base. Compatibility is practical: common dataframe workflows should feel familiar, while ambiguous semantics are redesigned.

## Performance philosophy

The core backend is pure Python and correctness-first. The architecture prepares for future NumPy, Arrow, and native compute backends through a backend boundary and reusable compute kernels. Benchmark results belong in `benchmarks/` and should include environment details.

## Roadmap

See `ROADMAP.md` and `docs/roadmap.md` for the staged plan from core semantics through ecosystem maturity.

## Contributing

Contributions should include tests, documentation updates, clear error messages, and benchmark evidence for performance claims. See `CONTRIBUTING.md`.

## License

Otter is licensed under the BSD-3-Clause license.

## Disclaimer

Otter is independent software. It is not affiliated with, endorsed by, sponsored by, or an official project of Pandas or the Pandas development team. Pandas is referenced only as an interoperability target, migration target, comparison point, and behavioral reference where useful.
