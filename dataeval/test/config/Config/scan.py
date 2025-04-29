from datavis import pyglet_workaround  # necessary as early as possible (#164)

import os
import sys
import argparse
from unittest import TestCase

from PySide import QtGui

from text.templates import viewTemplate
from config.modules import Modules
from config.helper import writeConfig
from config.Config import cScan, Config
from config.parameter import GroupParams
from datavis.GroupParam import cGroupParam
from datavis.Synchronizer import cNavigator
from interface.modules import ModuleName

grouptypes = {'foo', 'bar', 'baz'}

groups = GroupParams({})


prj_name = 'main'
params_cfg_name = '%s.params.cfg' %prj_name
null_param = 'interface.Parameter.iParameter;'

params =  {
  'Params': {
    'QuaNames': '__main__.quanames',
    'Labels': '__main__.labels',
    'Tags': '__main__.tags',
  },
  'General': {
    'cSource': 'measparser.SignalSource.cSignalSource',
  },
  'GroupTypes': {
        prj_name: '__main__.grouptypes',
  },
  'DocTemplates': {
    '%s.simple' %prj_name: 'datalab.doctemplate.SimpleDocTemplate',
  },
  'Groups': {
     prj_name: '__main__.groups',
  },
  'IntervalSortBys' : {
    '0.start' : 'False',
  },
  'IntervalHeader' : {
    '0.start' : ' SELECT start_time FROM entryintervals WHERE id = ?',
  },
}

def setUpModule():
  writeConfig(params_cfg_name, params)
  return

def tearDownModule():
  os.remove(params_cfg_name)
  return

class Build:
  def setUp(self):
    modules = Modules()
    dir_names = {'text.templates': os.path.dirname(viewTemplate.__file__)}
    for prj_name_, dir_name in dir_names.iteritems():
      modules.scan(prj_name_, dir_name)

    self.config = cScan(modules, dir_names, params_cfg_name, prj_name)

    modulename = ModuleName.create('viewTemplate', '', 'text.templates')
    self.Modules = {
      ('iView', modulename, 'def_param'),
    }
    return

class Test(Build, TestCase):
  def test_sections(self):
    self.assertTrue(self.config.has_section('__doc__'))
    self.assertTrue(self.config.has_section('iFill'))
    self.assertTrue(self.config.has_section('iAnalyze'))
    self.assertTrue(self.config.has_section('iCompare'))
    self.assertTrue(self.config.has_section('iSearch'))
    self.assertTrue(self.config.has_section('iView'))
    self.assertTrue(self.config.has_section('General'))
    self.assertTrue(self.config.has_section('Params'))
    self.assertTrue(self.config.has_section('GroupNames'))
    self.assertTrue(self.config.has_section('Groups'))
    self.assertTrue(self.config.has_section('ViewAngles'))
    self.assertTrue(self.config.has_section('Legends'))
    self.assertTrue(self.config.has_section('ShapeLegends'))
    self.assertTrue(self.config.has_section('DocTemplates'))
    self.assertTrue(self.config.has_section('IntervalHeader'))
    self.assertTrue(self.config.has_section('IntervalSortBys'))
    return

  def test_General(self):
    self.assertTrue(self.config.has_option('Measurement', 'main'))
    self.assertTrue(self.config.has_option('General', 'Backup'))
    self.assertTrue(self.config.has_option('General', 'Report'))
    self.assertTrue(self.config.has_option('General', 'BatchFile'))
    self.assertTrue(self.config.has_option('General', 'RepDir'))
    self.assertTrue(self.config.has_option('General', 'MeasPath'))
    self.assertTrue(self.config.has_option('General', 'MainPth'))
    self.assertEqual(self.config.get('General', 'MainPth'), 'main')
    self.assertTrue(self.config.has_option('General', 'MapDb'))
    self.assertTrue(self.config.has_option('General', 'cSource'))
    self.assertEqual(self.config.get('General', 'cSource'),
                     params['General']['cSource'])
    return

  def test_Modules(self):
    for Interface, Module, Param in self.Modules:
      self.assertTrue(self.config.has_option(Interface, Module))
      self.assertFalse(self.config.getboolean(Interface, Module))

      self.assertTrue(self.config.has_section(Module))
      self.assertTrue(self.config.has_option(Module, Param))
      self.assertTrue(self.config.getboolean(Module, Param))
    return

  def test_Groups(self):
    self.assertTrue(self.config.has_option('Groups', 'main'))
    self.assertEqual(self.config.get('Groups', 'main'),
                     params['Groups']['main'])
    return

  def test_removeInterfaceModule(self):
    self.config.removeModule('iView', 'viewTemplate')
    self.assertFalse(self.config.has_option('Modules', 'viewTemplate'))
    self.assertFalse(self.config.has_section('viewTemplate'))
    return

class BuildScanAgain(Build, TestCase):
  def setUp(self):
    Build.setUp(self)
    self.config.set('Path', 'foo', r'foo/bar')
    Build.setUp(self)
    return

  def test_path_overwritten_with_correct(self):
    self.assertFalse(self.config.has_option('Path', 'foo'))
    return

class BuildConfig(Build, TestCase):
  name = 'view.cfg'
  args = [
            '--interval-sortbys' , 'foo', 'ASC',
            '--forced-save'
         ]
  def setUp(self):
    Build.setUp(self)

    self.config.save(self.name)

    modules = Modules()
    self.config2 = Config(self.name, modules)
    parser = argparse.ArgumentParser()
    parser = Config.addArguments(parser)
    args = parser.parse_args(self.args)
    self.config2.procArgs(args)
    self.manager = self.config2.createManager('iAnalyze')
    self.init()
    self.config2.loadCfg(self.name, self.manager)
    self.config.save(self.name)
    return

  def tearDown(self):
    os.remove(self.name)
    return

  def init(self):
    return

class TestSaveLayout(BuildConfig):
  def init(self):
    sync = self.manager.get_sync()
    nav = cNavigator(title='foo')
    sync.addClient(nav)
    sync.start()
    return

  def test_layout(self):
    is_layout_section = False
    modules = Modules()
    temp_config = Config(self.name, modules)
    for section in temp_config.sections():
      if section.endswith('.layout'): is_layout_section = True
    self.assertTrue(is_layout_section)
    return


if __name__ == '__main__':
  from unittest import main
  app = QtGui.QApplication([])
  main()
