import os
import csv
import sys
import re
import logging
import traceback
import unittest

from interface.scan import Module as ModuleScan
from interface.module import MethodModuleParamValue, Parameter

class Modules:
  SEP = ':'
  def __init__(self):
    self._modules = {}
    """:type: dict
    {(module_name<str>, param_name<str>): (class_name<str>, param_type<str>,
                                           param_value<str>)}"""
    return

  def read(self, filename):
    with open(filename, 'rb') as fp:
      reader = csv.reader(fp, delimiter=self.SEP)
      for row in reader:
        self.add(*row)
    return

  def protected_write(self, filename):
    self.update(filename)
    self.write(filename)
    return

  def update(self, filename):
    if not os.path.exists(filename): return

    modules = Modules()
    modules.read(filename)
    for row in modules.iter_extra_modules(self):
      self.add(*row)
    return

  def write(self, filename):
    with open(filename, 'wb') as fp:
      writer = csv.writer(fp, delimiter=self.SEP)
      for row in self.iter_modules():
        writer.writerow(row)
    return

  def scan(self, prj_name, dirname):
    msg = {}
    if dirname not in sys.path:
      sys.path.append(dirname)
    for basename in os.listdir(dirname):
      name = os.path.join(dirname, basename)
      try:
        module = ModuleScan.from_file(name, prj_name)
      except ValueError, error:
        msg[name] = error.message
      except:
        msg[name] = traceback.format_exc()
      else:
        # Use a regex to filter out invalid names
        if re.search("[^\w\_]", os.path.splitext(basename)[0]) is None:
          self.add_module(prj_name, module)
        else:
          msg[name] = "Invalid characters in module name"
    return msg

  def add_module(self, prj_name, module):
    parameters = module.parameters if module.parameters else {'': ''}
    for param_name, param_value in parameters.iteritems():
      self.add(module.name, param_name, module.interface, module.class_name,
               module.param_type, param_value, prj_name, *module.channels)
    return

  def add(self, module_name, param_name, interface, class_name, param_type,
          param_value, prj_name, *channels):
    module = ModuleCreator.create_module(interface, class_name, param_type,
                                         param_value, prj_name, channels)
    self._add(module_name, param_name, module, prj_name)
    return module

  def _add(self, module_name, param_name, module, prj_name):
    name = module_name, param_name, prj_name
    ### workaround for improper temp module handling #2134; TODO: solve
    if name in self._modules:
      logger = logging.getLogger()
      logger.debug("AssertionError: Reserved name error: %s-%s@%s" %name)
      self.rm(module_name, param_name, prj_name)
    ### end of workaround
    #assert name not in self._modules, 'Reserved name error: %s-%s@%s' %name
    self._modules[name] = module
    return

  def rm(self, module_name, param_name, prj_name):
    name = module_name, param_name, prj_name
    ### workaround for improper temp module handling #2134; TODO: solve
    if name not in self._modules:
      logger = logging.getLogger()
      logger.debug("KeyError: %s-%s@%s is not self._modules" %name)
      return
    ### end of workaround
    del self._modules[name]
    return

  def iter_extra_modules(self, modules):
    keys = set(self._modules.iterkeys())
    for key in keys.difference(modules._modules):
      module = self._modules[key]
      module = extend_module(key, module)
      yield module
    return

  def __iter__(self):
    return self._modules.iterkeys()

  def iter_modules(self):
    for name, module in self._modules.iteritems():
      module = extend_module(name, module)
      yield module
    return


  def iter_by_interface(self, interface):
    for name, module in self._modules.iteritems():
      if module.interface == interface:
        yield name
    return

  def get(self, module_name, param_name, prj_name):
    name = module_name, param_name, prj_name
    module = self._modules[name]
    return module

  def get_channel(self, module_name, param_name, prj_name):
    module = self.get(module_name, param_name, prj_name)
    return module.channels

  def get_channels(self):
    channels = set()
    for module in self._modules.itervalues():
      channels.update(module.channels)
    return channels

  def clone_module(self, module_name, param_name, prj_name, param_value):
    modules = self.get_modules_by_module_name(module_name)
    check_module_attributes(modules)
    module = modules.pop().copy()
    module.set_param_value(param_value)
    self._add(module_name, param_name, module, prj_name)
    return module

  def clone_param(self, module_name, param_name, prj_name):
    module = self.get(module_name, param_name, prj_name)
    param = module.get_param_list()
    param_name = self._create_param_name(module_name, param_name)
    return param_name, param

  def _create_param_name(self, module_name, param_name):
    i = 0
    pattern = param_name + '%d'
    while (module_name, pattern %i) in self._modules:
      i += 1
    param_name = pattern %i
    return param_name

  def get_modules_by_module_name(self, module_name):
    modules = [module
               for (module_name_, param_name, prj_name), module
               in self._modules.iteritems()
               if module_name_ == module_name]
    return modules


def check_module_attributes(modules):
  attributes = dict(interface=set(), class_name=set(), param_type=set(),
                    channels=set())
  for module in modules:
    for name, attr in attributes.iteritems():
      attr.add( getattr(module, name) )
  for name, attribute in attributes.iteritems():
    assert len(attribute) == 1, "'%s' module attribute is ambiguous" %name
  return

def extend_module(name, module):
  module_name, param, prj = name
  _module = [module_name, param]
  _module.extend(module)
  return _module


class Module:
  param_type = 'spam'
  def __init__(self, interface, class_name, param_value, prj_name, channels):
    self.interface = interface
    self.class_name = class_name
    self.param_value = param_value
    self.prj_name = prj_name
    self.channels = channels
    return

  def copy(self):
    Class = self.__class__
    module = Class(self.interface, self.class_name, self.param_value,
                   self.prj_name, self.channels)
    return module

  def __iter__(self):
    yield self.interface
    yield self.class_name
    yield self.param_type
    yield self.param_value
    yield self.prj_name
    for channel in self.channels:
      yield channel
    return

  def set_param_value(self, param_value):
    raise NotImplementedError()

  def get_param_list(self):
    raise NotImplementedError()

class InitModule(Module):
  param_type = 'init'
  def set_param_value(self, param_value):
    self.param_value = param_value
    return

  def get_param_list(self):
    param_list = conv_param_value_to_list(self.param_value)
    return param_list

class MethodModule(Module):
  param_type = 'method'
  def set_param_value(self, param_value):
    self.param_value = MethodModuleParamValue.replace(self.param_value,
                                                      param_value)
    return

  def get_param_list(self):
    _, param_value = MethodModuleParamValue.split(self.param_value)
    param_list = conv_param_value_to_list(param_value)
    return param_list

def conv_param_value_to_list(param_value):
  param = Parameter.from_str(param_value)
  param_list = param.to_str_list()
  return param_list

class ModuleCreator:
  _module_classes = {
    InitModule.param_type: InitModule,
    MethodModule.param_type: MethodModule,
  }

  @classmethod
  def create_module(cls, interface, class_name, param_type, param_value,
                    prj_name, channels):
    ModuleClass = cls._module_classes[param_type]
    module = ModuleClass(interface, class_name, param_value, prj_name, channels)
    return module

class TestCase(unittest.TestCase):
  def assertModulesEqual(self, modules, module_dict):
    for name in module_dict:
      for attr in 'interface', 'class_name', 'param_value', 'channels':
        self.assertEqual(getattr(modules._modules[name], attr),
                         getattr(module_dict[name], attr))

    return

