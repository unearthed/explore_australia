""" file:    test_utilities.py (tests)
    author:  Jess Robertson, jess@unearthed.solutions
    date:    Thursday, 03 January 2019

    description: Utility function tests
"""

import unittest
from itertools import product

import numpy as np

from explore_australia.utilities import qclip

class TestUtilities(unittest.TestCase):

    "Unit tests for utilities"

    def test_qclip(self):
        "Check that qclip works ok"
        lowers = (0, 0.05, 0.1, None)
        uppers = (0.47, 0.95, 1, None)
        scales = (1, 10, 100)
        for lower, upper, scale in product(lowers, uppers, scales):
            with self.subTest(min=lower, max=upper, scale=scale):
                result = qclip(np.linspace(0, scale, 100), lower, upper)
                assert np.isclose(result.min(), (lower or 0) * scale)
                assert np.isclose(result.max(), (upper or 1) * scale)

    def test_isfinite(self):
        "Check finite qclip works"
        data = np.array([1, 2, 3, 4, np.nan, np.inf])
        result = qclip(data, lower=0.25, upper=0.6)[:4].astype(int) # skip nans
        self.assertTrue(not any(np.isnan(result)))
        self.assertTrue(any(np.isfinite(result)))
        self.assertEqual(result.min(), 2)
        self.assertEqual(result.max(), 3)

        result = qclip(data, lower=0.25, upper=0.6, finite_only=False)[:4].astype(int) # skip nans
        self.assertTrue(not any(np.isnan(result)))
        self.assertTrue(any(np.isfinite(result)))
        self.assertEqual(result.min(), 1)
        self.assertEqual(result.max(), 4)

if __name__ == '__main__':
    unittest.main()
