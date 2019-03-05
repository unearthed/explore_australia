""" file:    utilities.py (explore_australia)
    author:  Jess Robertson, @jesserobertson
    date:    Thursday, 03 January 2019

    description: Utilities for explore data generator
"""

from numpy import quantile, nanquantile, clip

def qclip(arr, lower=None, upper=None, finite_only=True):
    """
    Clip an array to lower and upper quantiles

    Parameters:
        arr - the array to clip
        lower, upper - the lower and upper quantiles to clip to
            Must lie in [0, 1]
        finite_only - whether to skip non finite values when
            calculating, quantiles - defaults to True.

    Returns:
        a clipped version of the array
    """
    if lower is None:
        lower = 0
    if upper is None:
        upper = 1

    # Mask out non-finite data with median
    if finite_only:
        minval, maxval = nanquantile(arr, [lower, upper])
    else:
        minval, maxval = quantile(arr, [lower, upper])

    return clip(arr, minval, maxval)

def omerc_projection(centre, angle):
    """
    Get a projection string for a oblique Mercator at some centre point rotated by angle

    Parameters:
        centre - the centre of the box, given as a shapely Point object
        angle - the angle to rotate the box through, in degrees

    Returns:
        a pyproj/Proj4 string for the projection
    """
    centre_lat = centre.y
    centre_lon = centre.x
    return (
        f"+proj=omerc +lat_0={centre_lat} +lonc={centre_lon} +alpha=-{angle} "\
        "+k=1 +x_0=0 +y_0=0 +gamma=0 "
        "+ellps=WGS84 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
    )
