

import unittest
from cache import CacheTestCase

def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CacheTestCase))
    return suite
