#!/usr/bin/python
# -*- coding=utf8 -*-


import urlparse
import magic

from twisted.web import client
from twisted.internet import reactor, defer

import tumblr

host = 'media.tumblr.com'
load = True


def process(request):
  print 'plugin: media-tumblr is serving'
  
  url = request.uri
  cached = tumblr.storage.get(url)
  if not cached:
    print 'cache miss', url
    return tumblr.get(url)
  else:
    assert cached
    print 'cache hit for', url
    d = defer.Deferred()
    def xxx(igonre):
      print 'psudo get complete'
      parsed = urlparse.urlparse(request.uri)
      path = parsed[2]
      if not path.endswith(('.png','.jpg', '.gif')):
        print 'not image, do not know how to add header :(', path
        raise
      print 'plugin: tumblr found %s in cache.'%(request.uri,)

      f = tumblr.DataFile(cached)
      f.message = "OK found in cache"
      if path.endswith('jpg'): #FIXME
        f.contentType = "image/jpeg"
      elif path.endswith('png'):
        f.contentType = "image/png"
      elif path.endswith('gif'):
        f.contentType = "image/gif"
      else:
        assert False
      return f
    d.addCallback(xxx)
    reactor.callLater(0, d.callback, None) #there is nothing block it. So fire it.
    return d
  assert False


if __name__ == '__main__':
  print tumblr.storage
  
