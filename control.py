#!/usr/bin/python
# -*- coding=utf8 -*-

import urllib

from lxml import etree
from xmlrpclib import ServerProxy
from twisted.internet import reactor
from twisted.web import client, xmlrpc, server
import cache
import model 

def Connection():
  return ServerProxy("http://localhost:9001", allow_none=True)

conn = cache.Connection()

posts = []  
class Controller(xmlrpc.XMLRPC):

  def xmlrpc_on_abacus(self, url):
    print url
    f = urllib.urlopen('http://bgnori.tumblr.com/api/read')
    data = f.read()
    f.close()

    t = etree.XML(data)
    find = etree.XPath('/tumblr/posts/post')
    for post in find(t):
      p = model.PostFactory(post)
      for u in p.assets_urls():
        conn.fetch(u)
      posts.append(p)


if __name__ == '__main__':
  c = Controller(allowNone=True)  
  reactor.listenTCP(9001, server.Site(c))
  reactor.run()

