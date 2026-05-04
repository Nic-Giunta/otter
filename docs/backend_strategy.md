# Backend Strategy

## Backend abstraction

`backends.py` defines a backend protocol and a `PythonBackend`. Public APIs should not expose physical backend storage.

## PythonBackend

The Python backend uses lists and standard-library algorithms. It is simple, inspectable, and suitable as the correctness reference.

## Future NumPyBackend

A NumPy backend can accelerate numeric arrays and vectorized operations while normalizing nulls at the Otter boundary.

## Future ArrowBackend

An Arrow backend can store columns in Arrow arrays and support zero-copy exchange with Arrow-native systems.

## Future NativeBackend

A native backend can provide compiled kernels for joins, grouping, sorting, and expression evaluation.

## Avoiding public leakage

Backends should implement compute and storage behind internal protocols. DataFrame, Series, Schema, and DType remain the stable public model.
