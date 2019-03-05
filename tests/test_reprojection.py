""" file:    test_reprojection.py (tests)
    author: Jess Robertson, jess@unearthed.solutions
    date:    Thursday, 03 January 2019

    description: Reprojection utilities testing
"""

import unittest

from shapely.geometry import Point, MultiPoint, LineString, MultiLineString, \
    GeometryCollection, Polygon, MultiPolygon
import numpy as np

from explore_generator.reprojection import reproject, get_projector

class TestReprojection(unittest.TestCase):

    "Unit test for reprojector"

    def test_identity_proj(self):
        "Check giving the same values gives us the identify function"
        projector = get_projector('epsg:4326', 'epsg:4326')
        geom = Point(135, -43)
        self.assertTrue(np.allclose(geom.xy, projector(*geom.xy)))

    def test_fail_on_unknown(self):
        "An unknown object should raise a valueerror"
        with self.assertRaises(ValueError):
            reproject({}, 'epsg:4326', 'epsg:3112')

    def test_fail_on_unknown_geom(self):
        "Unknown geometries should raise a ValueError"
        geom = GeometryCollection([])
        with self.assertRaises(ValueError):
            reproject(geom, 'epsg:4326', 'epsg:3112')

    def test_reproject_point(self):
        "Check round-trip through reprojection"
        geom = Point(135, -43)
        new_geom = reproject(geom, 'epsg:4326', 'epsg:3112')
        new_new_geom = reproject(new_geom, 'epsg:3112')
        self.assertTrue(np.allclose(geom.xy, new_new_geom.xy))

    def test_reproject_multipoint(self):
        "Check round-trip through reprojection"
        geom = MultiPoint([(135, -43), (165, -25)])
        new_geom = reproject(geom, 'epsg:4326', 'epsg:3112')
        new_new_geom = reproject(new_geom, 'epsg:3112')
        for g, ng in zip(geom, new_new_geom):
            self.assertTrue(np.allclose(g.xy, ng.xy))

    def test_reproject_linestring(self):
        "Check round-trip through reprojection"
        geom = LineString([(135, -43), (165, -25)])
        new_geom = reproject(geom, 'epsg:4326', 'epsg:3112')
        new_new_geom = reproject(new_geom, 'epsg:3112')
        self.assertTrue(np.allclose(geom.xy, new_new_geom.xy))

    def test_reproject_multilinestring(self):
        "Check round-trip through reprojection"
        geom = MultiLineString([[(135, -43), (165, -25)], [(134, -32), (132, -32)]])
        new_geom = reproject(geom, 'epsg:4326', 'epsg:3112')
        new_new_geom = reproject(new_geom, 'epsg:3112')
        for g, ng in zip(geom, new_new_geom):
            self.assertTrue(np.allclose(g.xy, ng.xy))

    def test_reproject_polygon(self):
        "Check round-trip through polygon"
        geom = Polygon([(0, 0), (1, 1), (1, 0)])
        new_geom = reproject(geom, 'epsg:4326', 'epsg:3112')
        new_new_geom = reproject(new_geom, 'epsg:3112')
        self.assertTrue(np.allclose(geom.exterior.xy, new_new_geom.exterior.xy))

    def test_reproject_polygon_holes(self):
        "Check round-trip through polygon"
        geom = Polygon(
            shell=[(-1, -1), (-1, 2), (2, 2), (2, -1)],
            holes=[[(0, 0), (1, 1), (1, 0)]]
        )
        new_geom = reproject(geom, 'epsg:4326', 'epsg:3112')
        new_new_geom = reproject(new_geom, 'epsg:3112')
        self.assertTrue(np.allclose(geom.exterior.xy, new_new_geom.exterior.xy))

    def test_reproject_multipolygon(self):
        "Check roundtrip through reprojection"
        geom = MultiPolygon([
            Polygon([(0, 0), (1, 1), (1, 0)]),
            Polygon(
                shell=[(-1, -1), (-1, 2), (2, 2), (2, -1)],
                holes=[[(0, 0), (1, 1), (1, 0)]]
            )
        ])
        new_geom = reproject(geom, 'epsg:4326', 'epsg:3112')
        new_new_geom = reproject(new_geom, 'epsg:3112')
        for g, ng in zip(geom, new_new_geom):
            self.assertTrue(np.allclose(g.exterior.xy, ng.exterior.xy))

if __name__ == '__main__':
    unittest.main()
