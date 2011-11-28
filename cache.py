#!/usr/bin/python
# -*- coding=utf8 -*-

import sys
import time
import subprocess
from twisted.web import client, xmlrpc, server
from twisted.internet import reactor
from twisted.python import log

from xmlrpclib import ServerProxy

import model

def Connection():
  return ServerProxy("http://localhost:9000", allow_none=True)

class CacheServerProcess(object):
  process = None
  server = None
  def __enter__(self):
    self.process = subprocess.Popen(['python', 'cache.py'])
    self.server = Connection()
    return self.server

  def __exit__(self, exc_type, exc_value, traceback):
    if self.process.poll() is None:
      print 'trying to terminate cache process'
      try:
        self.server.save_index()
      except:
        print 'failed to save index!'
      self.process.terminate()
      self.process.wait()
      print 'cache process looks terminated.'
    return False

  

def printError(failure):
  print >> sys.stderr, "Error", failure.getErrorMessage()

class CacheServer(xmlrpc.XMLRPC):
  def __init__(self, storage, *args, **kw):
    xmlrpc.XMLRPC.__init__(self, *args, **kw)
    self.storage = storage
    self.pool = {}

  def xmlrpc_get(self, url):
    '''
      return data pointed by url, None on no data
    '''
    d = self.storage.get(url, None)
    if d:
      return xmlrpc.Binary(d)
    else:
      return None 

  def xmlrpc_save(self, url, mime, data):
    print 'saving %s as %s'%(url, mime)
    self.storage.save(url, mime, data.data)


  def xmlrpc_fetch(self, url):
    '''
      if url is not in cache, 
        request url and store the data from url in cache
    '''
    if url not in self.storage:
      ticket = self.storage.reserve(url)
      self.pool.update({ticket: ()})

      d = client.getPage(url)
      def storePage(data):
        mime = 'application/octet-stream' #Ugh! fix me
        self.storage.set(ticket, mime, data)
        callbacks = self.pool.pop(ticket)
        for c in callbacks:
          c.call() #Ugh! use deferred
        
      d.addCallback(storePage)
      d.addErrback(printError)
  
    return url #Echo.

  def xmlrpc_pop(self, url):
    '''
      remove data pointed by the url from cache 
    '''
    return self.storage.pop(url)

  def xmlrpc_time(self):
    return time.time()
  
  def xmlrpc_count(self):
    return len(self.storage)

  def xmlrpc_save_index(self):
    self.storage.save_index()
    return None

  def xmlrpc_terminate(self):
    reactor.callLater(0.1, reactor.stop)
    return None

if __name__ == '__main__':
  with open('cache.log', 'w') as f:
    log.startLogging(f)
    storage = model.Storage('depot')
    c = CacheServer(storage, allowNone=True)
    reactor.listenTCP(9000, server.Site(c))
    reactor.run()

    print 'bye! (cache.py)'

