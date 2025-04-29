from datavis import pyglet_workaround  # necessary as early as possible (#164)

import os
import sys
import unittest

import text.templates
from config.modules import Modules, MethodModule, TestCase

dirname = os.path.dirname(text.templates.__file__)
print dirname

prj_name = 'text.templates'
modules = {
  ('analyzeTemplate', 'def_param', prj_name):
    MethodModule('iAnalyze', 'Analyze', 'interface.Parameter.iParameter;',
                 prj_name, ('main',)),
  ('viewTemplate',    'def_param', prj_name):
    MethodModule('iView',    'View',    'interface.Parameter.iParameter;',
                 prj_name, ('main',)),
  ('compareTemplate', 'Parameter', prj_name):
    MethodModule('iCompare', 'cCompare', 'interface.Parameter.iParameter;',
                 prj_name, ('main', 'compare')),
}

def setUpModule():
  sys.path.append(dirname)
  return

class TestScan(TestCase):
  def setUp(self):
    self.modules = Modules()
    return

  def test_scan(self):
    self.modules.scan(prj_name, dirname)
    self.assertModulesEqual(self.modules, modules)
    return


class TestReadWrite(TestCase):
  def setUp(self):
    self.filename = 'spam'
    self.modules = Modules()
    self.modules.scan(prj_name, dirname)
    return

  def tearDown(self):
    os.remove(self.filename)
    return

  def test_read_back(self):
    self.modules.write(self.filename)
    _modules = Modules()
    _modules.read(self.filename)
    self.assertModulesEqual(self.modules, modules)
    return


if __name__ == '__main__':
  unittest.main()

