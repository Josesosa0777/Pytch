import os

from unittest import main, TestCase

from interface.module import CreateModule
from interface.modules import Modules, ModuleName
from interface.manager import Manager
from measparser.signalgroup import SignalGroupError

prj_name = 'prj'
vidcalibs_path = os.path.join(os.getcwd(), "test", "vidcalibs.db") #"C:\\KBData\\Sandbox\\util_das\\dataeval\\test\\vidcalibs.db"# 
namespace = {
  'view_calc-egg@prj':
    CreateModule('view_calc', 'cView', 'method', 'Parameter;egg=56', prj_name),
  'search_calc-atomsk@prj':
    CreateModule('search_calc', 'cSearch', 'method', 'Parameter;egg=23', prj_name),
}

class Test(TestCase):
  def setUp(self):
    self.modules = Modules()
    for name, createmodule in namespace.iteritems():
      module_name, param_name, prj_name = ModuleName.split(name)
      self.modules.add(module_name, param_name, createmodule.class_name,
                       createmodule.param_type, createmodule.param,
                       createmodule.prj_name)
    self.manager = Manager()
    self.manager.set_vidcalibs(vidcalibs_path)
    return

  def test_calc(self):
    self.assertTupleEqual(self.modules.calc('view_calc-egg@prj', self.manager),
                          (12, 3))
    return

  def test_error(self):
    with self.assertRaisesRegexp(SignalGroupError, 'lucky'):
      self.modules.calc('search_calc-atomsk@prj', self.manager)
    return

if __name__ == '__main__':
  main()
