#!/usr/bin/env python

from distutils.core import setup

setup(name='kbtoolsuser',
      version='0.1.0',
      description='',
      long_description='',
      maintainer='Ulrich Guecker',
      maintainer_email='ulrich.guecker@knorr-bremse.com',
      platforms=['MS Windows'],
      packages=['kbtools_user'],
      package_dir={'': 'src'},
      requires=['scipy(>=0.10.1)',
                'numpy(>=1.6.1)',
                'matplotlib(>=1.1.0)', 
                'kbtools(>=0.1.0)', 
                'dataeval(>=0.1.0)', 
                'dataio(>=0.1.0)'],
      provides=['kbtools_user'],
      license=open('LICENSE').read())
