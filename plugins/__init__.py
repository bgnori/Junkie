#!/usr/bin/python
# -*- coding=utf8 -*-

import os.path
import glob

_mapper = {}


pluins_dir = os.path.dirname(__file__)
_pattern = os.path.join(pluins_dir, '*.py')


for p in glob.iglob(_pattern):
  n = os.path.basename(p)
  assert n.endswith('.py')
  m = n[:-3]
  if m == '__init__':
    continue
  print m
  obj = __import__(m, globals(), locals(), [], -1)
  _mapper[obj.host]=obj

print _mapper

def get(host):
  return _mapper[host]
