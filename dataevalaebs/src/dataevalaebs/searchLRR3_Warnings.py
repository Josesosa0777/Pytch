import interface
import viewWarnings

DefParam = interface.NullParam

class cLRR3_Warnings(interface.iSearch):
  def search(self, Param):
    Batch = self.get_batch()
    Source = self.get_source('main')
    Reports = Source.findEvents(viewWarnings.ACOs+viewWarnings.REPs, 10.0)
    for Report in Reports:
      Batch.add_entry(Report, self.NONE)
    pass
