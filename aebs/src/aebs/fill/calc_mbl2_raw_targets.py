# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

from primitives.bases import Primitive, PrimitiveCollection
from interface import iCalc
from pyutils.functional import cached_attribute
from measparser.signalgroup import SignalGroupError


#Signals in CAN channel
#CAN 2 MBM_TARGET_DETECTION_01_r
#      Range_01_r        m       The range is the radial distance between the sensor surface and the point of detection.
#      Velocity_01_r     m/s     The velocity is the radial velocity of the detection.
#      Azimuth_01_r      Degree  The azimuth is the azimuth angle of the detection
#      Power_01_r        dB      The power is the received power from the illuminated target.
#      BeamNumber_01_r  [1]      The beam number is the number of the beam in which the detection appears

#CAN 2   MBM_TARGET_DETECTION_HEADER_r
#      SPIP_mcc_curr_r
#      ucNumOfDetectonsInternal_r
#      ucNumOfDetectionsTransmitted_r


class Mbl2Target(Primitive):
  # sensor position & orientation in reference coordinate frame
  dx0 = -1.8
  dy0 = -1.275
  angle0 = np.deg2rad(-90.0)
  
  def __init__(self, time, id, range, range_rate, angle_deg, power):
    Primitive.__init__(self, time)
    self._range_raw = range
    self._angle_raw = angle_deg
    
    self.angle = self.transf_angle(angle_deg)
    self.dx = self.transf_dx(range)
    self.dy = self.transf_dy(range)
    self.range = self.transf_range()
    
    self.range_rate = range_rate
    self.power = power
    self.id = id
    return
  
  def transf_dx(self, dist):
    return dist * np.cos(self.angle) + self.dx0
  
  def transf_dy(self, dist):
    return dist * np.sin(self.angle) + self.dy0
  
  def transf_range(self):
    return np.sqrt(np.square(self.dx) + np.square(self.dy))
  
  def transf_angle(self, angle_deg):
    return np.deg2rad(angle_deg) + self.angle0 - np.pi/2.0
  
  def transform_dist(self, distance):
    return distance + self.dx0/np.cos(self.angle)
  
  @cached_attribute
  def vx(self):
    angle_rate = 0.0  # approximation
    return self.range_rate*np.cos(self.angle) - self.range*np.sin(self.angle)*angle_rate
  
  @cached_attribute
  def vy(self):
    angle_rate = 0.0  # approximation
    return self.range_rate*np.sin(self.angle) + self.range*np.cos(self.angle)*angle_rate


class Calc(iCalc):
  obj_factory = Mbl2Target
  n_obj_sig_def = ("MBM_TARGET_DETECTION_HEADER_r", "ucNumOfDetectionsTransmitted_r")
  sgs_template = {
    'range': ('MBM_TARGET_DETECTION_%(k)02d_r', 'Range_%(k)02d_r'),
    'range_rate': ('MBM_TARGET_DETECTION_%(k)02d_r', 'Velocity_%(k)02d_r'),
    'angle_deg': ('MBM_TARGET_DETECTION_%(k)02d_r','Azimuth_%(k)02d_r'),
    'power': ('MBM_TARGET_DETECTION_%(k)02d_r','Power_%(k)02d_r'),
  }
  
  dep = 'calc_mbl2_common_time',
  
  def check(self):
    nobj_group = self.source.selectSignalGroup([{"n_objs": self.n_obj_sig_def}])
    n_objs = nobj_group.get_value("n_objs").max()
    
    groups = {}
    for k in xrange(1, n_objs+1):
      sg = {alias: (dev_name % {'k':k}, sig_name % {'k':k})
            for alias, (dev_name, sig_name) in self.sgs_template.iteritems()}
      groups[k] = self.source.selectLazySignalGroup([sg])
    return groups, n_objs
  
  def fill(self, groups, n_objs):
    common_time = self.modules.fill(self.dep[0])
    rescale_kwargs = {'ScaleTime': common_time, 'Order': 'valid'}
    objs = PrimitiveCollection(common_time)
    for k in xrange(1, n_objs+1):
      try:
        values = {alias: groups[k].get_value(alias, **rescale_kwargs)
                  for alias in self.sgs_template}
      except SignalGroupError:
        self.logger.debug("Skip %s #%d (signals not available)" %
                            (self.obj_factory.__name__, k))
        continue
      if 'id' not in values:
        arbitrary_value = values.itervalues().next()
        values['id'] = np.ma.where(arbitrary_value.mask, np.ma.masked, k)
      objs[k] = self.obj_factory(common_time, **values)
    return objs
