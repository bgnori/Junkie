#!/usr/bin/python
# -*- coding=utf8 -*-
import sys
import urllib
import urlparse

from lxml import etree


from twisted.web import client
from twisted.internet import reactor

import tumblr

host = 'abacus.tumblr.com'
load = True


def printError(failure):
  print >> sys.stderr, "Error", failure.getErrorMessage()

def prefetch(uri):
  print 'abacus-tumblr.py:prefetch'

  data_dict = {'start': 0, 'num': 50}
  data_dict.update(tumblr.auth)
  postdata = urllib.urlencode(data_dict)
  d = client.getPage('http://www.tumblr.com/api/dashboard', 
                          method='POST',
                          agent=tumblr.agent,
                          headers = {'Content-Type': 'application/x-www-form-urlencoded'},
                          postdata=postdata)
  def onDataArrival(data):
    if data.startswith('''<!DOCTYPE html PUBLIC "-'''):
      ''' login '''
      print 'ugh! login failed.'
      return None
    tumblr.update_posts(data)
        
  d.addCallback(onDataArrival).addErrback(printError)


def process(request):
  print 'plugin: abacus.tumblr is serving'
  reactor.callLater(0.1, prefetch, request.uri)
  return None

if __name__ == '__main__':
  print auth
