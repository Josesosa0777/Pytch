# -*- dataeval: init -*-

from interface import iCalc

sgs = [
  {"NumOfDetectionsTransmitted" : {"MBM_TARGET_DETECTION_HEADER", "NumOfDetectionsTransmitted"},},
]

class cFill(iCalc):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    commonTime = group.get_time('NumOfDetectionsTransmitted')
    return commonTime
