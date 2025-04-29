import os

from datavis import pyglet_workaround  # necessary as early as possible (#164)

from interface.Interfaces import Interface, iFill, iView
from interface.modules import Modules, TestCase, ModuleName, Container
from interface.module import InitModule, MethodModule, ModuleWithoutParam,\
                             CreateModule
from interface.manager import Manager

prj_name = 'prj'
prj2_name = 'prj2'
vidcalibs_path = os.path.join(os.getcwd(), "test", "vidcalibs.db") #"C:\\KBData\\Sandbox\\util_das\\dataeval\\test\\vidcalibs.db"#
namespace = {
  'fill-bar@prj':
    CreateModule('fill', 'Fill', 'init', 'spam=42', prj_name),
  'fill-baz@prj':
    CreateModule('fill', 'Fill', 'init', 'spam=24', prj_name),
  'view@prj':
    CreateModule('view', 'View', 'init', '', prj_name),
  'view_w_param-egg@prj':
    CreateModule('view_w_param', 'cView', 'method', 'Parameter;egg=56', prj_name),
  'error-spam@prj':
    CreateModule('error', 'Error', 'init', 'foo=33', prj_name),
  'bunny-pyon@prj':
    CreateModule('bunny', 'Bunny', 'init', 'foo=66', prj_name),
  'tiger@prj':
    CreateModule('tiger', 'Tiger', 'init', 'foo=99', prj_name),
  'bear-takun@prj':
    CreateModule('bear', 'Bear', 'init', 'foo=132', prj_name),
  'tiger@prj2':
    CreateModule('tiger', 'Tiger', 'init', 'foo=99', prj2_name),
  'lion@prj2':
    CreateModule('lion', 'Lion', 'init', 'foo=132', prj2_name),
  'search_w_param-atomsk@prj':
    CreateModule('search_w_param', 'cSearch', 'method', 'Parameter;egg=23',
                 prj_name),
}

class BuildNameSpace(TestCase):
  def setUp(self):
    self.modules = Modules()
    for name, createmodule in namespace.iteritems():
      module_name, param_name, prj = ModuleName.split(name)
      self.modules.add(module_name, param_name, createmodule.class_name,
                       createmodule.param_type, createmodule.param,
                       createmodule.prj_name)
    self.manager = Manager()
    self.manager.set_vidcalibs(vidcalibs_path)
    return

class TestCreateNameSpace(BuildNameSpace):
  def test_create_namespace(self):
    self.assertNameSpaceEqual(self.modules, namespace)
    return

  def test_wake_lonely(self):
    name = 'view_w_param-egg@prj'
    self.modules.wake(name, self.manager)
    self.assertIsInstance(self.modules._modules[name], MethodModule)
    return

  def test_wake_depend(self):
    self.modules.wake('view@prj', self.manager)
    self.assertIsInstance(self.modules._modules['view@prj'], ModuleWithoutParam)
    self.assertIsInstance(self.modules._modules['fill-bar@prj'], InitModule)
    return

  def test_wake_optdep(self):
    self.modules.wake('bear-takun@prj', self.manager)
    self.assertIsInstance(self.modules._modules['bear-takun@prj'], InitModule)
    self.assertIsInstance(self.modules._modules['fill-bar@prj'], InitModule)
    return

class TestClone(BuildNameSpace):
  def test_clone(self):
    modules = self.modules.clone()
    self.assertDictEqual(modules._namespace, namespace)
    return

class BuildCheck(BuildNameSpace):
  def setUp(self):
    BuildNameSpace.setUp(self)
    for name in namespace:
      self.modules.wake(name, self.manager)
    return

