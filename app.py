#!/usr/bin/python
# -*- coding=utf8 -*-
import sys

import pickle

from twisted.python import log
from twisted.internet import reactor
from twisted.web import client
from twisted.internet import defer

import cache
import proxy
import dnmapper
from tumblr import render
from tumblr.junkie import Junkie


junkie = Junkie()
junkie.prefetch()

def abacus(request):
  reactor.callLater(0.1, junkie.prefetch) #FIXME
  return None

dnmapper.register('abacus.tumblr.com', abacus)

def media(request):
  url = request.uri
  entry = junkie.get(url) 
  return entry.read()

dnmapper.register('media.tumblr.com', media)

def mushboard(request):
  d = defer.Deferred()
  html = junkie.make_dashboard()
  f = cache.DataFile(html, 'OK', 'text/html;utf8') 
  reactor.callLater(0, d.callback, f) 
  return d

dnmapper.register('mushboard', mushboard)



def main():
    reactor.listenTCP(8080, proxy.PrefetchProxyFactory())#'proxy.log'))
    reactor.run()
    tumblr.junkie.save()
    print >> sys.stderr, 'bye! (proxy.py)'


with open('junkie.log', 'w') as f:
    log.startLogging(f)
    main()

