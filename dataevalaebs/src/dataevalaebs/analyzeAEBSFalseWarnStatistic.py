import numpy
import os
import csv
import re

import interface
import measproc
import analyzeAddLabels

class cParameter(interface.iParameter):
  def __init__(self, showReport):
    self.showReport = showReport
    self.genKeys()
    return

SHOWCOMMON = cParameter(True)
HIDECOMMON = cParameter(False)

OBJECT_STANCES = ['Stationary', 'Moving']
WARN_TYPES = ['acoustic_warn', 'part_brake', 'emer_brake']
CLASSIFIERS = ['dVarYvBase', 'wClassObst', 'dLength', 'wConstElem']

MeasNamePattern = re.compile(r'.+(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})_\d{2}-\d{2}-\d{2}.+')

def ceilDay(Day, Hour):
  Hour = int(Hour+0.5)
  if Hour < 6:
    CeilOffset = 1.25
  elif 6 <= Hour < 12:
    CeilOffset = 1.0
  elif 12 <= Hour < 18:
    CeilOffset = 0.75
  else:
    CeilOffset = 0.5
  return int(Day+CeilOffset)

class cAnalyze(interface.iAnalyze):
  dep = ('analyzeLabels',)
  def check(self):
    batch = self.get_batch()
    start = batch.get_last_entry_start()
    dateTimeWorkSpaceGroup = \
    batch.filter(start=start, type='measproc.FileWorkSpace',
                 class_name='dataevalaebs.searchAEBSWarnEval_RoadTypes.cSearch',
                 title='AEBS-DateTime')
    statisticGroup = \
    batch.filter(start=start, type='measproc.FileWorkSpace',
                 class_name='dataevalaebs.searchAEBSWarnEval_RoadTypes.cSearch')
    cvr2EgoWorkspaceGroup = \
    batch.filter(start=start, type='measproc.FileWorkSpace',
                 class_name='dataevalaebs.searchAEBSWarnEval_CVR2Warnings.cSearch',
                 title='AEBS-EgoData-CVR2')
    cvr3EgoWorkspaceGroup = \
    batch.filter(start=start, type='measproc.FileWorkSpace',
                 class_name='dataevalaebs.searchAEBSWarnEval_CVR3Warnings.cSearch',
                 title='AEBS-EgoData-CVR3')
    mapWorkspaceGroup = \
    batch.filter(start=start, type='measproc.FileWorkSpace',
                 class_name='dataevalaebs.searchAEBSWarnEval_Map.cSearch',
                 title='AEBS-MapData')
    scamWorkspaceGroup = \
    batch.filter(start=start, type='measproc.FileWorkSpace',
                 class_name='dataevalaebs.searchSensorCheck_SCam.cSearch',
                 title='SensorCheckWS-SCam')

    egoWsGroups = {}
    egoWsGroups['CVR3'] = cvr3EgoWorkspaceGroup
    egoWsGroups['CVR2'] = cvr2EgoWorkspaceGroup

    labeledGroup = set()
    for Title in analyzeAddLabels.iterTitles(analyzeAddLabels.cAnalyze.ReportTags, analyzeAddLabels.cAnalyze.TitleHead,
                                             Sensors=analyzeAddLabels.cAnalyze.Sensors, Tests=analyzeAddLabels.cAnalyze.Tests):
      Titles = batch.filter(start=start, type='measproc.cFileReport',
                            title=Title)
      labeledGroup.update(Titles)
    return dateTimeWorkSpaceGroup, statisticGroup, labeledGroup, egoWsGroups, scamWorkspaceGroup

  def fill(self, dateTimeWorkSpaceGroup, statisticGroup, labeledGroup, egoWsGroups, scamWorkspaceGroup):
    modules = self.get_modules()
    labelResult = modules.fill('analyzeLabels')

    batch = self.get_batch()
    start = batch.get_last_entry_start()
    csvDir = os.path.join(os.path.dirname(batch.dirname), 'CSV_Files')

    # determine measurement date -----------------------------------------------
    if dateTimeWorkSpaceGroup:
      recDateByMeas = {}
      for entry in dateTimeWorkSpaceGroup:
        measName = batch.get_entry_attr(entry, 'measurement')
        workspace = batch.wake_entry(entry)
        wsRecDate = workspace.workspace
        recDate = {}
        for key in wsRecDate.keys():
          if key in ('__version__', '__header__', '__globals__'):
            continue
          recDate[key] = {'start': wsRecDate[key].flatten()[0], 'end': wsRecDate[key].flatten()[-1]}
        recDateByMeas[measName] = recDate

      measWithRecDate = sorted(recDateByMeas.keys())
      RecDate = len(measWithRecDate) // 2
      RecDate = measWithRecDate[RecDate]
      measurementDate = MeasNamePattern.sub(r'\g<year>-\g<month>-\g<day>', RecDate)
      if not measurementDate:
        Day = ceilDay(recDateByMeas[RecDate]['Day']['start'],
                      recDateByMeas[RecDate]['Hour']['start'])
        measurementDate = "%d-%02d-%02d" % (int(recDateByMeas[RecDate]['Year']['start'] + 0.5),
                                            int(recDateByMeas[RecDate]['Month']['start'] + 0.5),
                                            Day)
    else:
      measPath = batch.get_entry_attr(list(labeledGroup)[0], 'fullmeas')
      measurementDate = measPath.split(os.path.sep)[-2]

    # calculate driven distance ------------------------------------------------
    roadtypes = ['rural', 'city', 'highway']
    drivenDist = {}
    for r in roadtypes:
      drivenDist[r] = 0
    for item in statisticGroup:
      stat = batch.wake_entry(item)
      for r in roadtypes:
        drivenDist[r] += stat.get([["RoadTypes",r]])

    # evaluate labeled reports -------------------------------------------------
    fwFullStat = {}
    fwRedExBridgeTunnelCVR3 = {}
    fwWithSDF = {}
    for sensor in analyzeAddLabels.cAnalyze.Sensors + ('common',):
      sensorStatDict = fwFullStat.setdefault(sensor, {})
      sensorRedDict = fwRedExBridgeTunnelCVR3.setdefault(sensor, {})
      sensorSDFDict = fwWithSDF.setdefault(sensor, {})
      for test in analyzeAddLabels.cAnalyze.Tests:
        testStatDict = sensorStatDict.setdefault(test, {})
        testStatDict.setdefault('votes', {})
        testRedDict = sensorRedDict.setdefault(test, {})
        testRedDict.setdefault('votes', {})
        testSDFDict = sensorSDFDict.setdefault(test, {})
        testSDFDict.setdefault('votes', {})
        for vote in analyzeAddLabels.cAnalyze.Votes:
          if sensor != 'common':
            voteStatDict = testStatDict['votes'].setdefault(vote, {})
            for stance in OBJECT_STANCES:
              stanceStatDict = voteStatDict.setdefault(stance, {})
              for warnType in WARN_TYPES:
                stanceStatDict.setdefault(warnType, 0)
          else:
            voteStatDict = testStatDict['votes'].setdefault(vote, {})
            for stance in OBJECT_STANCES:
              voteStatDict.setdefault(stance, 0)
          if vote not in ('bridge', 'tunnel'):
            voteRedDict = testRedDict['votes'].setdefault(vote, {})
            for stance in OBJECT_STANCES:
              voteRedDict.setdefault(stance, 0)
          if vote not in ('fw-red-with-sdf', 'scam-unavailable'):
            if sensor != 'common':
              voteSDFDict = testSDFDict['votes'].setdefault(vote, {})
              for stance in OBJECT_STANCES:
                stanceSDFDict = voteSDFDict.setdefault(stance, {})
                for warnType in WARN_TYPES:
                  stanceSDFDict.setdefault(warnType, 0)
            else:
              voteSDFDict = testSDFDict['votes'].setdefault(vote, {})
              for stance in OBJECT_STANCES:
                stanceSDFDict = voteSDFDict.setdefault(stance, 0)
        if sensor == 'CVR2': # as the excess warnings are on CVR2 side
          testStatDict.setdefault('classifiers', {})
          testRedDict.setdefault('classifiers', {})
          for classifier in CLASSIFIERS:
            testStatDict['classifiers'].setdefault(classifier, 0)
            testRedDict['classifiers'].setdefault(classifier, 0)

    overheadObjDataCVR3 = {'measurement': [],
                           'test': [],
                           'vote': [],
                           'startTime': [],
                           'endTime': [],
                           'cipv_dx': [],
                           'cipv_dy': [],
                           'cipv_vrel': [],
                           'cipv_objectID': [],
                           'Latitude': [],
                           'Longitude': []}

    availSensor = {}

    for sensor in labelResult.keys():
      if egoWsGroups[sensor]:
        availSensor[sensor] = 'yes'
      else:
        availSensor[sensor] = 'no'
      for testType in labelResult[sensor].keys():
        if sensor == 'CVR3':
          measWithExBriTu = set([])
          for vote in labelResult[sensor][testType].keys():
            if vote not in ('bridge', 'tunnel'):
              measWithExBriTu = measWithExBriTu.union(labelResult[sensor][testType][vote].keys())
          for measPath in measWithExBriTu:
            # determination like this is needed because of unordered interval lists
            # using union method of cIntervalList might skip intervals
            measBaseName = os.path.basename(measPath)
            redWithSDF = {}
            noSCam = {}
            for stance in labelResult[sensor][testType]['fw-red-with-sdf'][measPath].keys():
              redWithSDF[stance] = measproc.IntervalList.cIntervalList(
                  labelResult[sensor][testType]['fw-red-with-sdf'][measPath][stance].Time)
              noSCam[stance] = measproc.IntervalList.cIntervalList(
                  labelResult[sensor][testType]['scam-unavailable'][measPath][stance].Time)
            for vote in labelResult[sensor][testType].keys():
              if vote not in ('bridge', 'tunnel', 'fw-red-with-sdf', 'scam-unavailable'):
                for stance in labelResult[sensor][testType]['fw-red-with-sdf'][measPath].keys():
                  tmpRedWithSDF = \
                      labelResult[sensor][testType]['fw-red-with-sdf'][measPath][stance].intersect(
                          labelResult[sensor][testType][vote][measPath][stance])
                  tmpNoSCam = \
                      labelResult[sensor][testType]['scam-unavailable'][measPath][stance].intersect(
                          labelResult[sensor][testType][vote][measPath][stance])
                  for reduInterval in tmpRedWithSDF:
                    if reduInterval in redWithSDF[stance]:
                      # exclude intervals that have already been added or were already present
                      continue
                    else:
                      reduLower, reduUpper = reduInterval
                      redWithSDF[stance].add(reduLower, reduUpper)
                  for noReduInterval in tmpNoSCam:
                    if noReduInterval in noSCam[stance]:
                      # exclude intervals that have already been added or were already present
                      continue
                    else:
                      noReduLower, noReduUpper = noReduInterval
                      noSCam[stance].add(noReduLower, noReduUpper)
            for stance in fwRedExBridgeTunnelCVR3[sensor][testType]['votes']['fw-red-with-sdf'].keys():
              fwRedExBridgeTunnelCVR3[sensor][testType]['votes']['fw-red-with-sdf'][stance] += len(redWithSDF[stance])
              fwRedExBridgeTunnelCVR3[sensor][testType]['votes']['scam-unavailable'][stance] += len(noSCam[stance])

        classifActive = {'dVarYvBase' : [], 'wClassObst' : [], 'dLength' : [], 'wConstElem' : []}
        classifActiveExBridgeTunnel = {'dVarYvBase' : [], 'wClassObst' : [], 'dLength' : [], 'wConstElem' : []}

        for vote in labelResult[sensor][testType].keys():
          for measPath in labelResult[sensor][testType][vote].keys():
            for stance in labelResult[sensor][testType][vote][measPath].keys():
              intervalTimes = labelResult[sensor][testType][vote][measPath][stance].iterTime()
              for startTime, endTime in intervalTimes:
                if endTime - startTime < 0.6:
                  fwFullStat[sensor][testType]['votes'][vote][stance]['acoustic_warn'] += 1
                elif endTime - startTime < 1.4:
                  fwFullStat[sensor][testType]['votes'][vote][stance]['part_brake'] += 1
                else:
                  fwFullStat[sensor][testType]['votes'][vote][stance]['emer_brake'] += 1
              if vote not in ('fw-red-with-sdf', 'scam-unavailable'):
                fwRedIntervals = \
                    labelResult[sensor][testType]['fw-red-with-sdf'][measPath][stance].intersect(
                        labelResult[sensor][testType][vote][measPath][stance])
                for voteInt in labelResult[sensor][testType][vote][measPath][stance].Intervals:
                  if voteInt not in fwRedIntervals:
                    lower, upper = voteInt
                    startTime = fwRedIntervals.Time[lower]
                    endTime = fwRedIntervals.Time[upper - 1]
                    if endTime - startTime < 0.6:
                      fwWithSDF[sensor][testType]['votes'][vote][stance]['acoustic_warn'] += 1
                    elif endTime - startTime < 1.4:
                      fwWithSDF[sensor][testType]['votes'][vote][stance]['part_brake'] += 1
                    else:
                      fwWithSDF[sensor][testType]['votes'][vote][stance]['emer_brake'] += 1

            noWarnWSGroupwMeas = \
            batch.filter(start=start, type='measproc.FileWorkSpace',
                         class_name='dataevalaebs.searchAEBSWarnEval_CIPVRejectCVR3.cSearch',
                         title='AEBS-NoCVR3Warnings', measurement=measPath)

            warnIntervals = measproc.IntervalList.cIntervalList(
                labelResult[sensor][testType][vote][measPath]['Moving'].Time)
            for Lower, Upper in labelResult[sensor][testType][vote][measPath]['Moving'].Intervals:
              warnIntervals.add(Lower, Upper)
            for Lower, Upper in labelResult[sensor][testType][vote][measPath]['Stationary'].Intervals:
              warnIntervals.add(Lower, Upper)
            for intervalStart, intervalEnd in warnIntervals.iterTime():
              for wsEntry in noWarnWSGroupwMeas:
                workspace = batch.wake_entry(wsEntry)
                wsNoWarn = workspace.workspace
                founds = {'dVarYvBase' : False, 'wClassObst' : False, 'dLength' : False, 'wConstElem' : False}
                foundsExBridgeTunnel = {'dVarYvBase' : False, 'wClassObst' : False, 'dLength' : False, 'wConstElem' : False}
                timeIndeces = numpy.nonzero(wsNoWarn['times_start'].flatten() == intervalStart)[0] # needed as in some cases no CIPV rejection is present
                for timeIndex in timeIndeces: # needed as in some cases no CIPV rejection is present
                  if wsNoWarn['tests'][timeIndex].strip() == testType:
                    for classifier in CLASSIFIERS:
                      if wsNoWarn[classifier][timeIndex] > 99.99 and not founds[classifier]:
                        classifActive[classifier].append(timeIndex)
                        founds[classifier] = True
                    if vote not in ('bridge', 'tunnel'):
                      for classifier in CLASSIFIERS:
                        if wsNoWarn[classifier][timeIndex] > 99.99 and not foundsExBridgeTunnel[classifier]:
                          classifActiveExBridgeTunnel[classifier].append(timeIndex)
                          foundsExBridgeTunnel[classifier] = True

              cipvWSGroupwMeas = \
              batch.filter(start=start, type='measproc.FileWorkSpace',
                           class_name='dataevalaebs.searchAEBSWarnEval_CVR3Warnings.cSearch',
                           title='AEBS-CIPVData-CVR3', measurement=measBaseName)
              if sensor == 'CVR3' and vote in ('bridge'): # 'tunnel'
                overheadObjDataCVR3['measurement'].append(os.path.split(measPath)[-1])
                overheadObjDataCVR3['vote'].append(vote)
                overheadObjDataCVR3['startTime'].append(intervalStart)
                overheadObjDataCVR3['endTime'].append(intervalEnd)
                overheadObjDataCVR3['test'].append(testType)

                if cipvWSGroupwMeas:
                  for cipvWSEntry in cipvWSGroupwMeas:
                    workspace = batch.wake_entry(cipvWSEntry)
                    wsCIPV = workspace.workspace
                    timeIndex = numpy.searchsorted(wsCIPV['times_start'].flatten(), intervalStart)
                    timeIndex = min(timeIndex, (len(wsCIPV['times_start'].flatten())-1))
                    for cipvData in ('cipv_dx', 'cipv_dy', 'cipv_vrel', 'cipv_objectID'):
                      if cipvData in wsCIPV.keys():
                        overheadObjDataCVR3[cipvData].append(wsCIPV[cipvData].flatten()[timeIndex])
                      else:
                        overheadObjDataCVR3[cipvData].append('n/a')
                else:
                  for cipvData in ('cipv_dx', 'cipv_dy', 'cipv_vrel', 'cipv_objectID'):
                    overheadObjDataCVR3[cipvData].append('n/a')

                gpsWSGroupwMeas = \
                batch.filter(start=start, type='measproc.FileWorkSpace',
                             class_name='dataevalaebs.searchAEBSWarnEval_Map.cSearch',
                             title='AEBS-MapData', measurement=measBaseName)
                if gpsWSGroupwMeas:
                  for gpsWSEntry in gpsWSGroupwMeas:
                    workspace = batch.wake_entry(gpsWSEntry)
                    wsGPS = workspace.workspace
                    timeIndex = numpy.searchsorted(wsCIPV['times_start'].flatten(), intervalStart)
                    for gpsData in ('Latitude', 'Longitude'):
                      overheadObjDataCVR3[gpsData].append(wsGPS[gpsData].flatten()[timeIndex])
                else:
                  for gpsData in ('Latitude', 'Longitude'):
                    overheadObjDataCVR3[gpsData].append('n/a')
              else:
                overheadObjDataCVR3['measurement'].append(os.path.split(measPath)[-1])

          if sensor == 'CVR2': # as the excess warnings are on CVR2 side
            for classifier in CLASSIFIERS:
              fwFullStat[sensor][testType]['classifiers'][classifier] = len(classifActive[classifier])
              fwRedExBridgeTunnelCVR3[sensor][testType]['classifiers'][classifier] = len(classifActiveExBridgeTunnel[classifier])

    # check if overheadObjDataCVR3 was filled with proper data -----------------
    if not overheadObjDataCVR3['test']:
      # if any key of overheadObjDataCVR3 other than 'measurement' was not filled with data
      # fill the lists with 'n/a'
      overheadObjDataCVR3['measurement'] = list(set(overheadObjDataCVR3['measurement']))
      for key in overheadObjDataCVR3.keys():
        if key != 'measurement':
          overheadObjDataCVR3[key] = [emptyList[:] for emptyList in ['n/a'] * len(overheadObjDataCVR3['measurement'])]

    # determine common warnings ------------------------------------------------
    commonFWGroup = set([])
    cvr2Tests = set(labelResult['CVR2'])
    cvr3Tests = set(labelResult['CVR3'])
    commonTests = cvr2Tests.intersection(cvr3Tests)
    for test in commonTests:
      cvr2Votes = set(labelResult['CVR2'][test])
      cvr3Votes = set(labelResult['CVR3'][test])
      commonVotes = cvr2Votes.intersection(cvr3Votes)
      for vote in commonVotes:
        cvr2MeasPaths = set(labelResult['CVR2'][test][vote].keys())
        cvr3MeasPaths = set(labelResult['CVR3'][test][vote].keys())
        commonMeasPaths = cvr2MeasPaths.intersection(cvr3MeasPaths)
        for measPath in commonMeasPaths:
          for stance in fwFullStat['common'][test]['votes'][vote].keys():
            cvr2Intervals = labelResult['CVR2'][test][vote][measPath][stance]
            cvr3Intervals = labelResult['CVR3'][test][vote][measPath][stance]
            fwFullStat['common'][test]['votes'][vote][stance] += len(cvr2Intervals.intersect(cvr3Intervals))

            if len(cvr2Intervals.intersect(cvr3Intervals)) != 0:
              for entry in labeledGroup:
                if batch.get_entry_attr(entry, 'fullmeas') == measPath:
                  if test in batch.get_entry_attr(entry, 'title').split('-'):
                    if batch.get_entry_attr(entry, 'result') == 'passed':
                      commonFWGroup.add(entry)

    # calculate S-Cam availability ---------------------------------------------
    scamAvailable = {}
    for time in ['timeTotal', 'timeAvailable']:
      scamAvailable[time] = 0.0
    for wsEntry in scamWorkspaceGroup:
      workspace = batch.wake_entry(wsEntry)
      wsSCamAvail = workspace.workspace
      for time in ['timeTotal', 'timeAvailable']:
        scamAvailable[time] += wsSCamAvail[time].flatten()[0]

    return fwFullStat, measurementDate, drivenDist, csvDir, commonFWGroup, overheadObjDataCVR3, fwRedExBridgeTunnelCVR3, fwWithSDF, availSensor, scamAvailable, labelResult

  def analyze(self, Param, fwFullStat, measurementDate, drivenDist, csvDir, commonFWGroup, overheadObjDataCVR3, fwRedExBridgeTunnelCVR3, fwWithSDF, availSensor, scamAvailable, labelResult):
    # count available votes ----------------------------------------------------
    votePresent = []
    for sensor in fwFullStat.keys():
      for test in fwFullStat[sensor].keys():
        for vote in fwFullStat[sensor][test]['votes'].keys():
          if sensor != 'common':
            for stance in fwFullStat[sensor][test]['votes'][vote].keys():
              for warnType in fwFullStat[sensor][test]['votes'][vote][stance].keys():
                votePresent.append(fwFullStat[sensor][test]['votes'][vote][stance][warnType] != 0)

    if not os.path.exists(csvDir):
      os.makedirs(csvDir)
    # is there any vote present ------------------------------------------------
    if numpy.any(votePresent):

      # count FW occurrences in the case of CVR3 -------------------------------
      fwNumCVR3 = 0
      fwNumCVR3ExBridgeTunnel = 0
      fwNumCVR3SDF_offline = 0
      fwNumCVR3SDF_online = 0
      for vote in fwFullStat['CVR3']['KBASFAvoidance']['votes'].keys():
        if vote not in ('fw-red-with-sdf', 'scam-unavailable'):
          tmp = 0
          for stance in fwFullStat['CVR3']['KBASFAvoidance']['votes'][vote].keys():
            for warnType in fwFullStat['CVR3']['KBASFAvoidance']['votes'][vote][stance].keys():
              tmp += fwFullStat['CVR3']['KBASFAvoidance']['votes'][vote][stance][warnType]
          fwNumCVR3 += tmp
        if vote not in ('fw-red-with-sdf', 'scam-unavailable', 'bridge', 'tunnel'):
          tmp = 0
          for stance in fwFullStat['CVR3']['KBASFAvoidance']['votes'][vote].keys():
            for warnType in fwFullStat['CVR3']['KBASFAvoidance']['votes'][vote][stance].keys():
              tmp += fwFullStat['CVR3']['KBASFAvoidance']['votes'][vote][stance][warnType]
          fwNumCVR3ExBridgeTunnel += tmp
        if vote not in ('fw-red-with-sdf', 'scam-unavailable'):
          tmpOffline = 0
          for stance in fwWithSDF['CVR3']['KBASFAvoidance']['votes'][vote].keys():
            for warnType in fwWithSDF['CVR3']['KBASFAvoidance']['votes'][vote][stance].keys():
              tmpOffline += fwWithSDF['CVR3']['KBASFAvoidance']['votes'][vote][stance][warnType]
          tmpOnline = 0
          for stance in fwWithSDF['CVR3']['CVR3Warning']['votes'][vote].keys():
            for warnType in fwWithSDF['CVR3']['CVR3Warning']['votes'][vote][stance].keys():
              tmpOnline += fwWithSDF['CVR3']['CVR3Warning']['votes'][vote][stance][warnType]
          fwNumCVR3SDF_offline += tmpOffline
          fwNumCVR3SDF_online += tmpOnline

      # count FW occurrences in the case of CVR2 -------------------------------
      fwNumCVR2 = 0
      for vote in fwFullStat['CVR2']['KBASFAvoidance']['votes'].keys():
        if vote not in ('fw-red-with-sdf', 'scam-unavailable', 'bridge', 'tunnel'): # CVR2 is not likely to produce FW at bridges and tunnels
          tmp = 0
          for stance in fwFullStat['CVR2']['KBASFAvoidance']['votes'][vote].keys():
            for warnType in fwFullStat['CVR2']['KBASFAvoidance']['votes'][vote][stance].keys():
              tmp += fwFullStat['CVR2']['KBASFAvoidance']['votes'][vote][stance][warnType]
          fwNumCVR2 += tmp

      # count occurrences where no FW reduction is possible with S-Cam ---------
      fwRedCnt = 0
      for stance in fwFullStat['CVR3']['KBASFAvoidance']['votes']['fw-red-with-sdf'].keys():
        for warnType in fwFullStat['CVR3']['KBASFAvoidance']['votes']['fw-red-with-sdf'][stance].keys():
          fwRedCnt += fwFullStat['CVR3']['KBASFAvoidance']['votes']['fw-red-with-sdf'][stance][warnType]
      noSCamCnt = 0
      for stance in fwFullStat['CVR3']['KBASFAvoidance']['votes']['scam-unavailable'].keys():
        for warnType in fwFullStat['CVR3']['KBASFAvoidance']['votes']['scam-unavailable'][stance].keys():
          noSCamCnt += fwFullStat['CVR3']['KBASFAvoidance']['votes']['scam-unavailable'][stance][warnType]
      noRedPoss = fwNumCVR3 - fwRedCnt - noSCamCnt

      fwRedCntExBriTu = 0
      for stance in fwRedExBridgeTunnelCVR3['CVR3']['KBASFAvoidance']['votes']['fw-red-with-sdf'].keys():
        fwRedCntExBriTu += fwRedExBridgeTunnelCVR3['CVR3']['KBASFAvoidance']['votes']['fw-red-with-sdf'][stance]
      noSCamCntExBriTu = 0
      for stance in fwRedExBridgeTunnelCVR3['CVR3']['KBASFAvoidance']['votes']['scam-unavailable'].keys():
        noSCamCntExBriTu += fwRedExBridgeTunnelCVR3['CVR3']['KBASFAvoidance']['votes']['scam-unavailable'][stance]
      noRedPossExBridgeTunnel = fwNumCVR3ExBridgeTunnel - fwRedCntExBriTu - noSCamCntExBriTu

      # create rows to be written to CSV file ----------------------------------
      csvSumDataRow_FW = [drivenDist['rural'], drivenDist['city'], drivenDist['highway'], fwNumCVR3]
      csvSumHeaderRow_FW = ["Rural km", "City km", "Highway km", "No. of false warnings (CVR3)"]
      csvSumDataRow_SDF_offline = [fwNumCVR3SDF_offline]
      csvSumHeaderRow_SDF_offline = ["No. of false warnings (CVR3)"]
      csvSumDataRow_SDF_online = [fwNumCVR3SDF_online]
      csvSumHeaderRow_SDF_online = ["No. of false warnings (CVR3)"]
      for vote in analyzeAddLabels.VOTES_EXPLAINED.keys():
        if vote not in ('fw-red-with-sdf', 'scam-unavailable'):
          tmpFW = 0
          for stance in fwFullStat['CVR3']['KBASFAvoidance']['votes'][vote].keys():
            for warnType in fwFullStat['CVR3']['KBASFAvoidance']['votes'][vote][stance].keys():
              tmpFW += fwFullStat['CVR3']['KBASFAvoidance']['votes'][vote][stance][warnType]
          csvSumDataRow_FW.append(tmpFW)
          csvSumHeaderRow_FW.append(' '.join([analyzeAddLabels.VOTES_EXPLAINED[vote][0], '(CVR3)']))
          tmpSDF_offline = 0
          for stance in fwWithSDF['CVR3']['KBASFAvoidance']['votes'][vote].keys():
            for warnType in fwWithSDF['CVR3']['KBASFAvoidance']['votes'][vote][stance].keys():
              tmpSDF_offline += fwWithSDF['CVR3']['KBASFAvoidance']['votes'][vote][stance][warnType]
          csvSumDataRow_SDF_offline.append(tmpSDF_offline)
          csvSumHeaderRow_SDF_offline.append(' '.join([analyzeAddLabels.VOTES_EXPLAINED[vote][0], '(CVR3)']))
          tmpSDF_online = 0
          for stance in fwWithSDF['CVR3']['CVR3Warning']['votes'][vote].keys():
            for warnType in fwWithSDF['CVR3']['CVR3Warning']['votes'][vote][stance].keys():
              tmpSDF_online += fwWithSDF['CVR3']['CVR3Warning']['votes'][vote][stance][warnType]
          csvSumDataRow_SDF_online.append(tmpSDF_online)
          csvSumHeaderRow_SDF_online.append(' '.join([analyzeAddLabels.VOTES_EXPLAINED[vote][0], '(CVR3)']))
      tmpSumFW = 0
      for stance in fwFullStat['CVR3']['KBASFAvoidance']['votes']['fw-red-with-sdf'].keys():
        for warnType in fwFullStat['CVR3']['KBASFAvoidance']['votes']['fw-red-with-sdf'][stance].keys():
          tmpSumFW += fwFullStat['CVR3']['KBASFAvoidance']['votes']['fw-red-with-sdf'][stance][warnType]
      tmpSumNoSCam = 0
      for stance in fwFullStat['CVR3']['KBASFAvoidance']['votes']['scam-unavailable'].keys():
        for warnType in fwFullStat['CVR3']['KBASFAvoidance']['votes']['scam-unavailable'][stance].keys():
          tmpSumNoSCam += fwFullStat['CVR3']['KBASFAvoidance']['votes']['scam-unavailable'][stance][warnType]
      csvSumDataRow_FW.extend([tmpSumFW, noRedPoss, tmpSumNoSCam, fwNumCVR2])
      csvSumHeaderRow_FW.extend(["FW red. with SDF (CVR3)", "No red. possible (CVR3)", "No camera available (CVR3)",
                                 "No. of false warnings (CVR2)"])
      csvSumDataRow_SDF_offline.extend([scamAvailable['timeAvailable'], scamAvailable['timeTotal']])
      csvSumHeaderRow_SDF_offline.extend(['Availability time', 'Total time'])
      csvSumDataRow_SDF_online.extend([scamAvailable['timeAvailable'], scamAvailable['timeTotal']])
      csvSumHeaderRow_SDF_online.extend(['Availability time', 'Total time'])
      for vote in analyzeAddLabels.VOTES_EXPLAINED.keys():
        if vote not in ('fw-red-with-sdf', 'scam-unavailable', 'bridge', 'tunnel'):
          tmpFW = 0
          for stance in fwFullStat['CVR2']['KBASFAvoidance']['votes'][vote].keys():
            for warnType in fwFullStat['CVR2']['KBASFAvoidance']['votes'][vote][stance].keys():
              tmpFW += fwFullStat['CVR2']['KBASFAvoidance']['votes'][vote][stance][warnType]
          csvSumDataRow_FW.append(tmpFW)
          csvSumHeaderRow_FW.append(' '.join([analyzeAddLabels.VOTES_EXPLAINED[vote][0], '(CVR2)']))
      csvSumDataRow_FW.extend([fwFullStat['CVR2']['KBASFAvoidance']['classifiers']['wClassObst'],
                               fwFullStat['CVR2']['KBASFAvoidance']['classifiers']['dLength'],
                               fwFullStat['CVR2']['KBASFAvoidance']['classifiers']['dVarYvBase'],
                               fwFullStat['CVR2']['KBASFAvoidance']['classifiers']['wConstElem']])
      csvSumHeaderRow_FW.extend(["wClassObstacle (CVR3)", "dLength (CVR3)", "dVarYvBase (CVR3)", "wConstElem (CVR3)"])
      for vote in analyzeAddLabels.VOTES_EXPLAINED.keys():
        if vote not in ('fw-red-with-sdf', 'scam-unavailable', 'bridge', 'tunnel'):
          tmpCommon = 0
          for stance in fwFullStat['common']['KBASFAvoidance']['votes'][vote].keys():
            tmpCommon += fwFullStat['common']['KBASFAvoidance']['votes'][vote][stance]
          csvSumDataRow_FW.append(tmpCommon)
          csvSumHeaderRow_FW.append(' '.join(['Common', analyzeAddLabels.VOTES_EXPLAINED[vote][0]]))
      csvSumDataRow_FW.extend([availSensor['CVR2'], availSensor['CVR3']])
      csvSumHeaderRow_FW.extend(['CVR2 available', 'CVR3 available'])

      tmpFWredExBriTu = 0
      for stance in fwRedExBridgeTunnelCVR3['CVR3']['KBASFAvoidance']['votes']['fw-red-with-sdf'].keys():
        tmpFWredExBriTu += fwRedExBridgeTunnelCVR3['CVR3']['KBASFAvoidance']['votes']['fw-red-with-sdf'][stance]
      tmpNoSCamExBriTu = 0
      for stance in fwRedExBridgeTunnelCVR3['CVR3']['KBASFAvoidance']['votes']['scam-unavailable'].keys():
        tmpNoSCamExBriTu += fwRedExBridgeTunnelCVR3['CVR3']['KBASFAvoidance']['votes']['scam-unavailable'][stance]
      csvSumDataRow_FWExBridgeTunnel = [fwRedExBridgeTunnelCVR3['CVR2']['KBASFAvoidance']['classifiers']['wClassObst'],
                                        fwRedExBridgeTunnelCVR3['CVR2']['KBASFAvoidance']['classifiers']['dLength'],
                                        fwRedExBridgeTunnelCVR3['CVR2']['KBASFAvoidance']['classifiers']['dVarYvBase'],
                                        fwRedExBridgeTunnelCVR3['CVR2']['KBASFAvoidance']['classifiers']['wConstElem'],
                                        tmpFWredExBriTu,
                                        noRedPossExBridgeTunnel,
                                        tmpNoSCamExBriTu]
      csvSumHeaderRow_FWExBridgeTunnel = ["wClassObstacle (CVR3)", "dLength (CVR3)", "dVarYvBase (CVR3)", "wConstElem (CVR3)",
                                          "FW red. with SDF (CVR3)", "No red. possible (CVR3)", "No camera available (CVR3)"]

      csvSumHeaderRow_FW_categ = ["Kind of warning", "Radar only moving", "Radar only stationary",
                                  "Radar only total", "SDF moving", "SDF stationary", "SDF total"]

      tmpCategRadarFW = {'warn_kind': WARN_TYPES}
      tmpCategSDFFW = {'warn_kind': WARN_TYPES}
      tmpCategRadarFW_KBinfl = {'warn_kind': WARN_TYPES}
      tmpCategSDFFW_KBinfl = {'warn_kind': WARN_TYPES}
      for vote in analyzeAddLabels.VOTES_EXPLAINED.keys():
        if vote not in ('fw-red-with-sdf', 'scam-unavailable'):
          for stance in fwFullStat['CVR3']['KBASFAvoidance']['votes'][vote].keys():
            stanceDictRadar = tmpCategRadarFW.setdefault(stance, [0] * len(WARN_TYPES))
            for warnType in fwFullStat['CVR3']['KBASFAvoidance']['votes'][vote][stance].keys():
              listIndex = WARN_TYPES.index(warnType)
              stanceDictRadar[listIndex] += fwFullStat['CVR3']['KBASFAvoidance']['votes'][vote][stance][warnType]
          for stance in fwWithSDF['CVR3']['KBASFAvoidance']['votes'][vote].keys():
            stanceDictSDF = tmpCategSDFFW.setdefault(stance, [0] * len(WARN_TYPES))
            for warnType in fwWithSDF['CVR3']['KBASFAvoidance']['votes'][vote][stance].keys():
              listIndex = WARN_TYPES.index(warnType)
              stanceDictSDF[listIndex] += fwWithSDF['CVR3']['KBASFAvoidance']['votes'][vote][stance][warnType]
        if vote not in ('fw-red-with-sdf', 'scam-unavailable', 'bridge', 'tunnel'):
          for stance in fwFullStat['CVR3']['KBASFAvoidance']['votes'][vote].keys():
            stanceDictRadar_KBinfl = tmpCategRadarFW_KBinfl.setdefault(stance, [0] * len(WARN_TYPES))
            for warnType in fwFullStat['CVR3']['KBASFAvoidance']['votes'][vote][stance].keys():
              listIndex = WARN_TYPES.index(warnType)
              stanceDictRadar_KBinfl[listIndex] += fwFullStat['CVR3']['KBASFAvoidance']['votes'][vote][stance][warnType]
          for stance in fwWithSDF['CVR3']['KBASFAvoidance']['votes'][vote].keys():
            stanceDictSDF_KBinfl = tmpCategSDFFW_KBinfl.setdefault(stance, [0] * len(WARN_TYPES))
            for warnType in fwWithSDF['CVR3']['KBASFAvoidance']['votes'][vote][stance].keys():
              listIndex = WARN_TYPES.index(warnType)
              stanceDictSDF_KBinfl[listIndex] += fwWithSDF['CVR3']['KBASFAvoidance']['votes'][vote][stance][warnType]

      csvSumDataRow_FW_categ = []
      sumRadar = []
      sumSDF = []
      for warnType in WARN_TYPES:
        IndexRadarFW = tmpCategRadarFW['warn_kind'].index(warnType)
        IndexSDFFW = tmpCategSDFFW['warn_kind'].index(warnType)
        totalRadar = tmpCategRadarFW['Moving'][IndexRadarFW] + tmpCategRadarFW['Stationary'][IndexRadarFW]
        totalSDF = tmpCategSDFFW['Moving'][IndexSDFFW] + tmpCategSDFFW['Stationary'][IndexSDFFW]
        sumRadar.append(totalRadar)
        sumSDF.append(totalSDF)
        csvSumDataRow_FW_categ.append([warnType, tmpCategRadarFW['Moving'][IndexRadarFW],
            tmpCategRadarFW['Stationary'][IndexRadarFW], totalRadar,
            tmpCategSDFFW['Moving'][IndexSDFFW], tmpCategSDFFW['Stationary'][IndexSDFFW],
            totalSDF])
      csvSumDataRow_FW_categ.append(["Total",
                                     sum(tmpCategRadarFW['Moving']),
                                     sum(tmpCategRadarFW['Stationary']),
                                     sum(sumRadar),
                                     sum(tmpCategSDFFW['Moving']),
                                     sum(tmpCategSDFFW['Stationary']),
                                     sum(sumSDF)])

      csvSumDataRow_FW_categ_KB = []
      sumRadar = []
      sumSDF = []
      for warnType in WARN_TYPES:
        IndexRadarFW = tmpCategRadarFW_KBinfl['warn_kind'].index(warnType)
        IndexSDFFW = tmpCategSDFFW_KBinfl['warn_kind'].index(warnType)
        totalRadar = tmpCategRadarFW_KBinfl['Moving'][IndexRadarFW] + tmpCategRadarFW_KBinfl['Stationary'][IndexRadarFW]
        totalSDF = tmpCategSDFFW_KBinfl['Moving'][IndexSDFFW] + tmpCategSDFFW_KBinfl['Stationary'][IndexSDFFW]
        sumRadar.append(totalRadar)
        sumSDF.append(totalSDF)
        csvSumDataRow_FW_categ_KB.append([warnType, tmpCategRadarFW_KBinfl['Moving'][IndexRadarFW],
            tmpCategRadarFW_KBinfl['Stationary'][IndexRadarFW], totalRadar,
            tmpCategSDFFW_KBinfl['Moving'][IndexSDFFW],
            tmpCategSDFFW_KBinfl['Stationary'][IndexSDFFW], totalSDF])
      csvSumDataRow_FW_categ_KB.append(["Total",
                                        sum(tmpCategRadarFW_KBinfl['Moving']),
                                        sum(tmpCategRadarFW_KBinfl['Stationary']),
                                        sum(sumRadar),
                                        sum(tmpCategSDFFW_KBinfl['Moving']),
                                        sum(tmpCategSDFFW_KBinfl['Stationary']),
                                        sum(sumSDF)])

      # write rows to CSV file -------------------------------------------------
      csvWrite = csv.writer(open(os.path.join(csvDir, '%s_FalseWarnings.csv' %measurementDate), 'wb'), delimiter=':', lineterminator='\n')
      csvWrite.writerow(csvSumHeaderRow_FW)
      csvWrite.writerow(csvSumDataRow_FW)

      csvWrite = csv.writer(open(os.path.join(csvDir, '%s_FalseWarningsExBridgeTunnel.csv' %measurementDate), 'wb'), delimiter=':', lineterminator='\n')
      csvWrite.writerow(csvSumHeaderRow_FWExBridgeTunnel)
      csvWrite.writerow(csvSumDataRow_FWExBridgeTunnel)

      csvWrite = csv.writer(open(os.path.join(csvDir, '%s_FalseWarningsWithSDF-OfflineAlgo.csv' %measurementDate), 'wb'), delimiter=':', lineterminator='\n')
      csvWrite.writerow(csvSumHeaderRow_SDF_offline)
      csvWrite.writerow(csvSumDataRow_SDF_offline)

      csvWrite = csv.writer(open(os.path.join(csvDir, '%s_FalseWarningsWithSDF-OnlineAlgo.csv' %measurementDate), 'wb'), delimiter=':', lineterminator='\n')
      csvWrite.writerow(csvSumHeaderRow_SDF_online)
      csvWrite.writerow(csvSumDataRow_SDF_online)

      csvWrite = csv.writer(open(os.path.join(csvDir, '%s_FalseWarningsCategorized.csv' %measurementDate), 'wb'), delimiter=':', lineterminator='\n')
      csvWrite.writerow(csvSumHeaderRow_FW_categ)
      csvWrite.writerows(csvSumDataRow_FW_categ)

      csvWrite = csv.writer(open(os.path.join(csvDir, '%s_FalseWarnCateg-KBinfl.csv' %measurementDate), 'wb'), delimiter=':', lineterminator='\n')
      csvWrite.writerow(csvSumHeaderRow_FW_categ)
      csvWrite.writerows(csvSumDataRow_FW_categ_KB)

      # write data about FW's caused by overhead (bridge) objects --------------
      # sort overheadObjDataCVR3 by measurement file name and time and filter for KBASFAvoidance
      overheadObjDataCVR3_Zipped = zip(overheadObjDataCVR3['measurement'],
                                       overheadObjDataCVR3['startTime'],
                                       overheadObjDataCVR3['endTime'],
                                       overheadObjDataCVR3['test'],
                                       overheadObjDataCVR3['vote'],
                                       overheadObjDataCVR3['cipv_objectID'],
                                       overheadObjDataCVR3['cipv_dx'],
                                       overheadObjDataCVR3['cipv_dy'],
                                       overheadObjDataCVR3['cipv_vrel'],
                                       overheadObjDataCVR3['Latitude'],
                                       overheadObjDataCVR3['Longitude'])
      overheadObjDataCVR3_ZipSortMeas=sorted(overheadObjDataCVR3_Zipped, key=lambda elem: elem[0])

      overheadObjDataCVR3_ZipSort = []
      for meas in sorted(list(set(overheadObjDataCVR3['measurement']))):
        measData = filter(lambda elem: elem[0] == meas, overheadObjDataCVR3_ZipSortMeas)
        measDataSorted = sorted(measData, key=lambda elem: elem[1])
        overheadObjDataCVR3_ZipSort.extend(measDataSorted)

      overheadObjDataCVR3_ZipSortFilt = filter(lambda elem: elem[3] == 'KBASFAvoidance', overheadObjDataCVR3_ZipSort)
      if not overheadObjDataCVR3_ZipSortFilt:
        overheadObjDataCVR3_ZipSortFilt = overheadObjDataCVR3_ZipSort

      (overheadObjDataCVR3['measurement'],
       overheadObjDataCVR3['startTime'],
       overheadObjDataCVR3['endTime'],
       overheadObjDataCVR3['test'],
       overheadObjDataCVR3['vote'],
       overheadObjDataCVR3['cipv_objectID'],
       overheadObjDataCVR3['cipv_dx'],
       overheadObjDataCVR3['cipv_dy'],
       overheadObjDataCVR3['cipv_vrel'],
       overheadObjDataCVR3['Latitude'],
       overheadObjDataCVR3['Longitude']) = zip(*overheadObjDataCVR3_ZipSortFilt)

      csvWrite = csv.writer(open(os.path.join(csvDir, '%s_OverheadObjects.csv' %measurementDate), 'wb'), delimiter=':', lineterminator='\n')
      csvWrite.writerow(['Measurement',
                         'Start time [s]',
                         'Overhead object type',
                         'FUS ID',
                         'dx [m]',
                         'dy [m]',
                         'Relative speed [m/s]',
                         'GPS latitude',
                         'GPS longitude'])
      for index in xrange(len(overheadObjDataCVR3['measurement'])):
        csvWrite.writerow([overheadObjDataCVR3['measurement'][index],
                           overheadObjDataCVR3['startTime'][index],
                           overheadObjDataCVR3['vote'][index],
                           overheadObjDataCVR3['cipv_objectID'][index],
                           overheadObjDataCVR3['cipv_dx'][index],
                           overheadObjDataCVR3['cipv_dy'][index],
                           overheadObjDataCVR3['cipv_vrel'][index],
                           overheadObjDataCVR3['Latitude'][index],
                           overheadObjDataCVR3['Longitude'][index]])

    # categorized list of measurements/times of false warnings -----------------
    csvWrite = csv.writer(open(os.path.join(csvDir, '%s_MeasurementsOfFW.csv' %measurementDate), 'wb'), delimiter=':', lineterminator='\n')
    for sensor, sensorDict in labelResult.iteritems():
      for test, testDict in sensorDict.iteritems():
        for vote, voteDict in testDict.iteritems():
          for measPath, measDict in voteDict.iteritems():
            intListLen = 0
            for intList in measDict.itervalues():
              intListLen += len(intList)
            if intListLen and vote not in ('fw-red-with-sdf', 'scam-unavailable'):
              csvWrite.writerow([sensor, test, vote, os.path.split(measPath)[-1]])

    if Param.showReport:
      BatchNav = self.get_batchnav()
      BatchNav.BatchFrame.addEntries(commonFWGroup)
      BatchNav.CheckMeasExist = False
    pass

