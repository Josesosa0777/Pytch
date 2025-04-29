"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
__docformat__ = "restructuredtext en"

import sys
import re

import measparser

class ReservedFillName(BaseException):
  pass

class cObjectSource:
  """Container for the processed objects by the iFill interfaces."""
  def __init__(self):
    self.objects = {}
    self.fills = {}
    self.result = {}
    self.error = {}
    self.selected = set()
    self.passed = set()
    pass

  def select(self, name):
    if name in self.fills:
      self.selected.add(name)
    pass 

  def selects(self, names):
    for name in names:
      self.select(name)

  def add_fill(self, name, fill):
    try:
      loaded = self.fills[name]
    except KeyError:
      self.fills[name] = fill
    else:
      if loaded.__class__ is fill.__class__:
        self.fills[name] = fill
      else:
        raise ReservedFillName(name)
    pass
  
  def add_fills(self, fills):
    for name, fill in fills.iteritems():
      self.add_fill(name, fill)
    pass

  def _check(self, name):
    if name in self.error:
      error = self.error[name]
      raise error
    fill = self.fills[name]
    result = fill.check()
    return result

  def check(self, name):
    if name in self.result:
      return self.result[name]
    elif name in self.error:
      pass
    else:
      fill = self.fills[name]
      for dep in fill.dep:
        self.check(dep)
        try:
          error = self.error[dep]
        except KeyError:
          pass
        else:
          self.error[name] = error
          break
      else:
        try:
          result = fill.check()
        except measparser.signalgroup.SignalGroupError, error:
          self.error[name] = error
        else:
          self.result[name] = result
          if name in self.selected:
            self.passed.add(name)
          return result
    pass

  def get_name(self, fill):
    """
    Get the name of the regitered module.
    
    :Parameters:
      fill : `interface.Interfaces.iInterface`

    :Exceptions:
      ValueError: if the `fills` does not contain `fill`

    :ReturnType: str
    """
    for name, _fill in self.fills.iteritems():
      if fill is _fill:
        return name
    raise ValueError('The requested %s instance is not registered' %fill.__class__.__name__)

  def get_error_msg(self, name):
    """
    :Parameter:
      name : str

    :Exceptions:
      KeyError: the `error` does not contain `name`

    :ReturnType: str
    """
    error = self.error[name]
    msg = error.message
    return msg

  def get_passed(self, pattern):
    check = re.compile(pattern)
    return [passed 
            for passed in self.passed 
            if check.match(passed)]

  def fill(self, name):
    if name in self.objects:
      result = self.objects[name]
    else:
      fill = self.fills[name]
      result = self.result[name]
      if result is None:
        result = fill.fill()
      elif isinstance(result, tuple):
        result = fill.fill(*result)
      else:
        result = fill.fill(result)
      self.objects[name] = result
    return result

  def extract_signals(self):
    for result in self.result.itervalues():
      for signal in measparser.signalgroup.extract_signals(result):
        yield signal
  
  def remove(self, name):
    if name not in self.objects:
      return
    del self.fills[name]
    del self.objects[name]
    if name in self.result:
      del self.result[name]
    else:
      del self.error[name]
    if name in self.selected:
      self.selected.remove(name)
    if name in self.passed:
      self.passed.remove(name)
    return

