# -*- dataeval: init -*-

import numpy as np

import interface
from primitives.bases import Primitive
from pyutils.functional import cached_attribute

init_params = {  # coordinates of the ego vehicle when touching the point
  'boxberg_2014-03-20': dict(point_lat=2967.042, point_lon=-578.392),
}

class VBoxObject(Primitive):
  def __init__(self, time, **attrs):
    Primitive.__init__(self, time)
    for attr_name, attr_value in attrs.iteritems():
      setattr(self, attr_name, attr_value)
    return
  
  @cached_attribute
  def dx(self):
    return self.range * np.cos(self.angle)
  
  @cached_attribute
  def dy(self):
    return self.range * np.sin(self.angle)
  
  @cached_attribute
  def ttc(self):
    return -self.dx/self.vx

class Calc(interface.iCalc):
  dep = 'calc_vbox_egopath',
  
  def init(self, point_lat, point_lon):
    self.point_lat = point_lat
    self.point_lon = point_lon
    return
  
  def check(self):
    sgs = [
      {"speed": ("EBC2_BS", "FA_Spd_Cval")},
      {"speed": ("VBOX_2", "Velocity_kmh")},
    ]
    group = self.source.selectSignalGroup(sgs)
    return group
  
  def fill(self, group):
    # ego
    ego_path = self.modules.fill(self.dep[0])
    
    # point
    point_lat_rad = np.deg2rad(self.point_lat/60.0)
    point_lon_rad = np.deg2rad(self.point_lon/60.0)
    point_dx = point_lat_rad * 6371000.0
    point_dy = point_lon_rad * 6371000.0 * np.cos(point_lat_rad)  # TODO: check why not *(-1)
    
    # point relative to ego
    range_ = np.sqrt((point_dx-ego_path.dx)**2.0 + (point_dy-ego_path.dy)**2.0)
    angle = np.arctan2(point_dy-ego_path.dy, point_dx-ego_path.dx) - ego_path.heading  # TODO: dir corr as above
    vx = -1.0 * group.get_value('speed', ScaleTime=ego_path.time) / 3.6
    
    obj = VBoxObject(ego_path.time, range=range_, angle=angle, vx=vx)
    return obj
