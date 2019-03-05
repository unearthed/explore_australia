""" file:    raster.py (explore_australia)
    author: Jess Robertson, jess@unearthed.solutions
    date:    Tuesday, 05 March 2019

    description: Raster utilities
"""

from rasterio.transform import from_origin
from rasterio.crs import CRS

from .utilities import omerc_projection

def rasterio_reprojection_meta(centre, angle, distance=10, width=250, height=250):
    """
    Return a custom projection and grid transform rotated through some angle
    """
    km = 1000
    half = distance / 2
    return dict(
        driver='GTiff',
        dtype='float32',
        nodata=None,
        count=1,
        width=width,
        height=height,
        transform=from_origin(
            -half * km,
            half * km,
            distance * km / (width - 1),
            distance * km / (height - 1)
        ),
        crs=CRS.from_string(omerc_projection(centre, angle))
    )
