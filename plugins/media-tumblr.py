#!/usr/bin/python
# -*- coding=utf8 -*-

import tumblr

host = 'media.tumblr.com'
load = True


def process(request):
  print 'plugin: media-tumblr is serving'
  url = request.uri
  entry = tumblr.junkie.get(url) 
  return entry.read()

  
