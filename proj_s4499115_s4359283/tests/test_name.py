#!/usr/bin/env python3

import unittest

from dns.name import Name


class NameTestCase(unittest.TestCase):
    def test_name_init1(self):
        name = Name("www.example.com")
        self.assertEqual(name.labels, ["www", "example", "com"])

    def test_name_init2(self):
        name = Name("")
        self.assertEqual(name.labels, [])

    def test_name_str1(self):
        name = Name("example.com")
        self.assertEqual(str(name), "example.com.")

    def test_name_str2(self):
        name = Name("example.com.")
        self.assertEqual(str(name), "example.com.")

    def test_name_str3(self):
        name = Name("")
        self.assertEqual(str(name), "")

    def test_name_eq1(self):
        name1 = Name("www.example.com")
        name2 = Name("www.example.com")
        self.assertEqual(name1, name2)

    def test_name_eq2(self):
        name1 = Name("www.example.com")
        name2 = Name("www.example.com.")
        self.assertEqual(name1, name2)

    def test_name_eq3(self):
        name1 = Name("www.example.com")
        name2 = Name("WWW.example.com")
        self.assertEqual(name1, name2)

    def test_name_eq4(self):
        name1 = Name("www.example.com")
        name2 = Name("ftp.example.com")
        self.assertNotEqual(name1, name2)

    def test_name_to_bytes1(self):
        name = Name("www.example.com")
        self.assertEqual(name.to_bytes(0), b"\x03www\x07example\x03com\x00")

    def test_name_to_bytes2(self):
        name = Name("")
        self.assertEqual(name.to_bytes(0), b"\x00")

    def test_name_to_bytes_compress1(self):
        name1 = Name("www.example.com")
        compress = {}
        self.assertEqual(name1.to_bytes(0, compress),
                         b"\x03www\x07example\x03com\x00")

    def test_name_to_bytes_compress2(self):
        name1 = Name("www.example.com")
        name2 = Name("example.com")
        compress = {}
        name1.to_bytes(0, compress)
        self.assertEqual(name2.to_bytes(17, compress),
                         b"\xc0\x04")

    def test_name_to_bytes_compress3(self):
        name1 = Name("www.example.com")
        name2 = Name("ftp.example.com")
        compress = {}
        name1.to_bytes(0, compress)
        self.assertEqual(name2.to_bytes(17, compress),
                         b"\x03ftp\xc0\x04")

    def test_name_to_bytes_compress4(self):
        name1 = Name("www.example.com")
        name2 = Name("example.com")
        compress = {}
        name1.to_bytes(0, compress)
        self.assertEqual(name2.to_bytes(17),
                         b"\x07example\x03com\x00")

    def test_name_to_bytes_compress5(self):
        name1 = Name("www.example.com")
        name2 = Name("WWW.example.com")
        compress = {}
        name1.to_bytes(0, compress)
        self.assertEqual(name2.to_bytes(17, compress),
                         b"\xc0\x00")

    def test_name_from_bytes1(self):
        packet = b"\x03www\x07example\x03com\x00"
        name1, offset = Name.from_bytes(packet, 0)
        name2 = Name("www.example.com")
        self.assertEqual(offset, 17)
        self.assertEqual(name1, name2)

    def test_name_from_bytes2(self):
        packet = b"\x03www\x07example\x03com\x00\x03ftp\xc0\x04"
        name1, offset = Name.from_bytes(packet, 0)
        name2, offset = Name.from_bytes(packet, offset)
        self.assertEqual(name1, Name("www.example.com"))
        self.assertEqual(name2, Name("ftp.example.com"))
    
    def test_name_from_bytes3(self):
        packet = b"\x41" + b"a" * 65
        with self.assertRaises(ValueError):
            Name.from_bytes(packet, 0)

    def test_name_from_bytes4(self):
        packet = b"\x00"
        name, offset = Name.from_bytes(packet, 0)
        self.assertEqual(name.labels, [])

if __name__  == '__main__':
    unittest.main()
