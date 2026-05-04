# Performance Strategy

## Pure Python backend

The current backend is a reference implementation focused on correctness, predictable semantics, and maintainability.

## Future NumPy integration

A future NumPy backend can accelerate homogeneous numeric columns while preserving Otter's logical dtype and null semantics.

## Future Arrow integration

An Arrow backend can provide columnar memory layout, zero-copy interchange, and Parquet-native workflows.

## Future lazy execution

Lazy plans enable future projection pushdown, predicate pushdown, common subexpression elimination, and backend-specific execution.

## Future native backends

Native kernels may target Rust, C++, or C extensions behind the backend protocol.

## Benchmark philosophy

Benchmarks must be reproducible, include environment details, and avoid broad claims without data.

## Correctness before optimization

Otter prioritizes semantics and tests before speed. Performance work should preserve error quality and null behavior.

## Making benchmark claims

Claims should identify dataset shape, dtype mix, hardware, Python version, backend, and comparison versions.
