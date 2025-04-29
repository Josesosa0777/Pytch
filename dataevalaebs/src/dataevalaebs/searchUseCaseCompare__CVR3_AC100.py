import numpy

import interface
import measproc
from aebs.par import grouptypes
from aebs.proc import AEBSWarningSim
from aebs.fill.fillCVR3_POS import labelCrossTable as cvr3PosElementsLong

cvr3DeviceNames = ('MRR1plus', 'RadarFC')
FUS_OBJ_NUM = 32
cvr3PosElements = {'L1': 0,
                   'S1': 1,
                   'R1': 2,
                   'L2': 3,
                   'S2': 4,
                   'R2': 5}
cvr3ClassifAliases = ['dVarYvBase', 'wClassObstacle', 'wClassObstacleNear', 'qClass', 'wExistProb', 'wGroundReflex', 'wConstElem', 'dLength']

cvr3FUSSignalGroups = []
cvr3SITSignalGroups = []
for device in cvr3DeviceNames:
  cvr3FUSSignalGroup = {}
  cvr3SITSignalGroup = {}
  for fusID in xrange(FUS_OBJ_NUM):
    for fusAlias in cvr3ClassifAliases:
      cvr3FUSSignalGroup["%d_%s" % (fusID, fusAlias)] = (device, "fus.ObjData_TC.FusObj.i%d.%s" % (fusID, fusAlias))
  cvr3FUSSignalGroups.append(cvr3FUSSignalGroup)
  for posName, posID in cvr3PosElements.items():
    cvr3SITSignalGroup['%s_Object' % posName] = (device, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i%d' %posID)
  cvr3SITSignalGroups.append(cvr3SITSignalGroup)

ac100Alias  = 'CW_track'
ac100CWSignalGroups = []
for k in xrange(10):
  ac100CWSignalGroup = {ac100Alias: ('Tracks', 'tr%d_%s' %(k, ac100Alias))}
  ac100CWSignalGroups.append(ac100CWSignalGroup)

egoVehSignalGroups = []
for device in cvr3DeviceNames:
  egoVehSignalGroups.append({"vehicle_speed": (device, "evi.General_T20.vxvRef")})
egoVehSignalGroups.append({"vehicle_speed": ("General_radar_status", "actual_vehicle_speed")})

DefParam = interface.NullParam

def calcCVR3ObstIsRelevant(cvr3ObjDataFUS):
  dx = cvr3ObjDataFUS['dx']
  wExistProb = cvr3ObjDataFUS['wExistProb']
  dVarYvBase = cvr3ObjDataFUS['dVarYvBase']
  wGroundReflex = cvr3ObjDataFUS['wGroundReflex']
  wClassObstacle = cvr3ObjDataFUS['wClassObstacle']
  wConstElem = cvr3ObjDataFUS['wConstElem']
  dLength = cvr3ObjDataFUS['dLength']
  wClassObstacleNear = cvr3ObjDataFUS['wClassObstacleNear']
  qClass = cvr3ObjDataFUS['qClass']

  # Valid parameter values of 1.2.1.8 release
  P_dVarYLimitStationary_uw = 1.0 # K1 is 1.0 as well
  P_wExistStationary_uw = 0.8 # K1 is 0.8 as well
  P_wGroundReflex_ub = 0.1

  ObstacleIsValid = ((wExistProb >= P_wExistStationary_uw) &
                     (dVarYvBase <= P_dVarYLimitStationary_uw) &
                     (wGroundReflex <= P_wGroundReflex_ub))

  # Relevant parameter values of 1.2.1.8 release
  P_dOutOfSightSO_sw = 100.0
  P_wObstacleProbFar_uw = 0.5
  P_wObstacleNear_uw = 0.7
  P_wObstacleNearQClass_uw = 0.7
  P_dLengthFar_sw = 1.0
  P_wConstructionElementFar_ub = 0.003
  P_dVarYLimitFar_uw = 0.5

  ObstacleIsRelevant = ((dx <= P_dOutOfSightSO_sw)
                        &
                        ((wClassObstacle >= P_wObstacleProbFar_uw) &
                         (wConstElem < P_wConstructionElementFar_ub) &
                         (dLength > P_dLengthFar_sw) &
                         (dVarYvBase < P_dVarYLimitFar_uw))
                        |
                        ((wClassObstacleNear  >= P_wObstacleNearQClass_uw) &
                         (qClass >= P_wObstacleNearQClass_uw)))
  return ObstacleIsRelevant & ObstacleIsValid

class cSearch(interface.iSearch):
  dep = ('fillCVR3_POS@aebs.fill', 'fillCVR3_FUS@aebs.fill',
         'fillAC100_CW@aebs.fill', 'fillAC100@aebs.fill')
  eventNum = 0 # number of events (dirty hack: accumulates sequential search results)

  def check(self):
    source = self.get_source('main')
    egoVehGroups = source.selectSignalGroup(egoVehSignalGroups)
    cvr3FUSGroups = source.selectSignalGroup(cvr3FUSSignalGroups)
    cvr3SITGroups = source.selectSignalGroup(cvr3SITSignalGroups)
    ac100CWGroups = source.selectSignalGroup(ac100CWSignalGroups)
    return egoVehGroups, cvr3FUSGroups, cvr3SITGroups, ac100CWGroups

  def fill(self, egoVehGroups, cvr3FUSGroups, cvr3SITGroups, ac100CWGroups):
    source = self.get_source('main')
    modules = self.get_modules()
    cvr3TimePOS, cvr3ObjPOStmp = modules.fill('fillCVR3_POS@aebs.fill')
    cvr3TimeFUS, cvr3ObjFUStmp = modules.fill('fillCVR3_FUS@aebs.fill')
    ac100TimeCW, ac100ObjCWtmp = modules.fill('fillAC100_CW@aebs.fill')
    ac100TimeTr, ac100ObjTrtmp = modules.fill('fillAC100@aebs.fill')
    cvr3ObjPOS = list(cvr3ObjPOStmp)
    cvr3ObjFUS = list(cvr3ObjFUStmp)
    ac100ObjCW = list(ac100ObjCWtmp)
    ac100ObjTr = list(ac100ObjTrtmp)

    for posID in xrange(len(cvr3ObjPOStmp)):
      if cvr3ObjPOStmp[posID]['label'] in [posNameLong for posNameLong, color in cvr3PosElementsLong]:
        for signal in cvr3ObjPOStmp[posID].keys():
          cvr3Time, cvr3ObjPOS[posID][signal] = source.rescale(cvr3TimePOS, cvr3ObjPOStmp[posID][signal], cvr3TimeFUS)
        posName = [key for key, value in cvr3PosElements.iteritems() if value == posID][0]
        cvr3ObjPOS[posID]['objectFlag'] = source.getSignalFromSignalGroup(cvr3SITGroups, '%s_Object' %posName, ScaleTime=cvr3TimeFUS)[1]

    for fusID in xrange(FUS_OBJ_NUM): # only regular FUS objects are interesting (the FUS_32, external, video-only is not)
      for classifName in cvr3ClassifAliases:
        cvr3ObjFUS[fusID][classifName] = source.getSignalFromSignalGroup(cvr3FUSGroups, '%d_%s' % (fusID, classifName), ScaleTime=cvr3TimeFUS)[1]

    for index in xrange(len(ac100ObjCWtmp)):
      if ac100ObjCWtmp[index]['label'] == 'AC100_CO':
        for signal in ac100ObjCWtmp[index].keys():
          ac100Time, ac100ObjCW[index][signal] = source.rescale(ac100TimeCW, ac100ObjCWtmp[index][signal], ac100TimeTr)
        ac100ObjCW[index]['cwTrack'] = source.getSignalFromSignalGroup(ac100CWGroups, 'CW_track', ScaleTime=ac100TimeTr)[1]

    egoSpeedSignals = {}
    egoSpeedSignals['CVR3']  = source.getSignalFromSignalGroup(egoVehGroups, 'vehicle_speed', ScaleTime=cvr3Time)[1]
    egoSpeedSignals['AC100'] = source.getSignalFromSignalGroup(egoVehGroups, 'vehicle_speed', ScaleTime=ac100Time)[1]  # TODO: ac100Time might cause NameError

    return cvr3Time, cvr3ObjPOS, cvr3ObjFUS, ac100Time, ac100ObjCW, ac100ObjTr, egoSpeedSignals  # TODO: ac100Time might cause NameError

  def search(self, Param, cvr3Time, cvr3ObjPOS, cvr3ObjFUS, ac100Time, ac100ObjCW, ac100ObjTr, egoSpeedSignals):
    source = self.get_source('main')
    batch = self.get_batch()

    detectionInfo = {}

    # check CVR3 S1 ------------------------------------------------------------
    EgoSpeedNZInt = source.compare(cvr3Time, egoSpeedSignals['CVR3'], measproc.greater, 5 / 3.6)

    # dirty hack: check if the assumption, that cvr3ObjPOS[1] stores the object we need, still holds
    assert cvr3ObjPOS[1]['label'] == 'SameLane_near', 'Unexpected result... Hint: a fill module for CVR3 might have changed.'

    cvr3MaskPOS = numpy.zeros_like(cvr3Time)
    cvr3S1dxDiff = numpy.diff(cvr3ObjPOS[1]['dx'])
    cvr3MaskPOS[:-1] = cvr3S1dxDiff < 0

    cvr3S1dxMonDecInt = source.compare(cvr3Time, cvr3MaskPOS, measproc.not_equal, 0) # S1 object is being approached
    cvr3S1EgoMovingInt = cvr3S1dxMonDecInt.intersect(EgoSpeedNZInt) # ego-speed is not zero during approach
    cvr3S1StatObjInt = source.compare(cvr3Time, cvr3ObjPOS[1]['type'], measproc.equal, grouptypes.CVR3_POS_STAT) # S1 object being approached is stationary
    cvr3S1RelevantInt = cvr3S1EgoMovingInt.intersect(cvr3S1StatObjInt) # relevant object is stationary and is being approached with non-zero ego-speed
    cvr3S1RelevantInt = cvr3S1RelevantInt.merge(2)  # TODO: remove this

    cvr3FUSObjInS1 = {}
    for fusID in xrange(FUS_OBJ_NUM):
      cvr3S1Mask = numpy.logical_and(cvr3ObjPOS[1]['id'] > 0, cvr3ObjPOS[1]['id'] == cvr3ObjFUS[fusID]['id'])
      cvr3FUSInS1Int = source.compare(cvr3Time, cvr3S1Mask, measproc.not_equal, 0) # CVR3 FUS object entered S1
      cvr3FUSInS1Int = cvr3FUSInS1Int.drop(0.5) # drop intervals in which FUS entered S1 for shorter than 0.5 sec.
      cvr3FUSInS1RelevantInt = cvr3FUSInS1Int.intersect(cvr3S1RelevantInt) # the FUS object is actually the relevant object

      if len(cvr3FUSInS1RelevantInt) != 0:
        cvr3MaskFUS = numpy.zeros_like(cvr3Time)
        cvr3FUSdxDiff = numpy.diff(cvr3ObjFUS[fusID]['dx'])
        cvr3MaskFUS[:-1] = cvr3FUSdxDiff < 0

        cvr3FUSdxMonDecInt = source.compare(cvr3Time, cvr3MaskFUS, measproc.not_equal, 0) # dx of FUS object (that got into S1) is monotonically decreasing (approach)
        cvr3FUSEgoMovingInt = cvr3FUSdxMonDecInt.intersect(EgoSpeedNZInt) # ego-speed is not zero during approach
        statMask = (  (cvr3ObjFUS[fusID]['type'] == grouptypes.CVR3_FUS_FUSED_STAT)
                    | (cvr3ObjFUS[fusID]['type'] == grouptypes.CVR3_FUS_RADAR_ONLY_STAT)
                    | (cvr3ObjFUS[fusID]['type'] == grouptypes.CVR3_FUS_VIDEO_ONLY_STAT))
        cvr3FUSStatObjInt = measproc.cIntervalList.fromMask(cvr3Time, Mask=statMask) # FUS object being approached is stationary
        cvr3FUSRelevantInt = cvr3FUSStatObjInt.intersect(cvr3FUSEgoMovingInt)

        cvr3FUSWithS1Int = measproc.cIntervalList(cvr3Time)
        for start, end in cvr3FUSInS1RelevantInt:
          lower, upper = cvr3FUSRelevantInt.findInterval(start)
          cvr3FUSWithS1Int.add(lower, upper)
        cvr3FUSWithS1Int = cvr3FUSWithS1Int.merge(0) # remove duplicate intervals if any
        cvr3FUSObjInS1[fusID] = {'FullDetect': cvr3FUSWithS1Int, 'S1Detect': cvr3FUSInS1RelevantInt}
    detectionInfo['CVR3'] = cvr3FUSObjInS1

    # check AC100 Tr0 with CW --------------------------------------------------
    EgoSpeedNZInt = source.compare(ac100Time, egoSpeedSignals['AC100'], measproc.greater, 5 / 3.6)

    # dirty hack: check if the assumption, that ac100ObjCW[0] stores the object we need, still holds
    assert ac100ObjCW[0]['label'] == 'AC100_CO', 'Unexpected result... Hint: a fill module for AC100 might have changed.'

    ac100MaskCW = numpy.zeros_like(ac100Time)
    ac100CWdxDiff = numpy.diff(ac100ObjCW[0]['dx'])
    ac100MaskCW[:-1] = ac100CWdxDiff < 0

    ac100CWdxMonDecInt = source.compare(ac100Time, ac100MaskCW, measproc.not_equal, 0) # CW object is being approached
    ac100CWEgoMovingInt = ac100CWdxMonDecInt.intersect(EgoSpeedNZInt) # ego-speed is not zero during approach
    ac100CWObjInt = source.compare(ac100Time, ac100ObjCW[0]['type'], measproc.equal, grouptypes.AC100_CO)
    ac100CWRelevantInt = ac100CWEgoMovingInt.intersect(ac100CWObjInt) # relevant object is stationary and is being approached with non-zero ego-speed
    ac100CWRelevantInt = ac100CWRelevantInt.merge(2)  # TODO: remove this

    ac100TrObjInCW = {}
    for trID in xrange(1): # in case of AC100 only trID = 0 is relevant but for some reason other trID's might also receive CW flag
      ac100CWMask = ac100ObjCW[0]['id'] == ac100ObjTr[trID]['id']
      ac100TrInCWInt = source.compare(ac100Time, ac100CWMask, measproc.not_equal, 0) # AC100 Track object entered CW
      ac100TrStatObjInt = source.compare(ac100Time, ac100ObjTr[trID]['type'], measproc.equal, grouptypes.AC100_STAT) # AC100 Track object is stationary
      ac100CWRelevantInt = ac100CWRelevantInt.intersect(ac100TrStatObjInt) # object is relevant, stationary CW one
      ac100TrInCWRelevantInt = ac100TrInCWInt.intersect(ac100CWRelevantInt) # the Track object is actually the relevant object

      if len(ac100TrInCWRelevantInt) != 0:
        ac100MaskTr = numpy.zeros_like(ac100Time)
        ac100TrdxDiff = numpy.diff(ac100ObjTr[trID]['dx'])
        ac100MaskTr[:-1] = ac100TrdxDiff < 0

        ac100TrSdxMonDecInt = source.compare(ac100Time, ac100MaskTr, measproc.not_equal, 0) # dx of Track object (that got into Cw) is monotonically decreasing (approach)
        ac100TrEgoMovingInt = ac100TrSdxMonDecInt.intersect(EgoSpeedNZInt) # ego-speed is not zero during approach
        ac100TrStatObjInt = source.compare(ac100Time, ac100ObjTr[trID]['type'], measproc.equal, grouptypes.AC100_STAT) # Track object being approached is stationary
        ac100TrRelevantInt = ac100TrStatObjInt.intersect(ac100TrEgoMovingInt)

        ac100TrWithCwInt = measproc.cIntervalList(ac100Time)
        for start, end in ac100TrInCWRelevantInt:
          lower, upper = ac100TrRelevantInt.findInterval(start)
          ac100TrWithCwInt.add(lower, upper)
        ac100TrWithCwInt = ac100TrWithCwInt.merge(0) # remove duplicate intervals if any
        ac100TrObjInCW[trID] = {'FullDetect': ac100TrWithCwInt, 'CWDetect': ac100TrInCWRelevantInt}
    detectionInfo['AC100'] = ac100TrObjInCW

    # pair intervals (1-1) that belong to each other ---------------------------
    dummyIntervalCVR3 = measproc.cIntervalList(cvr3Time)
    intervalsAC100onCvr3time = {}
    # put AC100 interval lists to CVR3 domain ----------------------------------
    for j, detectionsAC100 in detectionInfo['AC100'].iteritems():
      ac100TrWithCwInt = detectionsAC100['FullDetect']
      interval = dummyIntervalCVR3.convertIndices(ac100TrWithCwInt)
      intervalsAC100onCvr3time[j] = interval

    j = 0 # we are only interested in first track of AC100 as it is the most relevant
    intervalAC100onCvr3time = intervalsAC100onCvr3time[j] if j in intervalsAC100onCvr3time.keys() else measproc.cIntervalList(cvr3Time)
    detectionsAC100 = detectionInfo['AC100'][j] if j in detectionInfo['AC100'].keys() else {'FullDetect': measproc.cIntervalList(ac100Time), 'CWDetect': measproc.cIntervalList(ac100Time)}

    # map SAS events to sensor detection pairs ---------------------------------
    events = {}
    """ eventNum<int> : event<dict> """
    if len(detectionInfo['CVR3'].keys()) != 0:
      for i, detectionsCVR3 in detectionInfo['CVR3'].iteritems():
        intervalsCVR3 = detectionsCVR3['FullDetect']
        if len(intervalsCVR3) > 1:
          # more than one event for the same object -> skip for now as it is difficult to handle
          print 'Warning: CVR3 FUS %d object skipped, more than 1 event occurred!' %i
          continue
        for Lower, Upper in intervalsCVR3:
          # for each CVR3 object interval, find the corresponding AC100 object
          event = {}
          """ sensorName<str> : (objID, FullDetectInterval, CWDetectInterval)
          intervals of the sensors might be on different time domain """
          overlaps = []
          for __Lower, __Upper in intervalAC100onCvr3time:
            # find interval of objects that fit to each other the best (the most overlapping)
            if (      Upper > __Lower
                and __Upper >   Lower):
              start = max(__Lower, Lower)
              end   = min(__Upper, Upper)
              overlap = end-start
              overlaps.append(overlap)
          if overlaps:
            maxoverlap = max(overlaps)
            if maxoverlap > 0:
              # valid interval found
              intervalNumAC100 = overlaps.index(maxoverlap)
              # remove the best fit interval
              intervalAC100onCvr3time.pop(intervalNumAC100)
              # find original AC100 interval that fits the best
              fullDetectAC100 = detectionsAC100['FullDetect']
              fullDetectIntervalBestFitAC100 = measproc.cIntervalList(ac100Time)
              bestFitIntervalAC100 = fullDetectAC100[intervalNumAC100]
              fullDetectIntervalBestFitAC100.add( *bestFitIntervalAC100 )
              cwDetectIntervalBestFitAC100 = fullDetectIntervalBestFitAC100.intersect(detectionsAC100['CWDetect']) # might not always be correct
              # create event
              event['CVR3']  = i, detectionsCVR3['FullDetect'],  detectionsCVR3['S1Detect']
              event['AC100'] = j, fullDetectIntervalBestFitAC100, cwDetectIntervalBestFitAC100
              events[self.eventNum] = event
              self.eventNum += 1
            else:
              # no AC100 interval belongs to current CVR3
              event['CVR3']  = i, detectionsCVR3['FullDetect'],  detectionsCVR3['S1Detect']
              event['AC100'] = j, measproc.cIntervalList(ac100Time), measproc.cIntervalList(ac100Time)
              events[self.eventNum] = event
              self.eventNum += 1
          else:
            # no AC100 interval at all (theoretically should not happen)
            event['CVR3']  = i, detectionsCVR3['FullDetect'],  detectionsCVR3['S1Detect']
            event['AC100'] = j, measproc.cIntervalList(ac100Time), measproc.cIntervalList(ac100Time)
            events[self.eventNum] = event
            self.eventNum += 1
    else:
      # no detection interval is present for CVR3; it should not occur so it is not handled (yet)
      print "Warning: no object detection for CVR3! The script does not handle such events as they should not occur."
      return

    # store data for each event to file ----------------------------------------
    for k, event in events.iteritems():
      workspaceDetDist = measproc.DinWorkSpace('UseCase_%02d' %k)
      kwargs = {}
      for sensor, (objID, FullDetectInterval, CWDetectInterval) in event.iteritems():
        start, end = FullDetectInterval[0] if len(FullDetectInterval) != 0 else (0, 0)
        FullDetectIntervalExt = FullDetectInterval.addMargin(TimeMargins=(1,0)) # extend interval for display purposes (display signals earlier by 1 sec.)
        startExt, endExt = FullDetectIntervalExt[0] if len(FullDetectIntervalExt) != 0 else (0, 0)
        if sensor == 'CVR3':
          dxDet = cvr3ObjFUS[objID]['dx'][startExt:endExt]
          timeDet = cvr3Time[startExt:endExt]
          vEgo = egoSpeedSignals['CVR3'][startExt:endExt] * 3.6
          maskL1 = cvr3ObjPOS[0]['objectFlag'] == cvr3ObjFUS[objID]['id']
          maskS1 = cvr3ObjPOS[1]['objectFlag'] == cvr3ObjFUS[objID]['id']
          maskR1 = cvr3ObjPOS[2]['objectFlag'] == cvr3ObjFUS[objID]['id']
          cvr3L1Obj = maskL1[startExt:endExt]
          cvr3S1Obj = maskS1[startExt:endExt]
          cvr3R1Obj = maskR1[startExt:endExt]

          cvr3RelevObst = calcCVR3ObstIsRelevant(cvr3ObjFUS[objID])
          cvr3ObstIsRel = cvr3RelevObst[startExt:endExt]

          firstDet = cvr3ObjFUS[objID]['dx'][start] if len(FullDetectInterval) != 0 else 0.0

          maxLength = 0.0
          longestS1Int = []
          for obsStart, obsEnd in CWDetectInterval:
            if cvr3Time[start] < cvr3Time[obsStart] and cvr3Time[obsStart] < cvr3Time[end]:
              if maxLength < (cvr3Time[obsEnd] - cvr3Time[obsStart]):
                maxLength = cvr3Time[obsEnd] - cvr3Time[obsStart]
                longestS1Int.append((obsStart, obsEnd))
          if len(longestS1Int) != 0:
            obsDet = cvr3ObjFUS[objID]['dx'][longestS1Int[-1][0]]
            vInit = egoSpeedSignals['CVR3'][longestS1Int[-1][0]]
            speedRed, collision = AEBSWarningSim.calcAEBSSpeedReduction(obsDet, vInit)
          else:
            obsDet = 0.0
            speedRed = 0.0
            collision = True

          maxLength = 0.0
          longestRelObstInt = []
          cvr3RelObstInt = source.compare(cvr3Time, cvr3RelevObst, measproc.not_equal, 0)

          for obsRelStart, obsRelEnd in cvr3RelObstInt:
            obsRelEnd = min(obsRelEnd, len(cvr3Time) - 1) # needed if the last interval's end lasts till the end of the measurement
            if cvr3Time[start] < cvr3Time[obsRelStart] and cvr3Time[obsRelStart] < cvr3Time[end]:
              if maxLength < (cvr3Time[obsRelEnd] - cvr3Time[obsRelStart]):
                maxLength = cvr3Time[obsRelEnd] - cvr3Time[obsRelStart]
                longestRelObstInt.append((obsRelStart, obsRelEnd))
          if len(longestRelObstInt) != 0:
            dxObstRelevant = cvr3ObjFUS[objID]['dx'][longestRelObstInt[-1][0]]
          else:
            dxObstRelevant = 0.0

        elif sensor == 'AC100':
          dxDet = ac100ObjTr[objID]['dx'][startExt:endExt]
          timeDet = ac100Time[startExt:endExt]
          #vEgo = egoSpeedSignals['CVR3'][startExt:endExt] * 3.6
          cwTrack = ac100ObjCW[objID]['cwTrack'][startExt:endExt]

          firstDet = ac100ObjTr[objID]['dx'][start] if len(FullDetectInterval) != 0 else 0.0
          maxLength = 0.0
          longestCWInt = []
          for obsStart, obsEnd in CWDetectInterval:
            if ac100Time[start] < ac100Time[obsStart] and ac100Time[obsStart] < ac100Time[end]:
              if maxLength < (ac100Time[obsEnd] - ac100Time[obsStart]):
                maxLength = ac100Time[obsEnd] - ac100Time[obsStart]
                longestCWInt.append((obsStart, obsEnd))
          if len(longestCWInt) != 0:
            obsDet = ac100ObjTr[objID]['dx'][longestCWInt[-1][0]]
            vInit = egoSpeedSignals['AC100'][longestCWInt[-1][0]]
            speedRed, collision = AEBSWarningSim.calcAEBSSpeedReduction(obsDet, vInit)
          else:
            obsDet = 0.0
            speedRed = 0.0
            collision = True

        kwargs['dxFull_%s'           %sensor] = dxDet
        kwargs['timeFull_%s'         %sensor] = timeDet
        kwargs['dxFirstDet_%s'       %sensor] = firstDet
        kwargs['dxObsDet_%s'         %sensor] = obsDet
        kwargs['speedReduc_%s'       %sensor] = speedRed
        kwargs['collisionOccured_%s' %sensor] = collision
        if sensor == 'CVR3':
          kwargs['egoVel_%s'         %sensor] = vEgo
          kwargs['obsIsRel_%s'       %sensor] = cvr3ObstIsRel
          kwargs['objIsL1_%s'        %sensor] = cvr3L1Obj
          kwargs['objIsS1_%s'        %sensor] = cvr3S1Obj
          kwargs['objIsR1_%s'        %sensor] = cvr3R1Obj
          kwargs['dxObsRelevant_%s'  %sensor] = dxObstRelevant
        elif sensor == 'AC100':
          kwargs['objIsCW_%s'        %sensor] = cwTrack

        workspaceDetDist.add(**kwargs)
        batch.add_entry(workspaceDetDist, self.NONE)
    return
