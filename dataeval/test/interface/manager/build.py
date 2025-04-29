from datavis import pyglet_workaround  # necessary as early as possible (#164)

import os
import sys
import time
import shutil
import unittest

import interface
from interface.manager import Manager
from interface.Interfaces import iFill, iView
from config.parameter import GroupParams
from datavis.GroupParam import cGroupParam
from measproc.Batch import cBatch
from measparser.BackupParser import BackupParser
from interface.modules import ModuleName

sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

grouptypes = {'foo', 'bar', 'baz'}

groups = GroupParams({
  'fillGood@modules': {
    'group-good': cGroupParam({'foo'}, '1', False, False),
  },
  'fillBad@modules': {
    'group-bad': cGroupParam({'bar', 'baz'}, '2', False, False),
  },
})

labels = {
  'foo': (False, ['bar', 'baz']),
}
tags = {
  'spam': ['egg', 'eggegg'],
}
quanames = {
  'tarack': ['sugar', 'hanyas'],
}
results = 'passed',

prj_name = 'modules'

backup = os.path.abspath('backup')
meas_name = 'foo.mdf'
db_name = os.path.abspath('batch.db')
repdir = os.path.abspath('reports')
start = time.strftime(cBatch.TIME_FORMAT)
vidcalibs_path = os.path.join(os.getcwd(), "test", "vidcalibs.db") #"C:\\KBData\\Sandbox\\util_das\\dataeval\\test\\vidcalibs.db"# 

def setUpModule():
  version = BackupParser.getVersion()
  dir_name = os.path.join(backup, meas_name)
  meas = BackupParser(dir_name, meas_name, version, version, '')
  meas.save()
  return

def tearDownModule():
  for name in backup, repdir:
    if os.path.exists(name):
      shutil.rmtree(name)
  if os.path.exists(db_name):
    os.remove(db_name)
  return


class BuildNameSpace(unittest.TestCase):
  def setUp(self):
    self.manager = Manager()
    self.manager.set_vidcalibs(vidcalibs_path)
    modules = self.manager.get_modules()
    for module_name, param_name, class_name, param_type, param in [
        ['fillGood', '',         'Fill',     'init',     ''],
        ['fillBad',  '',         'Fill',     'init',     ''],
        ['viewEgg',  '',         'View',     'init',     ''],
      ]:
      modules.add(module_name, param_name, class_name, param_type, param,
                  prj_name)
    return

  def tearDown(self):
    self.manager.close()
    return

class TestSelectModules(BuildNameSpace):
  def test(self):
    modules = [ModuleName.create(module, '', prj_name)
              for module in 'fillGood', 'fillBad']
    actives = self.manager.select_modules(modules)
    active = ModuleName.create('fillGood', '', prj_name)
    self.assertSetEqual(actives, {active})
    name = actives.pop()
    modules = self.manager.get_modules()
    self.assertIn(name, modules._checks)
    self.assertEqual(modules._checks[name], 4)
    return
  pass

class TestBuildModules(BuildNameSpace):
  def setUp(self):
    BuildNameSpace.setUp(self)
    modules = [ModuleName.create(module, '', prj_name)
              for module in 'fillGood', 'fillBad']
    self.actives = self.manager.select_modules(modules)
    return

  def test(self):
    self.manager.build_modules(self.actives)
    modules = self.manager.get_modules()
    name = self.actives.pop()
    self.assertIn(name, modules._fills)
    self.assertEqual(modules._fills[name], 12)
    self.assertIn(name, modules._runs)
    return

class BuildTypes(BuildNameSpace):
  def setUp(self):
    BuildNameSpace.setUp(self)
    self.manager.grouptypes.add_types(prj_name, grouptypes)
    self.manager.set_groups(prj_name, groups)

    self.types = {}
    for type_name in grouptypes:
      type_number = self.manager.grouptypes.get_type(prj_name, type_name)
      self.types[type_name] = type_number
    return

class TestBuild(BuildTypes):
  def test(self):
    modules = [ModuleName.create(module, '', prj_name)
              for module in 'fillGood', 'fillBad']
    view_module = ModuleName.create('viewEgg', '', prj_name)
    good_fill_module = ModuleName.create('fillGood', '', prj_name)
    self.manager.build([view_module], modules, ['group-good'])

    modules = self.manager.get_modules()
    self.assertSetEqual(modules.get_passed_by_parent(iView), {view_module})
    self.assertSetEqual(modules.get_passed_by_parent(iFill), {good_fill_module})
    self.assertDictEqual(self.manager.groups, {
      'group-good': cGroupParam({self.types['foo']}, '1', True, False)
    })
    return

class TestInterface(BuildTypes):
  def setUp(self):
    BuildTypes.setUp(self)
    self.manager.set_backup(backup)
    self.manager.set_measurement( os.path.join(backup, meas_name) )
    self.manager.set_batch_params(db_name, repdir, labels, tags, results,
                                  quanames, False)
    return

  def test(self):
    self._test_interface_is_clear()
    modules = [ModuleName.create(module, '', prj_name)
              for module in 'fillGood', 'fillBad']
    view_module = [ModuleName.create('viewEgg', '', prj_name)]
    self.manager.build(view_module, modules, ['group-good'])
    self._test_interface_is_loaded()
    return

  def _test_interface_is_clear(self):
    self.assertIsNot(interface.Objects, self.manager.get_modules())
    self.assertIsNot(interface.Legends, self.manager.legends)
    self.assertIsNot(interface.ShapeLegends, self.manager.shape_legends)
    self.assertIsNot(interface.Groups, self.manager.groups)
    self.assertIsNot(interface.ViewAngles, self.manager.view_angles)
    self.assertIsNot(interface.Reports, self.manager.reports)
    self.assertIsNot(interface.Report2s, self.manager.report2s)
    self.assertIsNot(interface.Statistics, self.manager.statistics)
    return

  def _test_interface_is_loaded(self):
    self.assertIs(interface.Source, self.manager.get_source('main'))
    self.assertIs(interface.Batch, self.manager.get_batch())
    self.assertIs(interface.Sync, self.manager.get_sync())
    self.assertIs(interface.Objects, self.manager.get_modules())
    self.assertIs(interface.Legends, self.manager.legends)
    self.assertIs(interface.ShapeLegends, self.manager.shape_legends)
    self.assertIs(interface.Groups, self.manager.groups)
    self.assertIs(interface.ViewAngles, self.manager.view_angles)
    self.assertIs(interface.Reports, self.manager.reports)
    self.assertIs(interface.Report2s, self.manager.report2s)
    self.assertIs(interface.Statistics, self.manager.statistics)
    return

  def test_reload_interface(self):
    self._test_interface_is_clear()
    self.manager.reload_interface()
    self._test_interface_is_loaded()
    return

unittest.main()

