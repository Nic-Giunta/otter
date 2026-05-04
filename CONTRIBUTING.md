# Contributing to Otter

Thank you for helping improve Otter.

## Setup instructions

```bash
git clone https://github.com/otter-dataframe/otter.git
cd otter
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pre-commit install
```

## Development workflow

Create a focused branch, write code with type annotations, add tests, update documentation, and run the full validation suite before opening a pull request.

## Testing instructions

```bash
pytest --cov=otter
```

Use Hypothesis for edge cases where randomized coverage is valuable.

## Linting instructions

```bash
ruff check .
mypy src
```

## Pull request expectations

A pull request should describe the problem, the solution, user-facing API changes, compatibility impact, tests, and documentation updates.

## Issue expectations

Issues should include a clear description, reproduction steps, expected behavior, actual behavior, environment details, and relevant code snippets.

## Code style rules

Code should be clear, typed, maintainable, and modular. Prefer focused modules over large multi-purpose classes. Public error messages, comments, docstrings, docs, templates, examples, and README text must be written in English.

## Documentation rules

New user-facing behavior requires documentation. Design changes should update architecture or API design docs.

## Benchmark rules

Performance claims require reproducible benchmarks in `benchmarks/`, including dataset shape, Python version, backend, dependency versions, and hardware context.

## Compatibility policy

Otter treats Pandas as a migration and interoperability target but is independent and does not copy Pandas source code or internals. Ambiguous semantics may be intentionally redesigned.
