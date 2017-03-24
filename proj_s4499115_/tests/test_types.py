#!/usr/bin/env python3

import unittest

from dns.rtypes import Type


class TypeTestCase(unittest.TestCase):
    def test_type_str(self):
        self.assertEqual(str(Type.NS), "NS")
    
    def test_type_from_str(self):
        self.assertEqual(Type["AAAA"], Type.AAAA)

    def test_type_int(self):
        self.assertEqual(Type.A, 1)


if __name__  == '__main__':
    unittest.main()
