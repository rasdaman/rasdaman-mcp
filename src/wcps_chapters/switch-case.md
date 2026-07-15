---
description: Per-cell conditionals: switch/case/default for classification and color-coding, including the branch type-compatibility rule (mixing scalar and multiband branches fails) and the mask-multiplication alternative.
---

Per-cell conditional evaluation — classification, thresholding to colors,
piecewise functions.

```
SWITCH
  CASE condExp RETURN resultExp
  [ CASE condExp RETURN resultExp ]*
  DEFAULT RETURN resultExpDefault
```

Examples (adapted from the rasdaman geo-services guide):

```
switch
  case $c < 10 return {red: 0;   green: 0;   blue: 255}
  case $c < 20 return {red: 0;   green: 255; blue:   0}
  case $c < 30 return {red: 255; green: 0;   blue:   0}
  default      return {red: 0;   green: 0;   blue:   0}
```

```
switch
  case $c > 0 return log($c)
  default     return 0
```

Constraints (from the guide):
- All condition expressions must return booleans (scalar or coverage) and
  share the same domain.
- All result expressions must share the same domain and compatible types —
  **all scalar, or all the same multiband structure**. Mixing a scalar branch
  with a coverage/multiband branch fails (errors like "Two branches in the
  CASE expression must be scalar or coverage").
- Cases evaluate top-down, least general first: `< 10`, then `< 20`, then
  `< 30`, then default — a more general condition placed earlier shadows the
  later ones.

If you want "value where condition, else 0" you can skip switch entirely and
use the documented masking idiom `C * ( C > 0 )` (see induced-operations) —
always type-safe.

Pitfalls:
- `default return` is mandatory.
- Bind a repeated subset once with `let` instead of repeating it in every
  case (see let-clause) — branches over different domains fail.
