#!/usr/bin/env python 

import os
import sys
from ConfigParser import RawConfigParser
from distutils.core import setup
from distutils.sysconfig import get_python_lib

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

option = '--dataeval-name'
if option in sys.argv:
  i = sys.argv.index(option)
  sys.argv.pop(i)
  dataeval_name = sys.argv.pop(i)
else:
  if 'install_data' in sys.argv:
    print >> sys.stderr, \
      "missing mandatory argument for install_data: `%s DATAEVAL_NAME`" % option
    exit(-1)
  dataeval_name = 'dataeval'

env_pth = 'dataeval-env.pth'
env = 'import os; os.environ["DATAEVAL_NAME"] = "%s"' %dataeval_name
open(env_pth, 'w').write(env)

prj_name = 'dataeval'
params_cfg_name = '%s.params.cfg' %prj_name

simple_configs = {
  params_cfg_name: {
    'DocTemplates': {
      '%s.simple' %prj_name: 'datalab.reportlab.doctemplate.SimpleDocTemplate',
      '%s.simpletxt' %prj_name: 'datalab.textilelab.doctemplate.SimpleDocTemplate',
    },
  },
}

configs = {
  params_cfg_name: {
    'Params': {
      'QuaNames': 'config.parameter.quanames',
      'Labels':   'config.parameter.labels',
      'Tags':     'config.parameter.tags',
    },
    'General': {
      'cSource': 'measparser.SignalSource.cSignalSource',
      'MainPth': prj_name,
    },
    'GroupTypes': {
      prj_name: 'config.parameter.grouptypes',
    },
  },
  '%s.filtparams.cfg' %prj_name: {
    'ShapeLegends': {
      prj_name: 'config.parameter.shapelegends',
    },
    'ViewAngles': {
      prj_name: 'config.parameter.viewangles',
    },
    'Groups': {
      prj_name: 'config.parameter.groups',
    },
    'Legends': {
      prj_name: 'config.parameter.legends',
    }
  },
}

# copy simple config into configs
for name, config in simple_configs.iteritems():
  for section, options in config.iteritems():
    configs[name][section] = options

option = '--alone'
if option in sys.argv:
  sys.argv.remove(option)
else:
  configs = simple_configs
for name, sections in configs.iteritems():
  write_cfg(name, sections)


data_files = [env_pth]
data_files.extend(configs)

dataeval_dir = os.path.expanduser( os.path.join('~', '.'+dataeval_name) )

packages = ['config', 'datavis', 'dmw', 'interface', 'measproc', 'text',
            'datalab', 'primitives']

setup(name='dataeval',
      version='9.0.2',
      description='Measurement evaluation toolchain',
      long_description='Measurement evaluation toolchain',
      maintainer='Rozsa, Tamas',
      maintainer_email='tamas.rozsa@knorr-bremse.com',
      url='http://leonidas/redmine/projects/dataevalcore',
      platforms=['MS Windows'],
      packages=packages,
      package_dir={'': 'src'},
      package_data={
        'measproc': ['batchsqlite/init.sql',
                     'batchsqlite/merge.sql'],
        'datalab': ['pics/Knorr_logo.png']
      },
      scripts=[
        'scripts/analyze.py',
        'scripts/atomsk.py',
        'scripts/compare.py',
        'scripts/compare_mdf.py',
        'scripts/dump_batch_db.py',
        'scripts/generate_map.py',
        'scripts/group_signals.py',
        'scripts/idataevalrc.py',
        'scripts/manage_batch.py',
        'scripts/mass.py',
        'scripts/measview.py',
        'scripts/merge_batch.py',
        'scripts/merge_batch_db.py',
        'scripts/mort.py',
        'scripts/omid.py',
        'scripts/pack_batch.py',
        'scripts/scan.py',
        'scripts/scene_vis.py',
        'scripts/search.py',
        'scripts/stelvio.py',
        'scripts/update_backup.py',
        'scripts/update_batch.py',
        'scripts/view.py',
      ],
      requires=[
        'numpy(>=1.6.2)',
        'matplotlib(>=1.2.1)',
        'pyglet(>=1.1.4)',
        'PyOpenGL(==3.0.1)',
        'PIL(>=1.1.7)',
        'dataio(>=2.11.0)',
        'PySide(>=1.1.2)',
        'utils(>=0.1.0)',
        'xlrd(>=0.7.1)',
        'reportlab(>=2.5)',
        'sqlalchemy(>=0.9.0)',
        # sphinx
      ],
      provides=packages,
      data_files=[(get_python_lib(), [env_pth]),
                  (dataeval_dir, configs.keys())],
      license=open('LICENSE').read())

for name in data_files:
  os.remove(name)
