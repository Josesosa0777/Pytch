import os
import unittest
import argparse

from config.helper import writeConfig
from config.Config import Config, cScan
from config.modules import Modules
from interface.manager import Manager

labels = {
  'foo': (False, ['bar', 'baz']),
}
tags = {
  'spam': ['egg', 'eggegg'],
}
quanames = {
  'tarack': ['sugar', 'hanyas'],
}

class Test(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.name = 'fura.cfg'
    cls.params_cfg_name = 'meg_furabb.cfg'

    writeConfig(cls.params_cfg_name, {
      'General': {
        'cSource': 'measparser.SignalSource.cSignalSource',
      },
      'Params': {
        'QuaNames': '__main__.quanames',
        'Labels': '__main__.labels',
        'Tags': '__main__.tags',
      },
    })
    modules = Modules()
    
    config = cScan(modules, {'foo': 'bar'}, cls.params_cfg_name, 'foo')
    config.save(cls.name)

    cls.config = Config(cls.name, modules)
    return
  
  @classmethod
  def tearDownClass(cls):
    for name in cls.name, cls.params_cfg_name:
      os.remove(name)
    return

  def setUp(self):
    self.parser = Config.addArguments( argparse.ArgumentParser() )
    self.manager = Manager()
    return

  def test_missing_measurement(self):
    args = self.parser.parse_args('-m never_have_never_will.mdf'.split())
    self.config.procArgs(args)
    self.config.load(self.manager, 'iView')
    self.assertDictEqual(self.manager._measurements, {})
    return

  def test_clear_measurement(self):
    for meas in os.path.abspath('never_have_never_will.mdf'), '':
      args = self.parser.parse_args(['-m', meas])
      self.config.procArgs(args)
      self.assertEqual(self.config.get('Measurement', 'main'), meas)
    return

  def test_clear_batch(self):
    args = self.parser.parse_args(['-b', ''])
    self.config.procArgs(args)
    self.assertEqual(self.config.get('General', 'BatchFile'), '')

    args = self.parser.parse_args(['--repdir', ''])
    self.config.procArgs(args)
    self.assertEqual(self.config.get('General', 'RepDir'), '')
    return

  def test_clear_backup(self):
    args = self.parser.parse_args(['-u', ''])
    self.config.procArgs(args)
    self.assertEqual(self.config.get('General', 'Backup'), '')
    return

  def test_missing_mapdb(self):
    args = self.parser.parse_args('--mapdb never_have_never_will.db'.split())
    self.config.procArgs(args)
    self.config.load(self.manager, 'iView')
    self.assertIsNone(self.manager._mapdb)
    return

  def test_clear_mapdb(self):
    args = self.parser.parse_args(['--mapdb', ''])
    self.config.procArgs(args)
    self.assertEqual(self.config.get('General', 'MapDb'), '')
    return

if __name__ == '__main__':
  unittest.main()

