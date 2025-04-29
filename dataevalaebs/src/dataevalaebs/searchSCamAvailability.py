import numpy

import interface
import measproc

DefParam = interface.NullParam

__type__ = 'search-2.0'

deviceNames = 'MRR1plus', 'RadarFC'

egoVelocitySG = []
for device in deviceNames:
  tmpSignalGroup = {}
  tmpSignalGroup['evi.General_TC.vxvRef'] = (device, 'evi.General_TC.vxvRef')
  egoVelocitySG.append(tmpSignalGroup)

sCamSG = [{'Refpoint_X': ('Host_Vehicle', 'Refpoint_X'),},]

class cSearch(interface.iSearch):
  def check(self):
    source = self.get_source('main')
    egoGroups = source.selectSignalGroup(egoVelocitySG)
    sCamGroups = source.filterSignalGroups(sCamSG)
    return egoGroups, sCamGroups
  
  def fill(self, egoGroups, sCamGroups):
    source = self.get_source('main')
    batch = self.get_batch()
    title = 'S-Cam availability during day and night'
    votes = batch.get_labelgroups('availability')
    
    egoVehTime, egoVehVel = source.getSignalFromSignalGroup(egoGroups, 'evi.General_TC.vxvRef')
    egoIntervalsTCTime = measproc.cIntervalList(egoVehTime)
    
    report = measproc.report2.Report(egoIntervalsTCTime, title, votes)
    
    sCamSignals = {}
    for alias in sCamGroups[0].keys():
      sCamSignals[alias] = source.getSignalFromSignalGroup(sCamGroups[0], alias)
    
    # determine camera availability intervals
    availMask = numpy.zeros_like(sCamSignals['Refpoint_X'][0])
    availMask[1:] = numpy.diff(sCamSignals['Refpoint_X'][0]) <= 0.2
    availIntervalsSCamTime = source.compare(sCamSignals['Refpoint_X'][0], availMask, measproc.not_equal, 0)
    
    # map those intervals onto TC time (egoVehTime is TC time)
    availIntervalsTCTime = measproc.cIntervalList(egoVehTime)
    for lowerSCam, upperSCam in availIntervalsSCamTime.Intervals:
      lowerTC = numpy.searchsorted(egoVehTime, sCamSignals['Refpoint_X'][0][lowerSCam])
      upperTC = numpy.searchsorted(egoVehTime, sCamSignals['Refpoint_X'][0][upperSCam-1])
      availIntervalsTCTime.add(lowerTC, upperTC)
    
    for lower, upper in availIntervalsTCTime:
      interval = (int(lower), int(upper))
      index = report.addInterval(interval)
      report.vote(index, 'availability', 'available')
    
    for lower, upper in availIntervalsTCTime.negate():
      if upper - lower == 1 and (lower == 0 or upper == availIntervalsTCTime.Time.size):
        # skip event at the very beginning or end of recording
        continue
      interval = (int(lower), int(upper))
      index = report.addInterval(interval)
      report.vote(index, 'availability', 'n/a')
    
    return report
  
  def search(self, param, report):
    batch = self.get_batch()
    result = self.FAILED if report.isEmpty() else self.PASSED
    batch.add_entry(report, result=result)
    return
  
