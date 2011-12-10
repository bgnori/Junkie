#!/usr/bin/python
# -*- coding=utf8 -*-
import sys
import urllib
import urlparse
import yaml

from lxml import etree

from twisted.web import client
from twisted.internet import reactor

import model

host = 'abacus.tumblr.com'
load = True


posts = []  
with open('config') as f:
  auth = yaml.load(f.read())
agent = 'Junkie https://github.com/bgnori/Junkie'

def printError(failure):
  print >> sys.stderr, "Error", failure.getErrorMessage()

def fetch(url):
  d = None
  if url not in model.storage:
    print 'prefetching ', url
    ticket = model.storage.reserve(url)

    d = client.getPage(url)
    def onPageArrival(data):
      # mime = 'application/octet-stream' #Ugh! fix me
      mime = magic.from_buffer(data, mime=True) #FIXME, better than above. Don't guess, use header
      model.storage.set(ticket, mime, data)
      for consumer, fail in model.storage.callbackPairs(ticket):
        reactor.callLater(0, consumer, f.clone())
    def onFail(f):#FIXME
      for consumer, fail in model.storage.callbackPairs(ticket):
        reactor.callLater(0, fail, f.clone())
      return 'fail' #FIXME
    d.addCallback(onPageArrival)
    d.addErrback(onFail) 
  return d

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
      p = model.PostFactory(post)
      for u in p.assets_urls():
        fetch(u)
      posts.append(p)
  d.addCallback(update_posts).addErrback(printError)



def process(request):
  print 'plugin: abacus.tumblr is serving'
  reactor.callLater(0.1, prefetch, request.uri)
  return None
