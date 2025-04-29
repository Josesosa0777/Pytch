import numpy

import interface
import measproc
from aebs.par import grouptypes

cvr3DeviceNames = ('MRR1plus', 'RadarFC')

egoVehSignalGroups = []
for device in cvr3DeviceNames:
  egoVehSignalGroup = {"evi.General_T20.vxvRef": (device, "evi.General_T20.vxvRef")}
  egoVehSignalGroups.append(egoVehSignalGroup)

FUS_OBJ_NUM = 32
cvr3ObjClassifiers = ('dLength', 'dVarYvBase', 'wConstElem', 'qClass', 'wClassObstacle', 'wClassObstacleNear', 'wExistProb', 'wGroundReflex')

cvr3SignalGroups = []
for device in cvr3DeviceNames:
  cvr3SignalGroup = {}
  for index in xrange(FUS_OBJ_NUM):
    for signaltemplate in cvr3ObjClassifiers:
      cvr3SignalGroup["%s_FUS%s" % (signaltemplate, index)] = (device, 'fus.ObjData_TC.FusObj.i%s.%s' % (index, signaltemplate))
  cvr3SignalGroups.append(cvr3SignalGroup)

posElements = {'L1': 0,
               'S1': 1,
               'R1': 2,
               'L2': 3,
               'S2': 4,
               'R2': 5}

DefParam = interface.NullParam

