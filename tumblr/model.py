#!/usr/bin/python
# -*- coding=utf8 -*-
import sys
import time
from copy import deepcopy

from lxml import etree

class Post(object):
  '''
    base class.
  '''
  _locations = {
    # elemetn post
    'id' : '@id', 
    'url' : '@url',
    'url_with_slug' : '@url-with_slug',
    'type' : '@type',
    'date_gmt' : '@date_gmt',
    'date' : '@date',
    'unix_timestamp' : '@unix-timestamp',
    'format' : '@format',
    'reblog_key' : '@reblog-key',
    'slug' : '@slug',
    'tumblelog' : '@tumblelog',
    'note_count' : '@note-count',
    'reblogged_from_url' : '@reblogged-from-url',
    'reblogged_from_name' : '@reblogged-from-name',
    'reblogged_from_title' : '@reblogged-from-title',
    'reblogged_from_avatar_url_16' : '@reblogged-from-avatar-url-16',
    'reblogged_from_avatar_url_24' : '@reblogged-from-avatar-url-24',
    'reblogged_from_avatar_url_30' : '@reblogged-from-avatar-url-30',
    'reblogged_from_avatar_url_40' : '@reblogged-from-avatar-url-40',
    'reblogged_from_avatar_url_48' : '@reblogged-from-avatar-url-48',
    'reblogged_from_avatar_url_64' : '@reblogged-from-avatar-url-64',
    'reblogged_from_avatar_url_96' : '@reblogged-from-avatar-url-96',
    'reblogged_from_avatar_url_128' : '@reblogged-from-avatar-url-128',
    'reblogged_from_avatar_url_512' : '@reblogged-from-avatar-url-512',
    'reblogged_root_url' : '@reblogged-root-url',
    'reblogged_root_avatar_url_16' : '@reblogged-root-avatar-url-16',
    'reblogged_root_avatar_url_24' : '@reblogged-root-avatar-url-24',
    'reblogged_root_avatar_url_30' : '@reblogged-root-avatar-url-30',
    'reblogged_root_avatar_url_40' : '@reblogged-root-avatar-url-40',
    'reblogged_root_avatar_url_48' : '@reblogged-root-avatar-url-48',
    'reblogged_root_avatar_url_64' : '@reblogged-root-avatar-url-64',
    'reblogged_root_avatar_url_96' : '@reblogged-root-avatar-url-96',
    'reblogged_root_avatar_url_128' : '@reblogged-root-avatar-url-128',
    'reblogged_root_avatar_url_512' : '@reblogged-root-avatar-url-512',
    'width' : '@width',
    'height' : '@height',

    #element tumblelog
    'title' : 'tumblelog@title',
    'name' : 'tumblelog@name',
    'url' : 'tumblelog@url',
    'timezone' : 'tumblelog@timezone',
    'avatar_url_16' : 'tumblelog@avatar-url-16',
    'avatar_url_24' : 'tumblelog@avatar-url-24',
    'avatar_url_30' : 'tumblelog@avatar-url-30',
    'avatar_url_40' : 'tumblelog@avatar-url-40',
    'avatar_url_48' : 'tumblelog@avatar-url-48',
    'avatar_url_64' : 'tumblelog@avatar-url-64',
    'avatar_url_96' : 'tumblelog@avatar-url-96',
    'avatar_url_128' : 'tumblelog@avatar-url-128',
    'avatar_url_512' : 'tumblelog@avatar-url-512',
  }

  def __init__(self, elem):
    self.elem = deepcopy(elem)

  def __str__(self):
    return "<%s object %s, %s, %s>" % (self.__class__.__name__, self.id, self.type, self.url)

  def render_as_text(self):
    print self

  def xpath(self, path):
    return self.elem.xpath(path)


  def __getattr__(self, name):
    p = self._locations.get(name, None)
    if p is None:
      p = super(self.__class__, self)._locations.get(name)
    x = self.xpath(p)

    if len(x) == 0:
      return None
    elif len(x) == 1:
      return x[0]
    assert False

  def avatar_urls(self):
    urls = []
    for key in self._locations.keys():
      if 'avatar_url' in key:
        urls.append(self._locations[key])
    return urls
    
  def assets_urls(self):
    return tuple()


class Text(Post):
  _locations = {
    'regular_title' : 'regular-title/text()', 
    'regular_body' : 'regular-body/text()'
  }

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
  '''
    file:///home/nori/Desktop/work/tumblr/dashboard/1323779788.34.xml
  '''
  _locations = {  
    'quote_text' : 'quote-text/text()',
    'quote_source' : 'quote-source/text()'
  }
    
  def render_as_text(self):
    # 'tumblelog'
    print self.quote_text
    print self.quote_source

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
  '''
    Photo set
    file:///home/nori/Desktop/work/tumblr/dashboard/1323778138.53.xml
  '''
  _locations = {  
  #photo-caption
    'photo_caption' : 'photo-caption/text()',
  #photo-url
    'photo_url_1280' : 'photo-url[@max-width="1280"]/text()',
    'photo_url_500' : 'photo-url[@max-width="500"]/text()',
    'photo_url_400' : 'photo-url[@max-width="400"]/text()',
    'photo_url_250' : 'photo-url[@max-width="250"]/text()',
    'photo_url_100' : 'photo-url[@max-width="100"]/text()',
    'photo_url_75' : 'photo-url[@max-width="75"]/text()',
  #photoset ... 
    'photoset' : 'photoset',
    'photoset_photo' : 'photoset/photo',
    'photoset_photo_offset' : 'photoset/photo@offset',
    'photoset_photo_caption' : 'photoset/photo@caption',
    'photoset_photo_width' : 'photoset/photo@width',
    'photoset_photo_height' : 'photoset/photo@height',
    'photoset_photo_url_1280' : 'photoset/photo/photo-url[@max-width="1280"]/text()',
    'photoset_photo_url_500' : 'photoset/photo/photo-url[@max-width="500"]/text()',
    'photoset_photo_url_400' : 'photoset/photo/photo-url[@max-width="400"]/text()',
    'photoset_photo_url_250' : 'photoset/photo/photo-url[@max-width="250"]/text()',
    'photoset_photo_url_100' : 'photoset/photo/photo-url[@max-width="100"]/text()',
    'photoset_photo_url_75' : 'photoset/photo/photo-url[@max-width="75"]/text()',

  }
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
    return self.elem.xpath('photo-url/text()')

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
  '''
    file:///home/nori/Desktop/work/tumblr/dashboard/1323777273.4.xml
  '''
  _locations = {  
    'link_text' : 'link-text/text()', 
    'link_url' : 'link-url/text()',
    'link_description' : 'link-description/text()',
  }

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
  '''
    file:///home/nori/Desktop/work/tumblr/dashboard/1323907776.95.xml
  '''
  _locations = {  
    'video-catption' : 'video-caption/text()', 
    'video-source' : 'video-source/text()', 
    'video-player' : 'video-source[/text()', 
    'video-player_500' : 'video-source[max-width="500"]/text()', 
    'video-player_25-' : 'video-source[max-width="250"]/text()', 
  }


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

