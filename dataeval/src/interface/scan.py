import re
import os
import sys
import inspect
import unittest

from .Interfaces import iInterface, iAnalyze, iCompare, iSearch, iView, iFill,\
                        iCalc
from .Parameter import iParameter
from .module import MethodModuleParamValue, Parameter

_class_names = {
  'iSearch':  ('cSearch',  'search'),
  'iCompare': ('cCompare', 'compare'),
  'iView':    ('cView',    'view'),
  'iAnalyze': ('cAnalyze', 'analyze'),
  'iFill':    ('cFill',    'fill'),
  'iCalc':    ('cCalc',    'fill'),
}

_interfaces = iAnalyze, iCompare, iSearch, iView, iFill, iCalc



class ModuleScanner:
  def __init__(self, module_name, prj):
    if prj:
      module_python_path = '.'.join((prj, module_name))
      if module_python_path in sys.modules:
        del sys.modules[module_python_path]
      self.module = __import__(module_python_path)
      pkgs = module_python_path.split('.')
      for pkg in pkgs[1:]:
        self.module = getattr(self.module, pkg)
    else:
      # if module_name is an absolute path
      self.module = __import__(module_name)
    return

  def __call__(self):
    interface, class_name, channels = self._get_interface()
    parameters = self._get_params()
    return interface, class_name, parameters, channels

  def _get_interface(self):
    for name in dir(self.module):
      attr = getattr(self.module, name)
      if (    inspect.isclass(attr) and self.module.__name__ ==  attr.__module__
          and issubclass(attr, iInterface)): break
    else:
      raise ValueError('No interface class found.')
    for parent in _interfaces:
      if issubclass(attr, parent): break
    else:
      raise ValueError('No valid parent found.')
    interface = parent.__name__
    channels = getattr(attr, 'channels')
    return interface, name, channels

  def _get_params(self):
    raise NotImplementedError()


class MethodModuleScanner(ModuleScanner):
  def _get_params(self):
    params = {}
    for name in dir(self.module):
      attr = getattr(self.module, name)
      if isinstance(attr, iParameter):
        sign = attr.getSign()
        class_name = attr.__class__.__name__
        if not hasattr(self.module, class_name):
          class_name = '%s.%s' %(attr.__class__.__module__, class_name)
        params[name] = MethodModuleParamValue.join(class_name, sign)
    return params

class InitModuleScanner(ModuleScanner):
  def _get_params(self):
    params = self._get_params_from_dict('init_params')
    return params

  def _get_params_from_dict(self, name):
    params = {}
    for name, param in getattr(self.module, name, {}).iteritems():
      params[name] = _get_param_value(param)
    return params

class CallModuleScanner(InitModuleScanner):
  def _get_params(self):
    params = self._get_params_from_dict('call_params')
    if params:
      param_class = self._get_param_class()
      params = dict([(name, MethodModuleParamValue.join(param_class,
                                                        param_value))
                     for name, param_value in params.iteritems()])
    return params

  def _get_param_class(self):
    for name in dir(self.module):
      attr = getattr(self.module, name)
      if (    inspect.isclass(attr) and attr is not iParameter
          and issubclass(attr, iParameter)): break
    else:
      raise ValueError('No parameter class found.')
    return name

def _get_param_value(param):
  param = Parameter.from_dict(param)
  param = param.to_str()
  return param

class Module:
  def __init__(self, param_type, name, interface, class_name, parameters,
               channels, prj):
    self.param_type = param_type
    self.name = name
    self.interface = interface
    self.class_name = class_name
    self.parameters = parameters
    self.channels = channels
    self.prj = prj
    return

  _scanners = {
    'method': ('method', MethodModuleScanner),
    'call':   ('method', CallModuleScanner),
    'init':   ('init', InitModuleScanner),
  }

  @classmethod
  def from_file(cls, filename, prj):
    name = _get_module_name(filename)
    with open(filename) as fp:
      scanner_type = _get_module_scanner_type(fp, filename=filename)

    return cls.from_file_object(name, prj, scanner_type)

  @classmethod
  def from_memory(cls, name, prj, fp):
    scanner_type = _get_module_scanner_type(fp)
    return cls.from_file_object(name, prj, scanner_type)

  @classmethod
  def from_file_object(cls, name, prj, scanner_type):
    signature, Scanner = cls._scanners[scanner_type]
    scanner = Scanner(name, prj)
    interface, class_name, parameters, channels = scanner()
    self = cls(signature, name, interface, class_name, parameters, channels,
               prj)
    return self

  def hold_parameters(self, active_parameters):
    for parameter in self.parameters.keys():
      if parameter not in active_parameters:
        del self.parameters[parameter]
    return

