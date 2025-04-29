#!/usr/bin/env python

import os
import sys
import glob

from distutils.core import setup

name = 'dataevalaebs'

root = os.path.abspath(os.path.dirname(__file__))
dataeval_dir = os.path.join('~', '.'+os.getenv('DATAEVAL_NAME', 'dataeval'))
dataeval_dir = os.path.expanduser(dataeval_dir)

# find subprojects (packages)
src_path = os.path.join(root, 'src')
subprojects = []
for dirpath, dirs, files in os.walk(src_path):
  if '__init__.py' in files:
    subprj_dir = os.path.relpath(dirpath, src_path)
    subprj = '.'.join(subprj_dir.split(os.path.sep))
    subprojects.append(subprj)

# remove existing pth files pointing to this project
if 'install_data' in sys.argv:
  for file in glob.glob1(dataeval_dir, '*.pth'):
    fullfile = os.path.join(dataeval_dir, file)
    file_points_here = False
    with open(fullfile) as fp:
      content = fp.read()
      file_points_here = root in content
    if file_points_here:
      os.remove(fullfile)

# write new pth files temporarily
pth_files = []
for subprj in subprojects:
  pth = subprj + '.pth'
  subprj_path = os.path.abspath(os.path.join(root, 'src', *subprj.split('.')))
  open(pth, 'w').write(subprj_path)
  pth_files.append(pth)

# call setup
setup(name=name,
      version='2.0.0',
      description='dataevalaebs',
      long_description='DAS-specific measurement processing user modules',
      maintainer='Rozsa, Tamas',
      maintainer_email='tamas.rozsa@knorr-bremse.com',
      url='http://leonidas/redmine/projects/dataevalaebs',
      platforms=['MS Windows'],
      package_dir={'': 'src'},
      packages=subprojects,
      py_modules=[n[:-3]
                  for n in os.listdir('src')
                  if n.endswith('.py')],
      package_data={'': ['dataevalaebs/images/*',  # TODO: update package_data
                         'dataevalaebs/cfg/*']},
      requires=['scipy(>=0.10.1)',
                'matplotlib(>=1.1.0)',
                'numpy(>=1.6.1)',
                'h5py(>=2.0.1)',
                'pandas(>=0.15.0)', # for arel branch
                'reportlab(>=2.5)',
                'pyglet(>=1.1.4)',
                'aebs(>=5.14.0)',
                'dataio(>=2.11.0)',
                'dataeval(>=9.0.1)',
                'utils(>=0.4.0)'],
                # silkbaebs
                # python-redmine
                # requests
                # portalocker
      data_files=[(dataeval_dir, pth_files)],
      license=open('LICENSE').read())

# remove temporary pth files
for pth in pth_files:
  os.remove(pth)
