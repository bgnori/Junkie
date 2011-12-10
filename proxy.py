#!/usr/bin/python
# -*- coding=utf8 -*-
'''
  from 
  http://wiki.python.org/moin/Twisted-Examples
'''

import urlparse
import subprocess
import sys

from twisted.web import proxy, http
from twisted.internet import reactor, defer
from twisted.python import log

 
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
    request object which describse HTTP request from client.    
    proxy may make requet during process to fulfill it, such as:

    in proxy.ProxyRequest.process:
    s = self.content.read()
    clientFactory = class_(self.method, rest, self.clientproto, headers,
                           s, self)
    self.reactor.connectTCP(host, port, clientFactory)

    or may read cache.
  '''
  protocols = {'http': PrefetchProxyClientFactory}

  def process(self):
    '''
      invoke plugin on intended host
    '''

    parsed = urlparse.urlparse(self.uri)
    host = parsed[1]

    m = plugins.get_mapper()
    matched = m.postfix(host)

    if len(matched) == 1:
      plugin_mod = matched.pop()
      d = plugin_mod.process(self)
      if isinstance(d, defer.Deferred):
        '''
          There are 3 possibilities
          a) not in cache, not requested
          b) not in cache, but requested
          c) in cache
          any case plugin must return deferred with DataFile instance.
          when it gets ready, we read it and write the response to fulfill the original request.
        '''
        def onReadyToRead(f):
          self.setResponseCode(200, f.message)
          self.responseHeaders.addRawHeader("Content-Type", f.contentType)
          self.write(f.read())
          f.close()
          self.finish()
        d.addCallback(onReadyToRead)
        def onError(f):
          self.setResponseCode(500, 'proxy error') #FIXME f.message)
          self.finish()
        d.addErrback(onError)
      else:
        proxy.ProxyRequest.process(self)
    elif len(matched) > 1:
      print 'ambiguous match', host
      proxy.ProxyRequest.process(self)
    else:
      proxy.ProxyRequest.process(self)


class PrefetchProxy(proxy.Proxy):
  '''
  copied from twited.web.proxy
    
    """

    This class implements a simple web proxy.

    Since it inherits from L{twisted.protocols.http.HTTPChannel}, to use it you
    should do something like this::

        from twisted.web import http
        f = http.HTTPFactory()
        f.protocol = Proxy

    Make the HTTPFactory a listener on a port as per usual, and you have
    a fully-functioning web proxy!
    """
  '''
  requestFactory = PrefetchProxyRequest


class PrefetchProxyFactory(http.HTTPFactory):
  protocol = PrefetchProxy


if __name__ == '__main__':
  with open('proxy.log', 'w') as f:
    log.startLogging(f)
    import plugins
    reactor.listenTCP(8080, PrefetchProxyFactory())#'proxy.log'))
    reactor.run()
    print 'bye! (proxy.py)'

