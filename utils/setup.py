#!/usr/bin/env python

from distutils.core import setup

setup(name='utils',
      version='0.6.0',
      description='Python programming utilities',
      long_description='Python programming utilities',
      maintainer='Rozsa, Tamas',
      maintainer_email='tamas.rozsa@knorr-bremse.com',
      url='http://bu2s0049/redmine/projects/utils',
      platforms=['MS Windows'],
      packages=['nputils', 'pyutils', 'osutils', 'debugutils'],
      package_dir={'': 'src'},
      requires=[
        'numpy(>=1.7.0)',
      ],
      provides=['nputils', 'pyutils', 'osutils', 'debugutils'],
      license=open('COPYING').read())
