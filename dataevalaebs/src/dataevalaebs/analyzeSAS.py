import interface
import os

DefParam = interface.NullParam

class cAnalyze(interface.iAnalyze):
  def analyze(self, Param):
    Batch = self.get_batch()
    EntryIds = Batch.filter(title="CVR3 Intro - Same Approach Stationary (SAS)",
                            result='passed')
    BatchNav = self.get_batchnav()
    BatchNav.BatchFrame.addEntries(EntryIds)
    pass

