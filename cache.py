#!/usr/bin/python
# -*- coding=utf8 -*-

import sys
import time
from twisted.web import client, xmlrpc, server
from twisted.internet import reactor

storage = {}


def printError(failure):
  print >> sys.stderr, "Error", failure.getErrorMessage()

class Cache(xmlrpc.XMLRPC):
  def xmlrpc_get(self, url):
    '''
      return data pointed by url, None on no data
    '''
    return storage.get(url, None)
  
  def xmlrpc_fetch(self, url):
    '''
      if url is not in cache, 
        request url and store the data from url in cache
    '''
    if url not in storage:
      def storePage(data):
        print >> sys.stderr, 'storing:', url
        storage[url] = data
    
      client.getPage(url)\
        .addCallback(storePage)\
        .addErrback(printError)
  
    return url #Echo.

  def xmlrpc_pop(self, url):
    '''
      remove data pointed by the url from cache 
    '''
    return storage.pop(url)

  def xmlrpc_time(self):
    return time.time()
  
  def xmlrpc_count(self):
    return len(storage)

  def xmlrpc_clear(self):
    storage.clear()
    return None

  def xmlrpc_terminate(self):
    reactor.callLater(0.1, reactor.stop)
    return None

c = Cache(allowNone=True)

reactor.listenTCP(9000, server.Site(c))
reactor.run()

print 'bye!'

