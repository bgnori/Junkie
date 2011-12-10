#!/usr/bin/python
# -*- coding=utf8 -*-
import sys
import urlparse
import os
import os.path
import time
import pickle
import StringIO
from lxml import etree


def url2name(url):
  parsed = urlparse.urlparse(url)
  return os.path.basename(parsed[2])#'path'


def assemble(url, rqtime, artime, data):
  '''
    ticket must be hashable.
  '''
  return (url, rqtime, artime, data)


class DataFile(StringIO.StringIO):
  def __init__(self, *args, **kws):
    StringIO.StringIO.__init__(self, *args, **kws)
    self.contentType = 'application/octet-stream' #default
    self.message = ''
  
  def clone(self):
    x = DataFile(self.getvalue())
    x.contentType = self.contentType
    x.message = self.message
    return x 


class Storage(object):
  '''
    Storage to hold cached contents
  '''
  def __init__(self, path):
    self.path = path
    self.load_index()
    self.pool = {} #.update({ticket: ()})
    print >> sys.stderr, 'Storage with %s is ready'%(self.path,)

  def __contains__(self, key):
    return key in self.index 

  def __len__(self):
    pass
  
  def __iter__(self):
    for key in self.index.keys():
      yield self.get(key)

  def reserve(self, key):
    assert key not in self.index
    ticket = self.pool.get(key, None)
    if ticket:
      return ticket
    ticket = assemble(key , time.time(), None, None)
    self.pool.update({ticket:[]})
    return ticket

  def isPrimaryTicket(self, ticket):
    assert ticket in self.pool
    return len(self.pool[ticket]) == 0

  def callbackPairs(self, ticket):
    for pair in self.pool.get(ticket):
      yield pair

  def register(self, ticket, callback):
    t = self.pool.get(ticket) 
    t.append[callback]
    self.pool[ticket] = t

  def _make_path(self, fname):
    return os.path.join(self.path, fname)

  def set(self, ticket, mime, data):
    assert ticket[0] not in self
    url = ticket[0]
    rq = ticket[1]
    ar = time.time()
    print >> sys.stderr, 'filling storage with %5f s:  %6i byte : %s'%( ar - rq , len(data), url)
    self.save(url, mime, data)

  def save(self, url, mime, data):
    fname = url2name(url)
    with file(self._make_path(fname), 'w') as f:
      self.index[url] = fname
      f.write(data)
      print 'saving:', url, ':', fname

  def get(self, key, default=None):
    p = self.peek_filepath(key, default)
    print 'Storage:get', key, p
    if p is None:
      return None
    with file(p, 'r') as f:
      return f.read()

  def peek_filepath(self, key,  default=None):
    fname = self.index.get(key, default)
    if fname is None:
      return None
    return self._make_path(fname)

  def pop(self, key):
    p = self.peek_filepath(key)
    if p:
      os.remove(p)
      del self.index[key]
    
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

  def save_index(self):
    p = self._make_path('index.pickle')
    print 'saving %i entries'%(len(self.index),)
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

storage = Storage('depot') #FIXME


