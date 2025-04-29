#!/usr/bin/env python

import os
from ConfigParser import RawConfigParser
from distutils.core import setup
from setuptools import find_packages

name = 'aebs'
user_projects = ('aebs', 'ad', 'ta')

dataeval_dir = os.path.join('~', '.'+os.getenv('DATAEVAL_NAME', 'dataeval'))
dataeval_dir = os.path.expanduser(dataeval_dir)
fill_dir = os.path.dirname(os.path.abspath(__file__))
par_dir = os.path.join(fill_dir, 'src', 'aebs', 'par')
vidcalibs_path = os.path.join(par_dir, 'vidcalibs.db')

data_files = []
for project in user_projects:
  pth = project + '.fill' + '.pth'
  open(pth, 'w').write( os.path.abspath( os.path.join('src', project, 'fill') ) )
  data_files.append(pth)


def write_cfg(name, sections):
  cfg = RawConfigParser()
  cfg.optionxform = str

  for section, options in sections.iteritems():
    cfg.add_section(section)
    for option, value in options.iteritems():
      cfg.set(section, option, value)

  fp = open(name, 'wb')
  cfg.write(fp)
  fp.close()
  return

aebs_sections = {
  'Params': {
    'QuaNames': 'aebs.par.quanames.default',
    'Labels':   'aebs.par.labels.default',
    'Tags':     'aebs.par.tags.default',
  },
  'General': {
    'cSource': 'aebs.proc.cLrr3Source',
  },
  'GroupTypes': {
    'aebs.fill': 'aebs.par.grouptypes.GroupTypes',
  },
  'ShapeLegends': {
    'aebs.fill': 'aebs.par.shapelegends.ShapeLegends',
  },
  'ViewAngles': {
    'aebs.fill': 'aebs.par.viewangles.ViewAngles',
  },
  'Groups': {
    'aebs.fill': 'aebs.par.groups.Groups',
  },
  'Legends': {
    'aebs.fill': 'aebs.par.legends.Legends',
  },
  'VidCalibs': {
    'aebs.fill': vidcalibs_path
  },
}

ad_sections =  {
    'GroupTypes': {
        'ad.fill': 'ad.par.grouptypes.GroupTypes',
    },
    'Legends': {
        'ad.fill': 'ad.par.legends.Legends',
    },
    'Groups': {
        'ad.fill': 'ad.par.groups.Groups',
    }
}

ta_sections =  {
    'GroupTypes': {
        'ta.fill': 'ta.par.grouptypes.GroupTypes',
    },
    'Legends': {
        'ta.fill': 'ta.par.legends.Legends',
    },
    'Groups': {
        'ta.fill': 'ta.par.groups.Groups',
    }
}

# merge sections
user_project_sections = (aebs_sections, ad_sections, ta_sections)
sections = {}
for project_sections in user_project_sections:
  if not sections:
      sections = project_sections.copy()
  else:
      for key, val in project_sections.iteritems():
          sections[key].update(val)

config = '%s.params.cfg' %name
write_cfg(config, sections)

data_files.append(config)

setup(name=name,
      version='5.16.0',
      description='aebs',
      long_description='DAS-specific measurement processing library',
      maintainer='Rozsa, Tamas',
      maintainer_email='tamas.rozsa@knorr-bremse.com',
      url='http://leonidas/redmine/projects/dataeval',
      platforms=['MS Windows'],
      packages=find_packages('src'),
      package_dir={'': 'src'},
      requires=['scipy(>=0.11.0)',
                'numpy(>=1.8.2)',
                'h5py(>=2.1.0)',
                'dataio(>=2.11.0)',
                'utils(>=0.6.0)',
                'fusion(>=0.1.8)',
                'kbtools_user(>=0.1.0)',
                'dataeval(>=8.9.0)'],
                # silkbaebs
                # sil
                # pandas
                # seaborn
      provides=['aebs', 'aebs.abc', 'aebs.dbc', 'aebs.fill', 'aebs.par', 'aebs.proc', 'aebs.sdf'],
      data_files=[(dataeval_dir, data_files)],
      license=open('LICENSE').read())

for name in data_files:
  os.remove(name)

