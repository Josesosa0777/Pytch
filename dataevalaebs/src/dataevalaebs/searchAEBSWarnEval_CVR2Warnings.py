import sys

import numpy

import interface
import measproc
from aebs.proc import calcAEBSDeceleration, calcAEBSActivity, calcASFActivity
from measproc.Object import rescaleObjects
from measproc.report2 import Report
from measproc.Object import getObjects
from measproc.IntervalList import cIntervalList
from measparser.signalgroup import SignalGroupError, SignalGroup

DefParam = interface.NullParam

class cSearch(interface.iSearch):
  sensorSignalGroups = [
    {
      "vx_ego": ("ECU", "evi.General_TC.vxvRef"),
      "ax_ego": ("ECU", "evi.General_TC.axvRef"),
      "ay_ego": ("ECU", "evi.General_TC.ayvRef"),
      "YR_ego": ("ECU", "evi.General_TC.psiDtOpt"),
    },
  ]
  onlineWarningGroups = [
    {
      "repPreStatus": ("ECU", "repprew.__b_Rep.__b_RepBase.status"),
    },
  ]
  canSignalGroups = [
    {
      "BPAct_b": ("ECU", "namespaceSIT._.Egve._.BPAct_b"),
      "GPPos_uw": ("ECU", "namespaceSIT._.Egve._.GPPos_uw"),
    },
  ]

  dep = 'fillLRR3_POS@aebs.fill', 'fillLRR3_FUS@aebs.fill'

  sensor = 'CVR2'
  s1Label = 'LRR3_SameLane_near'
  idx_vote_group = 'FUS object'
  cipvIndexDefault = 1
  cipvIndexKBAvoidance = cipvIndexDefault
  test_name = 'CVR2 Warning'

  tests = {
    'Mitigation20':     20.0 / 3.6,
    'Mitigation10':     10.0 / 3.6,
    'KB AEBS':           0.0,
    'Avoidance':        None,
  }
  a_e_threshold = 5.0

  def check(self):
    Source = self.get_source('main')
    SensorSignalGroup = SignalGroup.from_first_valid(self.sensorSignalGroups,
                                                     Source)
    CANSignalGroup = SignalGroup.from_first_valid(self.canSignalGroups, Source)
    return SensorSignalGroup, CANSignalGroup

  def fill(self, SensorSignalGroup, CANSignalGroup):
    Batch = self.get_batch()
    Source = self.get_source('main')
    Modules = self.get_modules()

    time, posObjects = Modules.fill(self.dep[0])

    sensordata = self.calc_sensordata(SensorSignalGroup, time)

    try:
      OnlineWarningGroup = Source.selectSignalGroup(self.onlineWarningGroups)
    except SignalGroupError:
      print >> sys.stderr, "No data for %s online warning." % (self.sensor)
    else:
      sensordata.update(OnlineWarningGroup.get_all_values(ScaleTime=time))

    sensordata.update(CANSignalGroup.get_all_values(ScaleTime=time))

    self.set_calced_accel(time, sensordata)


    activities = {}
    activities[self.test_name] = self.calc_activity(sensordata)

    posObj, = getObjects(posObjects, label=self.s1Label)
    intros1Mask = self.get_intros1_mask(posObjects)
    activities['KB ASF Avoidance'] = calc_kb_asf_avoidance(sensordata,
                                                           posObj, intros1Mask)
    for testname, vel_reduc in self.tests.iteritems():
      a_e, regu_viol,TTC_em = \
      calcAEBSDeceleration(posObj["dx"], posObj["vx"], posObj['stand'],
                           sensordata['vx_ego'], v_red=vel_reduc)
      activities[testname] = calcAEBSActivity(a_e, self.a_e_threshold)

    warnings = {}
    dominantHandles = {}
    for testname, activity in activities.iteritems():
      if activity is None: continue

      actives = cIntervalList.fromMask(time, activity)
      actives = actives.merge(2.0)
      warnings[testname] = actives

      dominantHandles[testname] = calc_dominant_handles(actives, posObj["id"])

    return time, warnings, dominantHandles, sensordata

  def search(self, param, time, warnings, dominantHandles, sensordata):
    Batch = self.get_batch()
    Modules = self.get_modules()

    time, posObjects = Modules.fill(self.dep[0])
    fustime, fusObjects = Modules.fill(self.dep[1])
    fusObjects = rescaleObjects(fusObjects, fustime, time)

    ego_quas = 'ego vehicle'
    target_quas = 'target'
    names = Batch.get_quanamegroups(ego_quas, target_quas)
    moving_votes = 'moving state'
    test_votes = 'AEBS algo'
    votes = Batch.get_labelgroups(moving_votes, self.idx_vote_group, test_votes)
    intervals = cIntervalList(time)
    report = Report(intervals, 'AEBS-warning', names=names, votes=votes)

    for testname, warning in warnings.iteritems():
      dominantHandle = dominantHandles[testname]
      for interval in warning:
        idx = report.addInterval(interval)
        report.vote(idx, test_votes, testname)

        start, end = interval
        report.set(idx, ego_quas, 'speed', sensordata['vx_ego'][start])
        report.set(idx, ego_quas, 'yaw rate', sensordata['YR_ego'][start])
        self.set_accel_quantities(report, idx, ego_quas, start, sensordata)

        if testname == 'KB ASF Avoidance':
          cipvIndex = self.cipvIndexKBAvoidance
        else:
          cipvIndex = self.cipvIndexDefault
        obj = posObjects[cipvIndex]

        report.set(idx, target_quas, 'dx start', obj['dx'][start])
        report.set(idx, target_quas, 'dy start', obj['dy'][start])
        report.set(idx, target_quas, 'vx start', obj['vx'][start])

        vote = 'stationary' if obj['stand'][start] else 'moving'
        report.vote(idx, moving_votes, vote)

        try:
          handle = self.get_handle(fusObjects, dominantHandle, interval)
        except ValueError:
          pass
        else:
          report.vote(idx, self.idx_vote_group, str(handle))

    Batch.add_entry(report, tags=[self.sensor])
    return

  def get_intros1_mask(self, objects):
    obj, = getObjects(objects, label=self.s1Label)
    mask = numpy.ones_like(obj['id'], dtype=bool)
    return mask

  def set_accel_quantities(self, report, idx, ego_quas, start, data):
    report.set(idx, ego_quas, 'acceleration', data['ax_ego'][start])
    report.set(idx, ego_quas, 'lateral acceleration', data['ay_ego'][start])
    return

  def get_handle(self, objects, handles, interval):
    start, end = interval
    for handle, obj in enumerate(objects):
      if numpy.any(obj['id'][start:end] == handles[interval]): break
    else:
      raise ValueError('No handle id have been found')
    return handle

  def set_calced_accel(self, time, data):
    return

  def calc_activity(self, data):
    if 'repPreStatus' in data:
      activity = data['repPreStatus'] == 6
    else:
      activity = None
    return activity

  def calc_sensordata(self, signalgroup, time):
    sensordata = signalgroup.get_all_values(ScaleTime=time)
    return sensordata

