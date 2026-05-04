# Architecture

## Module responsibilities

- `dataframe.py`: public eager `DataFrame` container and high-level dataframe methods.
- `series.py`: public `Series` container and scalar/column operations.
- `index.py`: explicit `Index` and `RangeIndex` row labels.
- `schema.py` and `dtypes.py`: logical schema and dtype inference/casting.
- `nulls.py`: logical `NULL`, normalization, and null predicates.
- `compute.py`: reusable arithmetic, comparison, aggregation, sorting, and casting helpers.
- `groupby.py`, `joins.py`, `reshape.py`, and `window.py`: focused dataframe operation modules.
- `expressions.py`: expression trees used by eager operations and lazy plans.
- `lazy.py` and `optimizer.py`: lazy API, logical plans, and optimizer passes.
- `io.py` and `interop.py`: standard-library I/O and optional ecosystem conversions.
- `backends.py`: execution backend protocol and pure Python backend.
- `testing.py`: public assertion helpers.

## Public API vs internals

The public API is exported from `otter.__init__`. Internal execution is split across focused modules so the public `DataFrame` class does not become a god object. High-level methods delegate to operation modules where practical.

## Why operations are non-mutating

Methods such as `select()`, `filter()`, `with_column()`, `drop()`, and `rename()` return new dataframes. This avoids hidden view/copy state and eliminates SettingWithCopyWarning-style ambiguity by design.

## Index design

Otter uses explicit row labels but does not use indexes for implicit alignment. Row operations are positional unless the user explicitly materializes or sets an index.

## Future backend strategy

The pure Python backend is the reference backend. Future NumPy, Arrow, and native backends should implement storage and compute boundaries without leaking backend-specific types into the public API.

## Future Arrow strategy

Arrow-native storage is planned as an optional backend. The current `to_arrow()` and `from_arrow()` functions define the interoperability boundary.

## Future lazy execution strategy

LazyFrame stores logical operations and evaluates them on `collect()`. Current optimizer passes include no-op removal and filter combination. The plan representation is intentionally simple so future projection pushdown, predicate pushdown, and join optimization can be added.

## Avoiding a DataFrame god object

New operations should live in focused modules and expose small delegation methods on `DataFrame` only when they are central user-facing API. Compute primitives should remain in `compute.py`; conversion code should remain in `interop.py`; data source code should remain in `io.py`.
