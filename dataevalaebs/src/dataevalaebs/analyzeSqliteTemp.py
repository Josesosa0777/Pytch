import interface

DefParam = interface.NullParam

class cAnalyze(interface.iAnalyze):
  def analyze(self, param):
    entryids = interface.Batch.filter(type='measproc.Report')
    interface.BatchNav.BatchFrame.addEntries(entryids)
    return

