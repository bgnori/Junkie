#!/usr/bin/python
# -*- coding=utf8 -*-

import sys

import urlparse
import magic

from twisted.web import client
from twisted.internet import reactor, defer

import tumblr

host = 'media.tumblr.com'
load = True


def process(request):
  print 'plugin: media-tumblr is serving'
  url = request.uri
  entry = tumblr.junkie.get(url) 
  return entry.read()

if __name__ == '__main__':
  print tumblr.junkie
  
