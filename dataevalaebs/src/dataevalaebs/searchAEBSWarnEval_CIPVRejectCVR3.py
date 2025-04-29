from collections import OrderedDict

import numpy

import interface
import measproc
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList
from measproc.relations import greater, less, equal
from measproc.Object import rescaleObjects
from aebs.sdf.assoOHL import AssoOHL
from measparser.signalgroup import SignalGroupList

DefParam = interface.NullParam

FUS_OBJ_NUM = 32

CVR3_FUSSignalTemplates = OrderedDict([
  ('dLength', 'length duty'),
  ('dVarYvBase', 'dy var duty'),
  ('wConstElem', 'infrastruct prob duty'),
  ('qClass', 'classif quality duty'),
  ('wClassObstacle', 'obstacle prob duty'),
  ('wClassObstacleNear', 'near obstacle prob duty'),
])

cvr3SignalGroups = []
for device in 'MRR1plus', 'RadarFC':
  signalGroupList = []
  for i in xrange(FUS_OBJ_NUM):
    signalGroup = {
      'ohl2fus': (device, 'fus_asso_mat.LrrObjIdx.i%d' % i),
    }
    for alias in CVR3_FUSSignalTemplates:
      signalGroup[alias] = device, 'fus.ObjData_TC.FusObj.i%d.%s' % (i, alias)
    signalGroupList.append(signalGroup)
  cvr3SignalGroups.append(signalGroupList)

signalGroupList = []
for i in xrange(FUS_OBJ_NUM):
  signalGroupList.append({
    'ohl2fus': ("ECU", 'fus_asso_mat.LrrObjIdx.i%d' % i)
  })
cvr2SignalGroups = [signalGroupList]


SIT_INTRO_OBJECTLIST_LEN = 6

