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
log.startLogging(sys.stdout)
 
import plugins


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
  reactor.listenTCP(8080, PrefetchProxyFactory())
  reactor.run()
  print 'bye! (proxy.py)'


