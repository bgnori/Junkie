#!/usr/bin/python
# -*- coding=utf8 -*-

from twisted.web import client, xmlrpc, server
from twisted.internet import reactor
import sys

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
      request url and store the data from url in cache
    '''
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
  
  def xmlrpc_clear(self):
    storage.clear()
    return None

c = Cache(allowNone=True)

reactor.listenTCP(9000, server.Site(c))
reactor.run()

