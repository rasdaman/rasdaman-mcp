---
description: clip() with WKT POLYGON/LINESTRING: exact syntax, unquoted WKT, vertex coordinate order = coverage axis order, closing the polygon. Fetch for cutting a coverage to a polygon/triangle/shape.
---

`clip()` cuts a coverage to a WKT geometry; cells outside become null.

Syntax:
```
clip( coverageExpression, wkt [, subsettingCrs ] )
```

where `coverageExpression` is any coverage-valued expression (e.g. `C + 10`),
`wkt` is a Well-Known Text geometry — `POLYGON((...))`, `LineString(...)`,
`Multipolygon(...)`, plus curtain/corridor variants for 3-D coverages — and
`subsettingCrs` optionally names the CRS the WKT coordinates are expressed
in (a CRS URL), when it differs from the coverage's native CRS.

```
for $c in (C)
return encode(
   clip( $c, POLYGON(( 20 40, 45 45, 30 70, 20 40 )) ),
   "image/png" )
```

- **Coordinate order follows the axis order of the CRS of $c** — for a
  (lat, long) CRS every vertex is `lat long`; for an (E, N) CRS it is `e n`.
  Getting this backwards is THE classic clip failure: a thin sliver, empty
  result, or out-of-extent error.
- Close polygons: repeat the first vertex as the last.
- The WKT is written **bare** (unquoted) inside clip(). If a quoted string
  form fails with a cast error mentioning AbstractWKTShape, remove the quotes.
- Result stays rectangular (the geometry's bounding box) with nulls outside
  the shape; encoding to PNG shows the shape on a null background.
- Subset the coverage expression first if a time/band selection is also
  needed.
