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
import subprocess

from lxml import etree
from xmlrpclib import ServerProxy
import model

class CacheServer(object):
  process = None
  def __enter__(self):
    self.process = subprocess.Popen(['python', 'cache.py'])
    return ServerProxy("http://localhost:9000", allow_none=True)

  def __exit__(self, exc_type, exc_value, traceback):
    if self.process.poll() is None:
      print 'trying to terminate cache process'
      server.terminate()
      self.process.wait()
      print 'cache process looks terminated.'
    return False



with CacheServer() as server:
  sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

  f = urllib.urlopen('http://bgnori.tumblr.com/api/read')
  data = f.read()
  f.close()

  t = etree.XML(data)
  find = etree.XPath('/tumblr/posts/post')

  renderer = model.TextRenderer()
  posts = []  
  for post in find(t):
    p = model.PostFactory(post)
    print '-' * 60
    for u in p.assets_urls():
      print u
      server.fetch(u)
    print renderer.render(p)
    posts.append(p)

  for n in range(5):
    time.sleep(1.0)
    print server.count()
  raw_input() #wait
  for post in posts:
    for url in post.assets_urls():
      print 'saving:', url
      server.save(url)
  
  import wx
  import viewer
  app = wx.App(False)
  frame = wx.Frame(None, wx.ID_ANY, 'Hey Tumblr Junkie!')
  cv = viewer.ContentViewer(frame, -1)
  cv.SetContent(posts[0])
  frame.Show(True)
  app.MainLoop()
  

