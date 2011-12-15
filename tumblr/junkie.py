#!/usr/bin/python
# -*- coding=utf8 -*-
import sys
import time

import urllib

import yaml
from lxml import etree
from lxml.html import builder as E

from twisted.web import client
from twisted.internet import defer, reactor

import cache


import tumblr.model
import tumblr.render

def printError(failure):
  print >> sys.stderr, "Error", failure.getErrorMessage()


class Junkie(object):
  agent = 'Junkie https://github.com/bgnori/Junkie'

  def __init__(self):
    self.posts = {}
    self.storage = cache.Storage('depot')
    self.renderer = tumblr.render.XSLTRenderer('tumblr/basic.xslt')
    with open('config') as f:
      self.auth = yaml.load(f.read())

  def get(self, url):
    ce = self._cache(url)
    if not ce:
      ce = self._web(url)
    return ce

  def _cache(self, url):
    '''
      retrieve content from cache.
      returns CacheEntry object
    '''
    return self.storage.get(url) 

  def _web(self, url):
    '''
      retrieve content from web.
      returns CacheEntry object
    '''
    entry = self.storage.make_entry(url)

    d = client.getPage(url)
    def onPageArrival(data):
      f = cache.DataFile(data, 'OK') #FIXME Don't guess, use header
      entry.write(f)
      return f
    d.addCallback(onPageArrival)
    def onFail(f):#FIXME
      entry.abort()
      return 'fail' #FIXME
    d.addErrback(onFail) 
    return entry

  def prefetch(self):
    data_dict = {'start': 0, 'num': 50}
    data_dict.update(self.auth)
    postdata = urllib.urlencode(data_dict)
    d = client.getPage('http://www.tumblr.com/api/dashboard', 
                            method='POST',
                            agent=self.agent,
                            headers = {'Content-Type': 'application/x-www-form-urlencoded'},
                            postdata=postdata)
    def onDataArrival(data):
      if data.startswith('''<!DOCTYPE html PUBLIC "-'''):
        ''' login '''
        print 'ugh! login failed.'
        return None
      with open('dashboard/%s.xml'%(time.time(),), 'w') as f:
        f.write(data)
      self.update_posts(data)
    d.addCallback(onDataArrival).addErrback(printError)


  def update_posts(self, xmldata):
    '''
      parse v1 XML data and store posts.
    '''
    t = etree.XML(xmldata)
    find = etree.XPath('/tumblr/posts/post')
    for post in find(t):
      p = tumblr.model.PostFactory(post)
      for url in p.assets_urls():
        self.get(url)
      self.posts[p.elem.attrib['id']] = p

  def make_dashboard(self):
    '''
      returns html
    '''
    post_div = self.renderer.render(self.posts)
    html = E.HTML(
      E.HEAD(
        E.META(charset="UTF-8"),
        E.META({"http-equiv":"Content-Type", "content":"text/html;charset=utf-8"}),
        E.TITLE("Mushboard"),
      ),
      E.BODY(
        post_div,
      )
    )
    return etree.tostring(html)

