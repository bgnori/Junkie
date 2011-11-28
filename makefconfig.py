#!/usr/bin/python
# -*- coding=utf8 -*-

template = open('buildout.in')

cfg = open('buildout.cfg', 'w')


cfg.write(template.read())
template.close()

freeze = open('freeze.txt')

cfg.write('eggs =\n')

for line in freeze:
  cfg.write(' '*4)
  cfg.write(line)
  
freeze.close()
cfg.close()
  
