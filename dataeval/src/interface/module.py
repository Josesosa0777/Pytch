import unittest

from measproc.Batch import get_version

class Module:
  "Handle dataeval user module."
  def __init__(self, module, signature):
    self.__version__ = get_version(module)
    self.signature = signature
    return

  def get_channels(self):
    return self.module.channels

  def get_dep(self):
    dep = self.module.dep
    return self.module.extend_deps(dep)

  def get_optdep(self):
    optdep = self.module.optdep
    return self.module.extend_deps(optdep)

  def set_passed_optdep(self, passed_optdep):
    self.module._passed_optdep = tuple(
      d for d in self.module.iterdep(self.module.optdep)
      if self.module.extend_dep(d) in passed_optdep)
    return

  def check(self):
    return self.module.check()

  def fill(self, *args):
    return self.module.fill(*args)

  def run(self, *args):
    raise NotImplementedError()

  def error(self):
    raise NotImplementedError()

  def get_class_sign(self):
    return self.module.getSign()

  def get_param_sign(self):
    return self.signature

  def get_version(self):
    return self.__version__

  def isinstance(self, parent):
    status = isinstance(self.module, parent)
    return status

  pass

class InitModule(Module):
  "Handle dataeval user module with constructor parameter"
  def __init__(self, module, class_name, param, manager, prj_name):
    Module.__init__(self, module, param)
    Class = getattr(module, class_name)
    param = Parameter.from_str(param)
    param = param.to_dict()
    self.module = Class(manager, prj_name, **param)
    return

  def run(self, *args):
    return self.module.run(*args)

  def error(self):
    self.module.error()
  pass

class MethodModule(Module):
  "Handle dataeval user module with method parameter"
  def __init__(self, module, class_name, param, manager, prj_name):
    param_class_name, param = MethodModuleParamValue.split(param)
    Module.__init__(self, module, param)
    Class = getattr(module, class_name)
    self.module = Class(manager, prj_name)
    if '.' in param_class_name:
      param_class = importModuleAttr(param_class_name)
    else:
      param_class = getattr(module, param_class_name)
    param = Parameter.from_str(param)
    param = param.to_dict()
    self.param = param_class(**param)
    return

  def run(self, *args):
    return self.module.run(self.param, *args)

  def error(self):
    self.module.error(self.param)
    return

class ModuleWithoutParam(Module):
  "Handle dataeval user module without parameter"
  def __init__(self, module, class_name, param, manager, prj_name):
    Module.__init__(self, module, param)
    Class = getattr(module, class_name)
    self.module = Class(manager, prj_name)
    return

  def run(self, *args):
    return self.module.run(*args)

  def error(self):
    return self.module.error()

class CreateModule:
  "Create module from text data"
  def __init__(self, module_name, class_name, param_type, param, prj_name):
    self.module_name = module_name
    self.class_name = class_name
    self.param_type = param_type
    self.param = param
    self.prj_name = prj_name
    return

  def __call__(self, manager):
    if not self.param:
      ModuleClass = ModuleWithoutParam
    elif self.param_type == 'init':
      ModuleClass = InitModule
    elif self.param_type == 'method':
      ModuleClass = MethodModule
    else:
      raise ValueError('Not implementes module type: %s' %self.param_type)
    module = __import__('.'.join((self.prj_name, self.module_name)),
                        fromlist=[self.class_name])
    module = ModuleClass(module, self.class_name, self.param, manager,
                         self.prj_name)
    return module

  def __eq__(self, other):
    result = (    isinstance(other, CreateModule)
              and self.module_name == other.module_name
              and self.class_name == other.class_name
              and self.param_type == other.param_type
              and self.param == other.param
              and self.prj_name == other.prj_name)
    return result

  def get_prj_name(self):
    return self.prj_name

class TestCase(unittest.TestCase):
  def assertCreateModuleEqual(self, a, b):
    for attr in 'module_name', 'class_name', 'param_type', 'param', 'prj_name':
      self.assertEqual(getattr(a, attr), getattr(b, attr))
    return

def importModuleAttr(FullName):
  ModuleName, AttrName = FullName.rsplit('.', 1)
  Module = __import__(ModuleName, fromlist=[AttrName])
  Attr = getattr(Module, AttrName)
  return Attr

class MethodModuleParamValue:
  PARAM_SEP = ';'

  @classmethod
  def split(cls, param):
    param_class, param_value = param.split(cls.PARAM_SEP, 1)
    return param_class, param_value

  @classmethod
  def join(cls, param_class, param_value):
    param = cls.PARAM_SEP.join( (param_class, param_value) )
    return param

  @classmethod
  def replace(cls, param, param_value):
    param_class, _ = cls.split(param)
    param = cls.join(param_class, param_value)
    return param

class Parameter:
  ATR_SEP = ','
  VALUE_SEP = '='

  def __init__(self, param):
    self._param = param
    return

  @classmethod
  def from_str(cls, param):
    param = eval("dict(%s)" %param)
    self = cls(param)
    return self

  @classmethod
  def from_dict(cls, param):
    self = cls(param)
    return self

  @classmethod
  def from_str_list(cls, param):
    param = dict([(name, eval(value)) for name, value in param])
    self = cls(param)
    return self

  @classmethod
  def from_module(cls, module, names):
    param = dict([(name, getattr(module, name)) for name in names])
    self = cls(param)
    return self

  def to_dict(self):
    return self._param

  def to_str(self):
    param = []
    for key in sorted(self._param):
      value = conv_param_value_to_str(self._param[key])
      param.append( self.VALUE_SEP.join( (key, value) ) )
    param = self.ATR_SEP.join(param)
    return param

  def to_str_list(self):
    param_list = [(name, conv_param_value_to_str(self._param[name]))
                  for name in sorted(self._param)]
    return param_list

def conv_param_value_to_str(value):
  value = "'%s'" %value if isinstance(value, str) else str(value)
  return value

