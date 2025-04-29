import numpy

import interface
import measproc
import aebs
from aebs.par import grouptypes
import numpy

def calcAebsWarning():
  #TODO Implementation
  return

def calcAebsPartialBraking():
  #TODO Implementation
  return

def calcAebsEmergencyBraking():
  #TODO Implementation
  return


mrr1SignalGroup = {"vx_ego": ("MRR1plus", "evi.General_TC.vxvRef")}
signalGroups = [mrr1SignalGroup]

class cParameter(interface.iParameter):
  def __init__(self, a_e_threshold):
    self.a_e_threshold = a_e_threshold
    self.genKeys()
    pass

# instantiation of module parameters
EMER_DECEL_30 = cParameter(3.0)
EMER_DECEL_35 = cParameter(3.5)
EMER_DECEL_40 = cParameter(4.0)
EMER_DECEL_45 = cParameter(4.5)
EMER_DECEL_50 = cParameter(5.0)
EMER_DECEL_55 = cParameter(5.5)
EMER_DECEL_60 = cParameter(6.0)
EMER_DECEL_65 = cParameter(6.5)
EMER_DECEL_70 = cParameter(7.0)
EMER_DECEL_75 = cParameter(7.5)
EMER_DECEL_80 = cParameter(8.0)

class cSearchAebsWarningsSim(interface.iSearch):
  dep = 'fillAC100_POS@aebs.fill', 'fillCVR3_POS@aebs.fill'
  def check(self):
    Source = self.get_source('main')
    signalGroup = Source.selectSignalGroup(signalGroups)
    return signalGroup

  def fill(self, group):
    Modules = self.get_modules()
    timeAC100, posObjectsAC100 = Modules.fill("fillAC100_POS@aebs.fill")
    timeCVR3, posObjectsCVR3  = Modules.fill("fillCVR3_POS@aebs.fill")
    return group, timeAC100, posObjectsAC100, timeCVR3, posObjectsCVR3

  def search(self, param, group, timeAC100, posObjectsAC100, timeCVR3, posObjectsCVR3):
    Source = self.get_source('main')
    Batch = self.get_batch()

    egoSpeedAC100 = Source.getSignalFromSignalGroup(group, 'vx_ego', ScaleTime=timeAC100)[1]  # m/s
    egoSpeedCVR3  = Source.getSignalFromSignalGroup(group, 'vx_ego', ScaleTime=timeCVR3)[1]   # m/s

    for obj in posObjectsAC100:
      if obj["label"] == 'ACC':
        stat = numpy.where(obj["type"] == grouptypes.AC100_STAT, True, False)
        a_e, regu_viol,TTC_em = aebs.proc.calcAEBSDeceleration(obj["dx"], obj["vx"], stat, egoSpeedAC100)
        activity = aebs.proc.calcAEBSActivity(a_e, param.a_e_threshold)
        activeIntervals = Source.compare(timeAC100, activity, measproc.equal, True)
        result = self.PASSED if activeIntervals else self.FAILED
        report = measproc.cIntervalListReport(activeIntervals, "AEBS_activity_AC100_aem=%f" % (param.a_e_threshold))
        Batch.add_entry(report, result)
        break

    for obj in posObjectsCVR3:
      if obj["label"] == 'SameLane_near':
        stat = numpy.where(obj["type"] == grouptypes.CVR3_POS_STAT, True, False)
        a_e, regu_viol,TTC_em = aebs.proc.calcAEBSDeceleration(obj["dx"], obj["vx"], stat, egoSpeedCVR3)
        activity = aebs.proc.calcAEBSActivity(a_e, param.a_e_threshold)
        activeIntervals = Source.compare(timeCVR3, activity, measproc.equal, True)
        result = self.PASSED if activeIntervals else self.FAILED
        report = measproc.cIntervalListReport(activeIntervals, "AEBS_activity_CVR3_aem=%f" % (param.a_e_threshold))
        Batch.add_entry(report, result)
        break
    return

