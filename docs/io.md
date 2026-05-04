# I/O

## CSV

CSV I/O uses Python's `csv` module. Readers require a header row, reject duplicate header names, parse common scalar values, normalize null tokens, and raise `DataSourceError` for invalid files.

## JSON

JSON I/O uses records orientation: a list of objects. JSON null maps to `NULL`.

## Parquet

Parquet support is optional and uses PyArrow. Missing PyArrow raises `BackendError` with installation guidance.

## SQL

`read_sql()` uses DB-API cursor behavior. SQLAlchemy is documented as an optional integration path, not a core dependency.

## Pandas

Pandas conversion is optional. `from_pandas()` and `DataFrame.to_pandas()` raise `BackendError` when pandas is unavailable.

## Arrow

Arrow conversion is optional. `from_arrow()` and `DataFrame.to_arrow()` require PyArrow.

## NumPy

NumPy conversion is optional. `from_numpy()` and `DataFrame.to_numpy()` require NumPy.
