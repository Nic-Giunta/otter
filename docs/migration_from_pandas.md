# Migration from Pandas

## Creating dataframes

```python
df = ot.DataFrame({"name": ["Ada"], "age": [36]})
```

## Selecting columns

```python
df["name"]
df[["name", "age"]]
df.select("name", "age")
```

## Filtering

```python
df.filter(df["age"] >= 40)
df.filter(ot.col("age") >= 40)
```

## Assigning columns

```python
df.with_column("is_adult", df["age"] >= 18)
df.assign(is_adult=df["age"] >= 18)
```

## Sorting

```python
df.sort("age")
```

## GroupBy

```python
df.group_by("country").agg({"revenue": "sum"})
```

## Joins

```python
left.join(right, on="id", how="left")
```

## Null handling

Use `ot.NULL`, `is_null()`, `not_null()`, `fill_null()`, and `drop_nulls()`.

## Dtype casting

```python
df.cast({"age": ot.Int64})
df.cast({"age": ot.Int64}, strict=False)
```

## Reshaping

```python
df.pivot(index="country", columns="year", values="revenue")
df.melt(id_vars=["country"], value_vars=["sales", "profit"])
df.explode("items")
```

## I/O

```python
ot.read_csv("data.csv")
ot.write_json(df, "data.json")
```

## Interoperability

```python
ot.from_pandas(pd_df)
df.to_pandas()
```

## Common idioms

- Pandas chained assignment becomes `with_column()` or `assign()`.
- Pandas boolean indexing becomes `filter()`.
- Pandas implicit alignment should be replaced with explicit joins or positional operations.
