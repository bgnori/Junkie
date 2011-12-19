#!/usr/bin/python
# -*- coding=utf8 -*-

from setuptools import setup, find_packages
name = "Junkie"
version = '0.0.1'


setup(
  name=name,
  packages = find_packages('src'),
  package_dir = {'':'src'},
  install_requires=open('freeze.txt').readlines(),
  include_package_data=True,
  package_data = {
    '': ['memo.txt'],
    'src/tumblr': ['basic.xslt'],
  },
  entry_points = {
    'console_scripts' :[
      'junkie = app:main',
    ],
  },
  author='Noriyuki Hosaka',
  author_email='bgnori@gmail.com',
  description='Local HTTP Proxy with prefetching etc. for Tumblr',
  license='MIT',
  keywords='Tumblr, proxy, twisted',
  url='https://github.com/bgnori/Junkie',
)
