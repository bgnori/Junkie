#!/usr/bin/python
# -*- coding=utf8 -*-
import sys
import os
import os.path
import time
import pickle
import StringIO

import urllib
import urlparse

from lxml import etree
import magic
import yaml


from twisted.web import client
from twisted.internet import defer, reactor

def printError(failure):
  print >> sys.stderr, "Error", failure.getErrorMessage()


def url2name(url):
  parsed = urlparse.urlparse(url)
  return os.path.basename(parsed[2])#'path'


def assemble(url, rqtime, artime, data):
  '''
    ticket must be hashable.
  '''
  return (url, rqtime, artime, data)


class DataFile(StringIO.StringIO):
  def __init__(self, data, message, mime=None, dontguess=None):
    StringIO.StringIO.__init__(self, data)
    self.message = message
    if mime:
      self.contentType = mime
    elif dontguess:
      self.contentType = 'application/octet-stream' #default
    else:
      self.contentType = magic.from_buffer(data, mime=True) 
  
  def clone(self):
    return DataFile(self.getvalue(), self.message, self.contentType)



class CacheEntry(object):
  def __init__(self, key, path):
    self.path = path
    self.key = key
    self.readRequests = []
    self.datafile = None
    self.fname = None
    self.message = None

  def _make_path(self):
    return os.path.join(self.path, self.fname)

  def _read(self):
    return self.datafile.clone()

  def read(self):
    d = defer.Deferred()
    self.readRequests.append(d)
    if self.datafile:
      print >> sys.stderr, 'immediate read from memory for %s'%(self.key,)
      self.onReadyToRead()
    elif self.fname:
      print >> sys.stderr, 'immediate read from disk for %s'%(self.key,)
      self.readFromFile()
    else:
      print >> sys.stderr, 'waiting web for %s'%(self.key,)
    return d
    
  def abort(self):
    for d in self.readRequests:
      reactor.callLater(0, d.errback, None)
    self.readRequests = []

  def onReadyToRead(self):
    assert self.datafile
    for d in self.readRequests:
      reactor.callLater(0, d.callback, self._read()) 
    self.readRequests = []

  def write(self, datafile):
    assert not self.datafile
    self.datafile = datafile.clone()
    self.onReadyToRead()

  def writeToFile(self):
    assert self.datafile
    if not self.fname:
      self.fname = url2name(self.key)
    p = self._make_path()
    print >>sys.stderr, 'trying %s, %s'%(self.fname, self.key,)
    with open(p, 'w') as f:
      f.write(self.datafile.read())
      self.message = self.datafile.message
      self.contentType = self.datafile.contentType
      self.datafile = None
      print >>sys.stderr, 'wrote %s, %s'%(self.fname, self.key,)
    
  def readFromFile(self):
    p = self._make_path()
    with open(p, 'r') as f:
      self.datafile = DataFile(f.read(), self.message, self.contentType)
    if self.datafile:
      self.onReadyToRead()
   


class Storage(object):
  '''
    Storage to hold cached contents
  '''
  def __init__(self, path):
    self.path = path
    self.load_index()

  def __contains__(self, key):
    return key in self.index 

  def __len__(self):
    return len(self.index)
  
  def __iter__(self):
    return self.index.values()

  def _make_path(self, fname):
    return os.path.join(self.path, fname)

  def make_entry(self, key):
    '''
      reserve
    '''
    assert key not in self.index
    entry = CacheEntry(key, self.path)
    self.index[key] = entry
    return entry

  def get(self, key):
    return self.index.get(key, None)

  def pop(self, key):
    return self.index.pop(key)
    
  def load_index(self):
    p = self._make_path('index.pickle')
    
    no_index = False
    try:
      f = open(p)
    except:
      f = None
      pass
    if f:
      try:
        self.index = pickle.load(f)
      except:
        no_index = True        
      finally:
        f.close()
    else:
      no_index = True

    if no_index: 
      self.index = {}
      self.save_index()

  def save_entries(self):
    for entry in self.index.itervalues():
      if entry.datafile:
        entry.writeToFile()

  def save_index(self):
    p = self._make_path('index.pickle')
    for entry in self.index.itervalues():
      entry.abort()
    with open(p, 'w') as f:
      pickle.dump(self.index, f)

  def fix(self):
    to_delete = []
    for k, v in self.index.items():
      p = self._make_path(v)
      try:
        f = open(p)
        f.close()
      except:
        to_delete.append[k]
    for k in to_delete:
      del self.index[k]
    self.save_index()


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



class Renderer(object):
  def render(self, post):
    raise

class TextRenderer(object):
  def render(self, post):
    tree = post.build_tree()
    return etree.tostring(tree, pretty_print=True)

class HTMLRenderer(Renderer):
  def __init__(self):
    super(HTMLRenderer, self).__init__()
    self.context = []


  def push(self, item):
    self.context.append(item)
  def pop(self):
    return self.context.pop()
    

  def dn_post(self, elem):
    return '<html>'
  def up_post(self, elem):
    return '</html>'

  def dn_content(self, elem):
    return '<div>' + elem.text

  def up_content(self, elem):
    return '</div>'
  
  def dn_image(self, elem):
    return ''
  def up_image(self, elem):
    url = self.pop()
    #Storage.peek_filepath( Ugh!
    return '<img src="%s"/>'%(url)

  def dn_assets(self, elem):
    if elem.attrib['max-width']=='500':
      self.push(elem.text)
    return ''
  def up_assets(self, elem):
    return ''


  def invoke_dn(self, elem):
    return self.invoke_x(elem, 'dn_')
  
  def invoke_up(self, elem):
    return self.invoke_x(elem, 'up_')

  def invoke_x(self, elem, prefix):
    name = prefix + elem.tag
    handler = getattr(self, name, None)
    if handler:
      return handler(elem)
    return ''

  def make_html(self, elem):
    r = [self.invoke_dn(elem)]
    r += [self.make_html(child) for child in elem]
    r += self.invoke_up(elem)
    return  ''.join(r)
    
  def render(self, post):
    tree = post.build_tree()
    return self.make_html(tree)


class Junkie(object):
  agent = 'Junkie https://github.com/bgnori/Junkie'

  def __init__(self):
    self.posts = []
    self.storage = Storage('depot')
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
      f = DataFile(data, 'OK') #FIXME Don't guess, use header
      entry.write(f)
      return f
    d.addCallback(onPageArrival)
    def onFail(f):#FIXME
      entry.abort()
      return 'fail' #FIXME
    d.addErrback(onFail) 
    return entry

  def prefetch(self, uri):
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

'''
  making global values.
'''
junkie = Junkie()


