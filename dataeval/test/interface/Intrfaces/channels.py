from datavis import pyglet_workaround  # necessary as early as possible (#164)

import os
import time
import glob
import shutil
import unittest

from PySide import QtGui, QtCore

import interface
from interface.Interfaces import iInterface, iView
from interface.modules import Modules
from interface.manager import AnalyzeManager
from measparser.BackupParser import BackupParser
from measparser.SignalSource import cSignalSource
from datavis.Synchronizer import cSynchronizer
from datavis.BatchNavigator import cBatchNavigator
from config.modules import Modules as ModuleScan
from config.Config import cScan, Config
from config.helper import writeConfig
from measproc.batchsqlite import Batch
from measproc.mapmanager import MapManager
from datavis.GroupParam import cGroupParam
from config.parameter import GroupParams

class View(iView):
  channels = 'main', 'can1'
  pass

db = os.path.abspath('batch.xml')
repdir = os.path.abspath('reports')
measpath = os.path.abspath('replace')
replmeas = False

prj_name = 'main'
cfg_name = os.path.abspath('batchnav.cfg')
params_cfg_name = os.path.abspath('%s.params.cfg' %prj_name)
path = os.path.abspath(__file__)
dir, file = os.path.split(path)
module_dir = os.path.join(dir, 'modules')
modules_csv = os.path.abspath('modules.csv')
mapdb = os.path.abspath('map.db')
grouptypes = {'foo', 'bar', 'baz'}
fills = {}
groups = GroupParams({
  'fillGood@modules': {
    'group-good': cGroupParam({'foo'}, '1', False, False),
  },
  'fillBad@modules': {
    'group-bad': cGroupParam({'bar', 'baz'}, '2', False, False),
  },
})
labels = {}
tags = {}
quanames = {}
results = ()
quanames = {}
header = ['measurement', 'title', 'type', 'intervals', 'query']
sortby = 'measurement'
query = ''
interval_header = [(('start',),
                    'SELECT start_time FROM entryintervals WHERE id = ?')]
interval_sortbys = [('start', True)]
enable_update = False
vidcalibs_path =  os.path.join(os.getcwd(), "test", "vidcalibs.db")#"C:\\KBData\\Sandbox\\util_das\\dataeval\\test\\vidcalibs.db"#

def setUpModule():
  global measurement
  meas_name = 'foo.mdf'
  dir_name = os.path.join('backup', meas_name)
  version = BackupParser.getVersion()
  measurement = BackupParser(dir_name, meas_name, version, version, '')
  measurement.save()
  os.makedirs(module_dir)
  init_file_path = os.path.join(module_dir, '__init__.py')
  file = open(init_file_path, 'w')
  file.close()

  writeConfig(params_cfg_name, {
    'Params': {
      'QuaNames': '__main__.quanames',
      'Labels': '__main__.labels',
      'Tags': '__main__.tags',
    },
    'General': {
      'cSource': 'measparser.SignalSource.cSignalSource',
    },
    'Fills': {
      prj_name: '__main__.fills',
    },
    'GroupTypes': {
        'modules': '__main__.grouptypes',
    },
    'Groups': {
      'modules': '__main__.groups',
    },
  })

  dirs = {'modules': module_dir}
  modules = ModuleScan()
  # dummy module to setup Measurement section in the config
  modules.add('dummy', '', 'iView', 'View', 'init', '', 'modules',
              *View.channels)
  config = cScan(modules, dirs, params_cfg_name, 'modules')
  config.set('Measurement', 'main', 'foo.mdf')
  config.set('Measurement', 'can1', 'foo.mdf')
  config.set('Measurement', 'compare', 'foo.mdf')
  config.save(cfg_name)
  modules.write(modules_csv)
  return

def tearDownModule():
  for name in os.path.dirname(measurement.NpyDir), repdir, module_dir:
    shutil.rmtree(name)

  rm_names = [cfg_name, params_cfg_name, modules_csv]
  dirname, basename = os.path.split(db)
  name, ext = os.path.splitext(basename)
  name = os.path.join(dirname, name+'*'+ext)
  rm_names.extend( glob.glob(name) )
  for name in rm_names:
    os.remove(name)
  return


class TestClass(unittest.TestCase):
  def test_source_aliases(self):
    self.assertTupleEqual(View.channels, ('main', 'can1'))
    return
  pass

class TestInstanceClose(unittest.TestCase):
  def setUp(self):
    channel = 'can1'
    manager = AnalyzeManager()
    manager.set_vidcalibs(vidcalibs_path)
    manager.set_measurement(measurement.NpyDir, channel=channel)
    manager.set_backup(measurement.NpyDir)
    manager.set_batch_params(db, repdir, labels, tags, results, quanames,
                             enable_update)
    modules = ModuleScan()
    modules.read(modules_csv)
    manager.set_int_table_params(interval_header, interval_sortbys)
    manager.set_batchnav_params(Config(cfg_name, modules), header, sortby, query,
                                interval_header, interval_sortbys)
    self.module  = View(manager, 'modules')
    self.module.get_source(channel)
    self.module.get_sync()
    self.module.get_modules()
    self.module.get_batchnav()

    self.module._manager.set_mapdb(mapdb)
    self.module._manager.get_mapman()

    manager.close()
    return

  def test_close(self):
    self.assertDictEqual(self.module._manager._sources, {})
    self.assertIsInstance(self.module._manager._modules, Modules)
    self.assertIsNone(self.module._manager._batch)
    self.assertIsNone(self.module._manager._batchnav)
    self.assertIsNone(self.module._manager._sync)
    self.assertIsNone(self.module._manager._mapdb)
    self.assertIsNone(self.module._manager._mapman)
    return
  pass

