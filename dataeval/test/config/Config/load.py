from datavis import pyglet_workaround  # necessary as early as possible (#164)

import os
import glob
import sys
import shutil
import time
import argparse
import ConfigParser

import numpy
from reportlab.platypus import BaseDocTemplate

from datavis.Synchronizer import cNavigator
from text.templates import viewTemplate
from config.modules import Modules
from config.Config import cScan, Config
from config.helper import writeConfig
from config.parameter import GroupParams
from interface.Interfaces import iFill, iInterface
from interface.module import CreateModule
from interface.modules import TestCase, ModuleName
from measparser.BackupParser import BackupParser
from measparser.SignalSource import cSignalSource
from measproc.Batch import cBatch
from datavis.GroupParam import cGroupParam

grouptypes = {'foo', 'bar', 'baz'}

groups = GroupParams({
  'fillFoo-bar': {
    'group-bar': cGroupParam({'foo'}, '1', False, False),
  },
  'fillFoo-baz': {
    'group-baz': cGroupParam({'bar', 'baz'}, '2', False, False),
  },
})

view_angle_values = {
  'group-bar': 1,
  'group-baz': 2,
}
view_angles, missing = groups.build_groupname_params(view_angle_values)

legend_values = {
  'foo':  8,
  'bar':  9,
  'baz': 10,
}
legends, missing = groups.build_type_params(legend_values)

shape_values = {
  'foo': 11,
  'bar': 12,
  'baz': 14,
}
shape_legends, missing = groups.build_type_params(shape_values)

labels = {
  'foo': (False, ['bar', 'baz']),
}
tags = {
  'spam': ['egg', 'eggegg'],
}
quanames = {
  'tarack': ['sugar', 'hanyas'],
}

measurements = {}
backup = os.path.abspath('backup')
db = os.path.abspath('batch.xml')
repdir = os.path.abspath('reports')
mapdb = os.path.abspath('map.db')
start = time.strftime(cBatch.TIME_FORMAT)

open(mapdb, 'w')

_time = numpy.arange(0, 10, 20e-3)
_value = numpy.sin(_time)
version = BackupParser.getVersion()
for channel, name in [['main', 'foo.mdf'], ['can1', 'can1.blf']]:
  dir_name = os.path.join(backup, name)
  meas = BackupParser(dir_name, name, version, version, '')
  meas.addTime('foo', _time)
  meas.addSignal('spam', 'egg', 'foo', _value)
  meas.save()
  measurements[channel] = meas

def tearDownModule():
  for name in backup, :
    shutil.rmtree(name)
  dirname, basename = os.path.split(db)
  name, ext = os.path.splitext(basename)
  name = os.path.join(dirname, name+'*'+ext)
  for name in glob.glob(name):
    os.remove(name)
  os.remove(mapdb)
  return

fill_prj_name = 'fill'

null_param = 'interface.Parameter.iParameter;'

class BuildLoadNameSpace(TestCase):
  args = []
  def setUp(self):
    self.prj_name = 'main'
    self.name = 'view.cfg'
    self.params_cfg_name = '%s.params.cfg' %self.prj_name

    writeConfig(self.params_cfg_name, {
      'Params': {
        'QuaNames': '__main__.quanames',
        'Labels': '__main__.labels',
        'Tags': '__main__.tags',
      },
      'General': {
        'cSource': 'measparser.SignalSource.cSignalSource',
      },
      'GroupTypes': {
        self.prj_name: '__main__.grouptypes',
      },
      'DocTemplates': {
        '%s.simple' %self.prj_name: 'datalab.doctemplate.SimpleDocTemplate',
      },
      'Groups': {
        self.prj_name: '__main__.groups',
      },
      'ViewAngles': {
        self.prj_name: '__main__.view_angles',
      },
      'Legends': {
        self.prj_name: '__main__.legends',
      },
      'ShapeLegends': {
        self.prj_name: '__main__.shape_legends',
      },
    })

    modules = Modules()
    fill_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fill'))
    dir_names = {'text.templates': os.path.dirname(viewTemplate.__file__),
                 self.prj_name: fill_dir}
    for prj_name, dir_name in dir_names.iteritems():
      modules.scan(prj_name, dir_name)

    config = cScan(modules, dir_names, self.params_cfg_name, self.prj_name)
    config.save(self.name)

    self.config = Config(self.name, modules)
    parser = argparse.ArgumentParser()
    parser = Config.addArguments(parser)
    args = parser.parse_args(self.args)
    self.config.procArgs(args)
    self.manager = self.config.createManager('iView')
    return

  def tearDown(self):
    for name in self.name, self.params_cfg_name:
      os.remove(name)
    return

class ConfigLoad(BuildLoadNameSpace):
  def setUp(self):
    BuildLoadNameSpace.setUp(self)
    self.active_module = "viewTemplate@text.templates"
    self.config.u(backup)
    self.config.i(self.active_module)

    self.read_config = ConfigParser.RawConfigParser()
    self.read_config.read(self.name)
    return

  def option_test(self, section, option):
    self.assertTrue(self.read_config.has_option(section, option))
    self.assertNotEqual(self.read_config.get(section, option),
                        self.config.get(section, option))


    self.config.loadCfg(self.name, self.manager)
    self.read_config.read(self.name)
    self.assertEqual(self.read_config.get(section, option),
                        self.config.get(section, option))
    return

  def test_change_backup_reload(self):
    self.option_test('General', 'Backup')
    self.assertEqual(backup, self.config.get('General', 'Backup'))
    return

  def test_interface(self):
    self.option_test('iView', self.active_module)
    self.assertTrue(self.config.get('iView', self.active_module))
    return

class SectionReload(BuildLoadNameSpace):
  meas_path = r'd:\measurment\foo.mdf'
  args = [
          '--add', meas_path,
         ]
  def setUp(self):
    BuildLoadNameSpace.setUp(self)
    self.manager = self.config.createManager('iSearch')
    return

  def test_save_layout(self):
    self.assertEqual(self.config.get('General', 'Measurements'), '')
    self.config.loadCfg(self.name, self.manager)
    self.assertEqual(self.config.get('General', 'Measurements'), self.meas_path)
    return

if __name__ == '__main__':
  from unittest import main
  from PySide import QtGui
  app = QtGui.QApplication([])
  main()
