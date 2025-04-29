__docformat__ = "restructuredtext en"

import re
import sys
import inspect
import logging
from module import CreateModule, TestCase as ModuleTestCase

from measparser.signalgroup import SignalGroupError
from measparser.signalgroup import extract_signals

class Modules:
  """Container for the user modules which implements iInterface"""
  def __init__(self):
    self._namespace = Container()
    self._modules = Container()
    self._checks = Container()
    self._errors = {}
    self._fills = {}
    self._runs = set()
    self._selects = set()
    return

  def close(self):
    self._modules.clear()
    self._checks.clear()
    self._errors.clear()
    self._fills.clear()
    self._runs.clear()
    self._selects.clear()
    return

  def clone(self):
    modules = Modules()
    modules._namespace = self._namespace.copy()
    return modules

  def add_csv_module(self, module_name, param_name, module):
    name = self.add(module_name, param_name, module.class_name,
                    module.param_type, module.param_value, module.prj_name)
    return name

  def add(self, module_name, param_name, class_name, param_type, param,
          prj_name):
    createmodule = CreateModule(module_name, class_name, param_type, param,
                                prj_name)
    name = ModuleName.create(module_name, param_name, prj_name)
    self._namespace[name] = createmodule
    return name

  def remove_from_runs(self, name):
    """
    Removes a module from the -runs- list
    """
    if name in self._runs:
      self._runs.remove(name)
    return

  def remove(self, name):
    for container in self._namespace,\
                     self._modules,\
                     self._checks,\
                     self._errors,\
                     self._fills:
      if name in container:
        del container[name]
    return

  def wake(self, pattern, manager):
    "Wake modules from namespace based on `pattern`"
    name = self._namespace.get_name(pattern)
    self._wake(name, manager)
    return

  def _wake(self, name, manager):

    if name in self._modules:
      return
    createmodule = self._namespace[name]
    module = createmodule(manager)
    self._modules[name] = module
    for dep in module.get_dep():
      self.wake(dep, manager)
    for dep in module.get_optdep():
      self.wake(dep, manager)
    return

  def get_module(self, pattern):
    name = self._modules.get_name(pattern)
    module = self._modules[name]
    return module.module

  def get_channels(self):
    channels = set()
    for module in self._modules.itervalues():
      module_channels = module.get_channels()
      channels = channels.union(module_channels)
    return channels

  def get_prj_name(self, pattern):
    try:
      name = self._modules.get_name(pattern)
      module = self._modules[name]
    except AssertionError:
      name = self._namespace.get_name(pattern)
      module = self._namespace[name]
    if isinstance(module, CreateModule):
      return module.get_prj_name()
    return module.module.get_prj_name()

  def select(self, pattern):
    name = self._modules.get_name(pattern)
    self._selects.add(name)
    self._check(name)
    status = name in self._checks
    return status

  def check(self, pattern):
    name = self._modules.get_name(pattern)
    return self._check(name)

  def _check(self, name):
    """
    Call the check method of the selected module.

    If the method raises a SignalGroupError then the method will be registered
    as failed and None will be return."""
    logger = logging.getLogger()
    if name in self._checks:
      return self._checks[name]
    if name in self._errors:
      return
    module = self._modules[name]
    # check dependencies
    for dep in module.get_dep():
      try:
        self.check(dep)
      except AssertionError:
        logger.error('As dep of %s' %name)
        raise
      dep = self._modules.get_name(dep)
      if dep in self._errors:
        error = self._errors[dep]
        self._errors[name] = error
        module.error()
        return

    passed_optdep = []
    for dep in module.get_optdep():
      self.check(dep)
      if dep not in self._errors:
        passed_optdep.append(dep)
    module.set_passed_optdep(passed_optdep)

    try:
      check = module.check()
    except (SignalGroupError, AssertionError), error:
      self._errors[name] = error
      module.error()
    else:
      self._checks[name] = check
      return check
    return

  def get_selected(self, pattern=''):
    "Get the selected and passed modules based on regexp `pattern`"
    pattern = re.compile(pattern)
    names = set([name for name in self._checks
                 if name in self._selects and pattern.search(name)])
    return names

  def get_passed(self, pattern=''):
    "Get the passed modules based on regexp `pattern`"
    pattern = re.compile(pattern)
    return set([name for name in self._checks if pattern.search(name)])

  def get_failed(self, pattern=''):
    "Get the failed modules based on regexp `pattern`"
    pattern = re.compile(pattern)
    return set([name for name in self._errors if pattern.search(name)])

  def get_error_msg(self, name):
    assert name in self._errors, '%s is not a failed module' %name
    error = self._errors[name]
    return error.message

  def fill(self, pattern):
    name = self._checks.get_name(pattern)
    return self._fill(name)

  def _fill(self, name):
    module = self._modules[name]
    check = self._checks[name]
    result = _call(module.fill, check)
    self._fills[name] = result
    return result

  def calc(self, pattern, manager):
    name = self._namespace.get_name(pattern)
    self._wake(name, manager)
    if self._check(name):
      return self._fill(name)
    else:
      raise self._errors[name]
    pass

  def get_passed_by_parent(self, parent):
    names = [name for name, module in self._modules.iteritems()
             if name in self._checks and module.isinstance(parent)]
    return set(names)

  def get_selected_by_parent(self, parent):
    names = [name for name, module in self._modules.iteritems()
             if    name in self._selects
               and name in self._checks
               and module.isinstance(parent)]
    names = set(names)
    return names

  def run(self, name):
    assert name in self._fills, '%s did not run fill' %name
    if name in self._runs:
      return
    else:
      self._runs.add(name)
    module = self._modules[name]
    fill = self._fills[name]
    _call(module.run, fill)
    return

  def get_selecteds(self):
    return self._selects

  def extract_signals(self):
    "Extract the signal names from the result of checks."
    for result in self._checks.itervalues():
      for signal in extract_signals(result):
        yield signal
    return

  def get_sign(self, name):
    "Get the class and parameter signature of the module."
    assert name in self._modules, '%s is not waked' %name
    module = self._modules[name]
    class_sign = module.get_class_sign()
    param_sign = module.get_param_sign()
    version = module.get_version()
    return class_sign, param_sign, version