class cSearch(interface.iSearch):
  dep = 'fillLRR3_FUS@aebs.fill', 'searchAEBSWarnEval_CVR2Warnings',\
        'searchAEBSWarnEval_CVR3Warnings'
  def check(self):
    Source = self.get_source('main')
    cvr3Group = SignalGroupList.from_first_allvalid(cvr3SignalGroups, Source)
    cvr2Group = SignalGroupList.from_first_allvalid(cvr2SignalGroups, Source)
    return cvr2Group, cvr3Group

  def fill(self, cvr2Group, cvr3Group):
    Modules = self.get_modules()

    time, cvr2WarningIntervals, cvr2DominantHandles = \
    Modules.fill('searchAEBSWarnEval_CVR2Warnings')[:3]
    cvr3WarningIntervals, cvr3DominantHandles = \
    Modules.fill('searchAEBSWarnEval_CVR3Warnings')[1:3]

    warningIntervals = {
      'CVR2': cvr2WarningIntervals,
      'CVR3': cvr3WarningIntervals,
    }

    timeCVR2_FUS, fusObjectsCVR2  = Modules.fill("fillLRR3_FUS@aebs.fill")
    objects = rescaleObjects(fusObjectsCVR2, timeCVR2_FUS, time)
    return time, cvr2Group, cvr3Group, warningIntervals, cvr2DominantHandles,\
           objects

  def search(self, param, time, cvr2Group, cvr3Group, warningIntervals,
             dominantHandles, objects):
    Source = self.get_source('main')
    CVR2n3_AssoObj = AssoOHL(Source, reliabilityLimit=0.4)
    CVR2n3_AssoObj.calc()

    cvr3_data = cvr3Group.get_values(CVR3_FUSSignalTemplates, ScaleTime=time)
    cvr3_ohl2fus = cvr3Group.get_value('ohl2fus', ScaleTime=time)

    cvr2_ohl2fus = cvr2Group.get_value('ohl2fus', ScaleTime=time)

    batch = self.get_batch()
    duty_quas = 'target'
    names = batch.get_quanamegroups(duty_quas)
    detect_votes = 'OHY object detection'
    fus_votes = 'FUS object'
    test_votes = 'AEBS algo'
    votes = batch.get_labelgroups(detect_votes, fus_votes, test_votes)

    intervals = cIntervalList(time)
    report = Report(intervals, 'AEBS-NoCVR3Warnings', names=names, votes=votes)

    cvr2_tests = set(warningIntervals['CVR2'])
    for test in cvr2_tests.intersection(warningIntervals['CVR3']):
      NoCVR3 = len(warningIntervals['CVR3'][test])
      NoCVR2 = len(warningIntervals['CVR2'][test])
      if NoCVR3 >= NoCVR2: continue

      for interval in warningIntervals['CVR2'][test]:
        start, end = interval

        intros1 = calc_cvr2_ohl_intros1(Source, objects, cvr2_ohl2fus,
                                        dominantHandles[test][interval],
                                        time, start, end)
        asso_index = numpy.searchsorted(CVR2n3_AssoObj.scaleTime, time[start])
        ohl_ids = calc_cvr3_ohl_ids(intros1,
                                    CVR2n3_AssoObj.objectPairs[asso_index])

        # using the association list, acquire the data that explains why CVR3
        # has not given a warning for the object that has triggered one in CVR2
        for ohl_id in ohl_ids:
          # it iterates through CVR3 FUS objects!!
          for fus_idx, (data, asso)  in enumerate(zip(cvr3_data, cvr3_ohl2fus)):
            if ohl_id not in asso[start:end]: continue

            idx = report.addInterval(interval)
            report.vote(idx, fus_votes, str(fus_idx))
            report.vote(idx, test_votes, test)
            for name,                 relation, threshold in [
               ('dLength',            less,     1.0),
               ('dVarYvBase',         greater,  0.5),
               ('wConstElem',         greater,  0.003),
               ('qClass',             less,     0.7),
               ('wClassObstacle',     less,     0.5),
               ('wClassObstacleNear', less,     0.7),
              ]:
              qua_name = CVR3_FUSSignalTemplates[name]
              qua = calc_duty(data[name], relation, threshold, start, end)
              report.set(idx, duty_quas, qua_name, qua)
        idx = report.addInterval(interval)
        vote = 'yes' if ohl_ids else 'no'
        report.vote(idx, detect_votes, vote)
      batch.add_entry(report, tags=['CVR3'])
    return


def calc_cvr3_ohl_ids(s1_ohl_ids, object_pairs):
  """
  select CVR3 OHL ID's that were associated with CVR2 OHL objects which have got
  into S1
  """
  cvr3_ohl_ids = [cvr3_ohl_id
                  for cvr2_ohl_id, cvr3_ohl_id in object_pairs
                  if  cvr2_ohl_id in s1_ohl_ids]
  cvr3_ohl_ids = set(cvr3_ohl_ids)
  return cvr3_ohl_ids


def calc_cvr2_ohl_intros1(source, objects, assocs, dominant, time, start, end):
  activities = cIntervalList(time)
  activities.add(start, end)
  cvr2_ohl_intros1 = []
  for obj, assoc in zip(objects, assocs):
    dom_fus_intervals = cIntervalList.fromMask(time, obj['id'] == dominant)
    dom_fus_intervals = dom_fus_intervals.intersect(activities)

    diff_ohlfus = numpy.zeros_like(assoc)
    diff_ohlfus[:-1] = numpy.diff(assoc)

    ohl_fus_intervals = source.compare(time, diff_ohlfus, equal, 0)
    ohl_fus_intervals = dom_fus_intervals.intersect(ohl_fus_intervals)
    if ohl_fus_intervals:
      dom_idx = ohl_fus_intervals[0][0]
      cvr2_ohl_intros1.append(assoc[dom_idx])
  return cvr2_ohl_intros1


def calc_duty(value, relation, threshold, start, end):
  value = value.flatten()[start:end]
  duty_cycle = numpy.count_nonzero(relation(value, threshold))
  duty_percent = 1.0 * duty_cycle / value.size
  return duty_percent

