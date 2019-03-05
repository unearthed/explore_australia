""" file:    vector.py (explore_australia)
    author:  Jess Robertson, @jesserobertson
    date:    Wednesday, 02 January 2019

    description: Vector data handlers
"""

import numpy as np
from shapely.geometry import LineString, Polygon

class LinestringSampler(object):

    """
    Manages resampling of linestrings

    Essentially a utility class which lets us parameterise resamplings
    by specifying positions along the linestring without worrying
    about reprojecting this along the line.

    Parameters:
        points - a list of points defining a path
    """

    norm_tolerance = 1e-10  # eps for managing zero vs nonzero norms

    def __init__(self, linestring):
        # Map the vectors between points
        self.points = np.asarray(linestring.xy).transpose()
        self.vectors = np.diff(self.points, axis=0)
        self.norms = np.linalg.norm(self.vectors, axis=1)

        # Fin unit vectors for each segment
        nonzero = self.norms > self.norm_tolerance
        self.unit_vectors = self.vectors.copy()
        self.unit_vectors[nonzero] /= self.norms[nonzero].reshape((-1, 1))

        # Total path distance
        self.length = self.norms.sum()
        self.cumulative_norm = np.cumsum(self.norms)

    def sample(self, distances):
        """
        Sample distances along our boundary

        Parameters:
            distances - points given as distances along the boundary
        """
        # Return the indices in cumulative norm that each sample
        # would need to be inserted at to maintain the sorted propery
        positions = np.searchsorted(self.cumulative_norm, distances)
        positions = np.clip(positions, 0, len(self.unit_vectors) - 1)
        offsets = np.append(0, self.cumulative_norm)[positions]

        # new points, parameterized as a projection length, direction from
        # an origin vertex
        projection = distances - offsets
        direction = self.unit_vectors[positions]
        origin = self.points[positions]
        return origin + (direction * projection.reshape((-1, 1)))

def resample_linestring_count(linestring, count=None, step=None,
                              step_round=True):
    """
    Given a path along (n, d) points, resample them such that the
    distance traversed along the path is constant in between each of
    the resampled points.

    Note that this will likely clip the corners of the original path,
    and the original vertices are NOT guaranteed to be in the new
    resampled path.

    Only one of count at step can be specified. Specify count for
    uniformly distributed samples (e.g. np.linspace(0, 1, count)), or
    step for a specified step length (e.g. np.arange(0, 1, step))

    Parameters:
        linestring - the linestring containing the path
        count, step - the number of points or a specified step length
            (see above for details)
        step_round - if True and step is specified, adjusts the step
            length so that an integer number of steps is used closest
            to the specified step length.

    Returns:
        an (m, d) set of resampled points on the path
    """
    # Check inputs
    if (count is None and step is None) or (count is not None and step is not None):
        raise ValueError("Only one of count or step can be specified")

    # Generate steps and sampler instance
    sampler = LinestringSampler(linestring)
    if step is not None:
        if step >= sampler.length and not step_round:
            raise ValueError('Step length is longer than the boundary length')
        else:
            # Set a step count so we use an integer number of equally-spaced
            # steps
            count = int(np.ceil(sampler.length / step))
    if count is not None:
        samples = np.linspace(0, sampler.length, count)
    else:
        samples = np.arange(0, sampler.length, step)
    return sampler.sample(samples)

# Default clipping for resampling
DEFAULT_CLIP = [4, np.inf]

def resample(geom, resolution, clip=None, return_points=False):
    """
    Resample a boundary based on some resolution rather than by number of points or step

    Parameters:
        linestring - the shapely.geometry.LineString instance to resample
        resolution - the resolution to resample at
        clip - If None, defaults to [8, 200]
        return_points - if True, returns a list of points located on the boundary
            ready for medial line analysis. If False, returns a shapely LineString
            instance with the resampled data

    Returns:
        depending on return_poly - either a list of points on the boundary or
        a new shapely LineString instance.
    """
    mapping = {
        'Polygon': resample_polygon,
        'LineString': resample_linestring
    }
    try:
        return mapping[geom.geom_type](
            geom,
            resolution=resolution,
            clip=clip,
            return_points=return_points
        )
    except KeyError:
        raise ValueError("Don't know how to resample a {} instance".format(geom.geom_type))

def resample_linestring(linestring, resolution, clip=None, return_points=True):
    """
    Resample a boundary based on some resolution rather than by number of points or step

    Parameters:
        linestring - the shapely.geometry.LineString instance to resample
        resolution - the resolution to resample at
        clip - If None, defaults to [8, 200]
        return_points - if True, returns a list of points located on the boundary
            ready for medial line analysis. If False, returns a shapely LineString
            instance with the resampled data

    Returns:
        depending on return_poly - either a list of points on the boundary or
        a new shapely LineString instance.
    """
    clip = clip or DEFAULT_CLIP
    sampler = LinestringSampler(linestring)
    count = sampler.length / resolution
    count = int(np.clip(count, *clip))
    samples = np.linspace(0, sampler.length, count)
    return sampler.sample(samples) if return_points \
           else LineString(sampler.sample(samples))

def resample_polygon(polygon, resolution=0.01, clip=None, return_points=True):
    """
    Resample the boundaries of a polygon using `resample_linestring`, including
    holes, if any

    Parameters:
        polygon - the shapely.geometry.Polygon instance to resample
        resolution - the resolution to resample at
        clip - If None, defaults to [8, 200]
        return_points - if True, returns a list of points located on the boundary
            ready for medial line analysis. If False, returns a shapely Polygon
            instance with the resampled data

    Returns:
        depending on return_poly - either a list of points on the boundary or
        a new shapely Polygon instance.
    """
    # Helper for resampling
    _rsamp = lambda ls: \
        resample_linestring(ls, resolution, clip or DEFAULT_CLIP)

    # Actually do resampling
    if polygon.interiors:
        result = {
            'shell': _rsamp(polygon.exterior),
            'holes': [_rsamp(i) for i in polygon.interiors]
        }
    else:
        result = {'shell': _rsamp(polygon.exterior)}

    # Work out what we're returning here
    if not return_points:
        result = Polygon(**result)
    elif polygon.interiors:
        result = np.vstack([
            result['shell'],
            np.vstack(result['holes'])
        ])
    else:
        result = result['shell']
    return result