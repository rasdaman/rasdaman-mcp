---
description: Symptom-to-fix table for frequent failures: syntax traps (let/and/pow/band access), switch branch types, InvalidAxisLabel, InvalidSubsetting, WKT cast errors, encoding mismatches, byte overflow, integer-literal limits, missing condense axes. Fetch FIRST when a query fails and the error is unclear.
---

The most frequent WCPS failure modes and their actual fixes. If a query
errors, find the matching symptom here BEFORE rewriting from scratch.

- **SyntaxError near a keyword** — usually one of: two `let` keywords (only
  one allowed, comma-separate); `&&`/`||` instead of `and`/`or`; `^` instead
  of `pow()`; `$c[band]` instead of `$c.band`; a shell/SQL habit leaking in
  (WCPS has no uppercase FOR/RETURN requirement but also no `SELECT`, no
  file operations, no variables without `$`).
- **"Two branches in the CASE expression must be scalar or coverage"** —
  switch branches mix scalar and multiband/coverage types. Make all branches
  the same shape, or replace switch with mask multiplication
  (see switch-case).
- **InvalidAxisLabel** — axis name wrong or case-mismatched; check
  describe_coverage. Also raised by inventing an axis (e.g. `band(...)` —
  band selection is `$c.red`).
- **InvalidSubsetting** — subset outside the coverage extent, lo > hi, or geo
  coordinates given where grid (CRS:1) expected / vice versa.
- **WKT / AbstractWKTShape cast error in clip()** — WKT was quoted as a
  string, or vertex order doesn't match the coverage axis order
  (see clipping-wkt).
- **UnsupportedEncodingFormat** — expression dimensionality/band count does
  not fit the format: slice remaining axes for PNG, or pick netcdf/json
  (see encoding-formats).
- **Invalid long literal / integer overflow** — an arithmetic constant beyond
  32-bit (e.g. positional encodings like 10^12). Redesign: WCPS is not for
  sequential/stateful logic; compute per-cell or aggregate instead.
- **Unsigned byte wraparound** — subtracting 8-bit bands gives huge values
  instead of negatives: cast first, `(int)$a - (int)$b`.
- **Result silently has wrong shape** — a condense/constructor `over` clause
  is missing an axis, or an axis you meant to slice was trimmed. Verify the
  result's dimensionality against the intent (see condensers-aggregation).
- **Repeating a 12-way manual enumeration** (12 lets + nested max/sum) — the
  language has condense for this; enumeration is a smell that also hits
  size/limit errors.
- **503 / server unavailable during retries** — back off; the failure is not
  in your query. Do not hammer the endpoint in a tight loop.
