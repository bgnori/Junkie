#!/usr/bin/python
# -*- coding=utf8 -*-


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


class Text(Post):
  pass

class Quote(Post):
  def render_as_text(self):
    qt = self.elem.find('quote-text')
    print qt.text
    qs = self.elem.find('quote-source')
    print qs.text

class Photo(Post):
  def render_as_text(self):
    pc = self.elem.find('photo-caption')
    if pc:
      print pc.text
    else:
      print 'No photo-caption available.'
    plu = self.elem.find('photo-link-url')
    if plu:
      print plu
    else:
      print 'No photo-link-url available'
    
    for pu in self.elem.findall('photo-url'):
      print pu.attrib['max-width'], pu.text

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
    text = self.elem.find('conversation-text')
    print text.text
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

