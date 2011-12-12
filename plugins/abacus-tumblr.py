#!/usr/bin/python
# -*- coding=utf8 -*-
import sys

from lxml import etree

from twisted.web import client
from twisted.internet import reactor

import tumblr

host = 'abacus.tumblr.com'
load = True


def process(request):
  print 'plugin: abacus.tumblr is serving'
  reactor.callLater(0.1, tumblr.junkie.prefetch, request.uri) #FIXME
  return None

if __name__ == '__main__':
  print auth
