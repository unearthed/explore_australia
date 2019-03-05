#!/usr/bin/env python
""" file:    test_coverage.py (tests)
    author:  Jess Robertson, jess@unearthed.solutions
    date:    Thursday, 03 January 2019

    description: Tests for coverage wrangling
"""

import unittest
from pathlib import Path

import numpy as np
import rasterio
import requests

from explore_australia.coverage import read_to_maskedarray, rotate_raster
from explore_australia import CoverageService

# Check for internet connection by connection to Google DNS
try:
    requests.get('http://8.8.8.8', timeout=1)
    HAS_CONNECTION = True
except requests.ConnectionError:
    HAS_CONNECTION = False

class TestCoverageIO(unittest.TestCase):
    "Tests for coverage utility functions"

    def setUp(self):
        self.resource_dir = Path(__file__).parent / 'resources'

    def test_read_to_maskedarray(self):
        "Check that we can read a band to a masked array"
        resource_file = self.resource_dir / 'tmp.tif'
        self.assertTrue(resource_file.exists())
        arr = read_to_maskedarray(resource_file)
        self.assertEqual(arr.shape, (201, 201))

class TestRotateRaster(unittest.TestCase):
    "Tests for raster rotations"
    def setUp(self):
        self.resource_dir = Path(__file__).parent / 'resources'
        self.raster_file = self.resource_dir / 'tmp.tif'

    def test_rotate_raster_no_mask(self):
        "Check we can rotate the raster with no mask"
        try:
            # Do rotation
            self.assertTrue(self.raster_file.exists())
            rotated_file = self.resource_dir / 'rad_ratio_tk_rotated.tif'
            self.assertFalse(rotated_file.exists())
            rotate_raster(self.raster_file, rotated_file, 32)

            # Check that the correct files get created
            self.assertTrue(rotated_file.exists())
            with rasterio.open(rotated_file, 'r') as src:
                data = src.read(1, masked=True)
                self.assertFalse(np.ma.is_masked(data))
                self.assertEqual(data.shape, (201, 201))
        finally:
            rotated_file = self.resource_dir / 'rad_ratio_tk_rotated.tif'
            if rotated_file.exists():
                rotated_file.unlink()
            self.assertFalse(rotated_file.exists())

    def generate_mask(self):
        "Make a mask file for testing"
        def make_random_mask(data):
            data[~np.isfinite(data)] = 0
            lower, upper = np.quantile(data, [0.05, 0.9])
            mask = (data < lower) | (data > upper)
            return np.ma.MaskedArray(data, mask.transpose())

        with rasterio.open(self.raster_file) as src:
            data = make_random_mask(src.read(1))
            with rasterio.open(str(self.resource_dir / 'masked.tif'), 'w', **src.meta) as sink:
                sink.write(data.data, 1)
                mask = (~data.mask * 255).astype('uint8')
                sink.write_mask(mask)

    @unittest.skip('Not implemented')
    def test_rotate_raster_masked(self):
        "Check rotation with masked arrays works"
        try:
            self.generate_mask()
            self.assertTrue((self.resource_dir / 'masked.tif').exists())
            self.assertTrue((self.resource_dir / 'masked.tif.msk').exists())
            rotate_raster(self.resource_dir / 'masked.tif',
                          self.resource_dir / 'masked_rotated.tif', -32)

            # Check that the correct files get created
            self.assertTrue((self.resource_dir / 'masked_rotated.tif').exists())
            self.assertTrue((self.resource_dir / 'masked_rotated.tif.msk').exists())
            with rasterio.open(self.resource_dir / 'masked_rotated.tif') as src:
                data = src.read(1, masked=True)
                self.assertTrue(np.ma.is_masked(data))
                self.assertEqual(data.shape, (501, 501))
        finally:
            for root in ('foomasked', 'masked_rotated'):
                for suffix in ('.tif', '.tif.msk'):
                    path = self.resource_dir / (root + suffix)
                    if path.exists():
                        path.unlink()
                    self.assertFalse(path.exists())

@unittest.skipIf(not HAS_CONNECTION, 'No connection')
class TestCoverageService(unittest.TestCase):
    "Tests for coverage service access"

    def setUp(self):
        self.url = ("http://dap-wms.nci.org.au/thredds/wcs/rr2/geophysics/"
                    "radmap_v3_2015_ratio_tk/radmap_v3_2015_ratio_tk.nc")
        self.resource_dir = Path(__file__).parent / 'resources'

    def test_get_data(self):
        "Check we can get data ok"
        tmpfile = self.resource_dir / 'get_file.tif'
        try:
            wcs = CoverageService(self.url)
            output_file = wcs((135.8, -35.2, 136, -35.4), output=str(tmpfile))
            self.assertTrue(output_file is not None)
            self.assertTrue(Path(output_file).exists())
        finally:
            if tmpfile.exists():
                tmpfile.unlink()
            self.assertFalse(tmpfile.exists())

    def test_get_data_no_name(self):
        "Check we can get data ok"
        tmpfile = self.resource_dir / 'get_file.tif'
        try:
            wcs = CoverageService(self.url)
            output_file = wcs((135.8, -35.2, 136, -35.4), output=str(tmpfile))
            self.assertTrue(output_file is not None)
            self.assertTrue(str(output_file).endswith('.tif'))
            output = Path(output_file)
            self.assertTrue(output.exists())
        finally:
            try:
                if output.exists():
                    output.unlink()
                self.assertFalse(tmpfile.exists())
            except NameError:
                pass

if __name__ == '__main__':
    unittest.main()