class TestInstance(unittest.TestCase):
  def setUp(self):
    self.manager = AnalyzeManager()
    self.manager.set_vidcalibs(vidcalibs_path)
    return

  def tearDown(self):
    self.manager.close()
    return

  def test_set_measurement(self):
    channel = 'main'
    self.manager.set_measurement(measurement.NpyDir, channel=channel)
    self.assertEqual(self.manager._measurements[channel], measurement.NpyDir)
    return

  def test_set_backup(self):
    self.manager.set_backup(measurement.NpyDir)
    self.assertEqual(self.manager._backup, measurement.NpyDir)
    return

  def test_set_batch_params(self):
    self.manager.set_batch_params(db, repdir, labels, tags, results,
                                  quanames, enable_update)
    self.assertEqual(self.manager._batch_params.db_name, db)
    self.assertEqual(self.manager._batch_params.dir_name, repdir)
    self.assertDictEqual(self.manager._batch_params.labels, labels)
    self.assertDictEqual(self.manager._batch_params.tags, tags)
    self.assertTupleEqual(self.manager._batch_params.results, results)
    return

  def test_set_batchnav_params(self):
    self.manager.set_batch_params(db, repdir, labels, tags, results, quanames,
                                  enable_update)
    modules = ModuleScan()
    modules.read(modules_csv)
    config = Config(cfg_name, modules)
    self.manager.set_int_table_params(interval_header, interval_sortbys)
    self.manager.set_batchnav_params(config, header, sortby, query,
                                     interval_header, interval_sortbys)
    self.assertEqual(self.manager._batchnav_params.Config, config)
    self.assertListEqual(self.manager._batchnav_params.Header, header)
    self.assertEqual(self.manager._batchnav_params.SortBy, sortby)
    self.assertEqual(self.manager._batchnav_params.Query, query)

  def test_set_mapdb(self):
    self.manager.set_mapdb(mapdb)
    self.assertEqual(self.manager._mapdb, mapdb)
    return
  pass


class SetUpInstance:
  channel = 'can1'
  def setUp(self):
    modules = ModuleScan()
    modules.read(modules_csv)
    manager = AnalyzeManager()
    manager.set_vidcalibs(vidcalibs_path)
    manager.set_measurement(measurement.NpyDir, channel=self.channel)
    manager.set_backup(measurement.NpyDir)
    manager.set_batch_params(db, repdir, labels, tags, results, quanames,
                             enable_update)
    manager.set_int_table_params(interval_header, interval_sortbys)
    manager.set_batchnav_params(Config(cfg_name, modules), header, sortby,
                                query, interval_header, interval_sortbys)
    manager.run_batchnav = True
    self.module  = View(manager, 'modules')
    self.module._manager.set_mapdb(mapdb)
    return

  def tearDown(self):
    self.module._manager.close()
    return

class TestChanneledInstance(SetUpInstance, unittest.TestCase):
  channel = 'can1'
  def test_get_source(self):
    source = self.module.get_source(self.channel)
    self.assertIsInstance(source, cSignalSource)
    return
  pass

class TestDefaultChanneledInstance(SetUpInstance, unittest.TestCase):
  channel = 'main'
  def test_get_source(self):
    source = self.module.get_source()
    self.assertIsInstance(source, cSignalSource)
    return

  def test_get_sync(self):
    sync = self.module.get_sync()
    self.assertIsInstance(sync, cSynchronizer)
    return

  def test_get_modules(self):
    modules = self.module.get_modules()
    self.assertIsInstance(modules, Modules)
    return

  def test_get_batch(self):
    batch = self.module.get_batch()
    self.assertIsInstance(batch, Batch)
    return

  def test_get_batchnav(self):
    batchnav = self.module.get_batchnav()
    self.assertIsInstance(batchnav, cBatchNavigator)
    return

  def test_get_mapman(self):
    mapman = self.module.get_mapman()
    self.assertIsInstance(mapman, MapManager)
  pass

class TestInterfaceLoad(SetUpInstance, unittest.TestCase):
  channel = 'main'
  def test_interface(self):
    self.assertNotIsInstance(interface.Source, cSignalSource)
    self.assertNotIsInstance(interface.Sync, cSynchronizer)
    self.assertNotIsInstance(interface.Objects, Modules)
    self.assertNotIsInstance(interface.Batch, Batch)
    self.assertNotIsInstance(interface.BatchNav, cBatchNavigator)

    self.module._manager.load_main()

    self.assertIsInstance(interface.Source, cSignalSource)
    self.assertIsInstance(interface.Sync, cSynchronizer)
    self.assertIsInstance(interface.Objects, Modules)
    self.assertIsInstance(interface.Batch, Batch)
    self.assertIsInstance(interface.BatchNav, cBatchNavigator)
    return

if __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()
