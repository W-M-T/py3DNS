#!/usr/bin/env python3

"""Domain names."""

import struct


class Name:
    """A domain name."""

    def __init__(self, hostname):
        """Initialize a domain name from a name or list of labels.

        Args:
            hostname (str/[str]): either a domain name or a list of labels
        """
        if isinstance(hostname, str):
            self.labels = hostname.split(".")
            if not self.labels[-1]:
                del self.labels[-1]
        elif isinstance(hostname, list):
            self.labels = hostname
        else:
            raise TypeError

    def __eq__(self, other):
        if isinstance(other, Name):
            return ([l.lower() for l in self.labels] ==
                    [l.lower() for l in other.labels])
        else:
            return False

    def __str__(self):
        result = ""
        for label in self.labels:
            result += label + "."
        return result

    def to_bytes(self, offset, compress=None):
        """Convert Name to bytes."""
        result = b""
        add_null = True
        for i, label in enumerate(self.labels):
            name = ".".join(self.labels[i:]).lower()
            if compress is not None and name in compress:
                pointer = compress[name]
                result += struct.pack("!H", (3 << 14) + pointer)
                add_null = False
                break
            else:
                if compress is not None:
                    compress[name] = offset
                blabel = label.encode("utf-8")
                result += struct.pack("!B{}s".format(len(blabel)),
                                      len(blabel), blabel)
                offset += 1 + len(blabel)
        if add_null:
            result += b"\x00"

        return result

    @classmethod
    def from_bytes(cls, packet, offset):
        """Create Name from bytes."""
        labels = []
        hops = 0
        while True:
            label_length = struct.unpack_from("!B", packet, offset)[0]
            if label_length < 64:
                offset += 1
                blabel = packet[offset:offset + label_length]
                if blabel:
                    labels.append(blabel.decode("utf-8"))
                offset += label_length
                if hops == 0:
                    next_offset = offset
                if label_length == 0:
                    break
            elif label_length >= 192:
                pointer = struct.unpack_from("!H", packet, offset)[0] - (3 << 14)
                if hops == 0:
                    next_offset = offset + 2
                hops += 1
                offset = pointer
            else:
                raise ValueError
        return cls(labels), next_offset
