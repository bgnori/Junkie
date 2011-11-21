#!/usr/bin/python
# -*- coding=utf8 -*-

import sys
import urllib
import time
import codecs
import Cookie
#import StringIO

#import zlib
import gzip

from lxml import etree
from xmlrpclib import ServerProxy

from twisted.python import log
from twisted.internet import reactor
from twisted.web import client, xmlrpc, server
import cache
import model 

sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

log.startLogging(sys.stdout)

def printError(failure):
  print >> sys.stderr, "Error", failure.getErrorMessage()

def Connection():
  return ServerProxy("http://localhost:9001", allow_none=True)

conn = cache.Connection()

def getter(url, contextFactory=None, *args, **kwargs):
    return client._makeGetterFactory(
        url,
        client.HTTPClientFactory,
        contextFactory=contextFactory,
        *args, **kwargs)



posts = []  
myheaders = None

class Controller(xmlrpc.XMLRPC): 
  def xmlrpc_store_headers(self, snatched):
    global myheaders
    print 'xmlrpc_store_cookie'
    if snatched:
      myheaders = snatched
    return None


  def xmlrpc_on_abacus(self, url):
    '''
      fires on request such as:
      http://abacus.tumblr.com/check_for_new_posts/a0146229bf7e844f190e2fcaecc47ab9.js?1321858402974

      this request genereted by following code in dashboard.html:
        var check_for_new_posts_url = 'http://abacus.tumblr.com/check_for_new_posts/a0146229bf7e844f190e2fcaecc47ab9.js';
        check_for_new_posts(60000);
    '''
    print time.time(), url
    if myheaders:
      print 'fetching dashboard'#, myheaders
      #g = getter('http://www.tumblr.com/dashboard', headers=myheaders)
      d = client.downloadPage('http://www.tumblr.com/dashboard', 'dashboard.xml.gz', headers=myheaders)
      def nyang(data):
        print 'Controller:self.nyang'
        '''
        for k, v in g.response_headers.items():
          print k, v

        print '-'*50
        print g.message[:40]

        coding = g.response_headers.get('content-encoding', ('plain',))[0]
        if coding == 'gzip':
          print 'gzip'
          data = zlib.decompress(f.data)#g.message)
        elif coding == 'plain':
          print 'plain'
          data = g.message
        else:
          print coding
        '''
        f = gzip.open('dashboard.xml.gz')
        data = f.read() 
        f.close()

        print '-'*50
        print data[:40]
        print '-'*50

        if data.startswith('''<!DOCTYPE html PUBLIC "-'''):
          ''' login '''
          print 'ugh! login requested.'
          return None
            
        t = etree.XML(data)
        find = etree.XPath('/tumblr/posts/post')
        for post in find(t):
          p = model.PostFactory(post)
          for u in p.assets_urls():
            conn.fetch(u)
          posts.append(p)
      d.addCallback(nyang).addErrback(printError)

    return None


if __name__ == '__main__':
  c = Controller(allowNone=True)  
  reactor.listenTCP(9001, server.Site(c))
  reactor.run()

