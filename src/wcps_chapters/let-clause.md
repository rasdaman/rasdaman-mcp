---
description: LET bindings: one let keyword, comma-separated $var := expr, reusing subsets, self-referential aggregates (compare a coverage against its own mean). Fetch when repeating subexpressions or hitting let syntax errors.
---

Bind a sub-expression once, reuse it everywhere.

```
FOR-CLAUSE
LET $variable := assignment [ , $variable := assignment ] ...
[ WHERE-CLAUSE ]
RETURN-CLAUSE

assignment ::= coverageExpression | [ dimensionalIntervalList ]
```

1. Scale a subset of Coverage to its original grid size, and add 2x its average to the scaled result:
```
for $c in (Coverage)
let $a := $c[i(0:50), j(0:40)],
    $b := avg($c) * 2
return encode( scale( $a, { imageCrsDomain( $c ) } ) + $b, "image/png" )
```
2. Add 10 to all values of $c subsetted to a spatial domain $dom:
```
for $c in (C)
let $dom := [i(20), j(40)]
return encode( $c[ $dom ] + 10, "application/json" )
```

**Notes**
- Exactly ONE `let` keyword; multiple definitions are comma-separated
  (writing `let` twice is a syntax error).
- Assignment operator is `:=`.
- The second form binds a subset spec (`[ ... ]`) that is later applied as
  `$c[$dom]`.
- Later definitions can reference earlier ones.

**Pitfalls**
- `let` comes AFTER `for` and BEFORE `where`/`return`.
- Every let variable should actually be used; unused bindings are legal but
  a sign the query drifted.
