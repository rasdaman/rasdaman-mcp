---
description: scale() resamples to a new grid/size (exact NxM output, factors) vs extend() which pads the domain with nulls. Fetch when output dimensions are wrong, or you must grow a canvas without stretching.
---

Two different domain operations that are easy to confuse:

**scale() — RESAMPLES** the data onto a new grid (changes resolution, keeps
the same picture). OGC 08-068r2 example — x/y scaling with per-field
interpolation and null resistance:

```
scale( C,
       { x ( lox : hix ) , y ( loy : hiy ) },
       { red ( cubic , full ), nir ( linear, half ) } )
```

rasdaman accepts the simpler forms without the interpolation block, and the
target may be an existing grid domain (guide example, inside a full query):

```
scale( $c, { imageCrsDomain( $c ) } )
```

For an exact output size, give the target in grid coordinates (CRS:1),
0-based inclusive — `x:"CRS:1"(0:99)` means 100 cells along x.

**extend() — PADS** the domain with null values (no resampling; the original
data keeps its position and resolution, the added area is empty).
OGC example:

```
extend( C, { x ( -200 : +200 ) } )
```

The extend target must contain the input domain — it cannot shrink; combine
with a subset first if needed.

Which one do I want?
- "output must be exactly N×M pixels" → scale to a CRS:1 grid.
- "grow the canvas / add empty margin" → extend.
- A stretched-looking result where a margin was expected = you used scale
  where extend was intended.

Pitfalls:
- Grid bounds are inclusive: `(0:99)` is 100 cells — off-by-one here is the
  most common scale error.
- scale interpolates — exact-value comparisons after scaling are only
  approximate.
- rasdaman extras (guide): auto-ratio scaling (give one axis, the other
  follows proportionally) and non-scaled axes (omit an axis to leave it
  untouched).
