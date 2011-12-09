#!/usr/bin/python
# -*- coding=utf8 -*-


import urlparse
import magic

from twisted.web import client
from twisted.internet import reactor, defer

import model

host = 'media.tumblr.com'
storage = model.Storage('depot')



def resolve(request):
  print 'plugin: media-tumblr is serving'
  
  url = request.uri
  cached = storage.get(url)
  if not cached:
    print 'cache miss', url
    ticket = storage.reserve(url)
    if storage.isPrimaryTicket(ticket):
      d = client.getPage(url)
      def onPageArrival(data):
        f = model.DataFile(data)
        # mime = 'application/octet-stream' #FIXME
        mime = magic.from_buffer(data, mime=True) #FIXME, better than above. Don't guess, use header
        print mime
        storage.set(ticket, mime, data)
        f.content_type = mime
        f.message = 'OK'
        for consumer, fail in storage.callbackPairs(ticket):
          reactor.callLater(0, consumer, f.clone())
        return f
      d.addCallback(onPageArrival)
      def onFail(f):#FIXME
        for consumer, fail in storage.callbackPairs(ticket):
          reactor.callLater(0, fail, f.clone())
        return 'fail' #FIXME
      d.addErrback(onFail) 
      return d
    else:
      d = defer.Deferred()
      print 'case not primary ticket'
      def consumer(f):
        print 'consumer', f.getvalue()[:40]
        return f
      def fail(f):
        f.close()
        return 'fail' #FIXME
      storage.register(ticket, (consumer, fail))
      return d
    assert False
  else:
    assert cached
    print 'cache hit for', url
    d = defer.Deferred()
    def xxx():
      parsed = urlparse.urlparse(request.uri)
      path = parsed[2]
      if not path.endswith(('.png','.jpg', '.gif')):
        print 'not image, do not know how to add header :(', path
        raise
      print 'plugin: tumblr found %s in cache.'%(request.uri,)

      f = model.DataFile(cached)
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
    return d
  assert False


