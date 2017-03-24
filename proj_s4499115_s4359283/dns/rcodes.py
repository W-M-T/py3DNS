#!/usr/bin/env python3

""" DNS RCODE values

This module contains an Enum of RCODE values. See section 4.1.4 of RFC 1035 for
more info.
"""


from enum import IntEnum


class RCode(IntEnum):
    """ Enum of RCODE values

    Usage:
        >>> RCode.NoError
        <RCode.NoError: 0>
        >>> RCode(1)
        <RCode.FormErr: 1>
        >>> str(RCode.NXDomain)
        'NXDomain'
        >>> RCode['NotAuth']
        <RCode.NotAuth: 9>
        >>> Rcode.ServFail == 2
        True
    """

    NoError = 0
    FormErr = 1
    ServFail = 2
    NXDomain = 3
    NotImp = 4
    Refused = 5
    YXDomain = 6
    YXRRSet = 7
    NXRRSet = 8
    NotAuth = 9
    NotZone = 10
    BADVERS = 16
    BADSIG = 16
    BADKEY = 17
    BADTIME = 18
    BADMODE = 19
    BADNAME = 20
    BADALG = 21
    BADTRUNC = 22

    def __str__(self):
        return self.name
