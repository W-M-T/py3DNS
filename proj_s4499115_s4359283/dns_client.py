#!/usr/bin/env python3

""" Simple DNS client

A simple example of a client using the DNS resolver.
"""

from argparse import ArgumentParser

from dns.resolver import Resolver

if __name__ == "__main__":
    # Parse arguments
    
    parser = ArgumentParser(description="DNS Client")
    parser.add_argument("hostname", help="hostname to resolve", nargs='?', type=str, default="nu.nl")
    parser.add_argument("--timeout", metavar="time", type=int, default=5,
            help="resolver timeout")
    parser.add_argument("-c", "--caching", action="store_true",
            help="Enable caching")
    parser.add_argument("-t", "--ttl", metavar="time", type=int, default=0, 
            help="TTL value of cached entries")
    args = parser.parse_args()
    
    # Resolve hostname
    resolver = Resolver(args.timeout, args.caching, args.ttl)
    hostname, aliaslist, ipaddrlist = resolver.gethostbyname(args.hostname)
    
    # Print output
    print(hostname)
    print(aliaslist)
    print(ipaddrlist)
