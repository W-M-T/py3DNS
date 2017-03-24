#!/usr/bin/env python3

"""Tests for your DNS resolver and server"""

import argparse
import unittest
import sys
import time
from threading import Thread
from unittest import TestCase

from argparse import ArgumentParser

import dns.resolver
import dns.resource
import dns.rtypes
import dns.classes
import dns.server
import dns.consts as Consts



PORT = 5001
SERVER = "localhost"



class TestResolver(TestCase):
    def setUp(self):
        self.resolver = dns.resolver.Resolver(Consts.DEFAULT_TIMEOUT, False, Consts.DEFAULT_TTL)

    def testNoCacheResolveExistingFQDN(self):
        h, al, ad = self.resolver.gethostbyname("gaia.cs.umass.edu")
        self.assertEqual("gaia.cs.umass.edu", h)
        self.assertEqual([], al)
        self.assertEqual(["128.119.245.12"], ad)

    def testNoCacheResolveNotExistingFQDN(self):
        h, al, ad = self.resolver.gethostbyname("s.h.u.c.k.l.e")
        self.assertEqual("s.h.u.c.k.l.e", h)
        self.assertEqual([], al)
        self.assertEqual([], ad)


class TestResolverCache(TestCase):
    def setUp(self):
        self.resolver = dns.resolver.Resolver(Consts.DEFAULT_TIMEOUT, True, Consts.DEFAULT_TTL)

    def testResolveInvalidCachedFQDN(self):
        shuckleRecord = dns.resource.ResourceRecord("s.h.u.c.k.l.e",\
                dns.rtypes.Type.A, dns.classes.Class.IN,\
                int(time.time() + 5), dns.resource.RecordData("42.42.42.42"))
        self.resolver.cache.add_record(shuckleRecord)

        #Server checks if FQDN is valid before processing, therefore
        #we use a FQDN that could be valid, but is not.

        h, al, ad = self.resolver.gethostbyname("s.h.u.c.k.l.e")
        self.assertEqual("s.h.u.c.k.l.e", h)
        self.assertEqual([], al)
        self.assertEqual(["42.42.42.42"], ad)

    def testResolveExpiredInvalidCachedFQDN(self):
        shuckleRecord = dns.resource.ResourceRecord("s.h.u.c.k.l.e",\
                dns.rtypes.Type.A, dns.classes.Class.IN,\
                int(time.time() + 5), dns.resource.RecordData("42.42.42.42"))
        self.resolver.cache.add_record(shuckleRecord)

        time.sleep(5+1)

        h, al, ad = self.resolver.gethostbyname("s.h.u.c.k.l.e")
        self.assertEqual("s.h.u.c.k.l.e", h)
        self.assertEqual([], al)
        self.assertEqual([], ad)

class TestServer(TestCase):
    def setUp(self):
        self.resolver = dns.resolver.Resolver(Consts.DEFAULT_TIMEOUT, False, Consts.DEFAULT_TTL)
        #By offline_resolver we mean a resolver that only knows about the local server (and not about the root servers).
        self.offline_resolver = dns.resolver.Resolver(Consts.DEFAULT_TIMEOUT, False, Consts.DEFAULT_TTL, ["localhost"], False)

    def testSolveFQDNDirectAuthority(self):
        h1, al1, ad1 = self.offline_resolver.gethostbyname("shuckle.ru.nl")
        h2, al2, ad2 = self.resolver.gethostbyname("ru.nl")

        self.assertEqual(ad1, ad2)

    def testSolveFQDNNoDirectAuthority(self):
        h1, al1, ad1 = self.resolver.gethostbyname("cs.ru.nl")
        h2, al2, ad2 = self.offline_resolver.gethostbyname("cs.ru.nl")

        self.assertEqual(h1, h2)
        self.assertEqual(al1, al2)
        self.assertEqual(ad1, ad2)

    def testSolveFQDNNotInZone(self):
        h, al, ad = self.offline_resolver.gethostbyname("hestia.dance")

        self.assertEqual("hestia.dance", h)
        self.assertEqual([], al)
        self.assertEqual(["162.246.59.52"], ad)

    def testParallelRequest(self):
        helper1 = ThreadHelper(self.offline_resolver, "hestia.dance")
        helper2 = ThreadHelper(self.offline_resolver, "gaia.cs.umass.edu")
        t1 = Thread(target=helper1.run)
        t2 = Thread(target=helper2.run)
        t1.daemon = True
        t2.daemon = True
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertEqual("hestia.dance", helper1.h)
        self.assertEqual([], helper1.al)
        self.assertEqual(["162.246.59.52"], helper1.ad)

        self.assertEqual("gaia.cs.umass.edu", helper2.h)
        self.assertEqual([], helper2.al)
        self.assertEqual(["128.119.245.12"], helper2.ad)
    

class ThreadHelper(Thread):

    def __init__(self, resolver, hname):
        super(ThreadHelper, self).__init__()
        self.resolver = resolver
        self.hname = hname
        self.h = []
        self.al = []
        self.ad = []

    def run(self):
        self.h, self.al, self.ad = self.resolver.gethostbyname(self.hname)
        


def run_tests():
    # Parse command line arguments
    
    parser = ArgumentParser(description="DNS Tests")
    parser.add_argument("-s", "--server", type=str, default="localhost",
                        help="the address of the server")
    parser.add_argument("-p", "--port", type=int, default=5001,
                        help="the port of the server")
    args, extra = parser.parse_known_args()
    
    global PORT, SERVER
    PORT = args.port
    SERVER = args.server
    
    # Pass the extra arguments to unittest
    sys.argv[1:] = extra

    # Start test suite
    unittest.main()


if __name__ == "__main__":
    run_tests()