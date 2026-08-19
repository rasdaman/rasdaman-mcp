---
description: FLIP $c ALONG axis (mirror an axis) and SORT $c ALONG axis [ASC|DESC] BY rankExpr (reorder slices). Keyword operators, not functions. Fetch for mirror/reverse/reorder tasks.
---

Two rasdaman extensions that reorder cells along an axis.

**FLIP — mirror an axis:**
Syntax:
```
flipExp: FLIP coverageExpression ALONG axisLabel
```
Example:
```
for $c in (C)
return encode( FLIP $c[x(0:100), y(0:100)] ALONG x, "image/png" )
```

Domain, type and dimensionality are unchanged — only the cell order along the
named axis reverses. Works on any coverage expression, e.g.
`FLIP $c + 20 ALONG t` on a 3-D timeseries reverses time order.

**SORT — reorder slices along an axis by a computed rank:**
Syntax:
```
sortExp: SORT coverageExp ALONG sortAxis [ASC|DESC] BY cellExp
```
Examples:
```
for $c in (C)
return encode( SORT $c ALONG x BY $c[y(0)], "image/png" )

for $c in (C)
return encode( SORT $c.b ALONG t DESC BY add($c), "json" )
```

The coverage is sliced along `sortAxis`; `cellExp` produces one scalar rank
per slice; slices are rearranged by rank (ASC default).

**Pitfalls**
- These are keyword operators, not functions: `FLIP $c ALONG x`, never
  `flip($c, x)`.
- In SORT's `BY` expression, do not subset the sort axis itself.
- Geo coordinates of the sorted/flipped axis are NOT updated — only cell
  order changes (the guide notes the flipped axis appears with a minus sign
  in gml:sequenceRule).
- If FLIP is unavailable, a coverage constructor iterating the axis in
  reverse (`values $c[x:"CRS:1"(hi - $i)]`) achieves the same.
