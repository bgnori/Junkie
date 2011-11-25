#!/usr/bin/python
# -*- coding=utf8 -*-
'''
  from 
  http://wiki.python.org/moin/Twisted-Examples
'''

from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log
import urlparse
import subprocess
import sys

 


class ProxyServerProcess(object):
  process = None
  server = None
  def __enter__(self):
    self.process = subprocess.Popen(['python', 'proxy.py'])
    return None

  def __exit__(self, exc_type, exc_value, traceback):
    if self.process.poll() is None:
      print 'trying to terminate proxy process'
      self.process.terminate()
      self.process.wait()
      print 'proxy process looks terminated.'
    return False

 
class PrefetchProxyClient(proxy.ProxyClient):
  pass
class PrefetchProxyClientFactory(proxy.ProxyClientFactory):
  protocol = PrefetchProxyClient 


class PrefetchProxyRequest(proxy.ProxyRequest):
  '''
    in proxy.ProxyRequest.process:
    s = self.content.read()
    clientFactory = class_(self.method, rest, self.clientproto, headers,
                           s, self)
    self.reactor.connectTCP(host, port, clientFactory)
  '''
  protocols = {'http': PrefetchProxyClientFactory}

  def __init__(self, channel, queued, reactor=reactor):
    proxy.ProxyRequest.__init__(self, channel, queued, reactor=reactor)
    self.peeker = None

  def set_peeker(self, peeker):
    self.peeker = peeker

  def handleStatus(self, version, code, message):
    proxy.ProxyRequest.handleStatus(self, version, code, message)
    if self.peeker:
      self.peeker.handleStatus(version, code, message)

  def handleHeader(self, key, value):
    proxy.ProxyRequest.handleHeader(self, key, value)
    if self.peeker:
      self.peeker.handleHeader(key, value)

  def handleResponsePart(self, buffer):
    proxy.ProxyRequest.handleResponsePart(self, buffer)
    if self.peeker:
      self.peeker.handleResponsePart(key, value)

  def handleResponseEnd(self):
    proxy.ProxyRequest.handleResponseEnd(self)
    if self.peeker:
      self.peeker.handleResponseEnd()

  def on_cache_miss(self, receiver):
    receiver('hoge')
    proxy.ProxyRequest.process(self)
    
  def on_cache_wait(self, producer):
    pass
    
  def process(self):
    '''
      if domain in target and  prefetched
        get it from cache.
      else:
        use ordinary request
    '''
    parsed = urlparse.urlparse(self.uri)
    host = parsed[1]
    m = plugins.get_mapper()
    matched = m.postfix(host)
    if len(matched) == 1:
      plugin_mod = matched.pop()
      plugin_mod.process(self)
    elif len(matched) > 1:
      print 'ambiguous match', host
      proxy.ProxyRequest.process(self)
    else:
      proxy.ProxyRequest.process(self)

class PrefetchProxy(proxy.Proxy):
  requestFactory = PrefetchProxyRequest

class PrefetchProxyFactory(http.HTTPFactory):
  protocol = PrefetchProxy

if __name__ == '__main__':
  with open('proxy.log', 'w') as f:
    log.startLogging(f)
    import plugins
    reactor.listenTCP(8080, PrefetchProxyFactory())
    reactor.run()
    print 'bye! (proxy.py)'


