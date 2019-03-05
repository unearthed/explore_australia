#!/usr/bin/env python
""" file:    test_geometry.py (tests)
    author: Jess Robertson, jess@unearthed.solutions
    date:    Thursday, 03 January 2019

    description: Tests for geometry creation
"""

import unittest
from itertools import product

from shapely.geometry import Point, MultiPolygon
import numpy as np
import pyproj

from explore_generator.geometry import make_box

EPSG_3112_BOUNDS = (-2918276.3772, -5287521.9260, 2362935.9369, -1372651.4100)

def random_points(npt):
    """
    Generate random points in the EPSG:3112 bounds

    Parameters:
        npt - the number of points to generate

    Returns:
        a (2, npt) length iterator over points
    """
    minx, miny, maxx, maxy = EPSG_3112_BOUNDS
    return zip(np.random.uniform(minx, maxx, npt), np.random.uniform(miny, maxy, npt))

class TestStamp(unittest.TestCase):
    """
    Tests for box creation
    """

    def setUp(self):
        "Fixture set up"
        self.distances = (1, 5, 10, 100)
        self.nsquares = (5, 10, 50)
        self.inputs = product(self.distances, self.nsquares)

        # Projections
        self.inproj = pyproj.Proj(init='epsg:3112')
        self.wgs84 = pyproj.Proj(init='epsg:4326')

    def test_make_box(self):
        """
        Check that n boxes with half-width d come out with approximately the correct area
        """
        # Loop over input data
        for distance, nsquares in self.inputs:
            with self.subTest(d=distance, n=nsquares):
                # Generate random points
                pts = [Point(*p) for p in random_points(nsquares)]
                polys = MultiPolygon([
                    make_box(p, distance=distance, npoints=150, projection='epsg:3112')
                    for p in pts
                ])

                # Check total areas - should be roughly size of squares
                expected = (2 * distance * 1000) ** 2 * nsquares # in m^2
                self.assertTrue(np.isclose(polys.area, expected, rtol=1e-1))

    def test_make_box_no_proj(self):
        """
        Check that points with no projection are just WGS84
        """
        # Loop over input data
        for distance, nsquares in self.inputs:
            with self.subTest(d=distance, n=nsquares):
                # Generate random points converted to WGS84
                transform = lambda p: pyproj.transform(self.inproj, self.wgs84, *p)
                pts = [Point(*transform(p)) for p in random_points(nsquares)]
                polys = MultiPolygon([
                    make_box(p, distance=distance, npoints=150, projection=None)
                    for p in pts
                ])
                self.assertEqual(len(polys), nsquares)

    def test_make_box_output_proj(self):
        """
        Check that output conversion works ok
        """
        # Loop over input data
        for distance, nsquares in self.inputs:
            with self.subTest(d=distance, n=nsquares):
                # Generate random points
                transform = lambda p: pyproj.transform(self.inproj, self.wgs84, *p)
                pts = [Point(*transform(p)) for p in random_points(nsquares)]
                polys = MultiPolygon([
                    make_box(p, distance=distance, npoints=150, output_projection='epsg:3112')
                    for p in pts
                ])

                # Check total areas - should be roughly size of squares
                expected = (2 * distance * 1000) ** 2 * nsquares # in m^2
                self.assertTrue(np.isclose(polys.area, expected, rtol=1e-1))

if __name__ == '__main__':
    unittest.main()