class TestCase(unittest.TestCase):
  def assertModuleEqual(self, a, b):
    names = 'param_type', 'name', 'interface', 'class_name', 'parameters',\
            'channels'
    for name in names:
      self.assertEqual(getattr(a, name), getattr(b, name))
    return

def _get_module_scanner_type(fp, filename=''):
  pattern = re.compile('#\\s*-\*-\\s*dataeval\\s*:\\s*(\\w+)\\s*-\*-')
  for line in fp:
    match = pattern.search(line)
    if match:
      fp.seek(0)
      return match.group(1)
  fp.seek(0)
  check_unknown_module(filename)
  fp.seek(0)
  return 'method'

def check_unknown_module(filename):
  status = 'param_class'
  module_name = _get_module_name(filename)

  for interface, (class_name, prefix) in _class_names.iteritems():
    if module_name.startswith(prefix): break
  else:
    raise ValueError('Invalid file prefix.')

  param_class_pat = ClassParentPat('iParameter')
  param_instance_pat = ReferencePat('interface.NullParam')
  interface_class_pat = ClassParentPat(interface)
  named_interface_class_pat = ClassNamePat(class_name)
  interface_method_pat = MethodPat(prefix)

  with open(filename) as fp:
    for line in fp:
      if status == 'param_class':
        param_class_name = param_class_pat(line)
        if param_class_name is None:
          param  = param_instance_pat(line)
          if param is not None:
            status = 'interface'
        else:
          param_instance_pat = InstancePat(param_class_name)
          status = 'param_instance'
      elif status == 'param_instance':
        parameter = param_instance_pat(line)
        if parameter is not None:
          status = 'interface'
      elif status == 'interface':
        class_name = interface_class_pat(line)
        if class_name is not None:
          status = 'end'
        else:
          parent_names = named_interface_class_pat(line)
          if parent_names is not None:
            status = 'end'
      elif status == 'end':
        break
  if status != 'end':
    raise ValueError('Reached status as unsigned module: %s' %status)
  return

def _get_module_name(filename):
  if not os.path.isfile(filename): raise ValueError('Not a file: %s' %filename)
  module_name, ext = os.path.splitext(os.path.basename(filename))
  if ext != '.py': raise ValueError('Invalid file extension.')
  return module_name

class ClassParentPat:
  pat = re.compile('^class\\s+(\\w+)(\(.+)\):')

  def __init__(self, parent):
    self.parent = parent
    return

  def __call__(self, line):
    match = self.pat.search(line)
    if match:
      name, parents = match.groups()
      parents = [parent.strip().split('.')[-1] for parent in parents.split(',')]
      if self.parent in parents:
        return name
    return

class Pattern:
  def __init__(self, pat):
    self.pat = pat
    return

  def __call__(self, line):
    match = self.pat.search(line)
    if match:
      name = match.group(1)
      return name
    return

class InstancePat(Pattern):
  def __init__(self, class_name):
    pat = re.compile('^(\\w+)\\s*=\\s*%s\(.*\)' %class_name)
    Pattern.__init__(self, pat)
    return

class ReferencePat(Pattern):
  def __init__(self, name):
    pat = re.compile('^(\\w+)\\s*=\\s*%s' %name)
    Pattern.__init__(self, pat)
    return

class MethodPat(Pattern):
  def __init__(self, method_name):
    pat = re.compile('^\\s+%s\(((self)|(cls)),' %method_name)
    Pattern.__init__(self, pat)
    return

class ClassNamePat(Pattern):
  def __init__(self, class_name):
    pat = re.compile('^class\\s+%s\((.+)\):' %class_name)
    Pattern.__init__(self, pat)
    return

