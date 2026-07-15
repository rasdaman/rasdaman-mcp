WCPS_CRASH_COURSE = """
# WCPS Crash Course

The OGC Web Coverage Processing Service (WCPS) standard defines a
protocol-independent declarative query language for the extraction, processing,
and analysis of multi-dimensional coverages representing sensor, image, or
statistics data. All WCPS queries follow this template:

    for $covIter1 in (covName, ...),
        $covIter2 in (covName, ...),
        ...
    let $aliasVar1 := covExpr,
        $aliasVar2 := covExpr,
        ...
    where booleanExpr
    return processingExpr

Key Rules:

- `for`: required (at least one coverage iterator)
- `let` and `where`: optional
- `return`: required (final output), contains aggregation or `encode`
- Multiple for iterators = nested loops (Cartesian product)


## Coverage Subsetting

**General syntax:** `covExpr[ axis1(lo:hi), axis2(slice), axis3:"crs"(...), ... ]`

1. `$c[Lat(30:40), Lon(10:20)]`           // Trim Lat/Lon axes
2. `$c[Lat(35:*), Lon(*:15)]`             // * = min/max bound
3. `$c[time("2020-01-01")]`               // Slice on time axis with a date
3. `$c[time("2020-01-01T10:00:00")]`      // Slice on time axis with an ISO datetime
4. `$c[Lat:"EPSG:4326"(30:40)]`           // Trim/slice coordinates in specific CRS
5. `extend($c, {Lat(25:45), Lon(5:25)})`  // Crop while padding with nulls beyond the bounds of $c

## Scalar operations

**Standard operations** applied on scalar operands return scalar results:

- Arithmetic: `+  -  *  /  abs  round  mod  floor  ceil`, Examples: `1.8 / 3`, `avg($c) * 2`
- Exponential: `exp  log  ln  pow  sqrt`, Examples: `pow(3, 2)`,
- Trigonometric: `sin  cos  tan  sinh  cosh  tanh`
- Comparison: `>  <  >=  <=  =  != min max`, Examples: `2 > 1` (true)
- Logical: `and  or  xor  not  bit  overlay`, Examples: `(2 > 1) and (3 != 5)`
- Create multiband value : `{ bandName: value; ..., bandName:  value }`, e.g. `{red: 0c; green: 255c; blue: 0c}`
- Select field from multiband value: `.`, Examples: `sum($rgbCoverage).blue`
- Type casting: `(baseType) value` where baseType is one of: boolean, [unsigned] char / short / int / long, float, double, complex, complex2; Examples: `(char) -2.0`

**Built-in condenser (aggregation) functions**

- numeric coverages: `avg`, `add` / `sum`, `min`, `max`, e.g. `max($cov)`
- boolean coverages: `count` number of true values, e.g. `count($cov.blue > 55uc)`

**General condenser**

- general condenser: `condense op over $iterVar axis(lo:hi), ... where boolScalarExpr using scalarExpr`
- *op* = `+`, `*`, `max`, `min`, `and`, `or`
- `where`: optional

## Coverage operations

**Standard operations**
- `cov op cov`, `cov op scalar`, `scalar op cov`, `op(cov)`, `cov.band`
- *op* is applied pair-wise on each cell from the coverage operands, or on the scalar and each cell from the coverage; result is a coverage.
- **Critical rule:** All coverage operands must have matching domains and CRS; use `scale`, `crsTransform`, and `extend` or subsetting to match coverages.

Examples:
- `pow($c, 2.0)` (squares each element of coverage $c)
 - **Critical:** operator `^` does not exist, use `pow` instead
- `sin($cov)` (applies sine on each element of the coverage)
- `$c.red <= 120` (compares each element of the red band <= 120)
- `$c.red <= 120 and $c.green > 150`
- `(unsigned char) $c` (cast all elements of $c to unsigned char, 0-255 values)

**Resample (scale)**
- `scale($c, {Lat(0:100), Lon(0:200)})` - To specific grid size
- `scale($c, {imageCrsDomain($otherCov)})` - To match another coverage's domain
- `scale($c, 2.0)` - By factor (f > 1 for scaling up, 0 < f < 1 scale down)
- `scale($c, {Lat(0.5), Lon(2.0)})` - By factor per-axis

**Reproject (crsTransform)**
- Full syntax:
```
crsTransform($c,
 { Lat:"EPSG:4326", Lon:"EPSG:4326" },        // Target CRS per axis
 { bilinear },                                // Interpolation (near, bilinear, cubic, etc.)
 { Lat:0.5, Lon:domain($d, Lat).resolution }, // Optional output resolution
 { Lat(30.5:60.5), Lon(50.5:70.5) }           // Optional crop output domain
)
```
- Shorthand CRS for all axes: `crsTransform($c, "EPSG:4326", { bilinear })`

**Conditional evaluation**
```
switch
case $c < 0 return 0uc
case $c > 100 return 255uc
default return $c
```

**Coverage construction**
```
coverage covName
over $iterVar axis(lo:hi), ...
values scalarExpr
```

**General condenser on coverages**
- aggregate whole coverage values (cell-wise) produced by the `using` clause
```
condense op
over $iterVar axis(lo:hi), ...
[ where boolScalarExpr ]
using covExpr
```

**Constant coverage**
```
coverage covName
over $iterVar axis(lo:hi), ...
value list <0;1>
```

**Encode**
- Always wrap final result in encode() for data export (unless the top expression produces scalar, like aggregation or subset slicing all axes).
```
encode($c[time("..")], "image/png")  // Raster format for visualizing 2D results: PNG, JPEG, TIFF, and any format supported by GDAL
encode($c, "application/json")       // JSON format (best for 1-D results)
encode($c, "netcdf")                 // netCDF (3D or higher-dimension results)
$c[time(t), Lat(y), Lon(x)]          // No encode needed, result is a scalar value
avg($c[time(t)])                     // No encode needed
```

## Atomic types & Literals

Atomic types:
- `boolean`
- `char` (signed 8-bit), `unsigned char`, `short`, `unsigned short`, `int`, `unsigned int`
- `float`, `double`
- `cint16`, `cint32`, `complex` (complex of `float`), `complexd` (complex of `double`)

Number literals with a suffix:
- `-3c` -> char (c)
- `255uc` -> unsigned char (uc)
- `-2000s` -> short (s)
- `1000us` -> unsigned short (us)
- `13l` == `13` -> int (l or none)
- `393ul` -> unsigned int (ul)
- `0.5f` -> float (f)
- `12.3d` == `12.3` -> double (d or none)

**Critical:** Without suffix, `5` -> `int`, `5.0` -> `double`

## Metadata operations

- `imageCrsDomain(cov, axis)` - Grid (lo, hi) bounds
- `imageCrsDomain(cov, axis).lo` - Grid lower bound (`.hi` for upper bound)
- `domain(cov)` - Geo (lo, hi) bounds of all axes
- `domain(cov, axis)` - Geo (lo, hi) bounds
- `domain(cov, axis).lo` - Geo lower bound (`.hi` for upper bound)
- `domain(cov, axis, crs)` - Geo (lo, hi) bounds in a crs
- `domain(cov, axis, crs).lo` - Geo lower bound in a crs (`.hi` for upper bound)
- `nullSet(cov)` - Null values of cov
- `cellCount(cov)` - Total number of grid pixels

## LLM Generation Checklist

Before outputting a WCPS query, verify:

- **Required clauses:** `for ... return ...` present
- **Coverage names:** Valid identifiers (no quotes/spaces)
- **Axis labels:** Match coverage metadata (case-sensitive: `Lat` ≠ `lat`)
- **CRS syntax:** `"EPSG:4326"` or full URI `"http://.../EPSG/0/4326"`
- **Brackets:** Subsetting uses `[...]`, `extend`/`scale` use `{...}`
- **Semicolons:** Only in multiband literals `{r:100; g:50; b:25}`
- **Encoding:** Final output wrapped in `encode(..., "format")` for data export
- **Boolean/comparison operators:** WCPS uses `and`/`or` (not `&&`/`||`), `!=` (not `<>`)

## Quick Reference Template

- Result is coverage (an array, not scalar number or boolean value):
```
for $cov in (your_coverage_name)
[let $var := expression]...
[where boolean_condition]
return encode(
  coverage-producing-expression,
  "output_format"
)
```
- Result is scalar:
```
for $cov in (your_coverage_name)
[let $var := expression]...
[where boolean_condition]
return sum(coverage-producing-expression)
```

**Critical:** operator `^` does not exist, use `pow` instead.
**Critical:** to select a band use `.`, e.g. `$c.u10`. Do not use spatio-temporal subsetting for bands!
**Critical:** alias definitions in `let` are separated by commas (not semicolons, or new lines!); the syntax is `let alias := def, alias := def, ...`
**Critical:** in encode use 'image/png' for visualizing 2-D image results, netcdf for n-D results, and json for 1-D small timeseries; avoid encode to 'application/gml+xml'.
**Critical:** scalar results do NOT need encode, e.g. when all axes/dimensions are sliced in the query.
**Critical:** Always apply spatio-temporal subsets, as a user does not generally want to get GBs of data as a result. Subsetting examples:

1. `$c[Lat(30:40), Lon(10:20)]`           // Trim Lat/Lon axes
2. `$c[Lat(35:*), Lon(*:15)]`             // * = min/max bound
4. `$c[Lat:"EPSG:4326"(30:40)]`           // Trim/slice coordinates in specific CRS
3. `$c[time("2020-01-01")]`               // Slice on time axis with a date
3. `$c[time("2020-01-01T10:00:00")]`      // Slice on time axis with an ISO datetime
"""

WCPS_UDFS = """
## UDFs (user-defined functions)

UDFs can be invoked like regular functions, except they are grouped in a namespace:
`namespace.function_name(parameters)`. E.g. `image.Stretch($cov)`, `stats.Var_pop($cov)`, etc.

The `list_coverages` tool also returns a list of available UDFs on the server
(if any have been registered).
"""

WCPS_CRASH_COURSE += """

## Need more detail?

This crash course is intentionally brief. Detailed per-topic documentation is
available as chapters: call `wcps_doc_chapters()` to list them (each with a
description of when to use it), then `wcps_get_chapter(name)` to read one.
If a query fails and the error is unclear, fetch the `common-errors` chapter
first — it maps error symptoms to concrete fixes.
"""
