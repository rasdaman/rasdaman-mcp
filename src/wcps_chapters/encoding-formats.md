---
description: encode() formats (png, tiff/GeoTIFF, json, netcdf, csv), what shape each format requires, when NOT to encode (scalars), value rescaling for PNG. Fetch for UnsupportedEncodingFormat or output-format questions.
---

Coverage-valued results must be wrapped in `encode(expr, "format")`; scalar
results (avg, count, a single cell) must NOT be encoded.

| Result | Format string |
|---|---|
| 2-D visualization | `"image/png"` (or `"png"`) |
| Georeferenced raster (reprojection output) | `"image/tiff"` — carries CRS/geo-tags |
| 1-D series, small arrays | `"application/json"` |
| n-D data exchange | `"application/netcdf"` |
| Tabular text | `"text/csv"` |
| Lossy photo-style image | `"image/jpeg"` |

- PNG needs a 2-D result with 1 (gray), 3 (RGB) or 4 (RGBA) 8-bit bands —
  slice all other axes first, cast/scale values into 0..255 if needed.
- JSON output of a 2-D subset is nested arrays; of a 1-D series, a flat array.
- Extra encoder parameters are a third argument, e.g.
  `encode($c, "image/tiff", "compression='LZW'")`.
- decode() (rasdaman) is the inverse — querying data uploaded in the request;
  rarely needed in analytics queries.

Pitfalls:
- "UnsupportedEncodingFormat" usually means the expression's dimensionality
  or band count doesn't fit the format (e.g. 3-D into PNG) — check axes were
  sliced, not trimmed.
- Encoding a scalar (or aggregating to scalar inside encode) errors or wastes
  a roundtrip — return scalars bare.
- Values outside 0..255 in PNG get clamped/wrapped — force the range type
  down explicitly, e.g. the standard's cast example `(char) ( C / 2 )`, or
  cast each band as in the OGC false-color example `(char) L.nir`
  (see range-constructor).
