---
description: Aggregation: avg/sum/min/max/count/some/all shorthands and the general 'condense op over $i axis(...) using ...'. Controls WHICH axes are aggregated — needed for per-pixel composites over time and any partial aggregation.
---

Two forms: shorthand reducers and the general condense.

**Shorthands (reduceExpr)** — aggregate a whole expression to one scalar:

- `add(a)` = `sum(a)` = `condense + over $p1 axis1(imageCrsDomain(a, axis)), … using a[axis1($p1),…]`
- `avg(a)` = `add(a) / cellcount(a)`
- `min(a)` / `max(a)` = `condense min/max over … using a[…]`
- `count(b)` = `condense + over … where b[…] using 1` (b boolean)
- `some(b)` / `all(b)` = `condense or/and over … using b[…]`
- `cellcount(a)` = number of values in a
  (in contrast to `count(b)` which is the number of true values)

Example: `count( $c > 10 )` — number of values in $c greater than 10.

**General condense** (control WHICH axes are aggregated):

Syntax:
```
condense <op>        -- <op>: + * max min and or
over $it1 axis1( lo1 : hi1 ) [, $it2 axis2( lo2 : hi2 ) ]...
[ where <boolean using $it1…> ]
using <expression using $it1…>
```

The critical property: axes you do NOT iterate remain axes of the result —
that is how per-pixel composites and moving windows work. For example,
average monthly precipitation in 2010 (assuming the ansi axis of $c has 
monthly resolution):
```
condense +
over  $pt ansi( "2010-01" : "2010-12" )
using avg( $c[ ansi($pt) ] )
```
Or, count how many months in 2023 have average temperature exceeding 20C:
```
condense +
over  $pt ansi( "2023-01" : "2023-12" )
using avg( $c[ ansi($pt) ] ) > 20
```
Another way to calculate the same is with a coverage constructor and count(b):
```
count(coverage averageTempPerMonth
      over  $pt ansi( "2023-01" : "2023-12" )
      values avg( $c[ ansi($pt) ] ) > 20)
```

Iterator domains are GRID coordinates — get them with `imageCrsDomain(...)`
(see domain-functions.md) or specify manually (e.g. `0:10`), 
and apply iterators on geo axes as `axis:"CRS:1"($t)`.

**Pitfalls**
- Omitting an axis from `over` does NOT error — it silently changes what is
  aggregated. Check the result's dimensionality against your intent.
- Do not manually enumerate slices (many lets + nested max()) — that is what
  condense is for; enumeration explodes query size and often hits limits.
- `count(b)` needs a boolean argument, not `count(a)` on a numeric coverage.
- avg over masked data: a 0-filled mask still contributes zeros to avg —
  combine `add()` and `count()` explicitly when you need a conditional mean.
