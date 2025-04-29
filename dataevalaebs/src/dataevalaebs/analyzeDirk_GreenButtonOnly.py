import os

import interface

DefParam = interface.NullParam

class cAnalyze(interface.iAnalyze):
  def analyze(self, Param):
    Batch = self.get_batch()
    EntryIds = Batch.filter(title='DFMgreenbutton', result='passed')
    BatchNav = self.get_batchnav()
    BatchNav.BatchFrame.addEntries(EntryIds)
    pass

