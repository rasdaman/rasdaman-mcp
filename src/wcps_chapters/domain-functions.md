---
description: domain() (geo extent, .lo/.hi) vs imageCrsDomain() (grid index range) and how over-clauses + CRS:1 iterators use them. Fetch when writing constructors/condensers without hardcoding extents.
---

Read a coverage's axis extents from within a query — the glue for
constructors and condensers.

- `imageCrsDomain($c, axis)` → the axis's GRID index range (integers,
  0-based). This is what `over`-clauses want. The standard itself defines the
  reduce shorthands this way (OGC 08-068r2, Table 4):

```
add(a) = condense +
         over p1 D1( imageCrsDomain(a, D1) ),
              ...,
              pd Dd( imageCrsDomain(a, Dd) )
         using a[ p1, ..., pd ]
```

- `imageCrsDomain($c)` (no axis) → the full grid domain; usable directly as
  a scale target (guide example): `scale( $c, { imageCrsDomain( $c ) } )`.
- `domain($c, axis)` → the axis's GEO extent (native CRS units), with
  `.lo` / `.hi` accessors — usable inside subsets:
  `$c[Lat( 30 : domain($c, Lat).hi )]`.
- Applying a grid iterator back onto a geo-referenced coverage requires the
  CRS:1 qualifier: `$c[ansi:"CRS:1"($t)]` (see subsetting).

Pitfalls:
- Mixing the two: an `over`-clause fed `domain()` (geo floats) instead of
  `imageCrsDomain()` (grid ints) fails or iterates nonsense.
- Subset the coverage inside the call to restrict the range:
  `imageCrsDomain($c[ ... subset ... ], axis)`.
