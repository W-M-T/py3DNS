#!/usr/bin/env python3

"""A DNS resource record.

This class contains classes for DNS resource records and record data. This
module is fully implemented. You will have this module in the implementation
of your resolver and server.
"""


import socket
import struct

from dns.classes import Class
from dns.name import Name
from dns.rtypes import Type


class ResourceRecord(object):
    """DNS resource record."""
    def __init__(self, name, type_, class_, ttl, rdata):
        """Create a new resource record.

        Args:
            name (Name): domain name.
            type_ (Type): the type.
            class_ (Class): the class.
            rdata (RecordData): the record data.
        """
        self.name = name
        self.type_ = type_
        self.class_ = class_
        self.ttl = ttl
        self.rdata = rdata

    def to_bytes(self, offset, compress):
        """Convert ResourceRecord to bytes."""
        record = self.name.to_bytes(offset, compress)
        record += struct.pack("!HHi", self.type_, self.class_, self.ttl)
        offset += len(record) + 2
        rdata = self.rdata.to_bytes(offset, compress)
        record += struct.pack("!H", len(rdata)) + rdata
        return record

    @classmethod
    def from_bytes(cls, packet, offset):
        """Convert ResourceRecord from bytes."""
        name, offset = Name.from_bytes(packet, offset)
        type_ = Type(struct.unpack_from("!H", packet, offset)[0])
        class_ = Class(struct.unpack_from("!H", packet, offset + 2)[0])
        ttl, rdlength = struct.unpack_from("!iH", packet, offset + 4)
        offset += 10
        rdata = RecordData.create_from_bytes(type_, packet, offset, rdlength)
        offset += rdlength
        return cls(name, type_, class_, ttl, rdata), offset

    def to_dict(self):
        """Convert ResourceRecord to dict."""
        return {"name" : str(self.name),
                "type" : str(self.type_),
                "class" : str(self.class_),
                "ttl" : self.ttl,
                "rdata" : self.rdata.to_dict()}

    @classmethod
    def from_dict(cls, dct):
        """Convert ResourceRecord from dict."""
        type_ = Type[dct["type"]]
        rdata = RecordData.create_from_dict(type_, dct["rdata"])
        return cls(Name(dct["name"]), type_, Class[dct["class"]], dct["ttl"],
                   rdata)


class RecordData:
    """Record Data."""

    @staticmethod
    def create(type_, data):
        """ Create a RecordData object from bytes
        Args:
            type_ (Type): type
            packet (bytes): packet
            offset (int): offset in message
            rdlength (int): length of rdata
            parser (int): domain name parser
        """
        classdict = {
            Type.A: ARecordData,
            Type.CNAME: CNAMERecordData,
            Type.NS: NSRecordData,
            Type.SOA: SOARecordData
        }
        if type_ in classdict:
            return classdict[type_](data)
        else:
            return GenericRecordData(data)

    @staticmethod
    def create_from_bytes(type_, packet, offset, rdlength):
        """Create a RecordData object from bytes.

        Args:
            type_ (Type): type.
            packet (bytes): packet.
            offset (int): offset in packet.
            rdlength (int): length of rdata.
        """
        classdict = {
            Type.A: ARecordData,
            Type.CNAME: CNAMERecordData,
            Type.NS: NSRecordData,
            Type.SOA: SOARecordData
        }
        if type_ in classdict:
            return classdict[type_].from_bytes(packet, offset, rdlength)
        else:
            return GenericRecordData.from_bytes(packet, offset, rdlength)

    @staticmethod
    def create_from_dict(type_, dct):
        """Create a RecordData object from dict."""
        classdict = {
            Type.A: ARecordData,
            Type.CNAME: CNAMERecordData,
            Type.NS: NSRecordData,
            Type.SOA: SOARecordData
        }
        if type_ in classdict:
            return classdict[type_].from_dict(dct)
        else:
            return GenericRecordData.from_dict(dct)


class ARecordData(RecordData):
    """Record data for A type."""

    def __init__(self, address):
        """Create RecordData for A type.

        Args:
            address (str): address.
        """
        self.address = address

    def to_bytes(self, offset, compress):
        """Convert to bytes.

        Args:
            offset (int): offset in packet.
            compress (dict): dict from domain names to pointers.
        """
        return socket.inet_aton(self.address)

    @classmethod
    def from_bytes(cls, packet, offset, rdlength):
        """Create a RecordData object from bytes.

        Args:
            packet (bytes): packet.
            offset (int): offset in message.
            rdlength (int): length of rdata.
        """
        address = socket.inet_ntoa(packet[offset:offset+4])
        return cls(address)

    def to_dict(self):
        """Convert to dict."""
        return {"address" : self.address}

    @classmethod
    def from_dict(cls, dct):
        """Create a RecordData object from dict."""
        return cls(dct["address"])


