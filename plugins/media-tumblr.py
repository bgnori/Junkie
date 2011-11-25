#!/usr/bin/python
# -*- coding=utf8 -*-


import StringIO
import sys
from twisted.python import log
from twisted.web import proxy
from xmlrpclib import ServerProxy
import urlparse
from cache import Connection

log.startLogging(sys.stdout)

host = 'media.tumblr.com'
server = Connection()


class CacheMiss(object):
  def __init__(self, father):
    self.father = father
    self.content = StringIO.StringIO()

  def handleStatus(self, version, code, message):
    print code, message
    self.version = version
    self.code = int(code)
    self.message = message

  def handleHeader(self, key, value):
    if key.lower() == 'content type':
      self.content_type = value

  def handleResponsePart(self, buffer):
    self.content.write(buffer)

  def handleResponseEnd(self):
    if code in (200,):
      data = self.content.getvalue()
      server.save(request.uri, self.content_type, data)


def process(request):
  print 'plugin: media-tumblr is serving'
  cached = server.get(request.uri)
  if not cached:
    cm = CacheMiss(request)
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


