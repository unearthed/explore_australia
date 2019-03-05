""" file:    geometry.py (explore_australia)
    author:  Jess Robertson, @jesserobertson
    date:    Wednesday, 02 January 2019

    description: Creating postage stamps for geospatial learners
"""

from shapely.geometry import LineString, Point
from shapely.ops import polygonize
import pint
import numpy as np

from .reprojection import reproject
from .rotation import rotate

# Constances
UNITS = pint.UnitRegistry()
EARTH_RADIUS = 6.3781e6 * UNITS.m

def linterpolate(point_a, point_b, npoints=2):
    """
    Return an interpolated linestring between two points

    Parameters:
        a, b - two `shapely.geometry.Points` to interpolate between
        npoints - the number of points in the interpolation

    Returns:
        a LineString with the interpolated points
    """
    return LineString(zip(np.linspace(point_a.x, point_b.x, npoints),
                          np.linspace(point_a.y, point_b.y, npoints)))

def make_box(centre, distance, projection=None, output_projection=None, npoints=2):
    """
    Make a box constructed about a centre point, with a length of approximately distance

    Note that becase we are constructing a box on the surface of the earth, you might not
    get back an exact square

    Parameters:
        centre - the centre of the box, given as a shapely Point object
        distance - the approximate length of the sides of the box (in km)
        projection - the projection of the input points as an EPSG code. If None then we
            assume WGS-84 (EPSG:4326, aka longitude and latitude).
        output_projection - the output projection of the polygon as an EPSG code. If None
            we use the same projection as the input projection.
        npoints - number of points on the side, must be >= 2. If 2 then only the corners are
            returned. If > 2 then the lines will be interpolated and a polygon returned in
            decimal degrees (you should use proj to reproject)

    Returns:
        a geometry with either an approximated polygon or a box approximating the polygon
    """
    # Constants and units
    distance = distance * UNITS.km

    # Project input points to WGS84 -> radians
    if projection is None:
        lon0, lat0 = (centre.xy * UNITS.deg).to('rad')
    else:
        lon0, lat0 = (reproject(centre, projection, 'epsg:4326').xy * UNITS.deg).to('rad')

    # Construct difference in latitude first (since this is independent of longitude)
    angular_dist = (distance / EARTH_RADIUS) * UNITS.rad
    lat1 = lat0 - angular_dist / 2
    lat2 = lat0 + angular_dist / 2

    # For each corner, construct the minimum and maximum seperately
    delta_lon = lambda lat: angular_dist / np.cos(lat)
    to_point = lambda x, y: Point(x.to('deg').magnitude, y.to('deg').magnitude)
    top_left = to_point(lon0 - delta_lon(lat1) / 2, lat1)
    top_right = to_point(lon0 + delta_lon(lat1) / 2, lat1)
    bottom_left = to_point(lon0 - delta_lon(lat2) / 2, lat2)
    bottom_right = to_point(lon0 + delta_lon(lat2) / 2, lat2)

    # Interpolate along sides, reproject
    top = linterpolate(top_left, top_right, npoints)
    right = linterpolate(top_right, bottom_right, npoints)
    bottom = linterpolate(bottom_left, bottom_right, npoints)
    left = linterpolate(bottom_left, top_left, npoints)
    shape = next(polygonize((top, right, bottom, left)))

    # Handle reprojection logic
    if output_projection is None and projection is not None:  # go back from wgs84
        shape = reproject(shape, 'epsg:4326', projection)
    elif output_projection is not None:  # output projection specified so just use it
        shape = shape = reproject(shape, 'epsg:4326', output_projection)
    elif output_projection is None and projection is None: # want WGS84 so do nothing
        pass
    else:
        raise AssertionError("Invalid input/output projection specification")

    return shape

def make_stamp(centre, angle=None, distance=25):
    """
    Make a rotated box with some angle and size

    Parameters:
        centre - the centre of the box, given as a shapely Point object
        angle - the angle to rotate the box through, in degrees
        distance - the approximate length of the sides of the box (in km)
    """
    angle = angle or np.random.uniform(0, 360)
    return rotate(make_box(centre, distance=distance), centre, angle)
