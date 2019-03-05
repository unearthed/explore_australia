""" file:    coverage.py (explore_australia)
    author:  Jess Robertson, @jesserobertson
    date:    Wednesday, 02 January 2019

    description: Coverage data getting
"""

import logging

from shapely.geometry import box
from owslib.wcs import WebCoverageService
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np

LOGGER = logging.getLogger('explore_australia')

def rotate_raster(input_raster, output_raster, angle, band=1):
    """
    Rotate a raster dataset through a given angle about the centre of the dataset

    This rotates the grid from N/E alignment while keeping the same resolution. Also
    handles masks nicely.

    Parameters:
        input_raster - the input geotiff to use
        output_raster - the output raster to use
        angle - the angle to rotate the output raster through
        band - the band to use (defaults to the first)
    """
    # Open first raster
    with rasterio.open(input_raster) as src:
        src_data = src.read(band, masked=True)
        has_mask = np.ma.is_masked(src_data)
        if has_mask:
            # Convert mask to gdal version
            src_mask = (~src_data.mask * 255).astype(rasterio.uint8)
            src_data = src_data.data

        # Construct a new projection using a local oblique mercator projection
        centre_latitude = (src.bounds.top + src.bounds.bottom) // 2
        centre_longitude = (src.bounds.left + src.bounds.right) // 2
        crs = (
            f"+proj=omerc +lat_0={centre_latitude} +lonc={centre_longitude} +alpha={-angle} "
            "+k=1 +x_0=0 +y_0=0 +gamma=0 +ellps=WGS84 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
        )

        # Calculate new transform from the source
        transform, width, height = calculate_default_transform(
            src.crs, crs, src.width, src.height, *src.bounds)

        # Warp data into a new array
        data = np.empty((width, height), dtype=rasterio.float32)
        reproject(src_data, data, src_crs=src.crs, src_transform=src.transform,
                  dst_crs=crs, dst_transform=transform)

        # Need to handle mask seperately for some reason
        if has_mask:
            mask = np.empty((width, height), dtype=rasterio.uint8)
            reproject(src_mask.astype(rasterio.uint8), mask,
                      src_crs=src.crs, src_transform=src.transform,
                      dst_crs=crs, dst_transform=transform,
                      resampling=Resampling.nearest)

        # Next we crop the grid so that it is the same size as the original
        wanted_width, wanted_height = src.shape
        assert wanted_width % 2 == 1, 'width resolution not odd'
        assert wanted_height % 2 == 1, 'height resolution not odd'
        width_buffer = (width - wanted_width) // 2
        height_buffer = (height - wanted_height) // 2
        data = data[width_buffer:-width_buffer,
                    height_buffer:-height_buffer]
        if has_mask:
            mask = mask[width_buffer:-width_buffer,
                        height_buffer:-height_buffer]

        # Make a new dataset with the source metadata, warp original geotiff into new band
        with rasterio.open(output_raster, 'w', **src.meta) as sink:
            sink.write(data, band)
            if has_mask:
                sink.write_mask(mask)

def read_to_maskedarray(geotiff, layer_id=1):
    """
    Use rasterio to read a geotiff into a masked array

    Parameters:
        geotiff - a path to a GeoTIFF file
        layer_id - the layer index to use. Optional, defaults
            to 1 (note raster indices start at 1)

    Returns:
        a masked array representing a particular band
    """
    with rasterio.open(geotiff, 'r') as src:
        band = np.ma.MaskedArray(
            data=src.read(layer_id),
            mask=~src.read_masks(layer_id).astype(bool))
    return band


class CoverageService:

    """
    Manages getting data from a Web Coverage Service

    Parameters:
        url - the URL pointing to the WCS endpoint
    """

    def __init__(self, url):
        "Initialize using a URL"
        self.wcs = WebCoverageService(url)

    def __call__(self, bbox, layer=None, output=None):
        """
        Get the coverage in the given box

        Parameters
            bbox - a bounding box given as (minx, miny, maxx, maxy)
            layer - the layer to pull from. Optional, if not specified
                this defaults to the first layer from the service
                (see self.default_layer).
            output = the name of the output file. Optional, if not specified
                this is just `f'{layer}.tif'` in the local directory

        Returns:
            the name of the output geotiff
        """
        if layer is None:  # just use first
            layer = self.default_layer
        if output is None:  # just use layer name
            output = f"{layer}.tif"

        # Make request
        LOGGER.debug(f'Getting coverage for {layer}')
        response = self.wcs.getCoverage(
            identifier=layer,
            bbox=self.snap_bounds(bbox, layer),
            format='GeoTIFF_Float'
        )

        # Dump to geotiff
        if response._response.ok:
            with open(output, 'wb') as sink:
                LOGGER.debug(f'Dumping to {output}')
                sink.write(response.read())
        else:
            raise IOError('Something went wrong getting raster!')
        return output

    @property
    def default_layer(self):
        "Pick a default layer for the coverage service"
        try:
            return self._default_layer
        except AttributeError:
            self._default_layer = next(iter(self.wcs.contents.keys()))
            return self._default_layer

    def snap_bounds(self, bounds, layer=None):
        "Snap a bounding box to the bounds of the coverage"
        if layer is None:
            layer = self.default_layer
        return box(*bounds)\
                   .intersection(box(*self.wcs[layer].boundingBoxWGS84))\
                   .bounds
