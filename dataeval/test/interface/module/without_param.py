from datavis import pyglet_workaround  # necessary as early as possible (#164)

import os

import unittest

from interface.module import CreateModule, ModuleWithoutParam, TestCase
from interface.manager import Manager

vidcalibs_path = os.path.join(os.getcwd(), "test", "vidcalibs.db") #"C:\\KBData\\Sandbox\\util_das\\dataeval\\test\\vidcalibs.db"# 

class TestCreateInitModule(TestCase):
  module_name = 'view_wo_param'
  class_name = 'View'
  param_type = 'init'
  param = ''
  prj_name = 'prj'

  def setUp(self):
    self.createmodule = CreateModule(self.module_name, self.class_name,
                                     self.param_type, self.param, self.prj_name)
    return

  def test_CreateModule(self):
    self.assertCreateModuleEqual(self.createmodule, self)
    return

class TestCreateInitModuleRun(TestCreateInitModule):
  def setUp(self):
    TestCreateInitModule.setUp(self)
    manager = Manager()
    manager.set_vidcalibs(vidcalibs_path)
    self.module = self.createmodule(manager)
    return

  def test_module_creation(self):
    self.assertIsInstance(self.module, ModuleWithoutParam)
    return

  def test_check(self):
    egg, eggegg = self.module.check()
    self.assertEqual(egg,    1)
    self.assertEqual(eggegg, 2)
    return

  def test_fill(self):
    egg, eggegg = self.module.check()
    spam = self.module.fill(egg, eggegg)
    self.assertEqual(spam, 6)
    return

  def test_run(self):
    egg, eggegg = self.module.check()
    spam = self.module.fill(egg, eggegg)
    self.module.run(spam)
    self.assertEqual(self.module.module.spam, 6)
    return

  def test_error(self):
    self.module.error()
    self.assertEqual(self.module.module.spam, 33)
    return

  def test_get_class_sign(self):
    self.assertEqual(self.module.get_class_sign(), 'prj.view_wo_param.View')
    return

  def test_get_param_sign(self):
    self.assertEqual(self.module.get_param_sign(), self.param)
    return

class TestCreateMethodModule(TestCreateInitModule):
  module_name = 'search_wo_param'
  class_name = 'Search'
  param_type = 'method'
  param = ''
  prj_name = 'prj'

class TestCreateMethodModuleRun(TestCreateMethodModule):
  def setUp(self):
    TestCreateMethodModule.setUp(self)
    manager = Manager()
    manager.set_vidcalibs(vidcalibs_path)
    self.module = self.createmodule(manager)
    return

  def test_module_creation(self):
    self.assertIsInstance(self.module, ModuleWithoutParam)
    return

  def test_check(self):
    egg = self.module.check()
    self.assertEqual(egg, 56)
    return

  def test_fill(self):
    egg = self.module.check()
    spam, spamspam = self.module.fill(egg)
    self.assertEqual(spam,     60)
    self.assertEqual(spamspam, 52)
    return

  def test_run(self):
    egg = self.module.check()
    spam, spamspam = self.module.fill(egg)
    self.module.run(spam, spamspam)
    self.assertEqual(self.module.module.egg, 8)
    return
    
  def test_error(self):
    self.module.error()
    self.assertEqual(self.module.module.egg, 11)
    return

  def test_get_class_sign(self):
    self.assertEqual(self.module.get_class_sign(), 'prj.search_wo_param.Search')
    return

  def test_get_param_sign(self):
    self.assertEqual(self.module.get_param_sign(), '')
    return

if __name__ == '__main__':
  unittest.main()

