from datavis import pyglet_workaround  # necessary as early as possible (#164)

import os
import unittest

from config.helper import getConfigPath
from config.Config import cScan, Config
from config.helper import writeConfig
from config.modules import Modules
from interface.manager import Manager

fills = {}
groups = {}
labels = {}
tags = {}
quanames = {}
prj_name = 'multichannel'

class Test(unittest.TestCase):
  module_name = "viewMultiChannel.py"
  config_name = "foo.cfg"
  params_cfg = '%s.params.cfg' %prj_name

  @classmethod
  def setUpClass(cls):
    modules_name = getConfigPath('modules', '.csv')
    cls.modules = Modules()
    file_dir = os.path.abspath(os.path.dirname(__file__))
    prj_dir = os.path.join(file_dir, prj_name)
    dir_names = {prj_name : prj_dir}

    writeConfig(cls.params_cfg, {
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
      'Groups': {
        prj_name: '__main__.groups',
      },
    })

    for prj_name_, dir_name in dir_names.iteritems():
      cls.modules.scan(prj_name_, dir_name)
    config = cScan(cls.modules, dir_names, cls.params_cfg, prj_name)
    config.save(cls.config_name)
    return

  @classmethod
  def tearDownClass(cls):
    for name in cls.config_name, cls.params_cfg:
      os.remove(name)
    return

  def setUp(self):
    self.config = Config(self.config_name, self.modules)
    return

  def test_insert_module(self):
    interface = 'iView'
    dir_name = os.path.dirname(__file__)
    manager = Manager()
    manager.append_dataeval_path(os.path.join(dir_name, "temp"))
    self.config._loadNameSpace(manager)

    manager.append_dataeval_path(os.path.join(dir_name, "multichannel"))
    name = os.path.join(dir_name, "multichannel", self.module_name)
    module = self.config.scanInterfaceModule(name, prj_name)
    self.config.activateModule(module.interface, module.name, module.parameters,
                               module.prj, module.channels)
    self.assertTrue(self.config.has_option('Measurement', 'main'))
    self.assertTrue(self.config.has_option('Measurement', 'foo'))
    return

  def test_plain_config(self):
    self.assertTrue(self.config.has_option('Measurement', 'main'))
    self.assertTrue(self.config.has_option('Measurement', 'foo'))
    return

if __name__ == '__main__':
  unittest.main()
