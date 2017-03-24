#!/usr/bin/env python3

from unittest.mock import MagicMock, patch

from util import DNSTestCase

from dns.resource import ResourceRecord, ARecordData
from dns.name import Name
from dns.rtypes import Type
from dns.classes import Class


class ResourceRecordTestCase(DNSTestCase):
    def setUp(self):
        self.addTypeEqualityFunc(ResourceRecord, self.equalsRR)

    def equalsRR(self, r1, r2, msg=None):
        if (r1.type_ != r2.type_ or
            r1.class_ != r2.class_ or
            r1.ttl != r2.ttl):
            raise self.inequalityException(r1, r2, msg)
    
    def test_resource_to_bytes(self):
        name = MagicMock()
        name.to_bytes.return_value = b"\x07example\x03com\x00"
        rdata = MagicMock()
        rdata.to_bytes.return_value = b"\x04\x05\x06\x07"
        record = ResourceRecord(name, Type.A, Class.CS, 3, rdata)
        compress = {}
        self.assertEqual(
            record.to_bytes(0, compress),
            (b"\x07example\x03com\x00\x00\x01\x00\x02\x00\x00\x00\x03\x00"
             b"\x04\x04\x05\x06\x07"))
    
    @patch("dns.resource.RecordData")
    @patch("dns.resource.Name")
    def test_resource_from_bytes(self, MockName, MockRData):
        MockName.from_bytes.return_value = (Name("example.com"), 13)
        MockRData.create_from_bytes.return_value = ARecordData("1.1.1.1")
        packet = (b"\x07example\x03com\x00\x00\x01\x00\x02\x00\x00\x00\x03\x00"
                  b"\x04\x01\x01\x01\x01")
        record1, offset = ResourceRecord.from_bytes(packet, 0)
        record2 = ResourceRecord(Name("example.com"), Type.A, Class.CS, 3,
                                 ARecordData("1.1.1.1"))
        self.assertEqual(record1, record2)
        MockName.from_bytes.assert_called_with(packet, 0)
        MockRData.create_from_bytes.assert_called_with(Type.A, packet, 23, 4)


class RecordDataTestCase(DNSTestCase):
    pass


class ARecordDataTestCase(DNSTestCase):
    pass
