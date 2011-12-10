#!/usr/bin/python
# -*- coding=utf8 -*-
import sys
import urllib
import urlparse
import yaml

from lxml import etree

import magic

from twisted.web import client
from twisted.internet import reactor

import tumblr

host = 'abacus.tumblr.com'
load = True


posts = []  
with open('config') as f:
  auth = yaml.load(f.read())
agent = 'Junkie https://github.com/bgnori/Junkie'

def printError(failure):
  print >> sys.stderr, "Error", failure.getErrorMessage()

def prefetch(uri):
  print 'abacus-tumblr.py:prefetch'

  data_dict = {'start': 0, 'num': 50}
  data_dict.update(auth)
  postdata = urllib.urlencode(data_dict)
  d = client.getPage('http://www.tumblr.com/api/dashboard', 
                          method='POST',
                          agent=agent,
                          headers = {'Content-Type': 'application/x-www-form-urlencoded'},
                          postdata=postdata)
  def update_posts(data):
    if data.startswith('''<!DOCTYPE html PUBLIC "-'''):
      ''' login '''
      print 'ugh! login failed.'
      return None
        
    t = etree.XML(data)
    find = etree.XPath('/tumblr/posts/post')
    for post in find(t):
      p = tumblr.PostFactory(post)
      for u in p.assets_urls():
        if url not in tumblr.storage:
          tumblr.get(url)
      posts.append(p)
  d.addCallback(update_posts).addErrback(printError)



def process(request):
  print 'plugin: abacus.tumblr is serving'
  reactor.callLater(0.1, prefetch, request.uri)
  return None

if __name__ == '__main__':
  print auth
