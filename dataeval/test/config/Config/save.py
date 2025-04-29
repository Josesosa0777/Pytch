import os
import shutil
from unittest import TestCase, main
from argparse import ArgumentParser

from config.modules import Modules
from config.helper import writeConfig
from config.Config import cScan, Config, iConfig
from text.templates import viewTemplate

fills = {}
groups = {}
labels = {}
tags = {}
quanames = {}

prj_name = 'main'
params_cfg_name = '%s.params.cfg' %prj_name
cfg_name = 'dataeval.cfg'

params =  {
  'Params': {
    'QuaNames': '__main__.quanames',
    'Labels': '__main__.labels',
    'Tags': '__main__.tags',
  },
  'General': {
    'cSource': 'measparser.SignalSource.cSignalSource',
  },
  'Groups': {
    prj_name: '__main__.groups',
  },
}

def setUpModule():
  writeConfig(params_cfg_name, params)

  modules = Modules()
  dir_names = {prj_name: os.path.dirname(viewTemplate.__file__)}
  for prj_name_, dir_name in dir_names.iteritems():
    modules.scan(prj_name_, dir_name)

  cfg = cScan(modules, dir_names, params_cfg_name, prj_name)
  cfg.save(cfg_name)
  return

def tearDownModule():
  for name in params_cfg_name, cfg_name:
    os.remove(name)
  return

class TestHash(TestCase):
  def setUp(self):
    modules = Modules()
    self.cfg = Config(cfg_name, modules)
    return

  def test_hash(self):
    self.assertEqual(self.cfg._Hash, self.cfg.hash())
    self.cfg.set('Params', 'QuaNames', 'egg')
    self.assertNotEqual(self.cfg._Hash, self.cfg.hash())
    return

class TestSave(TestCase):
  def setUp(self):
    self.cfg_name = 'other.cfg'
    shutil.copyfile(cfg_name, self.cfg_name)

    modules = Modules()
    self.cfg = Config(self.cfg_name, modules)
    return


  def tearDown(self):
    os.remove(self.cfg_name)
    return

  def test_unchanged_save(self):
    self.cfg.set('Params', 'QuaNames', 'egg')
    self.cfg.save('iView')
    
    cfg = iConfig()
    cfg.read(self.cfg_name)
    self.assertEqual(self.cfg.hash(), cfg.hash())
    return


  def test_save_block(self):
    cfg = iConfig()
    cfg.read(self.cfg_name)
    cfg.set('General', 'cSource', 'Egg')
    cfg.write(open(self.cfg_name, 'wb'))

    self.cfg.save('iView')

    dfg = iConfig()
    dfg.read(self.cfg_name)

    self.assertEqual(dfg.hash(), cfg.hash()) 
    self.assertNotEqual(dfg.hash(), self.cfg.hash()) 
    return

  def test_forced_save(self):
    cfg = iConfig()
    cfg.read(self.cfg_name)
    cfg.set('General', 'cSource', 'Egg')
    cfg.write(open(self.cfg_name, 'wb'))

    self.cfg.ForcedSave = True
    self.cfg.save('iView')

    dfg = iConfig()
    dfg.read(self.cfg_name)

    self.assertNotEqual(dfg.hash(), cfg.hash()) 
    self.assertEqual(dfg.hash(), self.cfg.hash()) 
    return

class TestForcedSaveCli(TestCase):
  def setUp(self):
    self.cfg_name = 'other.cfg'
    shutil.copyfile(cfg_name, self.cfg_name)

    modules = Modules()
    self.cfg = Config(self.cfg_name, modules)

    args = Config.addArguments( ArgumentParser() ).parse_args(['--forced-save'])
    self.cfg.init(args)
    return

  def test_forced_save(self):
    cfg = iConfig()
    cfg.read(self.cfg_name)
    cfg.set('General', 'cSource', 'Egg')
    cfg.write(open(self.cfg_name, 'wb'))

    self.cfg.save('iView')

    dfg = iConfig()
    dfg.read(self.cfg_name)

    self.assertNotEqual(dfg.hash(), cfg.hash()) 
    self.assertEqual(dfg.hash(), self.cfg.hash()) 
    return

if __name__ == '__main__':
  main()
