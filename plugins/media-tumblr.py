#!/usr/bin/python
# -*- coding=utf8 -*-


import StringIO
import sys
from twisted.python import log
from twisted.web import proxy, xmlrpc
from xmlrpclib import ServerProxy
import urlparse
from cache import Connection


host = 'media.tumblr.com'
server = Connection()


class CacheMissHelper(object):
  def __init__(self, father):
    print 'CacheMissHelper object made for %s'%(father.uri)
    self.father = father
    self.content_type = 'application/octet-stream'
    self.content = StringIO.StringIO()

  def setResponseCode(self, code, message=None):
    self.code = int(code)
    self.message = message

  def setContetType(self, value):
    self.content_type = value

  def write(self, buffer):
    self.content.write(buffer)

  def finish(self):
    data = self.content.getvalue()
    server.save(self.father.uri, self.content_type, xmlrpc.Binary(data))


def process(request):
  print 'plugin: media-tumblr is serving'
  cached = server.get(request.uri)
  if not cached:
    cm = CacheMissHelper(request)
    request.set_peeker(cm)
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
  else:
    assert False
  request.write(cached.data)
  request.finish()


