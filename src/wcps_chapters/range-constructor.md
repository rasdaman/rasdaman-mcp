---
description: Multi-band values {red: e; green: e; blue: e} — building RGB output, combining bands from different coverages, constant bands. Fetch when producing color images or multi-band results.
---

Builds a multi-band cell value from expressions — one entry per band,
separated by SEMICOLONS.

False-color encoding (OGC 08-068r2 example 1) — near-infrared, red and green
bands combined into a 3-band 8-bit image, visually interpretable as RGB:

```
struct
{ red:   (char) L.nir;
  green: (char) L.red;
  blue:  (char) L.green
}
```

Greyscale to RGB (OGC example 2) — a single-band image G with range field
`panchromatic` becomes an RGB-structured image:

```
{ red:   G.panchromatic;
  green: G.panchromatic;
  blue:  G.panchromatic }
```

- The `struct` keyword is optional in rasdaman; the brace form alone works.
- Band names are your choice (they name the output bands); values may be any
  coverage expression over identical domains, or scalars (constant band).
- Also used as the return value of switch cases for color output
  (see switch-case).

Pitfalls:
- Separator is `;` between bands, `:` after the name — never commas.
- All expression entries must share the same domain; a scalar entry adapts to
  the others' domain.
- Output band order = the order written; PNG encoders expect red, green, blue
  (optionally alpha) in that order.
- Cast bands to `(char)` when encoding to 8-bit image formats, as in the OGC
  example above.
