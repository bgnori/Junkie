#!/usr/bin/python
# -*- coding=utf8 -*-
import sys

import os.path
import glob
import igmatch


_mapper = igmatch.IGMatch({})


def load_plugins():
  pluins_dir = os.path.dirname(__file__)
  pattern = os.path.join(pluins_dir, '*.py')

  for p in glob.iglob(pattern):
    print >> sys.stderr, 'working on', p
    n = os.path.basename(p)
    assert n.endswith('.py')
    m = n[:-3]
    if m == '__init__':
      print >> sys.stderr, 'skipping.'
      continue
    obj = __import__(m, globals(), locals(), [], -1)
    if hasattr(obj, "load") and not obj.load:
      print >> sys.stderr, 'no load flag or False'
      continue
    print >> sys.stderr, 'loading', obj.host
    _mapper.add(obj.host, obj)

load_plugins()


def get_mapper():
  return _mapper

