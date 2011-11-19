#!/usr/bin/python
# -*- coding=utf8 -*-
'''
  from 
  http://wiki.python.org/moin/Twisted-Examples
'''

from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log
import sys
log.startLogging(sys.stdout)
 
 
class PrefetchProxyClient(proxy.ProxyClient):
  pass

class PrefetchProxyClientFactory(proxy.ProxyClientFactory):
  protocol = PrefetchProxyClient 

class PrefetchProxyRequest(proxy.ProxyRequest):
  protocols = {'http': PrefetchProxyClientFactory}
  def process(self):
    '''
      if domain in target and  prefetched
        get it from cache.
      else:
        use ordinary request
    '''
    if False:
      pass
    else:
      proxy.ProxyRequest.process(self)
      #super(PrefetchProxyRequest, self).process()

class PrefetchProxy(proxy.Proxy):
  requestFactory = PrefetchProxyRequest

class PrefetchProxyFactory(http.HTTPFactory):
  protocol = PrefetchProxy

class ProxyFactory(http.HTTPFactory):
  protocol = proxy.Proxy

	
#reactor.listenTCP(8080, ProxyFactory())
reactor.listenTCP(8080, PrefetchProxyFactory())
reactor.run()

