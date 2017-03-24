#!/usr/bin/env python3

import unittest

from dns.rcodes import RCode


class RCodeTestCase(unittest.TestCase):
    def test_rcode_str(self):
        self.assertEqual(str(RCode.NotZone), "NotZone")

    def test_rcode_from_str(self):
        self.assertEqual(RCode["NoError"], 0)


if __name__  == '__main__':
    unittest.main()
