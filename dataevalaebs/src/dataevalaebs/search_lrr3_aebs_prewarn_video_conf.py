import numpy

import interface
import measproc
from searchReactionPatterns import STATUS_LOCKED

defParam = interface.NullParam

signalGroup = {'prewarning'      : ('ECU', 'repprew.__b_Rep.__b_RepBase.status'),
               'video confirmed' : ('ECU', 'csi.4AsfSysCondBc_TC.sysCondBcFlags.sysCondBcFlags.ObjConfirmedByVideo_b'),
              }
signalGroups = [signalGroup,]

extraVotes = ('confirmed', 'suppressed')

class cSearch(interface.iSearch):
  def check(self):
    group = interface.Source.selectSignalGroup(signalGroups)
    return group
  
  def fill(self, group):
    return group

  def search(self, param, group):
    # prepare report attributes
    title = 'LRR3 prewarning video confirmation'
    # get signals
    tctime, prewarning = interface.Source.getSignalFromSignalGroup(group, 'prewarning')  
    _,      videoConf  = interface.Source.getSignalFromSignalGroup(group, 'video confirmed')
    # create intervals
    intervals = interface.Source.compare(tctime, prewarning, measproc.equal, STATUS_LOCKED)
    result = self.PASSED if intervals else self.FAILED
    # create report
    report = measproc.cIntervalListReport(intervals, title)
    report.addVotes(extraVotes)
    # set votes according to video confirmation
    for interval in intervals:
      start,end = interval
      if numpy.any(videoConf[start:end]):
        report.vote(interval, 'confirmed')
      else:
        report.vote(interval, 'suppressed')
    interface.Batch.add_entry(report, result)
    return
