# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

from primitives.bases import Primitive
from aebs.fill import calc_mbl2_raw_targets
from pyutils.functional import cached_attribute


#signals  Template
#MBM_TRACKS_XY_01_r
#       |  Track1_ID_XY_01_r      The track index indicates the number of the track, these values belong .
#       |  Track1_Flags_XY_01_r
#       |  Track1_sixPos         m        The position of the object in the ISO-coordinate system.
#       |  Track1_siyPos         m        The position of the object in the ISO-coordinate system.
#       |  Track1_V_X            m/s      The component of the speed in the ISO-coordinate system
#       |  Track1_V_Y            m/s      The component of the speed in the ISO-coordinate system
#MBM_TRACKS_CC_01_r
#       |  Track1_ID_CC_01_r              The track index indicates the number of the track, these values belong .
#       |  Track1_Flags_CC_01_r
#       |  Track1_latPos         m        The lateral coordinate in relation to the road curvature.
#       |  Track1_longPos        m        The longitudinal coordinate in relation to the road curvature.
#       |  Track1_TTC            s        The time to collison of the tracked object.
#       |  Track1_TTC_Threshold  m        The time to collision threshold which depends on the relative speed between the host and the target vehicle.

#MBM_TRACKS_XY_HEADER_r
#       |  uiTypeVersion_XY_HEADER_r        Only used for VRS internal testing.
#       |  uiMCC_XY_HEADER_r                The MBH sensor device internal major cycle counter.
#       |  ucNumOfTracks_XY_HEADER_r        The number of tracks detected by the MBH sensor device.
#       |  usFlags_XY_HEADER_r
#       |  usReserved_XY_HEADER_r


class Mbl2Track(Primitive):
  # transformation from reference coordinate frame to sensor's internal frame
  dx0 =  2.8
  dy0 = -2.6
  angle0 = np.deg2rad(25.0)

  def __init__(self, time, id, dx, dy, vx, vy, ttc):
    Primitive.__init__(self, time)
    self.id = id
    self._range_raw = np.sqrt(np.square(dx) + np.square(dy))
    self._angle_raw = np.arcsin(dy/self._range_raw)
    self.dx = self.transform_dx(dx, dy)
    self.dy = self.transform_dy(dx, dy)
    self.vx = vx
    self.vy = vy
    self.ttc = ttc
    return

  def transform_dx(self, dx, dy):
    return np.sign(dx) * np.cos(self._angle_raw + self.angle0) * self._range_raw + self.dx0

  def transform_dy(self, dx, dy):
    return -np.sign(dy) * np.sin(self._angle_raw + self.angle0) * self._range_raw + self.dy0

  @cached_attribute
  def range(self):
    return np.sqrt(np.square(self.dx) + np.square(self.dy))

  @cached_attribute
  def range_rate(self):
    return (self.dx*self.vx + self.dy*self.vy) / self.range

  @cached_attribute
  def angle(self):
    return np.arctan2(self.dy, self.dx)


class Calc(calc_mbl2_raw_targets.Calc):
  obj_factory = Mbl2Track
  n_obj_sig_def = ("MBM_TRACKS_XY_HEADER_r", "ucNumOfTracks_XY_HEADER_r")
  sgs_template = {
    "id": ("MBM_TRACKS_XY_%(k)02d_r", "Track%(k)d_ID_XY_%(k)02d_r"),
    "dx": ("MBM_TRACKS_XY_%(k)02d_r", "Track%(k)d_sixPos"),
    "dy": ("MBM_TRACKS_XY_%(k)02d_r", "Track%(k)d_siyPos"),
    "vx": ("MBM_TRACKS_XY_%(k)02d_r", "Track%(k)d_V_X"),
    "vy": ("MBM_TRACKS_XY_%(k)02d_r", "Track%(k)d_V_Y"),
    "ttc": ("MBM_TRACKS_CC_%(k)02d_r", "Track%(k)d_TTC"),
  }
