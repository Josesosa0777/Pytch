import os

import interface

DefParam = interface.NullParam

class cAnalyze(interface.iAnalyze):
  def analyze(self, Param):
    Batch = self.get_batch()
    Group = set()
    for Title in "AEBS-activity-CVR3-city-CVR3Warning", "AEBS-activity-CVR3-highway-CVR3Warning", "AEBS-activity-CVR3-rural-CVR3Warning":
      TitleGroup = Batch.filter(title=Title, class_name="dataevalaebs.searchAEBSWarnEval_CVR3Warnings.cSearch")
      Group.update(TitleGroup)
    BatchNav = self.get_batchnav()
    BatchNav.BatchFrame.addEntries(Group)
    pass

