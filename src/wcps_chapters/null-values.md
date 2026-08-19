---
description: null/nodata handling in query expressions. Fetch if the coverage has a null value.
---

A coverage may have a special value declared as a *null* (*nodata*) value.
Rasdaman even allows multiple null values, or an interval, e.g. `[-1:1]`.
Null values can apply to all bands (e.g. `[0]`) or per band (e.g. for RGB `{[0],[255],[255]}`).

Null values are usually ignored in operations, e.g.

- `null+something = null`
- `sum($c with some nulls)` -> nulls are ignored in the sum calculations

A null value can be attached to any expression with a postfix operator:
```
$c NULL VALUES [0]
$c NULL VALUES nullset($anotherCov)
```

To check for null, use the `IS [NOT] NULL` postfix operator, e.g.
to count how many values in $c are NULL:
```
count($c IS NULL)
```

Internally, intermediate results are paired with null masks,
initially calculated from the null value set and the coverage values.

A null mask can be discarded if needed with
```
$c NULL MASK DISCARD
```
A null values set can be discarded with
```
$c NULL VALUES []
```

**Propagation in query expressions**
- Null masks are updated and propagated through all query expressions.
- Null value set is propagated only through operations that do
  not change the values of a coverage: subsetting (spatiotemporal or band), 
  clip, crsTransform, scale, extend, shift, range constructor, overlay, encode;
  other operations will cause the null value set to be dropped.

**Pitfalls**
- `null` on its own is not a valid keyword in queries and will
  lead to a syntax error. To return an invalid value, e.g. in a
  switch, specify an unlikely numeric value, and make it a null value
  if necessary with the `null values [unlikelyValue]` postfix operator.