class CNAMERecordData(RecordData):
    """Record data for CNAME type."""

    def __init__(self, cname):
        """Create RecordData for CNAME type.

        Args:
            cname (Name): cname.
        """
        self.cname = cname

    def to_bytes(self, offset, compress):
        """Convert to bytes.

        Args:
            offset (int): offset in packet.
            compress (dict): dict from domain names to pointers.
        """
        return self.cname.to_bytes(offset, compress)

    @classmethod
    def from_bytes(cls, packet, offset, rdlength):
        """Create a RecordData object from bytes.

        Args:
            packet (bytes): packet.
            offset (int): offset in message.
            rdlength (int): length of rdata.
        """
        cname, offset = Name.from_bytes(packet, offset)
        return cls(cname)

    def to_dict(self):
        """Convert to dict."""
        return {"cname" : str(self.cname)}

    @classmethod
    def from_dict(cls, dct):
        """Create a RecordData object from dict."""
        print(dct)
        return cls(Name(dct["cname"]))


class NSRecordData(RecordData):
    """Record data for NS type.

    See RFC 1035 3.3.11.
    """

    def __init__(self, nsdname):
        """Create RecordData for NS type.

        Args:
            nsdname (Name): nsdname.
        """
        self.nsdname = nsdname

    def to_bytes(self, offset, compress):
        """Convert to bytes.

        Args:
            offset (int): offset in packet.
            compress (dict): dict from domain names to pointers.
        """
        return self.nsdname.to_bytes(offset, compress)

    @classmethod
    def from_bytes(cls, packet, offset, rdlength):
        """Create a RecordData object from bytes.

        Args:
            packet (bytes): packet.
            offset (int): offset in message.
            rdlength (int): length of rdata.
        """
        nsdname, offset = Name.from_bytes(packet, offset)
        return cls(nsdname)

    def to_dict(self):
        """Convert to dict."""
        return {"nsdname" : str(self.nsdname)}

    @classmethod
    def from_dict(cls, dct):
        """Create a RecordData object from dict."""
        return cls(Name(dct["nsdname"]))


class SOARecordData(RecordData):
    """Record data for SOA type.

    See RFC 1035 3.3.13.
    """

    def __init__(self, mname, rname, serial, refresh, retry, expire, minimum):
        """Create RecordData for SOA type.

        Args:
            mname (Name): mname.
            rname (Name): rname.
            serial (int): serial.
            refresh (int): refresh.
            retry (int): retry.
            expire (int): expire.
            minimum (int): minimum.
        """
        self.mname = mname
        self.rname = rname
        self.serial = serial
        self.refresh = refresh
        self.retry = retry
        self.expire = expire
        self.minimum = minimum

    def to_bytes(self, offset, compress):
        """Convert to bytes.

        Args:
            offset (int): offset in packet.
            compress (dict): dict from domain names to pointers.
        """
        data = self.mname.to_bytes(offset, compress)
        data += self.rname.to_bytes(len(data), compress)
        data += struct.pack("!I", self.serial)
        data += struct.pack("!i", self.refresh)
        data += struct.pack("!i", self.retry)
        data += struct.pack("!i", self.expire)
        data += struct.pack("!I", self.minimum)

    @classmethod
    def from_bytes(cls, packet, offset, rdlength):
        """Create a RecordData object from bytes.

        Args:
            packet (bytes): packet.
            offset (int): offset in message.
            rdlength (int): length of rdata.
        """
        mname, offset = Name.from_bytes(packet, offset)
        rname, offset = Name.from_bytes(packet, offset)
        serial = struct.unpack_from("!I", packet, offset)[0]
        refresh = struct.unpack_from("!i", packet, offset + 4)[0]
        retry = struct.unpack_from("!i", packet, offset + 8)[0]
        expire = struct.unpack_from("!i", packet, offset + 12)[0]
        minimum = struct.unpack_from("!I", packet, offset + 16)[0]
        return cls(mname, rname, serial, refresh, retry, expire, minimum), offset + 20

    def to_dict(self):
        """Convert to dict."""
        return {"mname" : str(self.mname), "rname" : str(self.rname),
                "serial" : self.serial, "refresh" : self.refresh,
                "retry" : self.retry, "expire" : self.expire,
                "minimum" : self.minimum}

    @classmethod
    def from_dict(cls, dct):
        """Create a RecordData object from dict."""
        return cls(Name(dct["mname"]), Name(dct["rname"]), dct["serial"],
                   dt["refresh"], dct["retry"], dct["expire"], dct["minimum"])


class GenericRecordData(RecordData):
    """Generic Record Data (for other types)."""

    def __init__(self, data):
        """Create RecordData for generic data.

        Args:
            data (bytes): record data.
        """
        self.data = data

    def to_bytes(self, offset, compress):
        """Convert to bytes.

        Args:
            offset (int): offset in packet.
            compress (dict): dict from domain names to pointers.
        """
        return self.data

    @classmethod
    def from_bytes(cls, packet, offset, rdlength):
        """Create a RecordData object from bytes.

        Args:
            packet (bytes): packet.
            offset (int): offset in message.
            rdlength (int): length of rdata.
        """
        data = packet[offset:offset+rdlength]
        return cls(data)

    def to_dict(self):
        """Convert to dict."""
        return {"data" : self.data}

    @classmethod
    def from_dict(cls, dct):
        """Create a RecordData object from dict."""
        return cls(dct["data"])
