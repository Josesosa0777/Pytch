import numpy

import interface
import measproc
import aebs
from aebs.par import grouptypes
from aebs.sdf.assoOHL import AssoOHL

mrr1SignalGroups = [{"vx_ego": ("MRR1plus", "evi.General_TC.vxvRef"),
                     "ax_ego": ("MRR1plus", "evi.General_TC.axvRef"),
                     "ay_ego": ("MRR1plus", "evi.General_TC.ayvRef"),
                     "YR_ego": ("MRR1plus", "evi.General_TC.psiDtOpt")}]

lrr3signalgroups = [{"repprew.__b_Rep.__b_RepBase.status": ("ECU", "repprew.__b_Rep.__b_RepBase.status")}]

FUS_OBJ_NUM = 32
CVR3_FUSSignalTemplates = ('dLength', 'dVarYvBase', 'wConstElem', 'qClass', 'wClassObstacle', 'wClassObstacleNear')

for index in xrange(FUS_OBJ_NUM):
  for signaltemplate in CVR3_FUSSignalTemplates:
    mrr1SignalGroups[0]["%s_FUS%s" % (signaltemplate, index)] = ("MRR1plus", 'fus.ObjData_TC.FusObj.i%s.%s' % (index, signaltemplate))
  mrr1SignalGroups[0]['OHL_2_FUS_%s_assoc' % index] = ("MRR1plus", 'fus_asso_mat.LrrObjIdx.i%s' % index)
  lrr3signalgroups[0]['OHL_2_FUS_%s_assoc' % index] = ("ECU", 'fus_asso_mat.LrrObjIdx.i%s' % index)

canSignalGroups = [{"tot_veh_dist": ("Veh_Dist_high_Res", "tot_veh_dist"),
                    "BPAct_b":  ("EBC1_2Wab_EBS5Knorr", "EBS_Brake_switch"),
                    "GPPos_uw":  ("EEC2", "AP_position")},
                   {"tot_veh_dist": ("Veh_Dist_high_Res", "tot_veh_dist"),
                    "BPAct_b":  ("EBC1_2Wab_EBS5Knorr", "EBS_Brake_switch"),
                    "GPPos_uw":  ("EEC2-8CF00300", "AP_position")}]

visuSignalGroups = [{"Longitude": ("VBOX_2", "Longitude"),
                     "Latitude": ("VBOX_1", "Latitude"),
                     "Multimedia_1": ("Multimedia", "Multimedia_1")}]

# module parameter class creation
class cParameter(interface.iParameter):
  def __init__(self, LessWarningEval):
    self.LessWarningEval = LessWarningEval
    """:type: boole
    True if the evaluation of why CVR3 or LRR3 gave less warnings is needed else
    false.
    """
    self.genKeys()

# instantiation of module parameters
LessWarningsEvaluation = cParameter(True)
NoLessWarningsEvaluation = cParameter(False)

a_e_threshold = 5.0

