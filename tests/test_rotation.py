""" file:    test_rotation.py (tests)
    author: Jess Robertson, jess@unearthed.solutions
    date:    Thursday, 03 January 2019

    description: Tests for rotation code
"""

import unittest

import numpy as np
from scipy.linalg import norm
from shapely.geometry import LineString, Polygon, Point, \
    MultiLineString, MultiPolygon, MultiPoint, LinearRing

from explore_australia.rotation import \
    geographic_to_spherical, spherical_to_geographic, \
    spherical_to_cartesian, cartesian_to_spherical, \
    geographic_to_cartesian, cartesian_to_geographic, \
    rotation_matrix, rotate
from explore_australia.geometry import make_box

class TestRotation(unittest.TestCase):

    "Unit tests for rotation code"

    def test_conversions(self):
        "Check conversions between geographic <-> spherical <-> cartesian"
        # Do a round-trip check for conversions
        line = LineString([
            (-139, 0), (0, 90), (90, -90), (130.0, -34.0),
            (131.0, -35.0), (132.0, -36.0), (130.0, -37.0),
            (131.0, -38.0), (132.0, -39.0)
        ])
        points = np.asarray(line.coords)
        npts = points.shape[0]

        # Checking all the way though...
        spoints = geographic_to_spherical(points)
        self.assertEqual(spoints.shape, (npts, 2))
        cpoints = spherical_to_cartesian(spoints)
        self.assertEqual(cpoints.shape, (npts, 3))
        spoints2 = cartesian_to_spherical(cpoints)
        self.assertEqual(spoints2.shape, (npts, 2))
        self.assertTrue(np.allclose(spoints2, spoints))
        points2 = spherical_to_geographic(spoints2)
        self.assertEqual(points2.shape, points.shape)
        self.assertTrue(np.allclose(points2, points))

        # Check one-hit
        cpoints2 = geographic_to_cartesian(points)
        self.assertEqual(cpoints2.shape, (npts, 3))
        self.assertTrue(np.allclose(cpoints2, cpoints))
        points3 = cartesian_to_geographic(cpoints2)
        self.assertEqual(points3.shape, points.shape)
        self.assertTrue(np.allclose(points3, points))

    def test_rotation(self):
        "Check rotation works ok"
        # Generate some data to play with
        centre = Point([116.35, -42.01])
        box = make_box(centre, distance=10)
        theta = 34.  # degrees

        # Convert centre to a cartesian vector
        pole = geographic_to_cartesian(np.asarray(centre.coords))[0]
        pole /= norm(pole)

        # Get a rotation matrix - check that we actually have one
        M = rotation_matrix(pole, np.radians(theta))
        self.assertTrue(np.allclose(np.identity(3), M @ M.T))
        self.assertTrue(np.allclose(1, np.linalg.det(M)))

        # Rotate the box to get what we want
        exterior = np.asarray(box.exterior.coords)
        v = geographic_to_cartesian(exterior)
        v_rot = (M @ v.T).T
        box_rot = Polygon(cartesian_to_geographic(v_rot))

        # Check that we've still got the same centre (shouldn't change
        # under SO(3))
        self.assertTrue(np.allclose(
            np.asarray(box.centroid.coords),
            np.asarray(box_rot.centroid.coords)
        ))

    def test_rotate_function(self):
        "Check rotation about pole doesn't change location"
        centre = Point([116.35, -42.01])
        box = make_box(centre, distance=10)
        for angle in np.random.uniform(0, 2 * np.pi, 10):
            rbox = rotate(box, box.centroid, angle)
            self.assertTrue(np.allclose(
                np.asarray(rbox.centroid.coords),
                np.asarray(box.centroid.coords)))

    def test_rotate_function_geometries(self):
        "Check rotation about pole doesn't change location"
        geoms = [
            Point([116.35, -42.01]),
            MultiPoint([(135, -43), (165, -25)]),
            LineString([
                (-139, 0), (0, 90), (90, -90), (130.0, -34.0),
                (131.0, -35.0), (132.0, -36.0), (130.0, -37.0),
                (131.0, -38.0), (132.0, -39.0)
            ]),
            MultiLineString([
                [(-139, 0), (0, 90), (90, -90), (130.0, -34.0)],
                [(131.0, -35.0), (132.0, -36.0), (130.0, -37.0)],
                [(131.0, -38.0), (132.0, -39.0)]
            ]),
            Polygon([(0, 0), (1, 1), (1, 0)]),
            Polygon(
                shell=[(-1, -1), (-1, 2), (2, 2), (2, -1)],
                holes=[[(0, 0), (1, 1), (1, 0)]]
            ),
            MultiPolygon([
                Polygon([(0, 0), (1, 1), (1, 0)]),
                Polygon(
                    shell=[(-1, -1), (-1, 2), (2, 2), (2, -1)],
                    holes=[[(0, 0), (1, 1), (1, 0)]]
                )
            ]),
            LinearRing([(-1, -1), (-1, 2), (2, 2), (2, -1)])
        ]

        centre = Point([116.35, -42.01])
        for geom in geoms:
            for angle in np.random.uniform(0, 2 * np.pi, 10):
                with self.subTest(geom=geom.geom_type, angle=angle):
                    rgeom = rotate(geom, centre, angle)
                    self.assertTrue(rgeom is not None)
                    self.assertEqual(rgeom.geom_type, geom.geom_type)

if __name__ == '__main__':
    unittest.main()
