from datavis import pyglet_workaround  # necessary as early as possible (#164)

import os
import shutil
import unittest

import numpy
from PySide import QtGui

from config.modules import Modules, InitModule, TestCase
from config.Config import cScan, Config
from config.helper import writeConfig
from measparser.BackupParser import BackupParser

prj_name = 'fill'
cfg_name = 'foo.cfg'
params_cfg = '%s.params.cfg' %prj_name
meas_name = 'foo.mdf'
backup = os.path.abspath('backup')
vidcalibs_path = os.path.join(os.getcwd(), "test", "vidcalibs.db") #"C:\\KBData\\Sandbox\\util_das\\dataeval\\test\\vidcalibs.db"# 

labels = {}
tags = {}
quanames = {}

def setUpModule():
  global dir_name
  time = numpy.arange(0, 10, 20e-3)
  value = numpy.sin(time)

  dir_name = os.path.join(backup, meas_name)
  version = BackupParser.getVersion()
  meas = BackupParser(dir_name, meas_name, version, version, '')
  meas.addTime('foo', time)
  meas.addSignal('spam', 'egg', 'foo', value)
  meas.save()
  return

def tearDownModule():
  for name in cfg_name, params_cfg:
    os.remove(name)
  shutil.rmtree(backup)
  return

class SetUp(TestCase):
  def setUp(self):
    modules = Modules()
    scan_dirs = {prj_name: os.path.join(os.path.dirname(__file__), 'fill')}
    for prj_name_, dir_name in scan_dirs.iteritems():
      modules.scan(prj_name, dir_name)
    writeConfig(params_cfg, {
      'Params': {
        'QuaNames': '__main__.quanames',
        'Labels': '__main__.labels',
        'Tags': '__main__.tags',
      },
      'General': {
        'cSource': 'measparser.SignalSource.cSignalSource',
      },
      'DocTemplates': {
        '%s.simple' %prj_name: 'datalab.doctemplate.SimpleDocTemplate',
      },
    })
    config = cScan(modules, scan_dirs, params_cfg, 'main')
    config.save(cfg_name)
    self.config = Config(cfg_name, modules)
    self.modules = {
      ('fillFoo', 'bar', prj_name):
        InitModule('iFill', 'Fill', 'spam=42', prj_name, ('main', 'can1')),
      ('fillFoo', 'baz', prj_name):
        InitModule('iFill', 'Fill', 'spam=24', prj_name, ('main', 'can1')),
    }
    return

class Test(SetUp):
  def test_modules_initial_params(self):
    self.assertModulesEqual(self.config.Modules, self.modules)
    return

  def test_cloneModuleParam(self):
    param_name, param_list = self.config.cloneModuleParam('fillFoo', 'bar',
                                                           prj_name)
    self.assertEqual(param_name, 'bar0')
    self.assertListEqual(param_list, [('spam', '42')])
    return

class SetUpParam(SetUp):
  def setUp(self):
    SetUp.setUp(self)
    self.config.param('fillFoo', 'bax', prj_name, 'spam=56')
    module = InitModule('iFill', 'Fill', 'spam=56', prj_name, ('main', 'can1'))
    self.modules[('fillFoo', 'bax', prj_name)] = module
    return

class TestParam(SetUpParam):
  def test_param_added_to_modules(self):
    self.assertModulesEqual(self.config.Modules, self.modules)
    return

class SetUpLoad(SetUpParam):
  def setUp(self):
    SetUpParam.setUp(self)
    self.config.m(dir_name)
    self.config.u('')
    self.manager = self.config.createManager('iView')
    self.manager.set_vidcalibs(vidcalibs_path)
    self.config.load(self.manager, 'iView')
    self.config.build(self.manager, 'iView')
    return


class TestLoad(SetUpLoad):
  def test_param_activated(self):
    modules = self.manager.get_modules()
    self.assertSetEqual(modules.get_passed(), {'fillFoo-bax@fill'})
    return

if __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()

