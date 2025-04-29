import copy
from collections import OrderedDict

import numpy as np

from measparser.signalproc import rescaledd


class PrimitiveCollection(OrderedDict):
  def __init__(self, time, *args, **kwargs):
    assert time.ndim == 1
    OrderedDict.__init__(self, *args, **kwargs)
    self.time = time
    return
  
  def __copy__(self):
    assert self.__class__ is PrimitiveCollection, "__copy__ override needed"
    newobj = PrimitiveCollection(self.time, self.iteritems())
    return newobj
  
  def rescale(self, time_scale, **kwargs):
    newobj = copy.copy(self)
    newobj.time = time_scale
    for key, primitive in self.iteritems():
      newobj[key] = primitive.rescale(time_scale, **kwargs)
    return newobj

class Primitive(object):
  RESERVED_ATTR_NAMES = {'time',}
  
  def __init__(self, time):
    assert time.ndim == 1
    self.time = time
    return
  
  @classmethod
  def from_states(cls, time, states):
    args = [states[:,i,...] for i in xrange(states.shape[1])]
    newobj = cls(time, *args)
    return newobj
  
  def rescale(self, time_scale, **kwargs):
    newobj = copy.copy(self)
    newobj.time = time_scale
    for attr_name, attr in self.__dict__.iteritems():
      if attr_name in self.RESERVED_ATTR_NAMES:
        continue
      if isinstance(attr, np.ndarray) and attr.shape[0] == self.time.shape[0]:
        _, newval = rescaledd(self.time, attr, time_scale, **kwargs)
        setattr(newobj, attr_name, newval)
      elif isinstance(attr, Primitive):
        newval = attr.rescale(time_scale, **kwargs)
        setattr(newobj, attr_name, newval)
    return newobj
  
  def _get_states(self):
    states = np.empty((self.time.size, 0))
    state_names = self.get_statenames2indices().iterkeys()
    for state_name in state_names:
      state = getattr(self, state_name)
      if state.ndim != 1:  # TODO: impl
        raise NotImplementedError("1-D array states are currently supported")
      states = np.hstack((states, state.reshape((self.time.size, 1))))
    return states
  get_states = _get_states
  
  def _get_stateindices2names(self):
    state_names = self.get_statenames2indices()
    state_indices = OrderedDict((y,x) for x,y in state_names.iteritems())
    return state_indices
  get_stateindices2names = _get_stateindices2names
  
  def get_statenames2indices(self):
    state_names = OrderedDict()
    state_idx = 0
    initparams = self.__class__.__dict__['__init__'].func_code.co_varnames
    for attr_name in initparams:
      if attr_name in self.RESERVED_ATTR_NAMES or attr_name == 'self':
        continue
      attr = getattr(self, attr_name)
      if isinstance(attr, np.ndarray) and attr.shape[0] == self.time.shape[0]:
        if attr.ndim != 1:  # TODO: impl
          raise NotImplementedError("1-D array states are currently supported")
        state_names[attr_name] = state_idx
        state_idx += 1
    return state_names

class TuplePrimitive(Primitive, tuple):
  def __new__(cls, time, items):  # needed because of tuple inheritance
    return tuple.__new__(cls, items)
  
  def __init__(self, time, items):
    Primitive.__init__(self, time)
    assert all(item.size == time.size for item in items), \
      "All items shall have the same size as 'time'"
    return
  
  def rescale(self, time_scale, **kwargs):
    raise NotImplementedError
  
  def get_statenames2indices(self):
    raise NotImplementedError

class ListPrimitive(Primitive, list):
  def __init__(self, time, items):
    list.__init__(self, items)
    Primitive.__init__(self, time)
    assert all(item.size == time.size for item in items), \
      "All items shall have the same size as 'time'"
    return
  
  def rescale(self, time_scale, **kwargs):
    raise NotImplementedError
  
  def get_statenames2indices(self):
    raise NotImplementedError
