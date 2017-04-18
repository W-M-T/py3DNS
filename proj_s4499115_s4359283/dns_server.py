#!/usr/bin/env python3

""" DNS server

This script contains the code for starting a DNS server.
"""

from dns.server import Server
import time
from argparse import ArgumentParser


def run_server():
    # Parse arguments
    
    parser = ArgumentParser(description="DNS Server")
    parser.add_argument("-c", "--caching", action="store_true",
            help="Enable caching")
    parser.add_argument("-t", "--ttl", metavar="time", type=int, default=0, 
            help="TTL value of cached entries (if > 0)")
    parser.add_argument("-p", "--port", type=int, default=53,
            help="Port which server listens on")
    args = parser.parse_args()

    # Start server
    server = Server(args.port, args.caching, args.ttl)
    
    try:
        server.serve()
        print("[*] - Server ended.")
    except KeyboardInterrupt:
        print("\n[*] - Trying to shut down.")
        server.shutdown()
        time.sleep(1)


if __name__ == "__main__":
    run_server()
