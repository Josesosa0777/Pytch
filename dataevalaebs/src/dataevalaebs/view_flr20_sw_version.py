# -*- dataeval: init -*-

from collections import OrderedDict

from interface import iView

sgs = [OrderedDict([
  ("SWcharVer1", ("General_radar_status", "software_version_char_1")),
  ("SWcharVer2", ("General_radar_status", "software_version_char_2")),
  ("SWcharVer3", ("General_radar_status", "software_version_char_3")),
  ("SWcharVer4", ("General_radar_status", "software_version_char_4")),
  ("SWcharVer5", ("General_radar_status", "software_version_char_5")),
  ("SWcharVer6", ("General_radar_status", "software_version_char_6")),
  ("SWcharVer7", ("General_radar_status", "software_version_char_7")),
  ("SWcharVer8", ("General_radar_status", "software_version_char_8")),
])]

class View(iView):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group
  
  def fill(self, group):
    version_str = "".join(chr(group.get_value(alias)[0]) for alias in sgs[0])
    return version_str
  
  def view(self, version_str):
    self.logger.info("FLR20 SW version: %s" % version_str)
    return
