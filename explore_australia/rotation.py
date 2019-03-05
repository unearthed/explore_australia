""" file:    rotation.py (explore_australia)
    author: Jess Robertson, @jesserobertson
    date:    Thursday, 03 January 2019

    description: Rotation of geographic points
"""

from scipy.linalg import expm, norm
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, MultiLineString, LineString, LinearRing, \
    Point, MultiPoint

def rotation_matrix(axis, angle):
    """
    Generate the Rodrigues' rotation matrix about a given axis with
    the given (counterclockwise/right-hand) angle

    Parameters:
        axis - the vector to rotate about
        theta - the amount of rotation, in radians
    """
    unit_axis = axis / norm(axis)
    return expm(np.cross(np.identity(3), unit_axis * angle))

def geographic_to_spherical(points):
    """
    Convert geographic coordinates (longitude, latitude) to spherical
    coordinates (inclination, azimuth)

    Uses the physics/ISO convention, in that theta is the inclination,
    running from 0 to pi, and phi is the azimuth, lying in (0, 2*pi)

    Parameters:
        points - an (N, 2) shaped array of longitude/latitude
            points, in degrees

    Returns:
        an (N, 2) shaped array of (theta/inclination, phi/azimuth)
        points, in radians
    """
    longitude, latitude = points.transpose()
    inclination = np.radians(90 - latitude)
    azimuth = np.radians(longitude + 180)
    return np.vstack([inclination, azimuth]).transpose()

def spherical_to_cartesian(points):
    """
    Convert spherical coordinates (inclination, azimuth) to cartesian
    coordinates (x, y, z) assuming r = 1.

    Uses the physics/ISO convention, in that theta is the inclination,
    running from 0 to pi, and phi is the azimuth, lying in (0, 2*pi)

    Parameters:
        points - an (N, 2) shaped array of (inclination, azimuth)
            points, in radians

    Returns:
        an (N, 3) shaped array of (x, y, z) points, in radians
    """
    inclination, azimuth = points.transpose()
    x = np.sin(inclination) * np.cos(azimuth)
    y = np.sin(inclination) * np.sin(azimuth)
    z = np.cos(inclination)
    return np.vstack([x, y, z]).transpose()

def cartesian_to_spherical(points):
    """
    Convert cartesian coordinates (x, y, z) to spherical coordinates
    (inclination, azimuth) to  assuming r = 1.

    Uses the physics/ISO convention, in that theta is the inclination,
    running from 0 to pi, and phi is the azimuth, lying in (0, 2*pi)

    Parameters:
        points - an (N, 3) shaped array of (x, y, z) points, in radians

    Returns:
        an (N, 2) shaped array of (inclination, azimuth) points,
        in radians
    """
    x, y, z = points.transpose()
    radius = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    inclination = np.arccos(z / radius)
    azimuth = np.arctan2(y, x)
    azimuth[azimuth < 0] += 2 * np.pi
    return np.vstack([inclination, azimuth]).transpose()

def spherical_to_geographic(points):
    """
    Convert spherical coordinates (inclination, azimuth) to geographic
    coordinates (longitude, latitude)

    Uses the physics/ISO convention, in that theta is the inclination,
    running from 0 to pi, and phi is the azimuth, lying in (0, 2*pi)

    Parameters:
        points - an (N, 2) shaped array of (theta/inclination, phi/azimuth)
        points, in radians

    Returns:
        an (N, 2) shaped array of longitude/latitude points, in degrees
    """
    inclination, azimuth = points.transpose()
    latitude = 90 - np.degrees(inclination)
    longitude = np.degrees(azimuth) - 180
    return np.vstack([longitude, latitude]).transpose()

def geographic_to_cartesian(points):
    """
    Convert geographic coordinates (longitude, latitude) into cartesian
    coordinates (x, y, z) assuming r = 1

    Parameters:
        points - an (N, 2) shaped array of longitude/latitude points, in degrees

    Returns:
        a 3 by N array containing cartesian values for the points
    """
    return spherical_to_cartesian(geographic_to_spherical(points))

def cartesian_to_geographic(points):
    """
    Convert cartesian coordinates (x, y, z) into geographic
    coordinates (longitude, latitude) assuming r = 1

    Parameters:
        points - a 3 by N array containing cartesian values for the points

    Returns:
        an (N, 2) shaped array of longitude/latitude points, in degrees
    """
    return spherical_to_geographic(cartesian_to_spherical(points))

def rotate(geom, pole, angle):
    """
    Rotate a shapely {Multi,}Polygon or {Multi,}LineString
    through a given angle on a spherical surface

    Parameters:
        geom - the geometry to rotate, given in WGS84 positions
        pole - the axis through which to rotate the geometry (again in WGS84 positions)
        angle - the angle to rotate the geometry by

    Returns:
        the rotated geometries
    """
    # Construct the rotation axis
    pole = geographic_to_cartesian(np.asarray(pole.coords))[0]
    pole /= norm(pole)

    # Construct the rotation matrix and a function to rotate vectors
    rmatrix = rotation_matrix(pole, np.radians(angle))
    def rotator(points):
        "Rotation function"
        vec = geographic_to_cartesian(points)
        vec_rot = (rmatrix @ vec.T).T
        return cartesian_to_geographic(vec_rot)

    # Handle different geometry types
    mapping = {
        'Point': _point,
        'MultiPoint': _multipoint,
        'Polygon': _polygon,
        'LineString': _linestring,
        'MultiPolygon': _multipolygon,
        'LinearRing': _linearring,
        'MultiLineString': _multilinestring
    }
    try:
        return mapping[geom.geom_type](geom, rotator)
    except KeyError:
        msg = "Don't know how to rotate a {}".format(geom.geom_type)
        raise ValueError(msg)
    except AttributeError:
        raise ValueError("Object doesn't look like a geometry object")

# Reprojection helpers
def _point(geom, rotator):
    return Point(*rotator(np.asarray(geom.coords)))

def _multipoint(geom, rotator):
    return MultiPoint([_point(p, rotator) for p in geom])

def _polygon(geom, rotator):
    if geom.interiors:
        return Polygon(
            shell=_linearring(geom.exterior, rotator),
            holes=[_linearring(i, rotator) for i in geom.interiors]
        )
    else:
        return Polygon(_linearring(geom.exterior, rotator))

def _linestring(geom, rotator):
    return LineString(rotator(np.asarray(geom.coords)))

def _linearring(geom, rotator):
    return LinearRing(rotator(np.asarray(geom.coords)))

def _multipolygon(geom, rotator):
    return MultiPolygon([_polygon(g, rotator) for g in geom])

def _multilinestring(geom, rotator):
    return MultiLineString([_linestring(g, rotator) for g in geom])
