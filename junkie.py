#!/usr/bin/python
# -*- coding=utf8 -*-


#import wx
#print wx.version()

#app = wx.App(False)
#frame = wx.Frame(None, wx.ID_ANY, 'Hey Tumblr Junkie!')
#frame.Show(True)
#app.MainLoop()

import sys
import time
import urllib
import codecs

from lxml import etree
from xmlrpclib import ServerProxy
import model 
from cache import CacheServerProcess 

with CacheServerProcess() as server:
  sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

  f = urllib.urlopen('http://bgnori.tumblr.com/api/read')
  data = f.read()
  f.close()

  t = etree.XML(data)
  find = etree.XPath('/tumblr/posts/post')

  #renderer = model.TextRenderer()
  posts = []  
  for post in find(t):
    p = model.PostFactory(post)
    for u in p.assets_urls():
      server.fetch(u)
    #print renderer.render(p)
    posts.append(p)

  raw_input() #wait
  server.save()
  raw_input() #wait
