---
description: domain() (geo extent, .lo/.hi) vs imageCrsDomain() (grid index range) and how over-clauses + CRS:1 iterators use them. Fetch when writing constructors/condensers without hardcoding extents.
---

Read a coverage's axis extents from within a query — the glue for
constructors and condensers.

- `imageCrsDomain($c, axis)` → the axis's GRID index range (integers,
  0-based). Often used in `over`-clauses, or as a scale target:
```
condense +
over $it1 axis1( imageCrsDomain($c, axis1) ),
     ...,
     $itD axisD( imageCrsDomain($c, axisD) )
using $c[ p1, ..., pd ]

scale( $c, { imageCrsDomain( $anotherCov ) } )
```

- `domain($c, axis)` → the axis's GEO extent (native CRS units), with
  `.lo` / `.hi` accessors — usable inside subsets:
```
$c[Lat( 30 : domain($c, Lat).hi )]  ==  $c[Lat( 30 : * )]
```

**Pitfalls**
- Mixing the two: a `domain()` in an `over`-clause (geo coordinates) instead of
  `imageCrsDomain()` (grid ints) fails or iterates nonsense.
- Subset the coverage inside the call to restrict the range:
  `imageCrsDomain($c[ ... subset ... ], axis)`.
