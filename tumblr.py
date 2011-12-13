#!/usr/bin/python
# -*- coding=utf8 -*-
import sys
import time

import urllib

from lxml import etree
import yaml


from twisted.web import client
from twisted.internet import defer, reactor

import cache

def printError(failure):
  print >> sys.stderr, "Error", failure.getErrorMessage()


class Post(object):
  '''
    base class.
  '''
  def __init__(self, elem):
    self.elem = elem

  def __str__(self):
    return "<Post object %s, %s, %s>"%(self.elem.attrib['id'], self.elem.attrib['type'], self.elem.attrib['url'])

  def render_as_text(self):
    print self

  def assets_urls(self):
    return tuple()


  def build_common(self):
    root = etree.Element('post')
    id = etree.SubElement(root, 'id')
    id.text = self.elem.attrib['id']
    url = etree.SubElement(root, 'url')
    url.text = self.elem.attrib['url']
    return root

  def build_tree(self):
    root = self.build_common()
    content = etree.SubElement(root, 'content')
    return root

class Text(Post):
  def render_as_text(self):
    rt = self.elem.find('regular-title')
    print rt.text
    rb = self.elem.find('regular-body')
    print rb.text

  def build_tree(self):
    root = self.build_common()
    content = etree.SubElement(root, 'content')
    content.text = self.elem.find('regular-title').text
    content = etree.SubElement(root, 'content')
    content.text = self.elem.find('regular-body').text
    return root

  def assets_urls(self):
    rb = self.elem.find('regular-body')
    return (img.attrib['src'] for img in rb.findall('img'))

class Quote(Post):
  def render_as_text(self):
    qt = self.elem.find('quote-text')
    print qt.text
    qs = self.elem.find('quote-source')
    if qs:
      print qs.text

  def build_tree(self):
    root = self.build_common()
    quote_text = etree.SubElement(root, 'content')
    quote_text.text = self.elem.find('quote-text').text
    qs = self.elem.find('quote-source')
    if qs:
      quote_source = etree.SubElement(root, 'content')
      quote_source.text = qs.text
    return root


class Photo(Post):
  def render_as_text(self):
    pc = self.elem.findall('photo-caption')
    if pc:
      print pc[0].text
    else:
      print 'No photo-caption available.'
    plu = self.elem.findall('photo-link-url')
    if plu:
      print plu[0].text
    else:
      print 'No photo-link-url available'
    
    for pu in self.elem.findall('photo-url'):
      print pu.attrib['max-width'], pu.text

    ps = self.elem.findall('photoset')
    if ps:
      for p in ps[0].findall('photo'):
        print p.attrib['offset'], p.attrib['caption'], p.attrib['width'], p.attrib['height']
        for pu in p.findall('photo-url'):
          print pu.attrib['max-width'], pu.text

  def assets_urls(self):
    for pu in self.elem.findall('photo-url'):
      yield pu.text
    ps = self.elem.findall('photoset')
    if ps:
      for p in ps[0].findall('photo'):
        for pu in p.findall('photo-url'):
          yield pu.text

  def build_tree(self):
    root = self.build_common()
    pc = self.elem.findall('photo-caption')
    if pc:
      photo_caption = etree.SubElement(root, 'content') 
      photo_caption.text = pc[0].text
  
    photo = etree.SubElement(root, 'image') 
    plu = self.elem.findall('photo-link-url')
    if plu:
      photo_link_url = etree.SubElement(photo, 'link')
      photo_link_url.text = plu[0].text
    for pu in self.elem.findall('photo-url'):
      photo_url = etree.SubElement(photo, 'assets')
      photo_url.text = pu.text
      photo_url.attrib['max-width'] = pu.attrib['max-width']

    ps = self.elem.findall('photoset')
    if ps:
      photoset = etree.SubElement(photo, 'content')
      for p in ps[0].findall('photo'):
        photo = etree.SubElement(photoset, 'image')
        for pu in p.findall('photo-url'):
          photo_url = etree.SubElement(photo, 'assets')
          photo_url.text = pu.text
          photo_url.attrib['max-width'] = pu.attrib['max-width']
    return root

class Link(Post):
  def render_as_text(self):
    lt = self.elem.find('link-text')
    print lt.text
    lu = self.elem.find('link-url')
    print lu.text

class Chat(Post):
  def render_as_text(self):
    title = self.elem.find('conversation-title')
    print title.text
    # content is very same as conversation/line
    # text = self.elem.find('conversation-text')
    # print text.text

    lines = self.elem.findall('conversation/line')
    for line in lines:
      print line.attrib['name'], line.attrib['label'], line.text

class Video(Post):
  pass

class Audio(Post):
  pass


# Must be one of text, quote, photo, link, chat, video, or audio.
mapper = {'regular':Text, 'quote':Quote, 'photo':Photo, 'link':Link, 'conversation':Chat, 'video':Video, 'audio':Audio}

def PostFactory(elem):
  '''
    create  Post object from lxml.etree.Elemnt object
    http://lxml.de/xpathxslt.html
  '''
  cls = mapper[elem.attrib['type']]
  return cls(elem)


class Junkie(object):
  agent = 'Junkie https://github.com/bgnori/Junkie'

  def __init__(self):
    self.posts = []
    self.storage = cache.Storage('depot')
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
      p = PostFactory(post)
      for url in p.assets_urls():
        self.get(url)
      self.posts.append(p)


