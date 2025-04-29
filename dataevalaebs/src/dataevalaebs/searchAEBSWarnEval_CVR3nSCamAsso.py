import numpy
import sys

import interface
import measparser
import measproc
import aebs.sdf.asso_cvr3_sCam
import aebs.sdf.asso_cvr3_sCam_cipv
import aebs.sdf.asso_cvr3_fus_result
from aebs.sdf.asso_cvr3_sCam import AssoCvr3SCam
from aebs.sdf.asso_cvr3_fus_result import AssoCvr3fusResult
from measproc.report2 import Report
from measproc.Object import rescaleObjects
from measproc.IntervalList import cIntervalList
from measparser.signalgroup import SignalGroupList, SignalGroupError

from searchAEBSWarnEval_CIPVRejectCVR3 import calc_cvr2_ohl_intros1

DefParam = interface.NullParam

FUS_OBJ_NUM = 32
cvr3DeviceNames = ('MRR1plus', 'RadarFC')
cvr3SignalGroups = []
for device in 'MRR1plus', 'RadarFC':
  signalgroups = []
  for i in xrange(FUS_OBJ_NUM):
    signalgroups.append({
      'ohl2fus': (device, 'fus_asso_mat.LrrObjIdx.i%s' % i)
    })
  cvr3SignalGroups.append(signalgroups)

class cSearch(interface.iSearch):
  dep = ('searchAEBSWarnEval_CVR3Warnings', 'fillCVR3_FUS@aebs.fill')

  def check(self):
    Source = self.get_source('main')
    cvr3Group = SignalGroupList.from_first_allvalid(cvr3SignalGroups, Source)

    # check if the necessary signal groups for AssoCvr3SCam are present
    Source.selectSignalGroup(aebs.sdf.asso_cvr3_sCam.signalGroups)
    Source.filterSignalGroups(aebs.sdf.asso_cvr3_sCam_cipv.sCamSignalGroups)
    Source.filterSignalGroups(aebs.sdf.asso_cvr3_fus_result.sgs)
    return cvr3Group

  def fill(self, cvr3Group):
    Source = self.get_source('main')
    Modules = self.get_modules()

    time,\
    cvr3WarningIntervals,\
    dominantHandles,\
    cvr3SensorData = Modules.fill('searchAEBSWarnEval_CVR3Warnings')

    fustime, fusObjects = Modules.fill('fillCVR3_FUS@aebs.fill')
    fusObjects = rescaleObjects(fusObjects, fustime, time)

    return time, cvr3Group, cvr3WarningIntervals, dominantHandles, fusObjects

  def search(self, param, time, cvr3Group, cvr3WarningIntervals,
             dominantHandles, fusObjects):
    Source = self.get_source('main')
    Batch = self.get_batch()


    OHL2FUSassoc = cvr3Group.get_value('ohl2fus', ScaleTime=time)

    cvr3SCam_AssoObj_offline = AssoCvr3SCam(Source, scaleTime=time,
                                            reliabilityLimit=0.4)
    cvr3SCam_AssoObj_offline.calc()
    try:
      cvr3SCam_AssoObj_online = AssoCvr3fusResult(Source)
    except SignalGroupError:
      print >> sys.stderr,\
      "No online S-Cam data for CVR3 and S-Cam association."
      onlinePresent = False
    else:
      onlinePresent = True
      cvr3SCam_AssoObj_online.calc()

    scaletime = cvr3SCam_AssoObj_offline.scaleTime

    test_votes = 'AEBS algo'
    votes = Batch.get_labelgroups(test_votes)
    asso_quas = 'association'
    names = Batch.get_quanamegroups(asso_quas)
    intervals = cIntervalList(time)
    report = Report(intervals, 'AEBS-CVR3ImprovBySCAM', names=names,
                    votes=votes)
    for test, intervals in cvr3WarningIntervals.iteritems():
      for interval in intervals:
        idx = report.addInterval(interval)
        report.vote(idx, test_votes, test)

        start, end = interval
        ohl_intros1 = calc_cvr2_ohl_intros1(Source, fusObjects, OHL2FUSassoc,
                                            dominantHandles[test][interval],
                                            time, start, end)
        asso_start = numpy.searchsorted(scaletime, time[start])
        asso_end = numpy.searchsorted(scaletime, time[end], side='right')
        offline_duty = calc_asso_match_duty(ohl_intros1,
                                            cvr3SCam_AssoObj_offline,
                                            asso_start, asso_end)
        report.set(idx, asso_quas, 'offline duty', offline_duty)
        if onlinePresent:
          online_duty = calc_asso_match_duty(ohl_intros1,
                                             cvr3SCam_AssoObj_online,
                                             asso_start, asso_end)
        else:
          online_duty = float('nan')
        report.set(idx, asso_quas, 'online duty', online_duty)
    Batch.add_entry(report, tags=['CVR3'])
    return

def calc_asso_match_duty(s1_ohl_ids, asso, asso_start, asso_end):
  duty = 0.0
  step = 1.0 / (asso_end - asso_start)
  for asso_id in xrange(asso_start, asso_end):
    for a, b in asso.objectPairs[asso_id]:
      if a in s1_ohl_ids:
        duty += step
        break
  return duty

