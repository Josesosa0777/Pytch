import interface
import measproc
import numpy

FUS_OBJ_NUM = 32
N_AC100_TR = 5 # 10

CVR3SignalTemplates = ('dxv'          ,
                       'dyv'          ,
                       'vxv'          ,
                       'vyv'          ,
                       'wExistProb'   ,
                       'wGroundReflex',
                       'wObstacle'    ,
                       'vVarYv'       ,
                       'CntAlive'     ,
                       'b.b.Stand_b'  ,
                       'b.b.Drive_b'  ,
                       'Handle'
                       )

cvr3DeviceNames = ('MRR1plus', 'RadarFC')

AC100SignalTemplates = ('range'                 ,
                        'uncorrected_angle'     ,
                        'power'                 ,
                        'credibility'           ,
                        'internal_track_index'  ,
                        'track_selection_status',
                        'CW_track'              ,
                        'acc_track_info'
                        )

CVR3SignalGroups = []
for CVR3DeviceName in cvr3DeviceNames:
  tmpSignalGroup = {}
  for index in xrange(FUS_OBJ_NUM):
    for signaltemplate in CVR3SignalTemplates:
      tmpSignalGroup['fus.ObjData_TC.FusObj.i%s.%s' % (index, signaltemplate)] = (CVR3DeviceName, 'fus.ObjData_TC.FusObj.i%s.%s' % (index, signaltemplate))
  tmpSignalGroup['sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i0'] = (CVR3DeviceName, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i0')
  tmpSignalGroup['sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i1'] = (CVR3DeviceName, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i1')
  tmpSignalGroup['sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i2'] = (CVR3DeviceName, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i2')
  tmpSignalGroup['sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i3'] = (CVR3DeviceName, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i3')
  tmpSignalGroup['sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i4'] = (CVR3DeviceName, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i4')
  tmpSignalGroup['sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i5'] = (CVR3DeviceName, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i5')
  CVR3SignalGroups.append(tmpSignalGroup)

AC100SignalGroups = {}
for index in xrange(N_AC100_TR):
  for signaltemplate in AC100SignalTemplates:
    AC100SignalGroups['tr%s_%s' % (index, signaltemplate)] = ('Tracks', 'tr%s_%s' % (index, signaltemplate))
AC100SignalGroups['cm_collision_warning'] = ('General_radar_status', 'cm_collision_warning')
AC100SignalGroups['cm_deceleration_demand'] = ('General_radar_status', 'cm_deceleration_demand')
AC100SignalGroups = [AC100SignalGroups, ]

EgoVehSignalGroups = []
for CVR3DeviceName in cvr3DeviceNames:
  EgoVehSignalGroup = {'evi.General_T20.vxvRef': (CVR3DeviceName, 'evi.General_T20.vxvRef')}
  EgoVehSignalGroups.append(EgoVehSignalGroup)

# module parameter class creation --------------------------------------------------------
class cParameter(interface.iParameter):
  def __init__(self, objNature):
    self.objNature = objNature  # value should be either 'Stationary' or 'Moving'
    self.genKeys()
    pass

# instantiation of module parameters ----------------------------------------------------- 
searchStationaryObjDet = cParameter('Stationary')
searchMovingObjDet = cParameter('Moving')

class cSearch(interface.iSearch):
  def check(self):
    Source = self.get_source('main')
    CVR3Groups = Source.selectSignalGroup(CVR3SignalGroups)
    EgoVehGroups = Source.selectSignalGroup(EgoVehSignalGroups)
    AC100Groups = Source.selectSignalGroup(AC100SignalGroups)
    return CVR3Groups, AC100Groups, EgoVehGroups

  def fill(self, CVR3Groups, AC100Groups, EgoVehGroups):
    return CVR3Groups, AC100Groups, EgoVehGroups

  def search(self, Param, CVR3Groups, AC100Groups, EgoVehGroups):
    # search object detection and classification (as obstacle) - CVR3 ----------
    Source = self.get_source('main')
    CVR3Intervals = {}
    CVR3Findings = {}
    for index in xrange(FUS_OBJ_NUM):
      CVR3Value = {}
      for signaltemplate in CVR3SignalTemplates:
        CVR3Time, CVR3Value[signaltemplate] = Source.getSignalFromSignalGroup(CVR3Groups, 'fus.ObjData_TC.FusObj.i%s.%s' % (index, signaltemplate))

      Time, CVR3Value['L1_handle'] = Source.getSignalFromSignalGroup(CVR3Groups, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i0', ScaleTime=CVR3Time)
      Time, CVR3Value['S1_handle'] = Source.getSignalFromSignalGroup(CVR3Groups, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i1', ScaleTime=CVR3Time)
      Time, CVR3Value['R1_handle'] = Source.getSignalFromSignalGroup(CVR3Groups, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i2', ScaleTime=CVR3Time)
      Time, CVR3Value['L2_handle'] = Source.getSignalFromSignalGroup(CVR3Groups, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i3', ScaleTime=CVR3Time)
      Time, CVR3Value['S2_handle'] = Source.getSignalFromSignalGroup(CVR3Groups, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i4', ScaleTime=CVR3Time)
      Time, CVR3Value['R2_handle'] = Source.getSignalFromSignalGroup(CVR3Groups, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i5', ScaleTime=CVR3Time)

      EgoSpeedTime, EgoSpeedValue = Source.getSignalFromSignalGroup(EgoVehGroups, 'evi.General_T20.vxvRef', ScaleTime=Time)
      EgoSpeedNZInt = Source.compare(EgoSpeedTime, EgoSpeedValue, measproc.greater, 15 / 3.6)

      CVR3ObstacleInt = Source.compare(Time, CVR3Value['wObstacle'], measproc.greater, 0.7)
      S1Mask = numpy.logical_and(CVR3Value['S1_handle'] > 0, CVR3Value['S1_handle'] == CVR3Value['Handle'])
      L1Mask = numpy.logical_and(CVR3Value['L1_handle'] > 0, CVR3Value['L1_handle'] == CVR3Value['Handle'])
      CVR3HandleS1Int = Source.compare(Time, S1Mask, measproc.not_equal, 0)
      CVR3HandleL1Int = Source.compare(Time, L1Mask, measproc.not_equal, 0)
      CVR3HandlesInt = CVR3HandleS1Int.union(CVR3HandleL1Int)

      if Param.objNature == 'Stationary':
        if numpy.any(CVR3Value['dxv'] > 80) and \
            numpy.any(CVR3Value['b.b.Stand_b'] > 0) and \
            numpy.any(CVR3Value['wObstacle'] > 0.4) and \
            numpy.any(CVR3Value['CntAlive'] > 40):
          CVR3StanceInt = Source.compare(Time, CVR3Value['b.b.Stand_b'], measproc.not_equal, 0)
          CVR3SelectedInt = measproc.cIntervalList(Time)

          # after pre-selection of fusion objects find appropriate interval
          for Lower, Upper in CVR3StanceInt.intersect(EgoSpeedNZInt):
            for ObsLower, ObsUpper in CVR3ObstacleInt.intersect(EgoSpeedNZInt).drop(0.6):
              for HandleLower, HandleUpper in CVR3HandlesInt.intersect(EgoSpeedNZInt):
                if ObsLower >= Lower and ObsLower < Upper and \
                    ObsUpper > Lower and ObsUpper <= Upper and \
                    HandleLower >= Lower and HandleLower < Upper and \
                    HandleUpper > Lower and HandleUpper <= Upper and \
                    CVR3Value['CntAlive'][Lower] < 10 and CVR3Value['CntAlive'][Upper - 1] > 40:
                  CVR3SelectedInt.add(Lower, Upper)

          # remove duplicate interval findings and store them for corresponding fusion object
          CVR3Intervals[index] = CVR3SelectedInt.merge(0)

          # store dx signal values at first object detection and classification as obstacle
          dx_Det = []
          dx_Obs = []
          for interval in CVR3Intervals[index]:
            TmpInterval = measproc.cIntervalList(Time)
            TmpInterval.add(interval[0], interval[1])
            tmp = CVR3ObstacleInt.drop(0.6).intersect(TmpInterval).merge(0.3)
            dx_Det.append(CVR3Value['dxv'][interval[0]])
            if len(tmp) != 0:
              dx_Obs.append(CVR3Value['dxv'][tmp[0][0]])
            CVR3Findings[index] = {'dx_Detected': dx_Det, 'dx_AsObstacle': dx_Obs}

      elif Param.objNature == 'Moving':
        if numpy.any(CVR3Value['CntAlive'] > 40) and \
            numpy.any(CVR3Value['b.b.Drive_b'] > 0) and \
            numpy.any(CVR3Value['wObstacle'] > 0.4):
          CVR3StanceInt = Source.compare(Time, CVR3Value['b.b.Drive_b'], measproc.not_equal, 0)
          CVR3SelectedInt = measproc.cIntervalList(Time)

          # after pre-selection of fusion objects find appropriate interval
          for Lower, Upper in CVR3StanceInt.intersect(EgoSpeedNZInt):
            for ObsLower, ObsUpper in CVR3ObstacleInt.intersect(EgoSpeedNZInt).drop(0.6):
              for HandleLower, HandleUpper in CVR3HandlesInt.intersect(EgoSpeedNZInt):
                if ObsLower >= Lower and ObsLower < Upper and \
                    ObsUpper > Lower and ObsUpper <= Upper and \
                    HandleLower >= Lower and HandleLower < Upper and \
                    HandleUpper > Lower and HandleUpper <= Upper and \
                    CVR3Value['CntAlive'][Lower] < 10 and CVR3Value['CntAlive'][Upper - 1] > 40:
                  CVR3SelectedInt.add(Lower, Upper)

          # remove duplicate interval findings and store them for corresponding fusion object
          CVR3Intervals[index] = CVR3SelectedInt.merge(0)

          # store dx signal values at first object detection and classification as obstacle
          dx_Det = []
          dx_Obs = []
          for interval in CVR3Intervals[index]:
            TmpInterval = measproc.cIntervalList(Time)
            TmpInterval.add(interval[0], interval[1])
            tmp = CVR3ObstacleInt.drop(0.6).intersect(TmpInterval).merge(0.3)
            dx_Det.append(CVR3Value['dxv'][interval[0]])
            if len(tmp) != 0:
              dx_Obs.append(CVR3Value['dxv'][tmp[0][0]])
            CVR3Findings[index] = {'dx_Detected': dx_Det, 'dx_AsObstacle': dx_Obs}

    # search object detection and classification (as obstacle) - AC100 ---------
    # NOTE: only track ID 0 is used (as it is the most relevant) 
    AC100Intervals = {}
    AC100Findings = {}
    AC100Value = {}
    AC100ValueTmp = {}
    for signaltemplate in AC100SignalTemplates:
      try:
        Time, AC100ValueTmp[signaltemplate] = Source.getSignalFromSignalGroup(AC100Groups, 'tr%s_%s' % (0, signaltemplate))
        AC100TrackTime = Time
      except KeyError:
        pass

    for signaltemplate in ('collision_warning', 'deceleration_demand'):
      try:
        Time, AC100ValueTmp[signaltemplate] = Source.getSignalFromSignalGroup(AC100Groups, 'cm_%s' % signaltemplate, ScaleTime=AC100TrackTime)
      except KeyError:
        pass

    EgoSpeedTime, EgoSpeedValue = Source.getSignalFromSignalGroup(EgoVehGroups, 'evi.General_T20.vxvRef', ScaleTime=AC100TrackTime)
    EgoSpeedNZInt = Source.compare(EgoSpeedTime, EgoSpeedValue, measproc.greater, 15 / 3.6)

    AngleRad = numpy.radians(AC100ValueTmp['uncorrected_angle'])
    AC100Value['dx'] = AC100ValueTmp['range'] * numpy.cos(AngleRad)
    AC100Value['dy'] = -AC100ValueTmp['range'] * numpy.sin(AngleRad)
    AC100Value['power'] = AC100ValueTmp['power']
    AC100Value['credibility'] = AC100ValueTmp['credibility'] / float(2 ** 6 - 1)
    AC100Value['internal_track_index'] = AC100ValueTmp['internal_track_index']
    AC100Value['track_selection_status'] = AC100ValueTmp['track_selection_status']
    AC100Value['CW_track'] = AC100ValueTmp['CW_track']
    AC100Value['acc_track_info'] = AC100ValueTmp['acc_track_info']
    AC100Value['collision_warning'] = AC100ValueTmp['collision_warning']
    AC100Value['deceleration_demand'] = AC100ValueTmp['deceleration_demand']
    
    if Param.objNature == 'Stationary':
      stancetmp = AC100Value['track_selection_status'] & (2 ** 4)
      AC100StanceInt = Source.compare(Time, stancetmp, measproc.not_equal, 0)
    elif Param.objNature == 'Moving':
      stancetmp = AC100Value['track_selection_status'] & (2 ** 3)
      AC100StanceInt = Source.compare(Time, stancetmp, measproc.not_equal, 0)

    inlanetmp = AC100Value['track_selection_status'] & (2 ** 2)
    AC100ObjIsInlane = Source.compare(Time, inlanetmp, measproc.not_equal, 0)

    AC100CredibleInt = Source.compare(Time, AC100Value['credibility'], measproc.greater, 0.8)
    AC100CollWarnInt = Source.compare(Time, AC100Value['collision_warning'], measproc.not_equal, 0)
    AC100ObstacleInt = Source.compare(Time, AC100Value['CW_track'], measproc.not_equal, 0)

    # get intervals where dx strictly monotonically decreases
    dxdiff = numpy.diff(AC100Value['dx'])
    mask1 = numpy.zeros_like(Time)
    mask2 = numpy.zeros_like(Time)
    mask1[:-1] = numpy.logical_and(dxdiff < 0, numpy.abs(dxdiff) < 2.5) # add intervals to list which contain monotonically decreasing (not more than 2.5 m) sections of dx
    mask2[:-1] = numpy.logical_and(dxdiff > 0, numpy.abs(dxdiff) < 2.5) # allow +/- 2.5 m inaccuracy 
    dx_mask = numpy.logical_or(mask1, mask2)
    AC100dxMonDecInt = Source.compare(Time, dx_mask, measproc.not_equal, 0)

    AC100SelectedInt = measproc.cIntervalList(Time)
    
    # select the AC100dxMonDecInt intervals where the normalized credibility rises above 0.8
    CreddxMonDecInt = measproc.cIntervalList(Time)
    for dxLower, dxUpper in AC100dxMonDecInt.intersect(EgoSpeedNZInt):
      for credLower, credUpper in AC100CredibleInt.intersect(EgoSpeedNZInt):
        if credLower >= dxLower and credLower < dxUpper and \
            (AC100TrackTime[dxUpper] - AC100TrackTime[dxLower]) > 2.0:
          CreddxMonDecInt.add(dxLower, dxUpper)

    # select the CreddxMonDecInt intervals (after removal of duplicates) where the object has been identified as an obstacle
    for ObsLower, ObsUpper in CreddxMonDecInt.merge(0).intersect(AC100ObstacleInt.union(AC100ObjIsInlane).intersect(EgoSpeedNZInt).drop(0.2)):
      for credLower, credUpper in CreddxMonDecInt.merge(0):
        if ObsLower >= credLower and ObsLower < credUpper and \
            ObsUpper > credLower and ObsUpper <= credUpper:
          AC100SelectedInt.add(credLower, credUpper)

    # after removal of duplicates store the found intervals that correspond to the appropriate object stance 
    AC100Intervals[0] = AC100StanceInt.intersect(AC100SelectedInt.merge(0))

    # store dx signal values at first object detection, classification as obstacle and warning
    dx_Det = []
    dx_Obs = []
    dx_CW = []
    for interval in AC100Intervals[0]:
      TmpInterval = measproc.cIntervalList(Time)
      TmpInterval.add(interval[0], interval[1])
      dx_Det.append(AC100Value['dx'][interval[0]])
      tmp = TmpInterval.intersect(AC100ObstacleInt)
      if len(tmp) != 0:
        dx_Obs.append(AC100Value['dx'][tmp[0][0]])
      tmp = TmpInterval.intersect(AC100CollWarnInt)
      if len(tmp) != 0:
        dx_CW.append(AC100Value['dx'][tmp[0][0]])
    AC100Findings[0] = {'dx_Detected':dx_Det, 'dx_AsObstacle':dx_Obs, 'dx_CW':dx_CW}

    # create reports -----------------------------------------------------------
    Reports = []
    Results = []
    for CVR3Idx in CVR3Intervals.keys():
      if len(CVR3Intervals[CVR3Idx]) != 0:
        Reports.append(measproc.cIntervalListReport(CVR3Intervals[CVR3Idx], '%s - CVR3_FUS_%s - Found (relevant %s object detection)' % (Source.BackupParser.Measurement, CVR3Idx, Param.objNature)))
        Results.append(self.PASSED)
      else:
        Reports.append(measproc.cEmptyReport('%s - CVR3_FUS_%s - Not found (relevant %s object detection)' % (Source.BackupParser.Measurement, CVR3Idx, Param.objNature)))
        Results.append(self.FAILED)

    if len(AC100Intervals[0]) != 0:
      Reports.append(measproc.cIntervalListReport(AC100Intervals[0], '%s - AC100_Track_%s - Found (relevant %s object detection)' % (Source.BackupParser.Measurement, 0, Param.objNature)))
      Results.append(self.PASSED)
    else:
      Reports.append(measproc.cEmptyReport('%s - AC100_Track_%s - Not found (relevant %s object detection)' % (Source.BackupParser.Measurement, 0, Param.objNature)))
      Results.append(self.FAILED)

    Batch = self.get_batch()
    for Report, Result in zip(Reports, Results):
      Batch.add_entry(Report, Result)

    # save results to mat file -------------------------------------------------
    # NOTE: Produces usable results for measurement files that have one relevant
    # object with one interval (only likely with test track measurements). This
    # is needed for the proper comparison of the sensors.
    
    ResultsWorkSpace = measproc.DinWorkSpace('%s - Use Case Evaluation Results (%s)' % (Source.BackupParser.Measurement, Param.objNature))
    if len(CVR3Findings.keys()) == 1 and len(AC100Findings.keys()) == 1 and len(AC100Findings[0]['dx_Detected']) == 1:
      CVR3ID = CVR3Findings.keys()[0]
      AC100ID = AC100Findings.keys()[0]
      ResultsWorkSpace.add(CVR3_dxDet=CVR3Findings[CVR3ID]['dx_Detected'], CVR3_dxAsObs=CVR3Findings[CVR3ID]['dx_AsObstacle'], AC100_dxDet=AC100Findings[AC100ID]['dx_Detected'], AC100_dxAsObs=AC100Findings[AC100ID]['dx_AsObstacle'], AC100_dxCW=AC100Findings[AC100ID]['dx_CW'], ResError=[])
    
    elif len(CVR3Findings.keys()) == 0 and len(AC100Findings.keys()) == 0:
      ResultsWorkSpace.add(CVR3_dxDet=[], CVR3_dxAsObs=[], AC100_dxDet=[], AC100_dxAsObs=[], AC100_dxCW=[], ResError='No relevant object found for both CVR3 and AC100!')
    
    elif len(CVR3Findings.keys()) > 1 and len(AC100Findings.keys()) > 1:
      ResultsWorkSpace.add(CVR3_dxDet=[], CVR3_dxAsObs=[], AC100_dxDet=[], AC100_dxAsObs=[], AC100_dxCW=[], ResError='More than one relevant objects found for both CVR3 and AC100!')
    
    elif len(CVR3Findings.keys()) == 0 and len(AC100Findings.keys()) == 1:
      AC100ID = AC100Findings.keys()[0]
      ResultsWorkSpace.add(CVR3_dxDet=[], CVR3_dxAsObs=[], AC100_dxDet=AC100Findings[AC100ID]['dx_Detected'], AC100_dxAsObs=AC100Findings[AC100ID]['dx_AsObstacle'], AC100_dxCW=AC100Findings[AC100ID]['dx_CW'], ResError='No relevant object found for CVR3 but AC100 is OK!')
    
    elif len(AC100Findings.keys()) == 0:
      CVR3ID = CVR3Findings.keys()[0]
      ResultsWorkSpace.add(CVR3_dxDet=CVR3Findings[CVR3ID]['dx_Detected'], CVR3_dxAsObs=CVR3Findings[CVR3ID]['dx_AsObstacle'], AC100_dxDet=[], AC100_dxAsObs=[], AC100_dxCW=[], ResError='No relevant object found for AC100 but CVR3 is OK!')
    
    elif len(CVR3Findings.keys()) > 1:
      AC100ID = AC100Findings.keys()[0]
      ResultsWorkSpace.add(CVR3_dxDet=[], CVR3_dxAsObs=[], AC100_dxDet=AC100Findings[AC100ID]['dx_Detected'], AC100_dxAsObs=AC100Findings[AC100ID]['dx_AsObstacle'], AC100_dxCW=AC100Findings[AC100ID]['dx_CW'], ResError='More than one relevant objects found for CVR3 but AC100 is OK!')
      
    elif len(AC100Findings.keys()) > 1:
      CVR3ID = CVR3Findings.keys()[0]
      ResultsWorkSpace.add(CVR3_dxDet=CVR3Findings[CVR3ID]['dx_Detected'], CVR3_dxAsObs=CVR3Findings[CVR3ID]['dx_AsObstacle'], AC100_dxDet=[], AC100_dxAsObs=[], AC100_dxCW=[], ResError='More than one relevant objects found for AC100 but CVR3 is OK!')
    else:
      ResultsWorkSpace.add(CVR3_dxDet=[], CVR3_dxAsObs=[], AC100_dxDet=[],
                           AC100_dxAsObs=[], AC100_dxCW=[], ResError='unknown')
    
    Batch.add_entry(ResultsWorkSpace, self.NONE)
