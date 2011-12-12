#!/usr/bin/python
# -*- coding=utf8 -*-
import sys


from twisted.python import log
from twisted.internet import reactor

import proxy

# junkie = tumblr.Junkie()

def main():
    reactor.listenTCP(8080, proxy.PrefetchProxyFactory())#'proxy.log'))
    reactor.run()
    tumblr.junkie.storage.save_entries()
    tumblr.junkie.storage.save_index()
    print >> sys.stderr, 'bye! (proxy.py)'


with open('junkie.log', 'w') as f:
    log.startLogging(f)
    import tumblr
    import plugins
    main()

