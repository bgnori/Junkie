#!/usr/bin/python
# -*- coding=utf8 -*-

import sys
import time
import subprocess
from twisted.web import client, xmlrpc, server
from twisted.internet import reactor

from xmlrpclib import ServerProxy

import model

storage = {}

class CacheServer(object):
  process = None
  def __enter__(self):
    self.process = subprocess.Popen(['python', 'cache.py'])
    return ServerProxy("http://localhost:9000", allow_none=True)

  def __exit__(self, exc_type, exc_value, traceback):
    if self.process.poll() is None:
      print 'trying to terminate cache process'
      server.terminate()
      self.process.wait()
      print 'cache process looks terminated.'
    return False


def printError(failure):
  print >> sys.stderr, "Error", failure.getErrorMessage()


def assemble(url, rqtime, artime, data):
  return (url, rqtime, artime, data)
  
class Cache(xmlrpc.XMLRPC):
  def xmlrpc_get(self, url):
    '''
      return data pointed by url, None on no data
    '''
    print url
    d = storage.get(url, None)
    if d:
      return xmlrpc.Binary(d[3])
    else:
      return None 

  def xmlrpc_save(self, url):
    d = storage.get(url, None)
    f = file(model.url2depot(url), 'w')
    f.write(d[3])
    f.close()
  
  def xmlrpc_fetch(self, url):
    '''
      if url is not in cache, 
        request url and store the data from url in cache
    '''
    if url not in storage:
      storage[url] = assemble(url, time.time(), None, None)
      def storePage(data):
        u, rq, ar, d = storage[url]
        ar = time.time()
        storage[url] = assemble(u, rq, ar, data)
        print >> sys.stderr, ' %5f s:  %6i byte : %s'%( ar - rq , len(data),url)
    
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

if __name__ == '__main__':
  c = Cache(allowNone=True)

  reactor.listenTCP(9000, server.Site(c))
  reactor.run()

  print 'bye!'


