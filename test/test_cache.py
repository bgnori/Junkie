#!/usr/bin/python
# -*- coding=utf8 -*-
import os

from twisted.internet import reactor, defer
from twisted.trial.unittest import TestCase

from cache import DataFile, CacheEntry, url2name

html = '<html><head>hoge</head><body>hello!</body></html>'

class TestDataFIle(TestCase):
  def test_mime(self):
    f = DataFile('', '', 'image/gif')
    self.assertEquals(f.contentType, 'image/gif')

  def test_do_not_guess(self):
    f = DataFile('', '', dontguess=True)
    self.assertEquals(f.contentType, 'application/octet-stream')

  def test_do_guess(self):
    f = DataFile(html, '', dontguess=False)
    self.assertEquals(f.contentType, 'text/html')

  def test_default(self):
    f = DataFile(html, '')
    self.assertEquals(f.contentType, 'text/html')


class TestCacheEntry(TestCase):
  def test_touch(self):
    import time
    ce = CacheEntry(None, None, 0.0, None)
    self.assert_(ce.last_touch == 0.0)

    before = time.time()
    ce.touch()
    after = time.time()
    self.assert_(before <= ce.last_touch)
    self.assert_(ce.last_touch <= after)
  
  def test_read_on_memory(self):
    ce = CacheEntry(None, None, 0.0, lambda x:x)
    ce.write(DataFile('deadbeaf', ''))
    d = ce.read()
    def xxx(f):
      self.assertEquals(f.read(), 'deadbeaf')
    d.addCallback(xxx)
    return d
  test_read_on_memory.timeout = 1

  
class TestCacheEntryDisk(TestCase):
  def setUp(self):
    os.mkdir('test')
    f = open('test/data', 'w')
    f.write('deadbeaf')
    f.close()

  def tearDown(self):
    os.remove('test/data')
    os.rmdir('test')


  def test_read_on_disk_ok(self):
    cells = {'flag':False,
             'x' : None,
             'y': None}

    def my_asserts():
      print 'my_asserts'
      self.assert_(cells['flag'])
      self.assertNotEquals(cells['x'], cells['y'])

    def onFire(ce):
      f = ce.datafile
      self.assertEquals(f.read(), 'deadbeaf')
      cells['y'] = id(f)

    ce = CacheEntry('http://example.com/foo/bar/data', 'test', 0.0, onFire)
    ce.datafile = None 
    ce.fname = url2name(ce.key)
    d = ce.read()

    def xxx(f):
      cells['flag'] = True
      self.assertEquals(f.read(), 'deadbeaf')
      cells['x'] = id(f)
      my_asserts()
    d.addCallback(xxx)

    return d
  test_read_on_disk_ok.timeout = 1


  def test_read_on_disk_err(self):
    flag = True
    def onFire(x):
      global flag
      flag = True
    ce = CacheEntry('http://example.com/foo/bar/doesnotexist', 'test', 0.0, onFire)
    ce.datafile = None 
    d = ce.read()
    def xxx(f):
      self.assert_(False)
    d.addCallback(xxx)

    def xxx(f):
      global flag
      flag = True
    d.addErrback(xxx)

    def xxx(f):
      self.assert_(flag)
    d.addCallback(xxx)
    return d
  test_read_on_disk_err.timeout = 1


class TestCacheEntryWeb(TestCase):
  def test_read_on_miss(self):
    ce = CacheEntry('http://example.com/foo/bar/data', 'test', 0.0, lambda x:x)
  def test_abort(self):
    pass


