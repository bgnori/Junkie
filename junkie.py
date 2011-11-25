#!/usr/bin/python
# -*- coding=utf8 -*-


import sys
import time
import urllib
import codecs

from lxml import etree
from xmlrpclib import ServerProxy
import model 
from cache import CacheServerProcess 
from proxy import ProxyServerProcess 
from control import Controller

with CacheServerProcess() as server:
  with ProxyServerProcess() as proxy:
    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

    while True:
      time.sleep(3.0)

