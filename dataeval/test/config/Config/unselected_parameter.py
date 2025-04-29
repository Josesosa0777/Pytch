from datavis import pyglet_workaround  # necessary as early as possible (#164)

import os
import unittest
from argparse import ArgumentParser

from config.Config import cScan, Config
from config.helper import writeConfig
from config.modules import Modules
from config.parameter import GroupParams
from text.templates import viewTemplate

fills = {}
groups = GroupParams()
labels = {}
tags = {}
quanames = {}

prj_name = 'main'
cfg_name = 'view.cfg'
params_cfg_name = '%s.params.cfg' %prj_name

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
  return

def tearDownModule():
  os.remove(params_cfg_name)
  return

class Test(unittest.TestCase):
  argv = [
    '-i', 'viewTemplate@text.templates',
    '-n', 'viewTemplate@text.templates',
  ]
  def setUp(self):
    modules = Modules()
    dir_names = {'text.templates': os.path.dirname(viewTemplate.__file__)}
    for prj_name_, dir_name in dir_names.iteritems():
      msgs = modules.scan(prj_name_, dir_name)

    config = cScan(modules, dir_names, params_cfg_name, prj_name)
    config.save(cfg_name)

    parser = ArgumentParser()
    args = Config.addArguments( ArgumentParser() ).parse_args(self.argv)
    self.config = Config(cfg_name, modules)
    self.config.init(args)
    self.manager = self.config.createManager('iView')
    return

  def tearDown(self):
    os.remove(cfg_name)
    return

  def test_unselected_parameter_causes_no_modules(self):
    modules = self.config.getActiveModules('iView')
    self.assertListEqual(modules, [])
    return

  def test_getMissingParameterSelection(self):
    missing = self.config.getMissingParameterSelection()
    self.assertListEqual(missing, ['viewTemplate@text.templates'])
    return

unittest.main()
