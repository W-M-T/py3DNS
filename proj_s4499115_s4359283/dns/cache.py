#!/usr/bin/env python3

"""A cache for resource records

This module contains a class which implements a cache for DNS resource records,
you still have to do most of the implementation. The module also provides a
class and a function for converting ResourceRecords from and to JSON strings.
It is highly recommended to use these.
"""

import json

from dns.resource import ResourceRecord, RecordData
from dns.rtypes import Type
from dns.classes import Class
import dns.consts as Consts
import threading
import time
from copy import deepcopy

class RecordCache(object):
    """ Cache for ResourceRecords """

    def __init__(self, ttl):
        """ Initialize the RecordCache """
        self.records = []
        self.ttl = ttl if ttl > 0 else 0 
        self.lock = threading.Lock()

        #Lees de cache in, update de ttls, gooi alle invalid data weg
        self.lastCleanup = int(time.time())
        self.read_cache_file()
    
    def cleanup(self):
        """ Remove all entries in the cache whose TTL has expired """

        self.lock.acquire()
        curTime = int(time.time())
        elapsed = curTime - self.lastCleanup
        self.records = [record for record in self.records if elapsed <= record.ttl]#Throw away expired records
        #Update ttls
        for record in self.records:
            record.ttl -= elapsed
        self.lock.release()

        self.lastCleanup = int(time.time())#curTime
    
    def lookup(self, dname, type_, class_):
        """ Lookup resource records in cache

        Lookup for the resource records for a domain name with a specific type
        and class.
        
        Args:
            dname (str): domain name
            type_ (Type): type
            class_ (Class): class
        """

        if (int(time.time()) - self.lastCleanup >= 3600): #Cache al een uur lang niet gecleaned, dus doe het nu maar
            self.cleanup()

        """
        print("STARTING LOOKUP FOR",dname, type_, class_)
        for record in self.records:
            print("-----COMPARING")
            print(type(str(record.name)),type(dname))
            print(dname,type_,class_)
            print(record.name,record.type_,record.class_)
            print("---------------")
            if str(record.name) == dname and record.type_ == type_ and record.class_ == class_:
                print("MATCH")
        """
        curTime = int(time.time())
        elapsed = curTime - self.lastCleanup

        foundrecords = [record for record in self.records \
                if str(record.name) == dname and record.type_ == type_ and record.class_ == class_ \
                and elapsed <= record.ttl]
        
        foundrecords = [deepcopy(record) for record in foundrecords]
        #Verschuif de ttl en timestamp naar nu
        for record in foundrecords:
            record.ttl -= elapsed
            
        return foundrecords
        
    def add_record(self, new_rec):
        """ Add a new Record to the cache
        
        Args:
            record (ResourceRecord): the record added to the cache
        """

        self.lock.acquire()
        found = self.lookup(str(new_rec.name), new_rec.type_, new_rec.class_)
        if not found:
            print("CACHE--Adding record..")
            if self.ttl > 0:#TTL was a parameter, so use it
                new_rec.ttl = self.ttl

            #Instead of cleaning the entire cache to keep the timestamp (lastCleanup) correct, we compensate the new ttl by adding the elapsed time
            curTime = int(time.time())
            elapsed = curTime - self.lastCleanup
            new_rec.ttl += elapsed
            print(new_rec.to_dict())
            self.records.append(new_rec)

        self.lock.release()

    def read_cache_file(self, cache_file=Consts.CACHE_FILE):
        """ Read the cache file from disk """
        #Empty current cache
        self.records = []

        #Load from file
        try:
            with open(cache_file + ".timestamp") as infile:
                self.lastCleanup = int(infile.readline())

            with open(cache_file,"r") as infile:
                curTime = int(time.time())
                dcts = json.load(infile)
                self.records = [ResourceRecord.from_dict(dct) for dct in dcts]
                #Don't add the entries whose TTL is expired and update the ttls
                self.cleanup()

        except (ValueError, IOError, FileNotFoundError) as e:
            print("An error has occured while loading cache from disk: " + str(e))
            self.records = []
            with open(cache_file, 'w') as outfile:
                json.dump([], outfile, indent=2)

            with open(cache_file + ".timestamp", 'w') as outfile:
                outfile.write(str(self.lastCleanup))
        #print("Loaded the following records:")
        #for rec in self.records:
        #    print(rec.to_dict())

    def write_cache_file(self):
        """ Write the cache file to disk """
        self.cleanup()
        dcts = [record.to_dict() for record in self.records]
        
        try:
            with open(Consts.CACHE_FILE, 'w') as outfile:
                json.dump(dcts, outfile, indent=2)

            with open(Consts.CACHE_FILE + ".timestamp", 'w') as outfile:
                outfile.write(str(self.lastCleanup))

        except IOError as e:
            print("An error has occured while writing cache to disk: " + str(e))
