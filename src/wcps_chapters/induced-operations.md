---
description: Per-cell math: arithmetic, trig, exp/log/sqrt/abs/pow, comparisons producing masks, and/or/not, casts like (int), band selection $c.red, overlay, mask multiplication. Fetch for band math, thresholds, change detection, overflow issues.
---

Operations applied independently to every cell of a coverage ("induced" from
scalar operations). Operands can be coverage+coverage (domains must match) or
coverage+scalar.

- Arithmetic: `+ - * /`, `mod`, `abs(e)`, `round(e)`
- Exponential: `exp(e)`, `log(e)` (base 10), `ln(e)`, `sqrt(e)`, `pow(e, x)`
- Trigonometric: `sin cos tan sinh cosh tanh arcsin arccos arctan`
- Comparison (result is a boolean coverage): `= != > >= < <=`
- Boolean: `and or xor not(e)` — combine masks per cell
- Cast: `(int) e`, `(float) e`, `(char) e`, `(long) e`, `(double) e` —
  truncates, applied per cell.
- Band (field) selection: `C.red` or by position `C.0`
- Overlay: `A overlay B` — B where A is null/zero, else A (layering images)

Examples (all from OGC 08-068r2):

```
sqrt( C + D )        -- square root of the sum of two coverages, per cell
sin( C )             -- replaces every value with its sine
ln( C )              -- natural logarithm of every (nonnegative) value
not C                -- inverts a boolean coverage
(char) ( C / 2 )     -- result range type forced to char (8 bit)
C.red - C.green      -- single-band difference of two bands
C.red + C.green + C.blue   -- sum of a coverage's fields
C * ( C > 0 )        -- mask multiplication: keep positive values, zero the rest
count( I * B )       -- integer coverage masked by boolean, then counted
```

Pitfalls:
- Comparing/adding two subsets works only if their domains align exactly —
  subset both operands identically except for the axis that differs.
- Integer division truncates: use a float literal (`/ 2.0`) when you want a
  float result.
- A boolean coverage is numeric 0/1 in arithmetic — `C * (C > 0)` above is
  the documented masking idiom, often simpler than switch.
- 8-bit unsigned bands wrap on subtraction — cast first: `(int)A - (int)B`.
- Type extension is automatic where possible (boolean < char < short < int <
  float …); an impossible cast raises an exception.
