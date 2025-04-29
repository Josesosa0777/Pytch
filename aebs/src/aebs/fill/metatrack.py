from collections import namedtuple

import numpy as np

from measparser import signalproc
from primitives.bases import Primitive
from pyutils.functional import is_pub_method, cached_attribute
from nputils.min_dtype import min_typecode


class MetaTrack(type):
  """ Metaclass that applies attribute caching on methods (whose names are
  collected into cls._methods) and on names defined in cls._attribs. """
  def __init__(cls, name, bases, dct):
    super(MetaTrack, cls).__init__(name, bases, dct)
    # collect and filter function objects of actual class definition
    funcs = tuple(f for f in dct.itervalues()
                      if is_pub_method(f) and f.__name__ not in cls._reserved_names)
    # set each function as cached attribute
    for func in funcs:
      setattr(cls, func.__name__, cached_attribute(func))
    # collect function names (from base classes too)
    methods = tuple( f.__name__ for f in funcs if f.__name__ not in cls._special_methods)
    for base in bases:
      if hasattr(base, '_methods'):
        methods += tuple( m for m in base._methods if m not in base._special_methods )
    setattr( cls, '_methods', methods)
    # cache predefined attribute names with the dedicated "_create" function
    prefix = cls._attribs_prefix if hasattr(cls, '_attribs_prefix') else ''
    for attrib in cls._attribs:
      setattr(cls, prefix + attrib, cached_attribute(cls._create, name=attrib, prefix=prefix))
    if prefix:
      cls._attribs = tuple(prefix + attrib for attrib in cls._attribs)
    return


class EmptyTrack(Primitive):
  __metaclass__ = MetaTrack

  _attribs = ()
  _attribs_prefix = '_'
  _reserved_names = tuple( name for name, f in Primitive.__dict__.iteritems()
                                  if is_pub_method(f) )
  _special_methods = ()

  def _create(self, signalName):
    raise NotImplementedError()

  def __getitem__(self, key):
    return getattr(self, key)

  @staticmethod
  def _get_asso_masks(asso_id, invalid_values):
    masks = {} # { id<int> : mask<ndarray> }
    unique_ids = np.lib.arraysetops.setdiff1d(asso_id.compressed(), invalid_values)
    for id in unique_ids:
      masks[id] = (asso_id.data == id) & ~asso_id.mask
    return masks


class ObjectFromMessage(EmptyTrack):
  " Base class for object data collected from CAN messages "
  def __init__(self, id, msgTime, source, dirCorr, scaleTime=None, **kwargs):
    self._id = id
    self._msgTime = msgTime
    self._source = source
    self._dirCorr = dirCorr
    self._scaleTime = scaleTime
    self._kwargs = kwargs
    self._rescalable = self._scaleTime is not None
    time = self._scaleTime if self._rescalable else self._msgTime
    super(ObjectFromMessage, self).__init__(time)
    return

  def _rescale(self, arr):
    if self._rescalable:
      arr = signalproc.rescale(self._msgTime, arr, self.time, **self._kwargs)[1] 
    return arr


class LinkedObject(object):
  def __init__(self, objects, asso_masks, invalid_value=0):
    self._objects = objects
    self._asso_masks = asso_masks
    self._invalid_value = invalid_value
    return

  def __getattr__(self, name):
    dummy_obj = self._objects.itervalues().next()
    dummy_data = dummy_obj[name] # this fails if there's no such attribute
    data = signalproc.masked_all_like_fill(dummy_data, value=self._invalid_value)
    for i, mask in self._asso_masks.iteritems():
      obj = self._objects[i]
      data[mask] = obj[name][mask]
    setattr(self, name, data)
    return data

  def __getitem__(self, key):
    return getattr(self, key)


def namedtuple_boolarrays(*args, **kwargs):
  class BoolArrays( namedtuple(*args, **kwargs) ):
    """ Implements composite attribute concept (of bool arrays) using namedtuple
    Assumption: data is held in bool arrays that are exclusive, meaning that one
    and only one is active in each timestamp (if not masked) """
    def join(self, mapping=None, fill_value=None):
      """ Join bool arrays into a single array

      :Parameters:
        mapping : dict, optional
          Value-to-fieldname mapping used in join. If not given, default field
          mapping is used (see `mapping` attribute).
        fill_value : int or float, optional
          Default fill value of the output array. Array is initialized with
          arbitrary (random) data if `fill_value` is not given.
      :ReturnType: `ndarray` or `MaskedArray`
        The same class as of the bool arrays
      """
      mapping = mapping if mapping is not None else self.mapping
      dtype = min_typecode( mapping.keys() )
      dummy = self[0]
      out = np.empty_like(dummy, dtype=dtype) # ma case: mask is shared (!)
      is_ma = isinstance(dummy, np.ma.MaskedArray)
      arr = out.data if is_ma else out
      if fill_value is not None:
        arr.fill(fill_value)
      for k,field in mapping.iteritems():
        attr = getattr(self, field)
        mask = attr.data & ~attr.mask if is_ma else attr
        arr[mask] = k # ma case: advanced indexing does not affect shared mask
      return out

    @cached_attribute
    def mapping(self):
      return dict( (k,v) for k,v in zip(xrange(len(self._fields)), self._fields) )
  return BoolArrays

TrackingState    = namedtuple('TrackingState', ('valid', 'measured', 'hist'))
MovingState      = namedtuple_boolarrays('MovingState', ('stat', 'stopped', 'moving', 'unknown', 'crossing', 'crossing_left', 'crossing_right', 'oncoming'))
ARS620MovingState      = namedtuple_boolarrays('ARS620MovingState', ('unknown', 'moving', 'oncoming', 'stat', 'stopped', 'crossing_left', 'crossing_right'))
MaintenanceState      = namedtuple_boolarrays('MaintenanceState', ('empty', 'new', 'measured', 'predicted', 'deleted', 'invalid'))
MovingDirection  = namedtuple_boolarrays('MovingDirection', ('oncoming', 'ongoing', 'undefined', 'crossing', 'crossing_left', 'crossing_right'))
ObjectType       = namedtuple_boolarrays('ObjectType', ('car', 'truck', 'motorcycle', 'pedestrian', 'bicycle', 'unknown', 'point', 'wide'))
SlrObjectType    = namedtuple_boolarrays('SlrObjectType', ('car', 'truck', 'motorcycle', 'pedestrian', 'bicycle', 'unknown', 'point', 'wide','mirror','multiple' , 'initialized' ))
LandmarkObjectType  = namedtuple_boolarrays('LandmarkObjectType', ('traffic_sign'))
BrakeLightStatus = namedtuple_boolarrays('BrakeLightStatus', ('on', 'off', 'unknown'))
BlinkerStatus    = namedtuple_boolarrays('BlinkerStatus', ('off', 'left', 'right', 'both', 'unknown'))
LaneStatus       = namedtuple_boolarrays('LaneStatus', ('same', 'left', 'right', 'uncorr_left', 'uncorr_right', 'unknown'))
MeasuredBy       = namedtuple_boolarrays('MeasuredBy', ('none', 'prediction', 'radar_only', 'camera_only', 'fused'))
ContributingSensors = namedtuple_boolarrays('ContributingSensors',('none', 'radar_only', 'camera_only', 'fused'))
InternalState = namedtuple_boolarrays('InternalState',('none', 'not_ready', 'temporarily_not_available',
                                                       'deactivated_by_driver','ready','driver_override','warning','partial_braking',
                                                       'partial_braking_icb', 'partial_braking_ssb', 'emergency_braking', 'emergency_braking_icb',
                                                       'emergency_braking_ssb', 'error'))
