#!/usr/bin/env python3

"""DNS messages.

This module contains classes for DNS messages, their header section and
question fields. See section 4 of RFC 1035 for more info.
"""


import struct

from dns.classes import Class
from dns.name import Name
from dns.resource import ResourceRecord
from dns.rtypes import Type


class Message:
    """DNS message."""

    def __init__(self, header, questions=None, answers=None, authorities=None,
                 additionals=None):
        """Create a new DNS message.

        Args:
            header (Header): the header section.
            questions ([Question]): the question section.
            answers ([ResourceRecord]): the answer section.
            authorities ([ResourceRecord]): the authority section.
            additionals ([ResourceRecord]): the additional section.
        """
        if questions is None:
            questions = []
        if answers is None:
            answers = []
        if authorities is None:
            authorities = []
        if additionals is None:
            additionals = []

        self.header = header
        self.questions = questions
        self.answers = answers
        self.authorities = authorities
        self.additionals = additionals

    @property
    def resources(self):
        """Getter for all resource records."""
        return self.answers + self.authorities + self.additionals

    def to_bytes(self):
        """Convert Message to bytes."""
        compress = {}

        result = self.header.to_bytes()
        
        for question in self.questions:
            offset = len(result)
            result += question.to_bytes(offset, compress)

        for answer in self.answers:
            offset = len(result)
            result += answer.to_bytes(offset, compress)

        for authority in self.authorities:
            offset = len(result)
            result += authority.to_bytes(offset, compress)

        for additional in self.additionals:
            offset = len(result)
            result += additional.to_bytes(offset, compress)
            
        return result

    @classmethod
    def from_bytes(cls, packet):
        """Create Message from bytes.

        Args:
            packet (bytes): byte representation of the message.
        """
        header, offset = Header.from_bytes(packet), 12

        questions = []
        for _ in range(header.qd_count):
            question, offset = Question.from_bytes(packet, offset)
            questions.append(question)

        answers = []
        for _ in range(header.an_count):
            answer, offset = ResourceRecord.from_bytes(packet, offset)
            answers.append(answer)

        authorities = []
        for _ in range(header.ns_count):
            authority, offset = ResourceRecord.from_bytes(packet, offset)
            authorities.append(authority)

        additionals = []
        for _ in range(header.ar_count):
            additional, offset = ResourceRecord.from_bytes(packet, offset)
            additionals.append(additional)

        return cls(header, questions, answers, authorities, additionals)


class Header:
    """The header section of a DNS message

    Contains a number of properties which are accessible as normal member
    variables.

    See section 4.1.1 of RFC 1035 for their meaning.
    """

    def __init__(self, ident, flags, qd_count, an_count, ns_count, ar_count):
        """ Create a new Header object

        Args:
            ident (int): identifier.
            flags (int): raw flags.
            qd_count (int): number of entries in question section.
            an_count (int): number of entries in answer section.
            ns_count (int): number of entries in authority section.
            ar_count (int): number of entries in additional section.
        """
        self.ident = ident
        self._flags = flags
        self.qd_count = qd_count
        self.an_count = an_count
        self.ns_count = ns_count
        self.ar_count = ar_count

    def to_bytes(self):
        """ Convert header to bytes."""
        return struct.pack("!6H",
                           self.ident,
                           self._flags,
                           self.qd_count,
                           self.an_count,
                           self.ns_count,
                           self.ar_count)

    @classmethod
    def from_bytes(cls, packet):
        """ Convert Header from bytes."""
        if len(packet) < 12:
            raise ValueError("header is too short")
        return cls(*struct.unpack_from("!6H", packet))

    @property
    def flags(self):
        """Get raw flag values."""
        return self._flags
    @flags.setter
    def flags(self, value):
        """Set raw flag values."""
        if value >= (1 << 16):
            raise ValueError("value too big for flags")
        self._flags = value

    @property
    def qr(self):
        """Get QR flag."""
        return (self._flags >> 15) & 0b1
    @qr.setter
    def qr(self, value):
        """Set QR flag."""
        if value:
            self._flags |= (1 << 15)
        else:
            self._flags &= ~(1 << 15)

    @property
    def opcode(self):
        """Get Opcode."""
        return (self._flags >> 11) & 0b1111
    @opcode.setter
    def opcode(self, value):
        """Set Opcode."""
        if value > 0b1111:
            raise ValueError("invalid opcode")
        self._flags &= ~(15 << 11)
        self._flags |= value << 11

    @property
    def aa(self):
        """Get aa flag."""
        return (self._flags >> 10) & 0b1
    @aa.setter
    def aa(self, value):
        """Set aa flag."""
        if value:
            self._flags |= (1 << 10)
        else:
            self._flags &= ~(1 << 10)

    @property
    def tc(self):
        """Get tc flag."""
        return (self._flags >> 9) & 0b1
    @tc.setter
    def tc(self, value):
        """Set tc flag."""
        if value:
            self._flags |= (1 << 9)
        else:
            self._flags &= ~(1 << 9)

    @property
    def rd(self):
        """Get rd flag."""
        return (self._flags >> 8) & 0b1
    @rd.setter
    def rd(self, value):
        """Set rd flag."""
        if value:
            self._flags |= (1 << 8)
        else:
            self._flags &= ~(1 << 8)

    @property
    def ra(self):
        """Get ra flag."""
        return (self._flags >> 7) & 0b1
    @ra.setter
    def ra(self, value):
        """Set ra flag."""
        if value:
            self._flags |= (1 << 7)
        else:
            self._flags &= ~(1 << 7)

    @property
    def z(self):
        """Get data in reserved field."""
        return (self._flags  >> 4) & 0b111

    @property
    def rcode(self):
        """Get RCODE."""
        return self._flags & 0b1111
    @rcode.setter
    def rcode(self, value):
        """Set RCODE."""
        if value > 0b1111:
            raise ValueError("invalid return code")
        self._flags &= ~0b1111
        self._flags |= value


class Question:
    """An entry in the question section.

    See section 4.1.2 of RFC 1035 for more info.
    """

    def __init__(self, qname, qtype, qclass):
        """Create a new entry in the question section.

        Args:
            qname (str): the QNAME.
            qtype (Type): the QTYPE.
            qclass (Class): the QCLASS.
        """
        self.qname = qname
        self.qtype = qtype
        self.qclass = qclass

    def to_bytes(self, offset, compress):
        """Convert Question to bytes."""
        bqname = (Name(self.qname)).to_bytes(offset, compress)
        bqtype = struct.pack("!H", self.qtype)
        bqclass = struct.pack("!H", self.qclass)
        return bqname + bqtype + bqclass

    @classmethod
    def from_bytes(cls, packet, offset):
        """Convert Question from bytes."""
        qname, offset = Name.from_bytes(packet, offset)
        qtype = Type(struct.unpack_from("!H", packet, offset)[0])
        qclass = Class(struct.unpack_from("!H", packet, offset + 2)[0])
        return cls(qname, qtype, qclass), offset + 4
