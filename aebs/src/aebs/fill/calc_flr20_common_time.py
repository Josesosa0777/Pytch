# -*- dataeval: init -*-

from interface import iCalc

sgs = [
  { "actual_vehicle_speed" : ("General_radar_status", "actual_vehicle_speed"), },
]

class cFill(iCalc):
  def check(self):
    source = self.get_source()
    group = source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    commonTime = group.get_time('actual_vehicle_speed')
    return commonTime
