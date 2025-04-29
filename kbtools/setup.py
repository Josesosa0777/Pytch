#!/usr/bin/env python

from distutils.core import setup

setup(name='kbtools',
      version='0.1.0',
      description='',
      long_description='',
      maintainer='Ulrich Guecker',
      maintainer_email='ulrich.guecker@knorr-bremse.com',
      url='http://bu2w0247/redmine/projects/kbtools',
      platforms=['MS Windows'],
      packages=['kbtools'],
      package_dir={'': 'src'},
      package_data={'kbtools': ['kb_tex_logo_default.ps', 'kb_tex_stylefile_default.sty']},
      requires=['numpy(>=1.6.1)', 
                'matplotlib(>=1.1.0)',
                'scipy(>=0.10.1)',
                'xlrd(>=0.7.1)',
                'dataio(>=0.1.0)',
                'dataeval(>=0.1.0)'],
      provides=['kbtools'],
      license=open('LICENSE').read())
