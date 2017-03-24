#!/usr/bin/env python3

import unittest

from dns.classes import Class


class ClassTestCase(unittest.TestCase):
    def test_class_str(self):
        self.assertEqual(str(Class.IN), "IN")

    def test_class_from_str(self):
        self.assertEqual(Class["CH"], Class.CH)

    def test_class_int(self):
        self.assertEqual(Class.IN, 1)


if __name__  == '__main__':
    unittest.main()
