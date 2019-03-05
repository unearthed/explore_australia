""" file:    reprojection.py (explore_australia)
    author:  Jess Robertson, @jesserobertson
    date:    Thursday, 03 January 2019

    description: Reprojection utilities
"""

from functools import partial
import logging

import pyproj
from shapely.geometry import Polygon, MultiPolygon, MultiLineString, \
        LineString, LinearRing, Point, MultiPoint
import numpy as np

LOGGER = logging.getLogger('explore_australia')
GEOJSON_PROJ = 'epsg:4326'  # Default/only projection used by GeoJSON

def get_projector(from_crs, to_crs=None):
    """
    Return a function to reproject something from one
    coordinate reference system (CRS) to another.

    Coordinate references can be specified as PROJ strings
    (e.g. '+datum=WGS84 +ellps=WGS84 +no_defs +proj=longlat'
    see fiona.crs.to_string for more on this) or using EPSG
    codes (e.g. 'epsg:3857').

    Parameters:
        from_crs - the source coordinate reference system
        to_crs - the destination coordinate reference system.
            Optiona, defaults to 'epsg:4326' which is Web
            Mercator projection (to make it easy to pass to
            leaflet maps)
    """
    # Generate pyproj objects from our CRSes
    prjs = [from_crs, to_crs or GEOJSON_PROJ]
    for idx, prj in enumerate(prjs):
        if isinstance(prj, str):
            if prj.lower().startswith('epsg'):
                try:
                    prjs[idx] = pyproj.Proj(init=prj)
                except Exception as err:
                    LOGGER.error("Can't handle {prj}: {err}")
                    raise err
            else:
                prjs[idx] = pyproj.Proj(prj)
        elif isinstance(prj, dict):
            prjs[idx] = pyproj.Proj(**prj)
        else:
            raise ValueError(f'Dont know what to do with {prj}')

    # Generate the function to actually carry out the transforms
    if prjs[0] == prjs[1]:
        _project = lambda *p: p
    else:
        _project = lambda *p: np.asarray(list(partial(pyproj.transform, *prjs)(*p)))
    return _project

def reproject(geom, from_crs=None, to_crs=None, projector=None):
    """
    Reproject a shapely {Multi,}Polygon or {Multi,}LineString
    using a given projector (see `get_projector`).

    Parameters:
        geom - the geometry to reproject
        from_crs - the source coordinate reference system
        to_crs - the destination coordinate reference system.
            Optional, defaults to 'epsg:4326' which is Web
            Mercator projection (to make it easy to pass to
            leaflet maps)

    Returns:
        the reprojected geometries
    """
    # Handle inputs
    from_crs = from_crs or GEOJSON_PROJ
    to_crs = to_crs or GEOJSON_PROJ
    if projector is None:
        projector = get_projector(from_crs, to_crs)

    # Handle different geometry types
    mapping = {
        'Polygon': _polygon,
        'LineString': _linestring,
        'MultiPolygon': _multipolygon,
        'LinearRing': _linearring,
        'MultiLineString': _multilinestring,
        'Point': _point,
        'MultiPoint': _multipoint
    }
    try:
        geom_type = geom.geom_type
        return mapping[geom_type](geom, projector=projector)
    except AttributeError:
        msg = "{} doesn't appear to be a shapely geometry".format(geom)
        raise ValueError(msg)
    except KeyError:
        msg = "Don't know how to reproject a {}".format(geom.geom_type)
        raise ValueError(msg)

# Reprojection helpers
def _point(geom, projector):
    return Point(projector(*geom.xy))

def _multipoint(geom, projector):
    return MultiPoint([_point(p, projector) for p in geom])

def _polygon(geom, projector):
    if geom.interiors:
        reproj = Polygon(
            shell=_linearring(geom.exterior, projector),
            holes=[_linearring(i, projector) for i in geom.interiors]
        )
    else:
        reproj = Polygon(reproject(geom.exterior, projector=projector))
    return reproj

def _linestring(geom, projector):
    return LineString(projector(*geom.xy).T)

def _linearring(geom, projector):
    return LinearRing(projector(*geom.coords.xy).T)

def _multipolygon(geom, projector):
    return MultiPolygon([_polygon(p, projector) for p in geom])

def _multilinestring(geom, projector):
    return MultiLineString([_linestring(p, projector) for p in geom])