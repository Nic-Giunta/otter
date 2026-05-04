# Dtype System

## Supported dtypes

`Int8`, `Int16`, `Int32`, `Int64`, `UInt8`, `UInt16`, `UInt32`, `UInt64`, `Float32`, `Float64`, `Boolean`, `String`, `Date`, `Datetime`, `Time`, `Duration`, `Decimal`, `Categorical`, `List`, `Struct`, `Null`, and `Object`.

## Inference rules

Integers infer as `Int64`. Mixed integers and floats infer as `Float64`. Booleans infer as `Boolean` and are not treated as integers. Strings infer as `String`. Safe date, datetime, time, timedelta, decimal, list, and struct values infer to corresponding dtypes. All-null columns infer as `Null`. `Object` is a conservative fallback.

## Casting rules

Casting is explicit. Strict casting rejects unsafe or lossy conversions. Passing `strict=False` allows practical conversions such as strings to integers and floats.

## Nullability

Dtypes are logical and nullable by default. Schema fields include a nullable flag for future stricter validation.

## Object fallback policy

`Object` is used only when values do not fit a clearer dtype.

## Future dtype roadmap

Future releases may add parameterized decimals, categorical dictionaries, nested child dtypes, timezone-aware datetimes, and backend-specific physical dtype mappings.