class TestCheck(BuildCheck, TestCase):
  def test_check_alone(self):
    self.assertEqual(self.modules.check('view_w_param-egg@prj'), 6)
    self.assertSetEqual(self.modules.get_passed(), {'view_w_param-egg@prj'})
    self.assertSetEqual(self.modules.get_failed(), set())
    return

  def test_select_alone(self):
    name = 'view_w_param-egg@prj'
    self.modules.select(name)
    self.assertEqual(self.modules.check(name), 6)
    self.assertSetEqual(self.modules.get_passed(), {'view_w_param-egg@prj'})
    self.assertSetEqual(self.modules.get_failed(), set())
    self.assertSetEqual(self.modules.get_selected(), {'view_w_param-egg@prj'})
    self.assertSetEqual(self.modules.get_selected_by_parent(iView),
                        {'view_w_param-egg@prj'})
    self.assertSetEqual(self.modules.get_selected_by_parent(iFill), set())
    return

  def test_check_with_dep(self):
    self.assertEqual(self.modules.check('view@prj'), (33, 66))
    self.assertSetEqual(self.modules.get_passed(), {'view@prj', 'fill-bar@prj'})
    self.assertSetEqual(self.modules.get_failed(), set())
    return

  def test_select_with_dep(self):
    self.modules.select('view@prj')
    self.assertEqual(self.modules.check('view@prj'), (33, 66))
    self.assertSetEqual(self.modules.get_passed(), {'view@prj', 'fill-bar@prj'})
    self.assertSetEqual(self.modules.get_failed(), set())
    self.assertSetEqual(self.modules.get_selected(), {'view@prj'})
    self.assertSetEqual(self.modules.get_selected_by_parent(Interface),
                        {'view@prj'})
    self.assertSetEqual(self.modules.get_selected_by_parent(iFill), set())
    return

  def test_check_error(self):
    self.assertIsNone(self.modules.check('error-spam@prj'))
    self.assertSetEqual(self.modules.get_passed(), set())
    self.assertSetEqual(self.modules.get_failed(), {'error-spam@prj'})
    return

  def test_check_error_at_dep(self):
    self.assertIsNone(self.modules.check('bunny-pyon@prj'))
    self.assertSetEqual(self.modules.get_passed(), set())
    self.assertSetEqual(self.modules.get_failed(), {'error-spam@prj', 'bunny-pyon@prj'})
    return

  def test_check_error_call(self):
    name = 'error-spam@prj'
    self.modules.check(name)
    module = self.modules._modules[name]
    self.assertEqual(module.module.spam, 42)
    return

  def test_check_error_call_method(self):
    name = 'search_w_param-atomsk@prj'
    self.modules.check(name)
    module = self.modules._modules[name]
    self.assertEqual(module.module.egg, 23)
    return

  def test_error_message(self):
    name = 'error-spam@prj'
    self.modules.check(name)
    self.assertEqual(self.modules.get_error_msg(name), 'foo')
    return

  def test_missing_error_message(self):
    name = 'view_w_param-egg@prj'
    self.modules.check(name)
    self.assertRaises(AssertionError, self.modules.get_error_msg, name)
    return

  def test_get_sign(self):
    self.assertTupleEqual(self.modules.get_sign('fill-bar@prj'),
                          ('prj.fill.Fill', 'spam=42', '0.5.6'))
    self.assertTupleEqual(self.modules.get_sign('view@prj'),
                          ('prj.view.View', '', '0.5.6'))
    self.assertTupleEqual(self.modules.get_sign('view_w_param-egg@prj'),
                          ('prj.view_w_param.cView', 'egg=56', '0.5.7'))
    return

class TestChannel(BuildCheck):
  def test_get_channels(self):
    self.assertSetEqual(self.modules.get_channels(), {'main', 'can1', 'can2'})
    return

class TestPrjName(BuildCheck):
  def test_get_prj_name(self):
    for name in namespace:
      if not name.endswith('@prj2'):
        self.assertEqual(self.modules.get_prj_name(name), prj_name)
      else:
        self.assertEqual(self.modules.get_prj_name(name), prj2_name)
    return

class BuildFill(BuildCheck):
  def setUp(self):
    BuildCheck.setUp(self)
    for name in namespace:
      self.modules.check(name)
    return

