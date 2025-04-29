#!/usr/bin/env python

from distutils.core import setup

setup(name='fusion',
      version='0.3.0',
      description='Sensor data fusion algorithms',
      long_description='Sensor data fusion algorithms',
      maintainer='Jozsa Gergely',
      maintainer_email='gergely.jozsa@knorr-bremse.com',
      platforms=['MS Windows'],
      packages=['asso', 'fus', 'fusutils', 'pathpred'],
      package_dir={'': 'src'},
      requires=['scipy(>=0.10.1)',
                'numpy(>=1.6.1)',
                'matplotlib(>=1.1.0)',
                'utils(>=0.1.0)',
                'dataio(>=0.1.10)',
                'dataeval(>=0.6.1)'],
      provides=['asso', 'fus', 'fusutils', 'pathpred'],
      license=open('LICENSE').read())
