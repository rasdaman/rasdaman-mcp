---
description: Aggregation: avg/sum/min/max/count/some/all shorthands and the general 'condense op over $i axis(...) using ...'. Controls WHICH axes are aggregated — needed for per-pixel composites over time and any partial aggregation.
---

Two forms: shorthand reducers and the general condense.

**Shorthands (reduceExpr)** — aggregate a whole expression to one scalar.
OGC 08-068r2 defines them AS general condensers (Table 4):

- `add(a)` (also `sum`) = `condense + over p1 D1(imageCrsDomain(a,D1)), … using a[p1,…]`
- `avg(a)` = `add(a) / |imageCrsDomain(a)|`
- `min(a)` / `max(a)` = `condense min|max over … using a[…]`
- `count(b)` = `condense + over … where b[…] using 1` (b boolean)
- `some(b)` / `all(b)` = `condense or|and over … using b[…]`

Example from the standard: `count( I * B )` — an integer coverage masked by a
boolean one, then counted.

**General condense** (control WHICH axes are aggregated):

```
condense <op>                    -- op: + * max min and or
over $n1 axis1 ( lo1 : hi1 ) [, $n2 axis2 ( lo2 : hi2 ) ]
[ where <boolean using $n1…> ]
using <expression using $n1…>
```

The critical property: axes you do NOT iterate remain axes of the result —
that is how per-pixel composites and moving windows work. The standard's
kernel-filter example (condense over the 3×3 neighbourhood, per output pixel):

```
condense +
over  kx x ( -1 : +1 ),
      ky y ( -1 : +1 )
using C.b[ kx + px , ky + py ] * k[ kx , ky ]
```

(see coverage-constructor for the full filteredImage query it lives in).

Iterator domains are GRID coordinates — get them with `imageCrsDomain(...)`
(see domain-functions), and apply iterators on geo axes as `axis:"CRS:1"($t)`.

Pitfalls:
- Omitting an axis from `over` does NOT error — it silently changes what is
  aggregated. Check the result's dimensionality against your intent.
- Do not manually enumerate slices (many lets + nested max()) — that is what
  condense is for; enumeration explodes query size and often hits limits.
- `count()` needs a boolean argument — `count(b)` per the standard's
  definition, not `count(a)` on a numeric coverage.
- avg over masked data: a 0-filled mask still contributes zeros to avg —
  combine `add()` and `count()` explicitly when you need a conditional mean.
