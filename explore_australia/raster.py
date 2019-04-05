""" file:    raster.py (explore_australia)
    author: Jess Robertson, jess@unearthed.solutions
    date:    Tuesday, 05 March 2019

    description: Raster utilities
"""

from rasterio.transform import from_origin
from rasterio.crs import CRS

def rasterio_reprojection_meta(crs, distance=10, width=250, height=250):
    """
    Return a custom projection and grid transform rotated through some angle
    """
    kilometres = 1000
    half = distance / 2
    return dict(
        driver='GTiff',
        dtype='float32',
        nodata=None,
        count=1,
        width=width,
        height=height,
        transform=from_origin(
            -half * kilometres,
            half * kilometres,
            distance * kilometres / (width - 1),
            distance * kilometres / (height - 1)
        ),
        crs=CRS.from_string(crs)
    )
