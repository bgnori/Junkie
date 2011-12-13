#!/usr/bin/python
# -*- coding=utf8 -*-

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


if __name__ == '__main__':
  import os
  #from genshi.template import TemplateLoader
  from lxml import etree

  import tumblr

  def make_postdata(xmldata):
    t = etree.XML(xmldata)
    find = etree.XPath('/tumblr/posts/post')
    return [tumblr.PostFactory(post) for post in find(t)]
  
  #loader = TemplateLoader(['./']) #os.path.dirname(__file__) )
  #tmpl = loader.load('test.html')
  
  with open('dashboard/1323777364.11.xml') as f:
    src = f.read()
    xml = etree.XML(src)
    #posts = make_postdata(f.read())
    
  with open('tumblr.xslt') as f:
    xslt = f.read()
    root = etree.XML(xslt)
    transform = etree.XSLT(root)
  
  r = transform(xml)
  print r#.tostring()
  #print posts
  #stream = tmpl.generate(title = u"mushboard", posts=posts)
  #html = stream.render("html")
  #print html


