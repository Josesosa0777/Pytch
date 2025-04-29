import numpy as np

import interface
import measproc
import aebs.fill

DefParam = interface.NullParam

SignalGroups = [{'FakePO0': ('ECU','fos_internal_states_pri.FakePO0')}]

class cSearch(interface.iSearch):
  dep = 'fillLRR3_ATS@aebs.fill', 'fillCVR3_ATS@aebs.fill'
  def check(self):
    Source = self.get_source('main')
    Group = Source.selectSignalGroup(SignalGroups)
    return Group

  def fill(self, Group):
    Source = self.get_source('main')
    Modules = self.get_modules()
    Reports = []
    for Status in self.dep:
      scaletime, Objects = Modules.fill(Status)
      Objects = Objects[:len(Objects)-1]
      intervallist = measproc.cIntervalList(scaletime)
      len_scaletime = len(scaletime)
      len_objects = len(Objects)
      ids = np.zeros((len_objects, len_scaletime))
      for i in xrange(len_objects):
        ids[:][i] = Objects[i]["id"]

      startindex = 0
      found_last_step = False
      for x in xrange(len_scaletime):
        if len(np.unique(ids[:,x][ids[:,x]!=0]))<len(ids[:,x][ids[:,x]!=0]):
          found_last_step = True
        elif found_last_step:
          found_last_step = False
          intervallist.add(startindex,x)
        else:
          startindex = x

      Name = Status[4:8]
      Report = measproc.cIntervalListReport(intervallist, Title="SameHandle%s" %Name)
      Reports.append(Report)

      time, value  = Source.getSignalFromSignalGroup(Group,'FakePO0', ScaleTime=scaletime)
      Intervallist = measproc.EventFinder.cEventFinder.compExtSigScal(time, value, measproc.greater, 0)
      Report = measproc.cIntervalListReport(Intervallist, Title="FakePO%s" %Name)
      Reports.append(Report)

    return Reports

  def search(self, Param, Reports):
    Batch = self.get_batch()
    for Report in Reports:
      interface.Batch.add_entry(Report, self.NONE)
    pass
