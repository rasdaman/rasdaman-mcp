---
description: Building a new coverage with 'coverage NAME over $i axis(lo:hi) values expr': histograms, per-row/per-slice statistics, timeseries analysis, and kernel constants (value list) for convolution. Fetch when output has a NEW axis (buckets, per-latitude…).
---

Builds a NEW coverage by iterating over one or more axes and computing a
value per position in the iteration domain.
(For aggregating an existing coverage, see condensers-aggregation.md)

**Syntax**
```
coverage <newName>
over $i axisName(lo:hi) [, $j other(lo:hi)]   -- integer grid bounds
values <expression using $i, $j>
```

**Examples**
1. A 2-D greyscale image with a diagonal shade from white to black:
```
coverage greyshade
over     $px x( 0 : 255 ),
         $py y( 0 : 255 )
values   (unsigned char) (( $px + $py ) / 2.0)
```
2. A 256-bucket histogram over the values of coverage $c:
```
coverage histogram
over     $bucket x( 0 : 255 )
values   count( $c = $bucket )
```
3. Coverage constant (literal cell values) — e.g. a Sobel 3×3 filter kernel:
```
coverage   Sobel3x3
over       $px x( -1 : 1 ), $py y( -1 : 1 )
value list < 1, 2, 1, 0, 0, 0, -1, -2, -1 >
```
4. Applying a 3×3 kernel k to coverage $c with axes x and y:
```
for $c in (Coverage)
let $k := coverage   Sobel3x3
          over       $px x( -1 : 1 ), $py y( -1 : 1 )
          value list < 1, 2, 1, 0, 0, 0, -1, -2, -1 >
return
  encode(
    coverage filteredImage
    over     $px x( x0 : x1 ), $py y( y0 : y1 )
    values   condense +
             over  $kx x( -1 : +1 ), $ky y( -1 : +1 )
             using $c[ x($px + $kx), y($py + $ky) ] * 
                   $k[ x($kx), y($ky) ],
    "image/png")
```

**Pitfalls**
- `over` bounds are integer grid coordinates; take an existing axis's index
  range from `imageCrsDomain()` (see domain-functions.md) and apply iterators
  with `axis:"CRS:1"($i)` on geo-referenced coverages.
- Include EVERY axis the values-expression should vary over — a missing
  iteration axis silently collapses the result.
- Don't use a constructor where a plain induced expression suffices
  (e.g. band math, see induced-operations.md).
