#!/usr/bin/python
# -*- coding=utf8 -*-

import sys

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
  #FIXME we should have file object for this, not buffer/data
  if not cached:
    print 'cache miss', url
    return tumblr.get(url)
  else:
    assert cached
    print 'cache hit for', url
    d = defer.Deferred()
    def xxx(igonre):
      print >> sys.stderr, 'plugin: making pseudo get, since found in cache, %s'%(url,)
      f = tumblr.DataFile(cached)
      f.message = "OK found in cache"
      f.contentType = magic.from_buffer(cached, mime=True) #FIXME, better than above. Don't guess, use header
      return f
    d.addCallback(xxx)
    reactor.callLater(0, d.callback, None) #there is nothing block it. So fire it.
    return d
  assert False


if __name__ == '__main__':
  print tumblr.storage
  
