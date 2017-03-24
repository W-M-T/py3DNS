#!/usr/bin/env python3

""" DNS CLASS and QCLASS values

This module contains an Enum of CLASS and QCLASS values. The Enum also contains
a method for converting values to strings. See sections 3.2.4 and 3.2.5 of RFC
1035 for more information.
"""


from enum import IntEnum


class Class(IntEnum):
    """ Enum of CLASS and QCLASS values

    Usage:
        >>> Class.CS
        <Class.CS: 2>
        >>> Class(1)
        <Class.IN: 1>
        >>> str(Class.CS)
        'CS'
        >>> Class["IN"]
        <Class.IN: 1>
        >>> Class.IN == 1
        True
    """

    IN = 1
    CS = 2
    CH = 3
    HS = 4
    ANY = 255

    def __str__(self):
        return self.name
