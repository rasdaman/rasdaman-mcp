---
description: crsTransform() reprojection to another EPSG CRS with interpolation choice (near/bilinear/…), and GeoTIFF output. Fetch for any reprojection / Web Mercator / CRS task.
---

Reprojects a coverage to another coordinate reference system (resamples the
grid; cell values are interpolated).

For example, to transform a coverage $c (with x and y axes) into
the CRS given by "EPSG:4326", with bilinear interpolation:
```
crsTransform( $c, { x: "EPSG:4326", y: "EPSG:4326" }, { bilinear } )
```
Or shorter form:
```
crsTransform( $c, "EPSG:4326", { bilinear } )
```
Further optional parameters allow to also rescale the grid to a given resolution
(per axis), and crop the result, e.g.
```
crsTransform( $c, "EPSG:4326", { bilinear },
              { Lat:0.5, Lon:-0.5 },          -- rescale reprojected result to axis resolutions
              { Lat(30.5:60.5), Lon(40:60) }  -- crop reprojected result
            )
```

**Notes**
- An axis without a CRS entry is not reprojected; prefer the short form of
  single CRS ("EPSG:4326") applying automatically to the spatial axes.
- Interpolation methods: `near` (default), `bilinear`, `cubic`,
  `cubicspline`, `lanczos`, `average`.
- GeoTIFF (`"image/tiff"`) is usually a best output format for reprojected
  2D results when preserving the geo-referencing information in the output
  is important.

**Pitfalls**
- Only 2-D (or 2-D slices of) coverages reproject — slice any time/elevation
  axes first on the coverage when applying crsTransform to it.
- Different tools/runs produce slightly different output grids for the same
  reprojection — sizes may differ by a few pixels; values change with the
  interpolation method (inherent to resampling, not an error).
