#!/usr/bin/python
# -*- coding=utf8 -*-

from copy import deepcopy
from lxml import etree

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
    

  def dn_id(self, elem):
    if elem.text:
      return '<p>' + elem.text
    return '<p>'
  def up_id(self, elem):
    return '</p>'

  def dn_url(self, elem):
    if elem.text:
      return '<p>' + elem.text
    return '<p>'
  def up_url(self, elem):
    return '</p>'


  def dn_post(self, elem):
    return '<div>'
  def up_post(self, elem):
    return '</div>'

  def dn_content(self, elem):
    if elem.text:
      return '<div>' + elem.text
    return '<div>'

  def up_content(self, elem):
    return '</div>'
  
  def dn_image(self, elem):
    return ''
  def up_image(self, elem):
    url = self.pop()
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


class GenshiRenderer(Renderer):
  pass


class XSLTRenderer(Renderer):
  def __init__(self, xslt_path):
    super(XSLTRenderer, self).__init__()
    self.load_xslt(xslt_path)

  def load_xslt(self, xslt_path):
    self.transform = None
    with open(xslt_path) as f:
      xml = etree.XML(f.read())
      self.transform = etree.XSLT(xml)

  def render(self, posts):
    dashboard = etree.Element('tumblr', version="1.0")
    x = etree.SubElement(dashboard, 'posts')
    
    if isinstance(posts, list):
      ps = posts
    else:
      assert isinstance(posts, Post)
      ps = [posts]
    for p in ps:
      x.append(deepcopy(p.elem))
    return self.transform(dashboard)

if __name__ == '__main__':

  import junkie

  def make_postdata(xmldata):
    t = etree.XML(xmldata)
    find = etree.XPath('/tumblr/posts/post')
    return [junkie.PostFactory(post) for post in find(t)]
  
  r = XSLTRenderer('tumblr.xslt')

  with open('dashboard/1323777364.11.xml') as f:
    posts = make_postdata(f.read())
    dashboard = r.render(posts)
    print dashboard 
  

