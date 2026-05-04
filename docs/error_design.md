# Error Design

## Error hierarchy

All public errors inherit from `OtterError`. Specialized subclasses include schema, dtype, cast, null, shape, row selection, join, group-by, expression, lazy execution, backend, data source, index, reshape, window, aggregation, and interoperability errors.

## Error message principles

Messages should be clear, specific, actionable, and written in English. They should name the failing object, describe available alternatives where useful, and include a suggested fix.

## Good error example

```text
Column 'revenue' does not exist.

Available columns:
- country
- sales

Suggested fix:
Check the column name or inspect df.columns.
```

## Suggested-fix philosophy

A good error should help the user recover without reading source code.