class cSearchAebsWarningsAndRoadTypes(interface.iSearch):
  dep = ('fillAC100_POS@aebs.fill', 'fillCVR3_POS@aebs.fill',
        'fillLRR3_POS@aebs.fill', 'fillCVR3_FUS@aebs.fill',
        'fillLRR3_FUS@aebs.fill')
  def check(self):
    Source = self.get_source('main')
    mrr1Group = Source.selectSignalGroup(mrr1SignalGroups)
    lrr3Group = Source.selectSignalGroup(lrr3signalgroups)
    canGroup = Source.selectSignalGroup(canSignalGroups)
    visuGroup = Source.selectSignalGroup(visuSignalGroups)
    return mrr1Group, lrr3Group, canGroup, visuGroup

  def fill(self, mrr1Group, lrr3Group, canGroup, visuGroup):
    Modules = self.get_modules()
    timeAC100, posObjectsAC100 = Modules.fill("fillAC100_POS@aebs.fill")
    timeCVR3, posObjectsCVR3  = Modules.fill("fillCVR3_POS@aebs.fill")
    timeLRR3, posObjectsLRR3  = Modules.fill("fillLRR3_POS@aebs.fill")
    timeCVR3_FUS, fusObjectsCVR3  = Modules.fill("fillCVR3_FUS@aebs.fill")
    timeLRR3_FUS, fusObjectsLRR3  = Modules.fill("fillLRR3_FUS@aebs.fill")
    return mrr1Group, lrr3Group, canGroup, visuGroup, timeAC100, posObjectsAC100, timeCVR3, posObjectsCVR3, timeLRR3, posObjectsLRR3, timeCVR3_FUS, fusObjectsCVR3, timeLRR3_FUS, fusObjectsLRR3

  def search(self, param, mrr1Group, lrr3Group, canGroup, visuGroup, timeAC100, posObjectsAC100, timeCVR3, posObjectsCVR3, timeLRR3, posObjectsLRR3, timeCVR3_FUS, fusObjectsCVR3, timeLRR3_FUS, fusObjectsLRR3):
    Source = self.get_source('main')
    Batch = self.get_batch()

    LRR3CVR3_AssoObj = AssoOHL(Source, reliabilityLimit=0.4)
    LRR3CVR3_AssoObj.calc()

    TestsToRun = {'Mitigation20': 20.0 / 3.6, 'Mitigation10': 10.0 / 3.6, 'KBAEBS': 0.0, 'Avoidance': None, 'KBASFAvoidance': None, 'LRR3Warning': None}
    Labels4Eval = ['Stationary', 'Moving', 'M_Unnecessary', 'M_False detection', 'M_Other']

    egoSpeedAC100 = Source.getSignalFromSignalGroup(mrr1Group, 'vx_ego', ScaleTime=timeAC100)[1]  # m/s
    egoSpeedCVR3  = Source.getSignalFromSignalGroup(mrr1Group, 'vx_ego', ScaleTime=timeCVR3)[1]   # m/s
    egoYrCVR3     = Source.getSignalFromSignalGroup(mrr1Group, 'YR_ego', ScaleTime=timeCVR3)[1]   # m/s
    egoSpeedLRR3  = Source.getSignalFromSignalGroup(mrr1Group, 'vx_ego', ScaleTime=timeLRR3)[1]   # m/s
    egoAccelAC100 = Source.getSignalFromSignalGroup(mrr1Group, 'ax_ego', ScaleTime=timeAC100)[1]
    egoAccelCVR3 = Source.getSignalFromSignalGroup(mrr1Group, 'ax_ego', ScaleTime=timeCVR3)[1]
    egoAccelLRR3 = Source.getSignalFromSignalGroup(mrr1Group, 'ax_ego', ScaleTime=timeLRR3)[1]
    egoLatAccelAC100 = Source.getSignalFromSignalGroup(mrr1Group, 'ay_ego', ScaleTime=timeAC100)[1]
    egoLatAccelCVR3 = Source.getSignalFromSignalGroup(mrr1Group, 'ay_ego', ScaleTime=timeCVR3)[1]
    egoLatAccelLRR3 = Source.getSignalFromSignalGroup(mrr1Group, 'ay_ego', ScaleTime=timeLRR3)[1]
    totdist   = Source.getSignalFromSignalGroup(canGroup, 'tot_veh_dist', ScaleTime=timeCVR3)[1]
    BPActAC100 = Source.getSignalFromSignalGroup(canGroup, 'BPAct_b', ScaleTime=timeAC100)[1]
    BPActCVR3  = Source.getSignalFromSignalGroup(canGroup, 'BPAct_b', ScaleTime=timeCVR3)[1]
    BPActLRR3  = Source.getSignalFromSignalGroup(canGroup, 'BPAct_b', ScaleTime=timeLRR3)[1]
    GPPosAC100 = Source.getSignalFromSignalGroup(canGroup, 'GPPos_uw', ScaleTime=timeAC100)[1]
    GPPosCVR3  = Source.getSignalFromSignalGroup(canGroup, 'GPPos_uw', ScaleTime=timeCVR3)[1]
    GPPosLRR3  = Source.getSignalFromSignalGroup(canGroup, 'GPPos_uw', ScaleTime=timeLRR3)[1]
    repPreStatusLRR3 = Source.getSignalFromSignalGroup(lrr3Group, 'repprew.__b_Rep.__b_RepBase.status', ScaleTime=timeLRR3)[1]

    FUSdLengthCVR3 = {}
    FUSdVarYvBaseCVR3 = {}
    FUSwConstElemCVR3 = {}
    FUSwClassObstCVR3 = {}
    FUSwClassObstNearCVR3 = {}
    FUSqClassCVR3 = {}
    OHL2FUSassocCVR3 = {}
    OHL2FUSassocLRR3 = {}
    for index in xrange(FUS_OBJ_NUM):
      FUSdLengthCVR3[index] = Source.getSignalFromSignalGroup(mrr1Group, 'dLength_FUS%s' % index, ScaleTime=timeCVR3)[1]
      FUSdVarYvBaseCVR3[index] = Source.getSignalFromSignalGroup(mrr1Group, 'dVarYvBase_FUS%s' % index, ScaleTime=timeCVR3)[1]
      FUSwConstElemCVR3[index] = Source.getSignalFromSignalGroup(mrr1Group, 'wConstElem_FUS%s' % index, ScaleTime=timeCVR3)[1]
      FUSwClassObstCVR3[index] = Source.getSignalFromSignalGroup(mrr1Group, 'wClassObstacle_FUS%s' % index, ScaleTime=timeCVR3)[1]
      FUSwClassObstNearCVR3[index] = Source.getSignalFromSignalGroup(mrr1Group, 'wClassObstacleNear_FUS%s' % index, ScaleTime=timeCVR3)[1]
      FUSqClassCVR3[index] = Source.getSignalFromSignalGroup(mrr1Group, 'qClass_FUS%s' % index, ScaleTime=timeCVR3)[1]
      OHL2FUSassocCVR3[index] = Source.getSignalFromSignalGroup(mrr1Group, 'OHL_2_FUS_%s_assoc' % index, ScaleTime=timeCVR3)[1]
      OHL2FUSassocLRR3[index] = Source.getSignalFromSignalGroup(lrr3Group, 'OHL_2_FUS_%s_assoc' % index, ScaleTime=timeLRR3)[1]

    sensorsToEvaluate = {
      'CVR3': {
        'time': timeCVR3,
        'obj': posObjectsCVR3,
        'label': 'SameLane_near',
        'egoSpeed': egoSpeedCVR3,
        'egoAccel': egoAccelCVR3,
        'egoLatAccel': egoLatAccelCVR3,
        'BPAct': BPActCVR3,
        'GPPos': GPPosCVR3,
        'statType': grouptypes.CVR3_POS_STAT,
        'dLength_FUS': FUSdLengthCVR3,
        'dVarYvBase_FUS': FUSdVarYvBaseCVR3,
        'wConstElem_FUS': FUSwConstElemCVR3,
        'wClassObst_FUS': FUSwClassObstCVR3,
        'wClassObstNear_FUS': FUSwClassObstNearCVR3,
        'qClass_FUS': FUSqClassCVR3,
        'OHL2FUSassoc': OHL2FUSassocCVR3,
        'obj_FUS': fusObjectsCVR3},
      'AC100': {
        'time': timeAC100,
        'obj': posObjectsAC100,
        'label': 'ACC',
        'egoSpeed': egoSpeedAC100,
        'egoAccel': egoAccelAC100,
        'egoLatAccel': egoLatAccelAC100,
        'BPAct': BPActAC100,
        'GPPos': GPPosAC100,
        'statType': grouptypes.AC100_STAT},
      'LRR3': {
        'time': timeLRR3,
        'obj': posObjectsLRR3,
        'label': 'LRR3_SameLane_near',
        'egoSpeed': egoSpeedLRR3,
        'egoAccel': egoAccelLRR3,
        'egoLatAccel': egoLatAccelLRR3,
        'BPAct': BPActLRR3,
        'GPPos': GPPosLRR3,
        'statType': grouptypes.LRR3_POS_STAT,
        'repPreStatus' : repPreStatusLRR3,
        'OHL2FUSassoc': OHL2FUSassocLRR3,
        'obj_FUS': fusObjectsLRR3}}

    curvature, city, ruralRoad, highway, cityKm, ruralKm, highwayKm  = aebs.proc.calcRoadTypes(egoSpeedCVR3, egoYrCVR3, totdist, timeCVR3)

    roadtypes = measproc.cDinStatistic('AEBS_RoadType_Milages', [['RoadTypes', ['rural', 'city', 'highway']]])
    roadtypes.set([['RoadTypes','city']], cityKm)
    roadtypes.set([['RoadTypes','rural']], ruralKm)
    roadtypes.set([['RoadTypes','highway']], highwayKm)
    Batch.add_entry(roadtypes, self.NONE)

    roadtypeIntervals = {}
    for sensor, prop in sensorsToEvaluate.iteritems():
      roadtypeIntervals[sensor] = {}
      roadtypeIntervals[sensor]["city"] = Source.compare(prop['time'], Source.rescale(timeCVR3, city, prop['time'])[1], measproc.equal, True)
      roadtypeIntervals[sensor]["rural"] = Source.compare(prop['time'], Source.rescale(timeCVR3, ruralRoad, prop['time'])[1], measproc.equal, True)
      roadtypeIntervals[sensor]["highway"] = Source.compare(prop['time'], Source.rescale(timeCVR3, highway, prop['time'])[1], measproc.equal, True)

    for rtname, intervals in roadtypeIntervals['CVR3'].iteritems():
      result = self.PASSED if intervals else self.FAILED
      report = measproc.cIntervalListReport(intervals, "AEBS_RoadType_Intervals_%s" % (rtname))
      Batch.add_entry(report, result)

    activityRoadTypeIntervals = {}
    for sensor, prop in sensorsToEvaluate.iteritems():
      activityRoadTypeIntervals[sensor] = {}
      for obj in prop['obj']:
        if obj["label"] == prop['label']:
          for testname, vel_reduc in TestsToRun.iteritems():
            activityRoadTypeIntervals[sensor][testname] = measproc.cIntervalList(prop['time'])
            stat = numpy.where(obj["type"] == prop['statType'], True, False)
            activity = None
            if testname == 'LRR3Warning':
              if sensor == 'LRR3':
                activity = prop['repPreStatus'] == 6
            elif testname == 'KBASFAvoidance':
              # AEBS ASF
              ego ={}
              ego['vx']   = prop['egoSpeed']
              ego['ax']   = prop['egoAccel']
              ego['BPact']  = prop['BPAct']
              ego['GPPos']  = prop['GPPos']

              obs = {}
              obs['dx']   =  obj["dx"]
              obs['vRel'] =  obj["vx"]
              obs['aRel'] =  obj["ax"]
              obs['dy']   =  obj["dy"]
              obs['vy']   =  obj["vy"]
              obs['MotionClassification'] = numpy.where(stat, 3, 1)

              par = {}
              par['tWarn']                =   0.6
              par['tPrediction']          =   0.8
              par['P_aStdPartialBraking'] =  -3.0
              par['P_aEmergencyBrake']    =  -5.0
              par['P_aGradientBrake']     = -10.0
              par['dxSecure']             =   2.5
              par['dyminComfortSwingOutMO'] = 3.0
              par['dyminComfortSwingOutSO'] = 3.0
              par['P_aComfortSwingOut']     = 1.0

              activity = aebs.proc.calcASFActivity(ego, obs, par)
            else:
              a_e, regu_viol,TTC_em = aebs.proc.calcAEBSDeceleration(obj["dx"], obj["vx"], stat, prop['egoSpeed'], v_red=vel_reduc)
              activity = aebs.proc.calcAEBSActivity(a_e, a_e_threshold)
            if activity is not None:
              activeIntervals = Source.compare(prop['time'], activity, measproc.equal, True)
              activeIntervals = activeIntervals.merge(2.0)

              for rtname, intervals in roadtypeIntervals[sensor].iteritems():
                activityRoadType = activeIntervals.intersect(intervals)
                result = self.PASSED if activityRoadType else self.FAILED
                report = measproc.cIntervalListReport(activityRoadType, "AEBS-activity-%s-%s-%s" % (sensor, rtname, testname))
                report.addVotes(Labels4Eval)
                for interval in activityRoadType:
                  start,end = interval
                  activityRoadTypeIntervals[sensor][testname].add(start, end)
                  if numpy.any(stat[start:end]):
                    report.vote(interval, 'Stationary')
                  else:
                    report.vote(interval, 'Moving')
                Batch.addReport(report, result)
          break

    if param.LessWarningEval:
      NoWarningsData = {}
      CVR3sensorprop = sensorsToEvaluate['CVR3']
      LRR3sensorprop = sensorsToEvaluate['LRR3']
      for test in TestsToRun.keys():
        # give reason for: fewer CVR3 warnings than LRR3
        if len(activityRoadTypeIntervals['CVR3'][test]) < len(activityRoadTypeIntervals['LRR3'][test]):
          for start, end in activityRoadTypeIntervals['LRR3'][test]:
            ActivityInterval = measproc.cIntervalList(LRR3sensorprop['time'])
            ActivityInterval.add(start, end)

            starttime = timeLRR3[start]
            endtime = timeLRR3[end]

            NoWarningsData[(starttime, endtime)] = {}
            NoWarningsData[(starttime, endtime)][test] = {}

            # in LRR3, look for OHL objects that have been put to S1 element of the position matrix
            LRR3_OHL_intoS1 = []
            for obj in LRR3sensorprop['obj']:
              if obj['label'] == LRR3sensorprop['label']:
                for idx in xrange(FUS_OBJ_NUM): # it iterates through LRR3 FUS objects!!
                  mask = numpy.logical_and(obj['id'] > 0, obj['id'] == LRR3sensorprop['obj_FUS'][idx]['id'])
                  S1Intervals = Source.compare(LRR3sensorprop['time'], mask, measproc.not_equal, 0)
                  ActS1Intervals = ActivityInterval.intersect(S1Intervals)

                  diff_ohlfus = numpy.zeros_like(LRR3sensorprop['OHL2FUSassoc'][idx])
                  diff_ohlfus[:-1] = numpy.diff(LRR3sensorprop['OHL2FUSassoc'][idx])
                  OHLFUSIntervals = Source.compare(LRR3sensorprop['time'], diff_ohlfus, measproc.equal, 0)
                  ActOHLFUSIntervals = ActS1Intervals.intersect(OHLFUSIntervals)

                  if len(ActOHLFUSIntervals) != 0:
                    LRR3_OHL_intoS1.append(LRR3sensorprop['OHL2FUSassoc'][idx][ActOHLFUSIntervals[0][0]])

            sensorTime = Source.rescale(timeCVR3, CVR3sensorprop['time'], timeLRR3)[1]

            # select CVR3 OHL ID's that were associated with LRR3 OHL objects which have got into S1
            assoIndex = numpy.searchsorted(LRR3CVR3_AssoObj.scaleTime, sensorTime[start])

            CVR3_OHLids = []
            for LRR3_S1_OHLid in LRR3_OHL_intoS1:
              for LRR3_OHLid, CVR3_OHLid in LRR3CVR3_AssoObj.objectPairs[assoIndex]:
                if LRR3_S1_OHLid == LRR3_OHLid:
                  CVR3_OHLids.append(CVR3_OHLid)

            CVR3_OHLids = list(set(CVR3_OHLids))

            # using the association list, acquire the data that explains why CVR3
            # has not given a warning for the object that has triggered one in LRR3
            if len(CVR3_OHLids) != 0:
              for CVR3_OHLid in CVR3_OHLids:
                for idx in xrange(FUS_OBJ_NUM): # it iterates through CVR3 FUS objects!!
                  CVR3_OHL2FUS = Source.rescale(timeCVR3, CVR3sensorprop['OHL2FUSassoc'][idx], timeLRR3)[1]
                  if CVR3_OHLid in CVR3_OHL2FUS[start:end]:
                    dLength = Source.rescale(timeCVR3, CVR3sensorprop['dLength_FUS'][idx], timeLRR3)[1]
                    dVarYvBase = Source.rescale(timeCVR3, CVR3sensorprop['dVarYvBase_FUS'][idx], timeLRR3)[1]
                    wConstElem = Source.rescale(timeCVR3, CVR3sensorprop['wConstElem_FUS'][idx], timeLRR3)[1]
                    wClassObst = Source.rescale(timeCVR3, CVR3sensorprop['wClassObst_FUS'][idx], timeLRR3)[1]
                    wClassObstNear = Source.rescale(timeCVR3, CVR3sensorprop['wClassObstNear_FUS'][idx], timeLRR3)[1]
                    qClass = Source.rescale(timeCVR3, CVR3sensorprop['qClass_FUS'][idx], timeLRR3)[1]

                    values = {}
                    values['dLength'] = float(numpy.count_nonzero(dLength[start:end] < 1.0)) / len(dLength[start:end].flatten()) * 100
                    values['dVarYvBase'] = float(numpy.count_nonzero(0.5 < dVarYvBase[start:end])) / len(dVarYvBase[start:end].flatten()) * 100
                    values['wConstElem'] = float(numpy.count_nonzero(0.003 < wConstElem[start:end])) / len(wConstElem[start:end].flatten()) * 100
                    values['wClassObst'] = float(numpy.count_nonzero(wClassObst[start:end] < 0.5)) / len(wClassObst[start:end].flatten()) * 100
                    values['wClassObstNear'] = float(numpy.count_nonzero(wClassObstNear[start:end] < 0.7)) / len(wClassObstNear[start:end].flatten()) * 100
                    values['qClass'] = float(numpy.count_nonzero(qClass[start:end] < 0.7)) / len(qClass[start:end].flatten()) * 100
                    NoWarningsData[(starttime, endtime)][test][idx] = values
            else:
              NoWarningsData[(starttime, endtime)][test]['NoDetect'] = 'CVR3 has not detected the object at all!'

        # give reason for fewer LRR3 warnings than CVR3
        elif len(activityRoadTypeIntervals['CVR3'][test]) > len(activityRoadTypeIntervals['LRR3'][test]):
          pass

      workspaceNoWarnData = measproc.DinWorkSpace('AEBS_NoCVR3Warnings')
      tmp_time_start = []
      tmp_time_end = []
      tmp_test = []
      tmp_FUS_ids = []
      tmp_dLength = []
      tmp_dVarYvBase = []
      tmp_wConstElem = []
      tmp_wClassObst = []
      tmp_wClassObstNear = []
      tmp_qClass = []
      tmp_Detected = []
      for interval in sorted(NoWarningsData.keys(), key=lambda timeinterval: timeinterval[0]):
        for test in NoWarningsData[interval].keys():
          for FUS_ID in NoWarningsData[interval][test].keys():
            tmp_time_start.append(interval[0])
            tmp_time_end.append(interval[1])
            tmp_test.append(test)
            if FUS_ID != 'NoDetect':
              tmp_FUS_ids.append(FUS_ID)
              tmp_dLength.append(NoWarningsData[interval][test][FUS_ID]['dLength'])
              tmp_dVarYvBase.append(NoWarningsData[interval][test][FUS_ID]['dVarYvBase'])
              tmp_wConstElem.append(NoWarningsData[interval][test][FUS_ID]['wConstElem'])
              tmp_wClassObst.append(NoWarningsData[interval][test][FUS_ID]['wClassObst'])
              tmp_wClassObstNear.append(NoWarningsData[interval][test][FUS_ID]['wClassObstNear'])
              tmp_qClass.append(NoWarningsData[interval][test][FUS_ID]['qClass'])
              tmp_Detected.append('yes')
            else:
              tmp_FUS_ids.append(-1)
              tmp_dLength.append(-1)
              tmp_dVarYvBase.append(-1)
              tmp_wConstElem.append(-1)
              tmp_wClassObst.append(-1)
              tmp_wClassObstNear.append(-1)
              tmp_qClass.append(-1)
              tmp_Detected.append('no')

        workspaceNoWarnData.add(times_start=tmp_time_start,
                                 times_end=tmp_time_end,
                                 tests=tmp_test,
                                 FUS_ids=tmp_FUS_ids,
                                 dLength=tmp_dLength,
                                 dVarYvBase=tmp_dVarYvBase,
                                 wConstElem=tmp_wConstElem,
                                 wClassObst=tmp_wClassObst,
                                 wClassObstNear=tmp_wClassObstNear,
                                 qClass=tmp_qClass,
                                 Detected=tmp_Detected)
        Batch.add_entry(workspaceNoWarnData, self.NONE)


    tmp_datalist = []
    for sensor in activityRoadTypeIntervals.keys():
      for test in activityRoadTypeIntervals[sensor].keys():
        for start, end in activityRoadTypeIntervals[sensor][test]:
          tmp_datalist.append((sensorsToEvaluate[sensor]['time'][start], start, end, sensor, test))

    tmp_sensors = []
    tmp_tests = []
    tmp_times_start = []
    tmp_times_end = []
    tmp_ego_v = []
    tmp_ego_ax = []
    tmp_ego_ay = []
    tmp_cipv_dx = []
    tmp_cipv_dy = []
    tmp_cipv_vrel = []
    tmp_cipv_stat = []
    workspaceCIPVnEgoData = measproc.DinWorkSpace('AEBS_CIPVnEgoData')
    for sorttime, start, end, sensor, test in sorted(tmp_datalist, key=lambda datalist: datalist[0]):
      tmp_sensors.append(sensor)
      tmp_tests.append(test)
      tmp_times_start.append(sensorsToEvaluate[sensor]['time'][start])
      tmp_times_end.append(sensorsToEvaluate[sensor]['time'][end])
      tmp_ego_v.append(sensorsToEvaluate[sensor]['egoSpeed'][start])
      tmp_ego_ax.append(sensorsToEvaluate[sensor]['egoAccel'][start])
      tmp_ego_ay.append(sensorsToEvaluate[sensor]['egoLatAccel'][start])
      if sensor == 'AC100':
        tmp_cipv_dx.append(sensorsToEvaluate['AC100']['obj'][0]['dx'][start])
        tmp_cipv_dy.append(sensorsToEvaluate['AC100']['obj'][0]['dy'][start])
        tmp_cipv_vrel.append(sensorsToEvaluate['AC100']['obj'][0]['vx'][start])
        tmp_cipv_stat.append('yes' if sensorsToEvaluate['AC100']['obj'][0]['type'][start] == grouptypes.AC100_STAT else 'no')
      elif sensor == 'CVR3':
        tmp_cipv_dx.append(sensorsToEvaluate['CVR3']['obj'][1]['dx'][start])
        tmp_cipv_dy.append(sensorsToEvaluate['CVR3']['obj'][1]['dy'][start])
        tmp_cipv_vrel.append(sensorsToEvaluate['CVR3']['obj'][1]['vx'][start])
        tmp_cipv_stat.append('yes' if sensorsToEvaluate['CVR3']['obj'][1]['type'][start] == grouptypes.CVR3_POS_STAT else 'no')
      elif sensor == 'LRR3':
        tmp_cipv_dx.append(sensorsToEvaluate['LRR3']['obj'][1]['dx'][start])
        tmp_cipv_dy.append(sensorsToEvaluate['LRR3']['obj'][1]['dy'][start])
        tmp_cipv_vrel.append(sensorsToEvaluate['LRR3']['obj'][1]['vx'][start])
        tmp_cipv_stat.append('yes' if sensorsToEvaluate['LRR3']['obj'][1]['type'][start] == grouptypes.LRR3_POS_STAT else 'no')

    workspaceCIPVnEgoData.add(sensors=tmp_sensors,
                              times_start=tmp_times_start,
                              times_end=tmp_times_end,
                              tests=tmp_tests,
                              ego_v=tmp_ego_v,
                              ego_ax=tmp_ego_ax,
                              ego_ay=tmp_ego_ay,
                              cipv_dx=tmp_cipv_dx,
                              cipv_dy=tmp_cipv_dy,
                              cipv_vrel=tmp_cipv_vrel,
                              cipv_stat=tmp_cipv_stat)
    Batch.add_entry(workspaceCIPVnEgoData, self.NONE)

    workspaceMap = measproc.DinWorkSpace('AEBS_workspace')
    mm = Source.getSignalFromSignalGroup(visuGroup, 'Multimedia_1', ScaleTime=timeCVR3)[1]
    lon = Source.getSignalFromSignalGroup(visuGroup, 'Longitude', ScaleTime=timeCVR3)[1]
    lat = Source.getSignalFromSignalGroup(visuGroup, 'Latitude', ScaleTime=timeCVR3)[1]
    workspaceMap.add(Time=timeCVR3, Latitude=lat, Longitude=lon, Multimedia_1=mm)
    Batch.add_entry(workspaceMap, self.NONE)

    return

