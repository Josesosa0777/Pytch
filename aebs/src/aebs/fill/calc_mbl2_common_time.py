# -*- dataeval: init -*-

from interface import iCalc

sgs = [
  { "actual_vehicle_speed" : ("MBM_VEHICLEDATA1_r", "usVehicleSpeed"), },
]

class cFill(iCalc):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    commonTime = group.get_time('actual_vehicle_speed')
    return commonTime
