---
description: Overall query shape: for/let/where/return, scalar vs encoded results, multi-coverage queries. Fetch when a whole query is rejected or you are unsure what a valid query skeleton looks like.
---

Every WCPS query has this shape (clauses in this exact order):

```
for $c in (CoverageName), $d in (OtherCoverage)     -- bind coverage variables
let $x := <sub-expression> [, $y := ...]            -- optional aliases (ONE let keyword, comma-separated)
where <boolean scalar expression>                    -- optional filter
return <expression>                                  -- the result
```

- The result is either a **scalar** (number/boolean — needs NO encode) or a
  **coverage**, which MUST be wrapped in `encode(expr, "format")`.
- Coverage names go in parentheses in the for-clause; variables start with `$`.
- Multiple coverages: OGC 08-068r2's example — a server offering coverages
  A, B, C may execute `for $c in ( A, B, C ) return encode( $c.red, "image/tiff" )`
  (the query runs once per listed coverage); binding several variables
  (`for $s in (A), $m in (M)`) lets you combine coverages cell-wise, as in
  the standard's masking example `$s * $m`.
- `where` filters whole coverages via scalar predicates (e.g.
  `where some($m)` in the standard's mask example); it does not mask cells —
  use `C * (C > 0)` style masking or switch for per-cell logic.

A complete query, adapted from the rasdaman geo-services guide:

```
for $c in (C)
let $a := $c[i(0:50), j(0:40)],
    $b := avg($c) * 2
return encode( scale( $c, { imageCrsDomain( $c ) } ) + $b, "image/png" )
```

Pitfalls:
- Do NOT write multiple `let` keywords — one `let`, definitions separated by
  commas.
- Operators are `and`/`or`/`not`, never `&&`/`||`; power is `pow(a,b)`,
  never `^`.
- Band access is `$c.bandName`, never `$c[bandName]` or `$c/bandName`.
- There is no loop/iteration statement; iteration happens only inside
  `coverage ... over` constructors and `condense ... over` aggregations.
