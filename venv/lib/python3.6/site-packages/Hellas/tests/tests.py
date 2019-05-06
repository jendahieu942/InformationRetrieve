# -*- coding: utf-8 -*-
"""Library Tests"""
import unittest
import random

from Hellas import (Olympia, Sparta, Pella)


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pickle_compress(self):
        obj = Sparta.DotDot({'a': 1, 'b': {'ba': 'b1', 'bb': 'b2'}})
        self.assertTrue(Olympia.pickle_compress_test(obj), "not pickled/compressed correctly")

    def test_b62(self):
        b62 = Pella.Base62()
        vl = random.randrange(1, 2**64)
        vl_decoded = b62.decode(b62.encode(vl))
        self.assertEqual(vl_decoded, vl, "decoded value doesn't match encoded value " + str(vl))

if __name__ == "__main__":
    unittest.main()
