---
description: LET bindings: one let keyword, comma-separated $var := expr, reusing subsets, self-referential aggregates (compare a coverage against its own mean). Fetch when repeating subexpressions or hitting let syntax errors.
---

Bind a sub-expression once, reuse it everywhere (rasdaman extension).

```
FOR-CLAUSE
LET $variable := assignment [ , $variable := assignment ] ...
[ WHERE-CLAUSE ]
RETURN-CLAUSE

assignment ::= coverageExpression | [ dimensionalIntervalList ]
```

Both assignment kinds, adapted from the rasdaman geo-services guide:

```
for $c in (C)
let $a := $c[i(0:50), j(0:40)],
    $b := avg($c) * 2
return encode( scale( $c, { imageCrsDomain( $c ) } ) + $b, "image/png" )
```

```
for $c in (C)
let $dom := [i(20), j(40)]
return encode( $c[ $dom ] + 10, "application/json" )
```

- Exactly ONE `let` keyword; multiple definitions are comma-separated
  (writing `let` twice is a syntax error).
- Assignment operator is `:=`.
- The second form binds a subset spec (`[ ... ]`) that is later applied as
  `$c[$dom]`.
- Later definitions can reference earlier ones.
- Note `$b := avg($c) * 2` above: a let can hold an aggregate of the same
  coverage it is later combined with — the pattern for self-referential
  statistics.

Related shorthands (rasdaman): binary `min(A, B)` / `max(A, B)` — cell-wise
minimum/maximum of two compatible coverages.

Pitfalls:
- `let` comes AFTER `for` and BEFORE `where`/`return`.
- Every let variable should actually be used; unused bindings are legal but
  a sign the query drifted.
