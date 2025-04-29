from datavis import pyglet_workaround  # necessary as early as possible (#164)

import os
import sys

from text.templates import viewTemplate, compareTemplate
from interface.scan import Module, TestCase

def setUpModule():
  sys.path.append(os.path.dirname(viewTemplate.__file__))
  sys.path.append(os.path.dirname(__file__))
  return

class TestScanMethodModule(TestCase):
  prj = 'prj'
  def setUp(self):
    self.param_type = 'method'
    self.name = 'viewTemplate'
    self.interface = 'iView'
    self.class_name = 'View'
    self.parameters = {'def_param': 'interface.Parameter.iParameter;'}
    self.channels = 'main',

    name = viewTemplate.__file__.replace('.pyc', '.py')
    self.module = Module.from_file(name, '')
    return

  def test(self):
    self.assertModuleEqual(self.module, self)
    return

class TestScanMethodModuleWithoutParam(TestScanMethodModule):
  def setUp(self):
    self.param_type = 'method'
    self.name = 'analyzeMethodWithoutParam'
    self.interface = 'iAnalyze'
    self.class_name = 'Analyze'
    self.parameters = {}
    self.channels = 'main',

    name = os.path.join(os.path.dirname(__file__), self.prj,
                        'analyzeMethodWithoutParam.py')
    self.module = Module.from_file(name, self.prj)
    return

class TestScanMethodModuleMultiChannel(TestScanMethodModule):
  def setUp(self):
    self.param_type = 'method'
    self.name = 'compareTemplate'
    self.interface = 'iCompare'
    self.class_name = 'cCompare'
    self.parameters = {'Parameter': 'interface.Parameter.iParameter;'}
    self.channels = 'main', 'compare'

    name = compareTemplate.__file__.replace('.pyc', '.py')
    self.module = Module.from_file(name, '')
    return

class TestScanInitModule(TestScanMethodModule):
  def setUp(self):
    self.param_type = 'init'
    self.name = 'viewInit'
    self.interface = 'iView'
    self.class_name = 'View'
    self.parameters = {'egg': 'spam=56', 'eggegg': 'spam=42'}
    self.channels = 'main',

    name = os.path.join(os.path.dirname(__file__), self.prj, 'viewInit.py')
    self.module = Module.from_file(name, self.prj)
    return

class TestScanInitModuleWithoutParam(TestScanMethodModule):
  def setUp(self):
    self.param_type = 'init'
    self.name = 'viewInitWithoutParam'
    self.interface = 'iView'
    self.class_name = 'View'
    self.parameters = {}
    self.channels = 'main',

    name = os.path.join(os.path.dirname(__file__), self.prj,
                                        'viewInitWithoutParam.py')
    self.module = Module.from_file(name, self.prj)
    return

class TestScanCallModule(TestScanMethodModule):
  def setUp(self):
    self.param_type = 'method'
    self.name = 'searchCall'
    self.interface = 'iSearch'
    self.class_name = 'Search'
    self.parameters = {'spam': 'Parameter;foo=9', 'egg': 'Parameter;foo=0'}
    self.channels = 'main',

    name = os.path.join(os.path.dirname(__file__), self.prj,
                       'searchCall.py')
    self.module = Module.from_file(name, self.prj)
    return

class TestScanCallModuleWithoutParam(TestScanMethodModule):
  def setUp(self):
    self.param_type = 'method'
    self.name = 'searchCallWithoutParam'
    self.interface = 'iSearch'
    self.class_name = 'Search'
    self.parameters = {}
    self.channels = 'main',

    name = os.path.join(os.path.dirname(__file__), self.prj,
                                        'searchCallWithoutParam.py')
    self.module = Module.from_file(name, self.prj)
    return

class TestParentDirectImport(TestScanInitModule):
  def setUp(self):
    self.param_type = 'init'
    self.name = 'viewParentDirectImport'
    self.interface = 'iView'
    self.class_name = 'MyView'
    self.parameters = {'egg': 'spam=23', 'eggegg': 'spam=32'}
    self.channels = 'main',

    name = os.path.join(os.path.dirname(__file__), self.prj,
                                        'viewParentDirectImport.py')
    self.module = Module.from_file(name, self.prj)
    return

if __name__ == '__main__':
  from unittest import main

  main()