class TestFill(BuildFill):
  def test_alone(self):
    self.assertEqual(self.modules.fill('fill-bar@prj'), 47)
    return

  def test_alone_baz(self):
    self.assertEqual(self.modules.fill('fill-baz@prj'), 29)
    return

  def test_with_dep(self):
    self.assertEqual(self.modules.fill('view@prj'), 33)
    return

  def test_alone_method(self):
    self.assertEqual(self.modules.fill('view_w_param-egg@prj'), (12, 3))
    return

  def test_error(self):
    self.assertRaises(AssertionError, self.modules.fill, 'error-spam@prj')
    return

  def test_error_dep(self):
    self.assertRaises(AssertionError, self.modules.fill, 'bunny-pyon@prj')
    return

  def test_error_method(self):
    self.assertRaises(AssertionError, self.modules.fill, 'search_w_param-atomsk@prj')
    return

class BuildRun(BuildFill):
  def setUp(self):
    BuildFill.setUp(self)
    for name in 'fill-bar@prj', 'fill-baz@prj', 'view@prj', \
                'view_w_param-egg@prj', 'tiger@prj', 'bear-takun@prj', \
                'tiger@prj2', 'lion@prj2':
      self.modules.fill(name)
    return

class TestRun(BuildRun):
  def test_alone(self):
    name = 'fill-bar@prj'
    self.modules.run(name)
    module = self.modules._modules[name]
    self.assertEqual(module.module.egg, 41)
    return

  def test_alone_baz(self):
    name = 'fill-baz@prj'
    self.modules.run(name)
    module = self.modules._modules[name]
    self.assertEqual(module.module.egg, 23)
    return

  def test_with_dep(self):
    name = 'view@prj'
    self.modules.run(name)
    module = self.modules._modules[name]
    self.assertEqual(module.module.spam, 24)
    return

  def test_alone_method(self):
    name = 'view_w_param-egg@prj'
    self.modules.run(name)
    module = self.modules._modules[name]
    self.assertEqual(module.module.egg, 41)
    return

  def test_error(self):
    self.assertRaises(AssertionError, self.modules.run, 'error-spam@prj')
    return

  def test_error_dep(self):
    self.assertRaises(AssertionError, self.modules.run, 'bunny-pyon@prj')
    return

  def test_error_method(self):
    self.assertRaises(AssertionError, self.modules.run, 'search_w_param-atomsk@prj')
    return

  def test_optdep(self):
    name = 'tiger@prj'
    self.modules.run(name)
    module = self.modules._modules[name]
    self.assertEqual(module.module.passed_optdep, ('fill-bar@prj',))
    return

  def test_one_of_optdep_fail(self):
    name = 'bear-takun@prj'
    self.modules.run(name)
    module = self.modules._modules[name]
    self.assertEqual(module.module.passed_optdep, ('fill-bar@prj',))
    return

  def test_dep_from_other_prj(self):
    name = 'lion@prj2'
    self.modules.run(name)
    module = self.modules._modules[name]
    self.assertEqual(set(module.module.dep), set(['tiger@prj', 'tiger']))
    return

class TestClose(BuildFill):
  def test_close(self):
    self.modules.close()
    self.assertDictEqual(self.modules._namespace, namespace)
    self.assertDictEqual(self.modules._modules, {})
    self.assertDictEqual(self.modules._checks, {})
    self.assertDictEqual(self.modules._errors, {})
    self.assertDictEqual(self.modules._fills, {})
    self.assertSetEqual(self.modules._runs, set())
    self.assertSetEqual(self.modules._selects, set())
    return

class TestRemove(BuildFill):
  def test_remove(self):
    name = 'error-spam@prj'
    self.modules.remove(name)
    self.assertNotIn(name, self.modules._namespace)
    self.assertNotIn(name, self.modules._modules)
    self.assertNotIn(name, self.modules._checks)
    self.assertNotIn(name, self.modules._errors)
    self.assertNotIn(name, self.modules._fills)
    self.assertNotIn(name, self.modules._runs)
    self.assertNotIn(name, self.modules._selects)
    return

class TestContainer(TestCase):
  def setUp(self):
    self.container = Container()
    return

  def test_copy(self):
    container = self.container.copy()
    self.assertIsInstance(container, Container)
    return

if __name__ == '__main__':
  from unittest import main

  main()
