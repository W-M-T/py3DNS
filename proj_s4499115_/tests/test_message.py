#!/usr/bin/env python3

from unittest.mock import MagicMock, patch, call

from util import DNSTestCase

from dns.name import Name
from dns.rtypes import Type
from dns.classes import Class
from dns.message import Message, Header, Question
import dns.message


class MessageTestCase(DNSTestCase):
    def setUp(self):
        self.addTypeEqualityFunc(Message, self.equalsMessage)

    def equalsMessage(self, m1, m2, msg=None):
        if (m1.header != m2.header or
            m1.questions != m2.questions or
            m1.answers != m2.answers or
            m1.authorities != m2.authorities or
            m1.additionals != m2.additionals):
            raise self.inequalityException(m1, m2, msg)

    def test_message_to_bytes(self):
        header = MagicMock()
        header.to_bytes.return_value = b"\x01"
        question = MagicMock()
        question.to_bytes.return_value = b"\x02"
        answer = MagicMock()
        answer.to_bytes.return_value = b"\x03"
        authority = MagicMock()
        authority.to_bytes.return_value = b"\x04"
        additional = MagicMock()
        additional.to_bytes.return_value = b"\x05"
        message = Message(header, [question], [answer], [authority], [additional])
        self.assertEqual(message.to_bytes(), b"\x01\x02\x03\x04\x05")

    @patch("dns.message.ResourceRecord")
    @patch("dns.message.Question")
    @patch("dns.message.Header")
    def test_message_from_bytes(self, HeaderMock, QuestionMock, ResourceMock):
        packet = b"\x01\x02\x03\x04\x05"
        header = Header(9001, 0, 1, 1, 1, 1)
        HeaderMock.from_bytes.return_value = header
        QuestionMock.from_bytes.return_value = (1, 13)
        ResourceMock.from_bytes.side_effect = [(2, 14), (3, 15), (4, 16)]
        message1 = Message.from_bytes(packet)
        message2 = Message(header, [1], [2], [3], [4])
        self.assertEqual(message1, message2)
        HeaderMock.from_bytes.assert_called_with(packet)
        QuestionMock.from_bytes.assert_called_with(packet, 12)
        calls = [call(packet, 13), call(packet, 14), call(packet, 15)]
        ResourceMock.from_bytes.assert_has_calls(calls)


class HeaderTestCase(DNSTestCase):
    def setUp(self):
        self.addTypeEqualityFunc(Header, self.equalsHeader)

    def equalsHeader(self, h1, h2, msg=None):
        if (h1.ident != h2.ident or
            h1._flags != h2._flags or
            h1.qd_count != h2.qd_count or
            h1.an_count != h2.an_count or
            h1.ns_count != h2.ns_count or
            h1.ar_count != h2.ar_count):
            raise self.inequalityException(h1, h2, msg)

    def test_qr(self):
        header = Header(0, 0, 0, 0, 0, 0)
        header.qr = 1
        self.assertEqual(header.qr, 1)

    def test_flags_qr(self):
        header = Header(0, 0, 0, 0, 0, 0)
        header.qr = 1
        self.assertEqual(header.flags, 1 << 15)

    def test_opcode(self):
        header = Header(0, 0, 0, 0, 0, 0)
        header.opcode = 1
        self.assertEqual(header.opcode, 1)

    def test_flags_opcode(self):
        header = Header(0, 0, 0, 0, 0, 0)
        header.opcode = 15
        self.assertEqual(header.flags, 15 << 11)

    def test_aa(self):
        header = Header(0, 0, 0, 0, 0, 0)
        header.aa = 1
        self.assertEqual(header.aa, 1)

    def test_flags_aa(self):
        header = Header(0, 0, 0, 0, 0, 0)
        header.aa = 1
        self.assertEqual(header.flags, 1 << 10)

    def test_tc(self):
        header = Header(0, 0, 0, 0, 0, 0)
        header.tc = 1
        self.assertEqual(header.tc, 1)

    def test_flags_tc(self):
        header = Header(0, 0, 0, 0, 0, 0)
        header.tc = 1
        self.assertEqual(header.flags, 1 << 9)

    def test_rd(self):
        header = Header(0, 0, 0, 0, 0, 0)
        header.rd = 1
        self.assertEqual(header.rd, 1)

    def test_flags_rd(self):
        header = Header(0, 0, 0, 0, 0, 0)
        header.rd = 1
        self.assertEqual(header.flags, 1 << 8)

    def test_ra(self):
        header = Header(0, 0, 0, 0, 0, 0)
        header.ra = 1
        self.assertEqual(header.ra, 1)

    def test_flags_ra(self):
        header = Header(0, 0, 0, 0, 0, 0)
        header.ra = 1
        self.assertEqual(header.flags, 1 << 7)

    def test_rcode(self):
        header = Header(0, 0, 0, 0, 0, 0)
        header.rcode = 1
        self.assertEqual(header.rcode, 1)

    def test_flags_rcode(self):
        header = Header(0, 0, 0, 0, 0, 0)
        header.rcode = 15
        self.assertEqual(header.flags, 15)

    def test_header_to_bytes(self):
        header = Header(1, 2, 3, 4, 5, 6)
        self.assertEqual(header.to_bytes(),
                         b"\x00\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\x06")

    def test_header_from_bytes(self):
        packet = b"\x00\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\x06"
        header = Header(1, 2, 3, 4, 5, 6)
        self.assertEqual(Header.from_bytes(packet), header)


class QuestionTestCase(DNSTestCase):
    def setUp(self):
        self.addTypeEqualityFunc(Question, self.equalsQuestion)

    def equalsQuestion(self, q1, q2, msg=None):
        if (q1.qname != q2.qname or
            q1.qtype != q2.qtype or
            q1.qclass != q2.qclass):
            raise self.inequalityException(q1, q2, msg)

    def test_question_to_bytes(self):
        name = MagicMock()
        name.to_bytes.return_value = b"\x07example\x03com\x00"
        question = Question(name, Type.NS, Class.IN)
        self.assertEqual(question.to_bytes(0, {}),
                         b"\x07example\x03com\x00\x00\x02\x00\x01")

    @patch("dns.message.Name")
    def test_question_from_bytes(self, MockName):
        packet = b"\x07example\x03com\x00\x00\x02\x00\x01"
        MockName.from_bytes.return_value = (Name("example.com"), 13)
        question1, offset = Question.from_bytes(packet, 0)
        question2 = Question(Name("example.com"), Type.NS, Class.IN)
        self.assertEqual(question1, question2)
        self.assertEqual(offset, 17)
        MockName.from_bytes.assert_called_with(packet, 0)
