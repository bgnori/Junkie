#!/usr/bin/python
# -*- coding=utf8 -*-
import sys


from twisted.python import log
from twisted.internet import reactor
from twisted.web import client
from twisted.internet import defer

import proxy
import dnmapper
import tumblr

junkie = tumblr.Junkie()

def abacus(request):
  reactor.callLater(0.1, junkie.prefetch, request.uri) #FIXME
  return None

dnmapper.register('abacus.tumblr.com', abacus)

def media(request):
  url = request.uri
  entry = junkie.get(url) 
  return entry.read()

dnmapper.register('media.tumblr.com', media)

def www(request):
  url = request.uri
  print 'plugin: www-tumblr is serving'
  print url
  d = client.getPage(url,
          headers = request.headers,
      )
  def onPageArrival(data):
    f = tumblr.DataFile(data, 'OK') #FIXME DO not guess. use header
    return f
  d.addCallback(onPageArrival)
  def onFail(f):#FIXME
    return 'fail' #FIXME
  d.addErrback(onFail) 
  return d
#dnmapper.register('www.tumblr.com', www)



def main():
    reactor.listenTCP(8080, proxy.PrefetchProxyFactory())#'proxy.log'))
    reactor.run()
    tumblr.junkie.storage.save_entries()
    tumblr.junkie.storage.save_index()
    print >> sys.stderr, 'bye! (proxy.py)'


with open('junkie.log', 'w') as f:
    log.startLogging(f)
    import tumblr
    import plugins
    main()

