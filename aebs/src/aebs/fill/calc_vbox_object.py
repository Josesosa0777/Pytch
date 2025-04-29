# -*- dataeval: init -*-

from interface import iCalc
from primitives.bases import Primitive

time_sgs = [{
  "first_in_burst": ("ADAS_VCI_T1_1", "RelSpd_tg1"),
}]
sgs = [{
  "dx": ("ADAS_VCI_T1_2", "LngRsv_tg1"),
  "dy": ("ADAS_VCI_T1_2", "LatRsv_tg1"),
  "range": ("ADAS_VCI_T1_1", "Range_tg1"),
  "range_rate": ("ADAS_VCI_T1_1", "RelSpd_tg1"),
  "ttc": ("ADAS_VCI_T1_6", "T2Csv_tg1"),
  "angle": ("ADAS_VCI_T1_4", "Angle_tg1"),
  "vx_abs": ("ADAS_VCI_T1_7", "Spd_tg1"),
  "ax_abs": ("ADAS_VCI_T1_8", "Accel_tg1"),
}]

class VBoxObject(Primitive):
  def __init__(self, time, **attrs):
    Primitive.__init__(self, time)
    for attr_name, attr_value in attrs.iteritems():
      setattr(self, attr_name, attr_value)
    return

class Calc(iCalc):
  def check(self):
    time_group = self.source.selectSignalGroup(time_sgs)
    group = self.source.selectSignalGroup(sgs)
    return time_group, group

  def fill(self, time_group, group):
    time = time_group.get_time("first_in_burst")
    rescale_kwargs = {'ScaleTime': time, 'Order': 'valid'}
    attrs = {}
    for attr_name in sgs[0].iterkeys():
      attrs[attr_name] = group.get_value(attr_name, **rescale_kwargs)
    obj = VBoxObject(time, **attrs)
    return obj
