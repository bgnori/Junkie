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
  f = urllib.urlopen('http://bgnori.tumblr.com/api/read')
  data = f.read()
  f.close()

  sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
  t = etree.XML(data)
  find = etree.XPath('/tumblr/posts/post')

  for post in find(t):
    p = model.PostFactory(post)
    print '-' * 60
    for u in p.urls():
      print u
      server.fetch(u)
    p.render_as_text()

  for n in range(10):
    time.sleep(1.0)
    print server.count()

  raw_input() #wait