def calc_kb_asf_avoidance(data, obj, intros1_mask):
  ego ={}
  ego['vx']    = data['vx_ego']
  ego['ax']    = data['ax_ego']
  ego['BPact'] = data['BPAct_b']
  ego['GPPos'] = data['GPPos_uw']

  obs = {}
  obs['dx']   =  obj["dx"]
  obs['vRel'] =  obj["vx"]
  obs['aRel'] =  obj["ax"]
  obs['dy']   =  obj["dy"]
  obs['vy']   =  obj["vy"]
  obs['MotionClassification'] = numpy.where(obj['stand'], 3, 1)

  par = {}
  par['tWarn']                  =   0.6
  par['tPrediction']            =   0.8
  par['P_aStdPartialBraking']   =  -3.0
  par['P_aEmergencyBrake']      =  -5.0
  par['P_aGradientBrake']       = -10.0
  par['dxSecure']               =   2.5
  par['dyminComfortSwingOutMO'] =   3.0
  par['dyminComfortSwingOutSO'] =   3.0
  par['P_aComfortSwingOut']     =   1.0

  activity = calcASFActivity(ego, obs, par)
  activity = numpy.logical_and(activity, intros1_mask)
  return activity

def calc_dominant_handles(actives, ids):
  handles = {}
  for interval in actives:
    start, end = interval
    handles[interval] = calc_dominant_handle(ids[start:end])
  return handles

def calc_dominant_handle(handles):
  """
  get the most dominant handle ID (i.e. with the longest existence as same
  lane near) corresponding to an interval
  """
  handle_cnt = numpy.bincount(handles)
  dominant_handle = handle_cnt.argmax()
  return dominant_handle

