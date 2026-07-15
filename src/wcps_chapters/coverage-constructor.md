---
description: Building a new coverage with 'coverage NAME over $i axis(lo:hi) values expr': histograms, per-row/per-slice statistics, timeseries, and kernel constants (value list) for convolution. Fetch when output has a NEW axis (buckets, per-latitude…).
---

Builds a NEW coverage by iterating one or more fresh axes and computing a
value per position. (For aggregating an existing coverage, see
condensers-aggregation.)

```
coverage <newName>
over $i axisName(lo:hi) [, $j other(lo:hi)]   -- integer grid bounds
values <expression using $i, $j>
```

A 2-D greyscale image with a diagonal shade from white to black
(OGC 08-068r2 example; the cast forces the float division into an integer):

```
coverage greyshade
over     px x ( 0 : 255 ),
         py y ( 0 : 255 )
values   (unsigned char) ( px + py ) / 2
```

A 256-bucket histogram over band b of some coverage C of unknown domain and
dimension (OGC example):

```
coverage histogram
over     bucket x ( 0 : 255 )
values   count( C.b = bucket )
```

**Coverage constant** (literal cell values) — a Sobel 3×3 filter kernel
(OGC example):

```
coverage   Sobel3x3
over       px x ( -1 : 1 ),
           py y ( -1 : 1 )
value list < 1, 2, 1,
             0, 0, 0,
            -1, -2, -1 >
```

Applying a 3×3 kernel k to band b of coverage C with extent x0…x1/y0…y1
(OGC example — constructor over the image domain, condense over the kernel):

```
coverage filteredImage
over     px x ( x0 : x1 ),
         py y ( y0 : y1 )
values   condense +
         over  kx x ( -1 : +1 ),
               ky y ( -1 : +1 )
         using C.b[ kx + px , ky + py ] * k[ kx , ky ]
```

Pitfalls:
- `over` bounds are integer grid coordinates; take an existing axis's index
  range from `imageCrsDomain()` (see domain-functions) and apply iterators
  with `axis:"CRS:1"($i)` on geo-referenced coverages.
- Include EVERY axis the values-expression should vary over — a missing
  iteration axis silently collapses the result.
- Don't use a constructor where a plain induced expression suffices
  (band math needs no constructor).
