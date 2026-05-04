# Indexing

## RangeIndex

`RangeIndex` is the default explicit row label container.

## Index

`Index` stores user-provided row labels. It supports iteration, positional access, copying, and conversion to a list.

## Positional row model

Row operations are positional. Otter does not silently align by labels.

## Differences from Pandas

Pandas indexes participate in many alignment operations. Otter intentionally avoids this because implicit alignment can surprise users and hide bugs.

## Avoiding implicit alignment surprises

Use explicit joins for key-based combination and explicit row positions for positional work.
