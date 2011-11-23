#!/usr/bin/python
# -*- coding=utf8 -*-

import sys
import urllib
import time
import codecs

import urlparse
import urllib

#import zlib
import gzip

from lxml import etree
from xmlrpclib import ServerProxy

import yaml

from twisted.python import log
from twisted.internet import reactor
from twisted.web import client, xmlrpc, server, http
import cache
import model 

sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

log.startLogging(sys.stdout)

def printError(failure):
  print >> sys.stderr, "Error", failure.getErrorMessage()

def Connection():
  return ServerProxy("http://localhost:9001", allow_none=True)

conn = cache.Connection()

posts = []  
with open('config') as f:
  auth = yaml.load(f.read())
agent = 'Junkie https://github.com/bgnori/Junkie'

class Controller(xmlrpc.XMLRPC): 
  def xmlrpc_store_headers(self, snatched):
    ''' todo: rename and use this for fetch control '''
    print 'xmlrpc_store_cookie'
    return None


  def xmlrpc_on_abacus(self, url):
    '''
      Access to abacus fired by js in browser, to know new arrivals.
    '''
    '''
      fires on request such as:
      http://abacus.tumblr.com/check_for_new_posts/a0146229bf7e844f190e2fcaecc47ab9.js?1321858402974 
      this request genereted by following code in dashboard.html:
        var check_for_new_posts_url = 'http://abacus.tumblr.com/check_for_new_posts/a0146229bf7e844f190e2fcaecc47ab9.js';
        check_for_new_posts(60000);
    '''
    print time.time(), url

    #if myheaders:
    if True:
      data_dict = {'start': 0, 'num': 50}
      data_dict.update(auth)
      postdata = urllib.urlencode(data_dict)
      d = client.getPage('http://www.tumblr.com/api/dashboard', 
                              method='POST',
                              agent=agent,
                              headers = {'Content-Type': 'application/x-www-form-urlencoded'},
                              postdata=postdata)
      def nyang(data):
        print 'Controller:self.nyang'
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

