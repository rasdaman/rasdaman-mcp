---
description: Selecting parts of a coverage: trim `axis(lo:hi)` vs slice `axis(p)`, spatio-temporal vs grid (CRS:1) coordinates, pinning all axes of n-D coverages. Fetch for any wrong-region/wrong-axis/extent problem.
---

Select part of a coverage with bracket syntax on axis names.

**Trims** keep the axes:
```
$cov[ x:"EPSG:4326"(-180 : 180), y:"EPSG:4326"(-90 : 90) ]
```
The CRS `:"EPSG:4326"` qualifier is optional when coordinates are in the native CRS, which is the common case.
```
$cov[ Long(-180 : 180), Lat(-90 : 90) ]
```

**Slices** drop axes:
```
$cov[ x(120) ]
```
A d-dimensional coverage sliced on k axes becomes (d−k)-dimensional.

**Further details**

- Time axes take ISO 8601 strings in double quotes: `ansi("2020-03-21T00:00:00.000Z")`
  (short forms like `"2020-03"` are also accepted by rasdaman).
- Grid (integer pixel) coordinates instead of geo coordinates: qualify with
  CRS:1 — `C[x:"CRS:1"(0:99)]` means grid columns 0..99. Needed whenever a
  target is defined in pixels (constructor iteration, exact-size scaling).
- Axis bounds can come from `domain()`: `$c[Lat(30:domain($c, Lat).hi)]`
  (see domain-functions.md).
- ALL axes you don't subset stay unchanged — an n-D coverage needs every
  extra axis sliced to yield a 2-D result.
- Trimming beyond the coverage extent is an error; use `extend()` to grow a
  domain (see scale-extend.md).

**Pitfalls**
- Axis names are case-sensitive and coverage-specific (`Lat` vs `lat`,
  `Long` vs `Lon`, `E`/`N`, `date` vs `ansi` vs `unix`); read them from
  describe_coverage, never guess.
- Do not invent an axis for bands — band selection is `C.red`
  (see induced-operations.md), not a subset.
- A point exactly on a grid-cell boundary resolves to one neighboring cell;
  results at boundary coordinates can legitimately differ by one cell.
