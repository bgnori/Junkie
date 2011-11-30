#!/usr/bin/python
# -*- coding=utf8 -*-

import os.path
import glob
import igmatch

_mapper = igmatch.IGMatch({})


def load_plugins():
  pluins_dir = os.path.dirname(__file__)
  pattern = os.path.join(pluins_dir, '*.py')

  for p in glob.iglob(pattern):
    n = os.path.basename(p)
    assert n.endswith('.py')
    m = n[:-3]
    if m == '__init__':
      continue
    obj = __import__(m, globals(), locals(), [], -1)
    if hasattr(obj, "load") and not obj.load:
      continue
    print 'loading', obj.host
    _mapper.add(obj.host, obj)

load_plugins()


def get_mapper():
  return _mapper

