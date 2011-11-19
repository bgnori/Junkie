#!/usr/bin/python
# -*- coding=utf8 -*-


host = 'tumblr.com'



from twisted.web import proxy

def process(request):
  print 'plugin: tumblr is serving'
  proxy.ProxyRequest.process(request)


