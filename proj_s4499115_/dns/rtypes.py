#!/usr/bin/env python3

"""DNS TYPE and QTYPE values

This module contains an Enum for TYPE and QTYPE values. This Enum also contains
a method for converting Enum values to strings. See sections 3.2.2 and 3.2.3 of
RFC 1035 for more information.
"""


from enum import IntEnum


class Type(IntEnum):
    """DNS TYPE and QTYPE

    Usage:
        >>> Type.A
        <Type.A: 1>
        >>> Type(2)
        <Type.NS: 2>
        >>> str(Type.A)
        'A'
        >>> Type['SOA']
        <Type.SOA: 6>
        >>> Type.MX == 15
        True
    """

    A = 1
    NS = 2
    CNAME = 5
    SOA = 6
    PTR = 12
    MX = 15
    TXT = 16
    AAAA = 28
    ANY = 255

    def __str__(self):
        return self.name
