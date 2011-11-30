#!/usr/bin/python
# -*- coding=utf8 -*-

from twisted.web import proxy
from twisted.internet import reactor
import urlparse
from control import Connection 

host = 'abacus.tumblr.com'
load = False
server = Connection()


def prefetch(uri):
  print 'abacus-tumblr.py:prefetch'
  server.on_abacus(uri)

def process(request):
  print 'plugin: abacus.tumblr is serving'
  reactor.callLater(0.1, prefetch, request.uri)
  proxy.ProxyRequest.process(request)


