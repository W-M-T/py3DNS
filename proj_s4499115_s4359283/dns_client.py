#!/usr/bin/env python3

""" Simple DNS client

A simple example of a client using the DNS resolver.
"""

from argparse import ArgumentParser

from dns.resolver import Resolver
import dns.consts as Consts

if __name__ == "__main__":
    # Parse arguments
    
    parser = ArgumentParser(description="DNS Client")
    parser.add_argument("hostname", help="hostname to resolve", nargs='?', type=str)
    parser.add_argument("--timeout", metavar="time", type=int, default=Consts.DEFAULT_TIMEOUT,
            help="resolver timeout")
    parser.add_argument("-c", "--caching", action="store_true",
            help="Enable caching")
    parser.add_argument("-t", "--ttl", metavar="time", type=int, default=0, 
            help="TTL value of cached entries")
    args = parser.parse_args()
    
    if not args.hostname:
        parser.print_help()
        exit()
    
    # Resolve hostname
    resolver = Resolver(args.timeout, args.caching, args.ttl)
    hostname, aliaslist, ipaddrlist = resolver.gethostbyname(args.hostname)
    if args.caching:
        resolver.cache.write_cache_file()
    
    # Print output
    print(hostname)
    print(aliaslist)
    print(ipaddrlist)
