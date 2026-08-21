---
description: scale() resamples to a new grid/size (exact NxM output, factors) vs extend() which pads the domain with nulls. Fetch when output dimensions are wrong, or you must grow a canvas without stretching.
---

Two different domain operations that are easy to confuse:

**scale() — RESAMPLES** the data onto a new grid (changes resolution, keeps
the same picture) with nearest neighbour interpolation. Example x/y scaling
```
scale( $c, { x ( lox : hix ) , y ( loy : hiy ) } )
```

The target may be the grid domain of another coverage:
```
scale( $cov, { imageCrsDomain( $otherCov ) } )
```

Notes:
- For an exact output size, give the target in grid coordinates (CRS:1),
  0-based inclusive — `x:"CRS:1"(0:99)` means 100 cells along x.
- Auto-ratio scaling allows to specify one spatial axis, so the other follows proportionally
- Omit an axis to leave it unchanged in the scale result

**extend() — PADS** the domain with null values (no resampling; the original
data keeps its position and resolution, the added area is empty). Example:
```
extend( C, { x ( -200 : 200 ) } )
```

The extend target must contain the input domain — it cannot shrink; combine
with a subset first if needed.

Which one do I want?
- "output must be exactly N×M pixels" → scale to a CRS:1 grid.
- "grow the canvas / add empty margin" → extend.
- A stretched-looking result where a margin was expected = you used scale
  where extend was intended.

**Pitfalls**
- Grid bounds are inclusive: `(0:99)` is 100 cells — off-by-one here is the
  most common scale error.
- scale in rasdaman is done with nearest-neighbour interpolation.
