#!/usr/bin/env python3

""" DNS Resolver

This module contains a class for resolving hostnames. You will have to implement
things in this module. This resolver will be both used by the DNS client and the
DNS server, but with a different list of servers.
"""

import socket
from random import randint
import re
import time

from dns.classes import Class
from dns.rtypes import Type
from dns.cache import RecordCache
import dns.cache
from dns.message import Message, Question, Header
import dns.rcodes
import dns.consts

class Resolver(object):
    """ DNS resolver """
    
    def __init__(self, timeout, caching, ttl, nameservers=[], use_rs=True):
        """ Initialize the resolver
        
        Args:
            caching (bool): caching is enabled if True
            ttl (int): ttl of cache entries (if > 0)
        """
        self.timeout = timeout
        self.caching = caching
        if caching:
            self.cache = RecordCache(ttl)
        self.nameservers = nameservers
        if use_rs:
            self.nameservers += dns.consts.ROOT_SERVERS


    def is_valid_hostname(self, hostname):
        """ Check if hostname could be a valid hostname

        Args:
            hostname (str): the hostname that is to be checked

        Returns:
            boolean indiciting if hostname could be valid
        """
        valid_hostnames = "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
        return re.match(valid_hostnames, hostname)


    def save_cache(self):
        """ Save the cache if appropriate """
        if self.caching:
            if self.cache is not None:
                self.cache.write_cache_file()


    def ask_server(self, query, server):
        """ Send query to a server

        Args: 
            query (Message): the query that is to be sent
            server (str): IP address of the server that the query must be sent to
        
        Returns:
            responses ([Message]): the responses received converted to Messages
        """
        response = None
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        try:
            sock.sendto(query.to_bytes(), (server, 53))
            data = sock.recv(1024)
            response = Message.from_bytes(data)
            if response.header.ident != query.header.ident:
                sock.close()
                return None
                    
        except socket.timeout:
            pass

        sock.close()
        return response


    def gethostbyname(self, hostname, resolvingnameservers=[]):
        """ Resolve hostname to an IP address

        Args:
            hostname (str): the FQDN that we want to resolve

        Returns:
            hostname (str): the FQDN that we want to resolve,
            aliaslist ([str]): list of aliases of the hostname,
            ipaddrlist ([str]): list of IP addresses of the hostname 

        """
        print("==GETHOSTNAME START================= (",hostname,")")
        aliaslist = []
        ipaddrlist = []

        #Check if the hostname is valid
        #Do stuff with last dot
        if hostname[-1] == '.':
            hostname = hostname[0:-1]
        valid = self.is_valid_hostname(hostname)
        if not valid:
            print("Invalid hostname!")
            return hostname, [], []
        hostname = hostname + '.'
        
        #Check if the information is in the cache
        if self.caching:
            #print("Checking cache..")
            for addr in self.cache.lookup(hostname, Type.A, Class.IN):
                print("Found A in cache: ", addr.to_dict())
                ipaddrlist.append(str(addr.rdata.address))

            if ipaddrlist:#If we already found the ip here, don't go after possible cname stuff
                print("We found an address in the cache!")
                return hostname, aliaslist, ipaddrlist

            for alias in self.cache.lookup(hostname, Type.CNAME, Class.IN):
                print("Found CNAME in cache: ", alias.to_dict())
                aliaslist.append(str(alias.rdata.cname))
                _, recaliaslist, recipaddrlist = self.gethostbyname(str(alias.rdata.cname))

                aliaslist += recaliaslist
                ipaddrlist += recipaddrlist
            
            if ipaddrlist:
                print("We found an address in the cache!")
                return hostname, aliaslist, ipaddrlist



        #Do the recursive algorithm
        hints = self.nameservers
        usedhints = []#List of addresses
        usednameservers = []#List of names of nameservers that have been seen
        
        while hints:
            #Get the server to ask
            hint = hints[0]
            usedhints.append(hint)
            hints = hints[1:]
            #print("Hints: ",hints)

            #Build the query to send to that server
            identifier = randint(0, 65535)

            #Make question
            questions = [Question(hostname, Type.A, Class.IN)]
            
            #Make header
            header = Header(identifier, 0, 1, 0, 0, 0)
            header.qr = 0
            header.opcode = 0
            header.rd = 0
            query = Message(header, questions)

            #print("Asking the server "+ hint)
            #Try to get a response
            response = self.ask_server(query, hint)

            if response == None:#We didn't get a response for this server, so check the next one
                print("Server at " + hint + " did not respond.")
                continue

            #print(response)

            #Cache the response A and CNAME records
            if self.caching:
                #print(response)
                for answer in response.answers + response.additionals:
                    if answer.type_ == Type.A or answer.type_ == Type.CNAME:
                        self.cache.add_record(answer)



            #Analyze the response
            for answer in response.answers:#First try to get an address
                if answer.type_ == Type.A and (str(answer.name) == hostname or str(answer.name) in aliaslist):
                    ipaddrlist.append(str(answer.rdata.address))

            for answer in response.answers:#Then get the aliases
                if answer.type_ == Type.CNAME and str(answer.rdata.cname) not in aliaslist:
                    #We found an alias, so restart the request using it
                    aliaslist.append(str(answer.rdata.cname))
                    _, recaliaslist, recipaddrlist = self.gethostbyname(str(answer.rdata.cname))

                    aliaslist += recaliaslist
                    ipaddrlist += recipaddrlist

                
            if ipaddrlist != []:
                print("We found an address for " + hostname + " using the recursive search!")
                return hostname, aliaslist, ipaddrlist

            else:
                for nameserver in response.authorities:
                    if nameserver.type_ == Type.NS:
                        #Check if we got the ip of this nameserver in the additional section
                        for additional in response.additionals:
                            if nameserver.rdata.nsdname == additional.name:
                                if str(additional.rdata.address) not in usedhints:#Prevent recycling of old hints
                                    hints = [str(additional.rdata.address)] + hints
                                    usednameservers.append(str(additional.name))
                                break
                        else:#This nameserver wasn't in the additional section
                            if str(nameserver.rdata.nsdname) not in usednameservers and str(nameserver.rdata.nsdname) != hostname and not str(nameserver.rdata.nsdname) in resolvingnameservers:#It is an unseen nameserver
                                _, _, nsipaddrlist = self.gethostbyname(str(nameserver.rdata.nsdname), resolvingnameservers=resolvingnameservers + [str(nameserver.rdata.nsdname)])
                                hints = nsipaddrlist + hints
                                usednameservers.append(str(nameserver.rdata.nsdname))
                                

        print("Recursive search for " + hostname + " was a total failure")
        #print("We still had the following unresolved hints:",unresolvedhints)
        return hostname, [], []