def _call(method, param):
  if param is None:
    result = method()
  elif isinstance(param, tuple):
    result = method(*param)
  else:
    result = method(param)
  return result

class Container(dict):
  def get_names(self, pattern):
    if pattern in self:
      names = [pattern]

    else:
      _, _, prj = ModuleName.split(pattern)
      if not prj:
        try:
          prj = self.get_caller_prj()
        except AssertionError:
          msg = 'Cannot identify `%s` module\'s project' % pattern
          raise AssertionError(msg)
        pattern = ModuleName.extend_prj_name(pattern, prj)
      names = [ name for name in sorted(self)
              if ModuleName.check_module_name_extended_part(name, pattern)]
    return names

  def get_name(self, pattern):
    names = self.get_names(pattern)
    no_names = len(names)
    if no_names == 0:
      msg = '`%s` is not a registered module name' % pattern
      raise AssertionError(msg)
    elif no_names > 1:
      msg = 'Multiple modules registered with `%s`: %s'\
            % (pattern, ', '.join(names))
      raise AssertionError(msg)
    return names[0]

  def get_caller_prj(self):
    # TODO: refactor whole method
    from .Interfaces import iInterface  # here to avoid cyclic import
    stack = inspect.stack()
    for data in stack:
      frame, _, _, _, _, _ = data
      object_ = frame.f_locals.get('self', None)
      if isinstance(object_, iInterface):
        prj = object_.get_prj_name()
        return prj
    raise AssertionError("Caller project cannot be determined")

  def copy(self):
    other = dict.copy(self)
    other = self.__class__(other)
    return other



class ModuleName:
  PARAM_SEP = '-'
  PRJ_SEP = '@'
  @classmethod
  def split(cls, name):
    names = name.rsplit(cls.PRJ_SEP, 1)
    if len(names) == 1:
      prj = ''
    else:
      prj = names[1]

    names = names[0].split(cls.PARAM_SEP, 1)
    if len(names) == 1:
      names.append('')

    names.append(prj)
    module_name, param_name, prj_name = names
    return module_name, param_name, prj_name

  @classmethod
  def create(cls, module_name, param_name, prj_name):
    name = module_name + cls.PARAM_SEP + param_name if param_name else module_name
    name = name + cls.PRJ_SEP + prj_name if prj_name else name
    return name

  @classmethod
  def check_module_name_extended_part(cls, name, module_name):
    result = name == module_name
    return result

  @classmethod
  def check_module_name_base_part(cls, name, module_name):
    _module_name, param, prj = cls.split(name)
    result = _module_name == module_name
    return result

  @classmethod
  def extend_prj_name(cls, name, prj_name):
    if cls.PRJ_SEP in name:
      return name

    return name + cls.PRJ_SEP + prj_name

class TestCase(ModuleTestCase):
  def assertNameSpaceEqual(self, modules, namespace):
    for name in namespace:
      self.assertCreateModuleEqual(modules._namespace[name], namespace[name])
    return

