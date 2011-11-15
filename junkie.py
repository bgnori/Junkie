#!/usr/bin/python
# -*- coding=utf8 -*-


#import wx
#print wx.version()

#app = wx.App(False)
#frame = wx.Frame(None, wx.ID_ANY, 'Hey Tumblr Junkie!')
#frame.Show(True)
#app.MainLoop()

import urllib
from lxml import etree
import model

f = urllib.urlopen('http://bgnori.tumblr.com/api/read')
data = f.read()
f.close()

t = etree.XML(data)

find = etree.XPath('/tumblr/posts/post')

for post in find(t):
  p = model.PostFactory(post)
  print '-' * 60
  p.render_as_text()
  

