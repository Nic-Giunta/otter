# Compatibility with Pandas

## Similarities

Otter uses familiar concepts: dataframes, series, column selection, boolean filtering, grouping, joins, sorting, reshaping, CSV/JSON/Parquet/SQL I/O, and optional Pandas conversion.

## Intentional differences

- Operations are non-mutating by default.
- Duplicate column names are rejected unless suffixes resolve conflicts.
- Indexes do not trigger implicit alignment.
- Null semantics are centered on logical `NULL`.
- Unsafe casts raise clear errors unless `strict=False` is explicit.
- Otter avoids SettingWithCopyWarning-style semantics by not exposing ambiguous views.

## Migration examples

```python
# Pandas style
# df[df["age"] >= 40][["name", "age"]]

# Otter
result = df.filter(df["age"] >= 40).select("name", "age")
```

## Compatibility philosophy

Otter aims to support common dataframe workflows while redesigning ambiguous behavior. Pandas is a migration and interoperability target, not an implementation dependency.

## Disclaimer

Otter is independent and not affiliated with Pandas. Otter does not copy Pandas source code or internals.

## Supported features

Construction, column selection, filtering, assignment, sorting, casting, grouping, joining, reshaping, windows, lazy planning, CSV, JSON, Parquet through PyArrow, SQL through DB-API, and optional Pandas/Arrow/NumPy interop.

## Designed differently

Otter intentionally avoids implicit alignment surprises and warning-driven mutation semantics. Users are expected to write explicit transformations.
