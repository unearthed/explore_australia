import unittest

import explore_australia

class TestVersion(unittest.TestCase):

    def test_version(self):
        "Check version is correct"
        self.assertEqual(explore_australia.__version__, '0.0.1')

if __name__ == '__main__':
    unittest.main()
