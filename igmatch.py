#!/usr/bin/python
# -*- coding=utf8 -*-

'''
  igmatch = increametal greedy match object for domain name

'''

class IGMatch(object):
  '''
    >>> igm = IGMatch([('tumblr.com', 0), ('www.tumblr.com', 1), ('media.tumblr.com', 2), ('www.google.com', 3)])
    >>> igm._imp
    {'com': ({'tumblr': ({'media': ({}, 2), 'www': ({}, 1)}, 0), 'google': ({'www': ({}, 3)},)},)}

    >>> igm.exact('tumblr.com')
    0

    >>> igm.exact('www.google.com')
    3

    >>> igm.postfix('com')
    set([0, 1, 2, 3])

    >>> igm.postfix('tumblr.com')
    set([0, 1, 2])

    >>> igm.postfix('media.tumblr.com')
    set([2])

    >>> igm.postfix('23.media.tumblr.com')
    set([2])

    >>> igm.postfix('jp')
    set([])

  '''
  def _add(self, d, ss, v):
    #print d
    assert isinstance(d, dict)
    if ss[-1] in d:
      if len(ss[:-1]) > 0:
        self._add(d[ss[-1]][0], ss[:-1], v)
      else:
        assert len(d[ss[-1]]) == 1
        d[ss[-1]] =([d[ss[-1]][0]], v)
    else:
      def nest(s, x):
        return {s:(x, )}
      x = {ss[0]:({},v)}
      for s in ss[1:]:
        x = nest(s, x)
      d.update(x)

  def add(self, s, v):
    self._add(self._imp, s.split('.'), v)

  def __init__(self, t):
    if isinstance(t, (tuple, list)):
      self._imp = {}
      for s, v in t:
        self.add(s, v)
    else:
      self._imp = dict(t)
      
  def exact(self, s):
    xs = s.split('.')
    xs.reverse()
    return self._exact(self._imp, xs)

  def _exact(self, imp, xs):
    assert isinstance(imp, dict)
    if len(xs) > 1: 
      r = imp.get(xs[0], None)
      if r:
        return self._exact(r[0], xs[1:])
      else:
        return None
    elif len(xs) == 1:
      r = imp.get(xs[0], None)
      if r is not None and len(r) == 2:
        return r[1]      
      return None
    else:
      pass
    assert False

      
  def postfix(self, s):
    xs = s.split('.')
    xs.reverse()
    return self._postfix(self._imp, xs)

  def _postfix(self, imp, xs):
    assert isinstance(imp, dict)
    if len(xs) > 1: 
      r = imp.get(xs[0], None)
      if r:
        if len(r[0]) > 0:
          return self._postfix(r[0], xs[1:])
        else:
          return set([r[1]])
      else:
        return set([])
    elif len(xs) == 1:
      r = imp.get(xs[0], None)
      if r is not None:
        if len(r) == 2:
          x = self._to_set(r[0])
          if len(xs) == 1:
            x.add(r[1])
          return x
        elif len(r) == 1:
          return self._to_set(r[0])
        else:
          assert False
      else:
        return set([])
    else:
      pass
    assert False

  def _to_set(self, imp):
    assert isinstance(imp, dict)
    r = set([])
    for v in imp.itervalues():
      if len(v) == 2:
        r.add(v[1])
        r.update(self._to_set(v[0]))
      elif len(v) == 1:
        r.update(self._to_set(v[0]))
      else:
        assert False
    return r

_mapper = IGMatch({})

def register(dname, handler):
  _mapper.add(dname, handler)

if __name__ == '__main__':
  import doctest
  doctest.testmod()


