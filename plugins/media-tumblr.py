#!/usr/bin/python
# -*- coding=utf8 -*-


from twisted.web import proxy
from xmlrpclib import ServerProxy
import urlparse
from cache import Connection

host = 'media.tumblr.com'
server = Connection()

def process(request):
  print 'plugin: media-tumblr is serving'
  cached = server.get(request.uri)
  if not cached:
    proxy.ProxyRequest.process(request)
    return
  
  parsed = urlparse.urlparse(request.uri)
  path = parsed[2]
  if not path.endswith(('.png','.jpg')):
    print 'not image, do not know how to add header :(', path
    proxy.ProxyRequest.process(request)
    return
  print 'plugin: tumblr found %s in cache.'%(request.uri,)

  request.setResponseCode(200, "found in cache")
  if path.endswith('jpg'):
    request.responseHeaders.addRawHeader("Content-Type", "image/jpeg")
  elif path.endswith('png'):
    request.responseHeaders.addRawHeader("Content-Type", "image/png")
  request.write(cached.data)
  request.finish()


