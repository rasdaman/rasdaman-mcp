---
description: Per-cell conditionals: switch/case/default for classification and color-coding, including the branch type-compatibility rule (mixing scalar and multiband branches fails) and the mask-multiplication alternative.
---

Per-cell conditional evaluation — classification, thresholding to colors,
piecewise functions. Syntax:

```
SWITCH
  CASE condExp RETURN resultExp
  [ CASE condExp RETURN resultExp ]*
  DEFAULT RETURN resultExpDefault
```

1. Color-code the coverage based on its values:
```
switch
  case $c < 10 return {red: 0uc;   green: 0uc;   blue: 255uc}
  case $c < 20 return {red: 0uc;   green: 255uc; blue:   0uc}
  case $c < 30 return {red: 255uc; green: 0uc;   blue:   0uc}
  default      return {red: 0uc;   green: 0uc;   blue:   0uc}
```
2. Calculate log only at valid coverage values:
```
switch
  case $c > 0 return log($c)
  default     return 0
```

**Constraints**:
- All condition expressions must return booleans, scalar or coverages with the same domain.
- All result expressions must have the same domain and compatible cell types.
- Cases evaluate top-down, least general first: `< 10`, then `< 20`, then
  `< 30`, then default — a more general condition placed earlier shadows the
  later ones.

If you want "value where condition, else 0" you can skip switch entirely and
use the documented masking idiom `C * ( C > 0 )` (see induced-operations) —
always type-safe.

**Pitfalls**
- `default return` is mandatory.
- Bind a repeated subset once with `let` instead of repeating it in every
  case (see let-clause.md).