class cSearch(interface.iSearch):
  dep = ('fillCVR3_POS@aebs.fill', 'fillCVR3_FUS@aebs.fill')
  def check(self):
    source = self.get_source('main')
    egoVehGroups = source.selectSignalGroup(egoVehSignalGroups)
    cvr3ClassifGroups = source.selectSignalGroup(cvr3SignalGroups)
    return egoVehGroups, cvr3ClassifGroups

  def fill(self, egoVehGroups, cvr3ClassifGroups):
    source = self.get_source('main')
    modules = self.get_modules()
    timePOS, objPOStmp = modules.fill('fillCVR3_POS@aebs.fill')
    timeFUS, objFUS = modules.fill('fillCVR3_FUS@aebs.fill')
    objPOS = list(objPOStmp)
    for index in xrange(len(objPOStmp)):
      for signal in objPOStmp[index].keys():
        time, objPOS[index][signal] = source.rescale(timePOS, objPOStmp[index][signal], timeFUS)
    return time, objPOS, objFUS, egoVehGroups, cvr3ClassifGroups

  def search(self, Param, time, objPOS, objFUS, egoVehGroups, cvr3ClassifGroups):
    source = self.get_source('main')
    batch = self.get_batch()

    EgoSpeedTime, EgoSpeedValue = source.getSignalFromSignalGroup(egoVehGroups, 'evi.General_T20.vxvRef', ScaleTime=time)
    EgoSpeedNZInt = source.compare(EgoSpeedTime, EgoSpeedValue, measproc.greater, 15 / 3.6)

    classifSignals = {}
    for classif in cvr3ObjClassifiers:
      classifSignals[classif] = {}
    for classif in cvr3ObjClassifiers:
      for index in xrange(FUS_OBJ_NUM):
        classifSignals[classif][index] = source.getSignalFromSignalGroup(cvr3ClassifGroups, '%s_FUS%s' % (classif, index), ScaleTime=time)[1]


    maskPOS = numpy.zeros_like(time)
    S1dxDiff = numpy.diff(objPOS[1]['dx'])
    maskPOS[:-1] = S1dxDiff < 0

    S1dxMonDecInt = source.compare(time, maskPOS, measproc.not_equal, 0)
    S1EgoMovingInt = S1dxMonDecInt.intersect(EgoSpeedNZInt)
    S1StatObjInt = source.compare(time, objPOS[1]['type'], measproc.equal, grouptypes.CVR3_POS_STAT)
    S1RelevantInt = S1EgoMovingInt.intersect(S1StatObjInt)
    S1RelevantInt = S1RelevantInt.merge(2)

    for fusID in xrange(FUS_OBJ_NUM):
      S1Mask = numpy.logical_and(objPOS[1]['id'] > 0, objPOS[1]['id'] == objFUS[fusID]['id'])
      FUSInS1Int = source.compare(time, S1Mask, measproc.not_equal, 0)
      FUSInS1RelevantInt = FUSInS1Int.intersect(S1RelevantInt)

      if len(FUSInS1RelevantInt) != 0:
        maskFUS = numpy.zeros_like(time)
        FUSdxDiff = numpy.diff(objFUS[fusID]['dx'])
        maskFUS[:-1] = FUSdxDiff < 0

        FUSdxMonDecInt = source.compare(time, maskFUS, measproc.not_equal, 0)
        FUSEgoMovingInt = FUSdxMonDecInt.intersect(EgoSpeedNZInt)
        FUSStatObjInt = source.compare(time, objFUS[fusID]['type'], measproc.equal, grouptypes.CVR3_FUS_FUSED_STAT)
        FUSRelevantInt = FUSStatObjInt.intersect(FUSEgoMovingInt)

        FUSWithS1Int = measproc.cIntervalList(time)
        for start, end in FUSInS1RelevantInt:
          for lower, upper in FUSRelevantInt.findIntervals(start):
            FUSWithS1Int.add(lower, upper)
        FUSWithS1Int = FUSWithS1Int.merge(0) # remove duplicate intervals if any

        FUSRejectedFromS1 = FUSWithS1Int.intersect(FUSInS1RelevantInt.negate())

        # Valid
        P_dVarYLimitStationary_uw = 1.0
        P_wExistStationary_uw = 0.8
        P_wGroundReflex_ub = 0.1

        # Threshold parameters for the classifiers
        P_dOutOfSightSO_sw = 100.0
        P_wObstacleProbFar_uw = 0.5
        P_wObstacleNear_uw = 0.7
        P_wObstacleNearQClass_uw = 0.7
        P_dLengthFar_sw = 1.0
        P_wConstructionElementFar_ub = 0.003
        P_dVarYLimitFar_uw = 0.5

        ObjectClassif = measproc.cIntervalList(time)
        LaneClassif = {}
        for posName in posElements.keys():
          if posName != 'S1':
            LaneClassif[posName] = measproc.cIntervalList(time)

        for start, end in FUSRejectedFromS1:
          ObstacleIsRelevant = (objFUS[fusID]['dx'] <= P_dOutOfSightSO_sw) & \
                                ( (classifSignals['wClassObstacle'][fusID] >= P_wObstacleProbFar_uw) & \
                                  (classifSignals['wConstElem'][fusID] < P_wConstructionElementFar_ub) & \
                                  (classifSignals['dLength'][fusID] > P_dLengthFar_sw) & \
                                  (classifSignals['dVarYvBase'][fusID] < P_dVarYLimitFar_uw)) | \
                                ( (classifSignals['wClassObstacleNear'][fusID] >= P_wObstacleNear_uw) & \
                                  (classifSignals['qClass'][fusID] >= P_wObstacleNearQClass_uw))

          ObstacleIsValid = (classifSignals['wExistProb'][fusID] >= P_wExistStationary_uw) & \
                            (classifSignals['dVarYvBase'][fusID] <= P_dVarYLimitStationary_uw) & \
                            (classifSignals['wGroundReflex'][fusID] <= P_wGroundReflex_ub)

          ObstIsValidnRelevant = ObstacleIsRelevant[start:end] & ObstacleIsValid[start:end]
          ObjClassifLength = float(numpy.count_nonzero(ObstIsValidnRelevant)) / len(ObstIsValidnRelevant)

          if ObjClassifLength > 0.5:
            for posName, posID in posElements.items():
              if posName != 'S1':
                LaneClassifInPOS = numpy.logical_and(objPOS[posID]['id'][start:end] > 0, objPOS[posID]['id'][start:end] == objFUS[fusID]['id'][start:end])
                LaneClassifLength = float(numpy.count_nonzero(LaneClassifInPOS)) / len(LaneClassifInPOS)

                if (1.0 - ObjClassifLength) < LaneClassifLength:
                  LaneClassif[posName].add(start, end)
          else:
            ObjectClassif.add(start, end)

        for posName in LaneClassif.keys():
          if len(LaneClassif[posName]) != 0:
            Results = self.PASSED
          else:
            Results = self.FAILED
          Report = measproc.cIntervalListReport(LaneClassif[posName], 'UseCaseEval - CVR3 FUS%02d rejected - LaneClassif as %s' % (fusID, posName))
          batch.add_entry(Report, Results)

        fusIsObstacle = source.compare(time, classifSignals['wClassObstacle'][fusID], measproc.not_equal, 0)
        fusIsObstacle = FUSWithS1Int.intersect(fusIsObstacle)
        fusIsObstacle = fusIsObstacle.drop(0.6)
        fusIsValidnRelevant = source.compare(time, (ObstacleIsRelevant & ObstacleIsValid), measproc.not_equal, 0)
        fusIsValidnRelevant = FUSWithS1Int.intersect(fusIsValidnRelevant)
        fusIsValidnRelevant = fusIsValidnRelevant.drop(0.6)

        wsSummaryData = measproc.DinWorkSpace('UseCaseEvalSummary-FUS_%02d' % (fusID))
        summaryData = {'dxFirstDet': [], 'dxAsObst': [], 'dxValRel': []}

        for interval in FUSWithS1Int:
          summaryData['dxFirstDet'].append(objFUS[fusID]['dx'][interval[0]])
        for interval in fusIsObstacle:
          summaryData['dxAsObst'].append(objFUS[fusID]['dx'][interval[0]])
        for interval in fusIsValidnRelevant:
          summaryData['dxValRel'].append(objFUS[fusID]['dx'][interval[0]])

        wsSummaryData.add(**summaryData)
        batch.addEntry(wsSummaryData, 'none', 'measproc.FileWorkSpace')

        if len(ObjectClassif) != 0:
          Results = self.PASSED
        else:
          Results = self.FAILED
        Report = measproc.cIntervalListReport(ObjectClassif, 'UseCaseEval - CVR3 FUS%02d rejected - ObjectClassif' % (fusID))
        batch.add_entry(Report, Results)
    pass

