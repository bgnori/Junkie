#!/usr/bin/python
# -*- coding=utf8 -*-



import time
from xmlrpclib import ServerProxy


server = ServerProxy("http://localhost:9000", allow_none=True)

print server.fetch('http://www.python.org')
print 'waiting for cache'
time.sleep(10)
print 'now making get request'
data = server.get('http://www.python.org')

print data[:40]

data = server.get('http://www.python.org')
print data[:40]

data = server.pop('http://www.python.org')
print data[:40]

data = server.get('http://www.python.org')
print data is None


