---
description: Multi-band values {red: $covExpr; green: $scalarExpr; blue: $covExpr } — building RGB output, combining bands from different coverage and scalar expressions. Fetch when producing color images or multi-band results.
---

Builds a multi-band cell value from expressions — one entry per band,
separated by SEMICOLONS.

1. False-color encoding — near-infrared, red and green bands combined 
   into a 3-band 8-bit image, visually interpretable as RGB:
```
{ red:   (unsigned char) $cov.nir;
  green: (unsigned char) $cov.red;
  blue:  (unsigned char) $cov.green
}
```
2. Greyscale to RGB (OGC example 2) — a single-band image $cov with range field
   `panchromatic` becomes an RGB-structured image:
```
{ red: $cov; green: $cov; blue: $cov }
```
3. Red band values are taken from the single-band $cov, while blue and green 
   are set to scalar constants:
```
{ red: $cov; green: 0uc; blue: 200uc }
```

**Notes**
- Band names are your choice (they name the output bands); values may be any
  coverage expression over identical domains, or scalars.
- Often used as the return value of switch cases for color output (see switch-case.md).

**Pitfalls**
- Separator is `;` between bands, `:` after the name — never commas.
- All coverage expressions must share the same domain; a scalar value adapts to
  the others' domain.
- Output band order = the order written; PNG encoders expect red, green, blue
  (optionally alpha) in that order.
- Cast bands to `(unsigned char)` when encoding to 8-bit image formats, if the
  input coverage value is of a different type.
