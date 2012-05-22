#!/usr/bin/env python

from distutils.core import setup

setup(name='python-dabepg',
      version='0.4.0',
      description='DAB EPG XML/binary implementation',
      author='Ben Poor',
      author_email='ben.poor@thisisglobal.com',
      packages=['dabepg', 'dabepg.xml', 'dabepg.binary'],
      package_dir = {'' : 'src'}
)
