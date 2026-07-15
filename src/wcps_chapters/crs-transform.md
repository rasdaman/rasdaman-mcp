---
description: crsTransform() reprojection to another EPSG CRS with interpolation choice (near/bilinear/…), and GeoTIFF output. Fetch for any reprojection / Web Mercator / CRS task.
---

Reprojects a coverage to another coordinate reference system (resamples the
grid; cell values are interpolated).

OGC 08-068r2 example — transform coverage C (with x and y dimensions) into
the CRS given by URN, with linear interpolation and null resistance "none"
applied to range field red:

```
crsTransform( C,
              { x: "urn:ogc:def:crs:EPSG::63266405",
                y: "urn:ogc:def:crs:EPSG::63266405" },
              { red( linear, none ) } )
```

rasdaman also accepts the short EPSG form and axis names as they appear in
the coverage, and the interpolation set may name just a method:

```
crsTransform( $c, { Lat: "EPSG:4326", Lon: "EPSG:4326" }, { bilinear } )
```

- Give both spatial axes the same target CRS for a normal reprojection; a
  dimension without a CRS entry is not reprojected.
- Interpolation methods: `near` (default), `bilinear`, `cubic`,
  `cubicspline`, `average`.
- GeoTIFF (`"image/tiff"`) is the right output format for reprojected
  results — per the standard, a GeoTIFF response carries the coverage's geo
  coordinates.

Pitfalls:
- Only 2-D (or 2-D slices of) coverages reproject — slice time/elevation
  axes first.
- Different tools/runs produce slightly different output grids for the same
  reprojection — sizes may differ by a few pixels; values change with the
  interpolation method (inherent to resampling, not an error).
- The standard notes a server may refuse some CRS combinations (e.g.
  different CRSs for x and y).
