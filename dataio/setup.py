#!/usr/bin/env python

from distutils.core import setup

setup(name='dataio',
      version='2.12.1',
      description='Measurement parser toolchain',
      long_description='Measurement parser toolchain',
      maintainer='Rozsa, Tamas',
      maintainer_email='tamas.rozsa@knorr-bremse.com',
      url='http://leonidas/redmine/projects/dataio',
      platforms=['MS Windows'],
      packages=['measparser'],
      package_dir={'': 'src'},
      package_data={'measparser': ['dcnvt3_64.exe', 'ffmpeg.exe', 'mdfsort.exe', 'MdfLibms8.dll']},
      scripts=['scripts/parsemdf.py',
               'scripts/parsemf4.py',
               'scripts/purge_mdf.py',
               'scripts/purge_mf4.py',
               'scripts/merge_dbcs.py',],
      requires=['scipy(>=0.11.0)',
                'numpy(>=1.7.0)',
                'h5py(>=2.1.0)',
                'sqlalchemy(>=1.0.9)',
                'utils(>=0.1.0)'],
      provides=['measparser'],
      license=open('LICENSE').read())
