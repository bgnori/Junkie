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
import sys
log.startLogging(sys.stdout)
 
import plugins
 
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
    parsed = urlparse.urlparse(self.uri)
    host = parsed[1]
    if host.endswith('tumblr.com') :
      print 'plug in'
      proxy.ProxyRequest.process(self)
    else:
      proxy.ProxyRequest.process(self)
      #super(PrefetchProxyRequest, self).process()

class PrefetchProxy(proxy.Proxy):
  requestFactory = PrefetchProxyRequest

class PrefetchProxyFactory(http.HTTPFactory):
  protocol = PrefetchProxy

reactor.listenTCP(8080, PrefetchProxyFactory())
reactor.run()

