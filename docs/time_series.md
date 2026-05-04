# Time Series

## Date and datetime dtype strategy

Otter includes logical `Date`, `Datetime`, `Time`, and `Duration` dtypes. Inference detects safe Python standard-library temporal values.

## Parsing

CSV parsing recognizes ISO date and datetime values where safe. Explicit casting can parse ISO strings with `strict=False`.

## Extraction helpers

Series methods `dt_year()`, `dt_month()`, and `dt_day()` extract components from date-like values. The namespace `series.dt.year()` is also available.

## Future timezone plan

Timezone-aware datetime support should be implemented through logical dtype metadata and Arrow-compatible physical storage.
