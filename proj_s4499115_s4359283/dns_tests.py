#!/usr/bin/env python3

"""Tests for your DNS resolver and server"""

import argparse
import unittest
import sys
import time
from threading import Thread
from unittest import TestCase

from argparse import ArgumentParser

from dns.resolver import Resolver
from dns.resource import ResourceRecord, RecordData
from dns.rtypes import Type
from dns.classes import Class
import dns.server
import dns.consts as Consts



PORT = 5001
SERVER = "localhost"


"""
class TestResolver(TestCase):
    def setUp(self):
        self.resolver = Resolver(Consts.DEFAULT_TIMEOUT, False, Consts.DEFAULT_TTL)

    def testNoCacheResolveExistingFQDN(self):
        h, al, ad = self.resolver.gethostbyname("gaia.cs.umass.edu")
        self.assertEqual("gaia.cs.umass.edu.", h)
        self.assertEqual([], al)
        self.assertEqual(["128.119.245.12"], ad)

    def testNoCacheResolveNotExistingFQDN(self):
        h, al, ad = self.resolver.gethostbyname("l.a.r.v.i.t.a.r")
        self.assertEqual("l.a.r.v.i.t.a.r.", h)
        self.assertEqual([], al)
        self.assertEqual([], ad)


class TestResolverCache(TestCase):
    def setUp(self):
        self.resolver = Resolver(Consts.DEFAULT_TIMEOUT, True, 0)

    def testResolveInvalidCachedFQDN(self):#Invalid in the sense that it isn't an existing fqdn
        shuckleRecord = ResourceRecord("c.y.n.d.a.q.u.i.l.",\
                Type.A, Class.IN,\
                5, RecordData.create(Type.A, "42.42.42.42"))
        self.resolver.cache.add_record(shuckleRecord)

        #Server checks if FQDN is valid before processing, therefore
        #we use a FQDN that could be valid, but is not.

        h, al, ad = self.resolver.gethostbyname("c.y.n.d.a.q.u.i.l")
        self.assertEqual("c.y.n.d.a.q.u.i.l.", h)
        self.assertEqual([], al)
        self.assertEqual(["42.42.42.42"], ad)

    def testResolveExpiredInvalidCachedFQDN(self):
        shuckleRecord = ResourceRecord("s.h.u.c.k.l.e.",\
                Type.A, Class.IN,\
                5, RecordData.create(Type.A, "42.42.42.42"))
        self.resolver.cache.add_record(shuckleRecord)

        time.sleep(5+1)

        h, al, ad = self.resolver.gethostbyname("s.h.u.c.k.l.e")
        self.assertEqual("s.h.u.c.k.l.e.", h)
        self.assertEqual([], al)
        self.assertEqual([], ad)
"""
#INCOMPLETE
class TestServer(TestCase):
    def setUp(self):
        self.resolver = Resolver(Consts.DEFAULT_TIMEOUT, False, Consts.DEFAULT_TTL)
        #By offline_resolver we mean a resolver that only knows about the local server (and not about the root servers).
        #This means that the server should be running in order to perform these tests
        self.offline_resolver1 = Resolver(Consts.DEFAULT_TIMEOUT, False, Consts.DEFAULT_TTL, ["localhost"], False)
        self.offline_resolver2 = Resolver(Consts.DEFAULT_TIMEOUT, False, Consts.DEFAULT_TTL, ["localhost"], False)
    """
    def testSolveFQDNDirectAuthority(self):
        h1, al1, ad1 = self.offline_resolver1.gethostbyname("shuckle.ru.nl.")
        h2, al2, ad2 = self.resolver.gethostbyname("ru.nl")

        self.assertEqual(ad1, ad2)

    def testSolveFQDNNoDirectAuthority(self):
        h1, al1, ad1 = self.resolver.gethostbyname("cs.ru.nl")
        h2, al2, ad2 = self.offline_resolver1.gethostbyname("cs.ru.nl.")

        self.assertEqual(h1, h2)
        self.assertEqual(al1, al2)
        self.assertEqual(ad1, ad2)
    """
    def testSolveFQDNNotInZone(self):
        h, al, ad = self.offline_resolver1.gethostbyname("hestia.dance")

        self.assertEqual("hestia.dance.", h)
        self.assertEqual([], al)
        self.assertEqual(["162.246.59.52"], ad)

    def testParallelRequest(self):
        helper1 = ThreadHelper(self.offline_resolver1, "hestia.dance.")
        helper2 = ThreadHelper(self.offline_resolver2, "gaia.cs.umass.edu.")
        t1 = Thread(target=helper1.run)
        t2 = Thread(target=helper2.run)
        t1.daemon = True
        t2.daemon = True
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertEqual("hestia.dance.", helper1.h)
        self.assertEqual([], helper1.al)
        self.assertEqual(["162.246.59.52"], helper1.ad)

        self.assertEqual("gaia.cs.umass.edu.", helper2.h)
        self.assertEqual([], helper2.al)
        self.assertEqual(["128.119.245.12"], helper2.ad)
    

class ThreadHelper(Thread):

    def __init__(self, resolver, hname):
        super(ThreadHelper, self).__init__()
        self.resolver = resolver
        self.hname = hname
        self.h = None
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
