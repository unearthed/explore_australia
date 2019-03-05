import unittest

import explore_generator

class TestVersion(unittest.TestCase):

    def test_version(self):
        "Check version is correct"
        self.assertEqual(explore_generator.__version__, '0.0.1')

if __name__ == '__main__':
    unittest.main()
