import numpy

import interface
import measproc
from aebs.par import grouptypes
from aebs.proc import AEBSWarningSim

ac100Alias  = 'CW_track'
ac100CWSignalGroups = []
for k in xrange(10):
  ac100CWSignalGroup = {ac100Alias: ('Tracks', 'tr%d_%s' %(k, ac100Alias))}
  ac100CWSignalGroups.append(ac100CWSignalGroup)

egoVehSignalGroups = []
egoVehSignalGroups.append({"vehicle_speed": ("General_radar_status", "actual_vehicle_speed")})

DefParam = interface.NullParam

class cSearch(interface.iSearch):
  dep = ('fillAC100_CW@aebs.fill', 'fillAC100@aebs.fill')
  eventNum = 0 # number of events (dirty hack: accumulates sequential search results)

  def check(self):
    source = self.get_source('main')
    egoVehGroups = source.selectSignalGroup(egoVehSignalGroups)
    ac100CWGroups = source.selectSignalGroup(ac100CWSignalGroups)
    return egoVehGroups, ac100CWGroups

  def fill(self, egoVehGroups, ac100CWGroups):
    source = self.get_source('main')
    modules = self.get_modules()
    ac100TimeCW, ac100ObjCWtmp = modules.fill('fillAC100_CW@aebs.fill')
    ac100TimeTr, ac100ObjTrtmp = modules.fill('fillAC100@aebs.fill')
    ac100ObjCW = list(ac100ObjCWtmp)
    ac100ObjTr = list(ac100ObjTrtmp)

    for index in xrange(len(ac100ObjCWtmp)):
      if ac100ObjCWtmp[index]['label'] == 'AC100_CO':
        for signal in ac100ObjCWtmp[index].keys():
          ac100Time, ac100ObjCW[index][signal] = source.rescale(ac100TimeCW, ac100ObjCWtmp[index][signal], ac100TimeTr)
        ac100ObjCW[index]['cwTrack'] = source.getSignalFromSignalGroup(ac100CWGroups, 'CW_track', ScaleTime=ac100TimeTr)[1]

    egoSpeedSignals = {}
    egoSpeedSignals['AC100'] = source.getSignalFromSignalGroup(egoVehGroups, 'vehicle_speed', ScaleTime=ac100Time)[1]

    return ac100Time, ac100ObjCW, ac100ObjTr, egoSpeedSignals

  def search(self, Param, ac100Time, ac100ObjCW, ac100ObjTr, egoSpeedSignals):
    source = self.get_source('main')
    batch = self.get_batch()

    detectionInfo = {}

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

    j = 0 # we are only interested in first track of AC100 as it is the most relevant
    detectionsAC100 = detectionInfo['AC100'][j] if j in detectionInfo['AC100'].keys() else {'FullDetect': measproc.cIntervalList(ac100Time), 'CWDetect': measproc.cIntervalList(ac100Time)}

    # SAS events ---------------------------------------------------------------
    events = {}
    """ eventNum<int> : event<dict> """
    intervalsAC100 = detectionsAC100['FullDetect']
    if len(intervalsAC100) <= 1:
      event = {}
      """ sensorName<str> : (objID, FullDetectInterval, CWDetectInterval)
      intervals of the sensors might be on different time domain """
      event['AC100'] = j, detectionsAC100['FullDetect'], detectionsAC100['CWDetect']
      events[self.eventNum] = event
      self.eventNum += 1
    else:
      # more than one event for the same object -> skip for now as it is difficult to handle
      print 'Warning: AC100 tr %d object skipped, more than 1 event occurred!' %j

    # store data for each event to file ----------------------------------------
    for k, event in events.iteritems():
      workspaceDetDist = measproc.DinWorkSpace('UseCase_%02d' %k)
      kwargs = {}
      for sensor, (objID, FullDetectInterval, CWDetectInterval) in event.iteritems():
        start, end = FullDetectInterval[0] if len(FullDetectInterval) != 0 else (0, 0)
        FullDetectIntervalExt = FullDetectInterval.addMargin(TimeMargins=(1,0)) # extend interval for display purposes (display signals earlier by 1 sec.)
        startExt, endExt = FullDetectIntervalExt[0] if len(FullDetectIntervalExt) != 0 else (0, 0)
        if sensor == 'AC100':
          dxDet = ac100ObjTr[objID]['dx'][startExt:endExt]
          powerDet = ac100ObjTr[objID]['power'][startExt:endExt]
          timeDet = ac100Time[startExt:endExt]
          vEgo = egoSpeedSignals['AC100'][startExt:endExt] * 3.6
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
        kwargs['powerFull_%s'        %sensor] = powerDet
        kwargs['timeFull_%s'         %sensor] = timeDet
        kwargs['dxFirstDet_%s'       %sensor] = firstDet
        kwargs['dxObsDet_%s'         %sensor] = obsDet
        kwargs['speedReduc_%s'       %sensor] = speedRed
        kwargs['collisionOccured_%s' %sensor] = collision
        if sensor == 'AC100':
          kwargs['egoVel_%s'         %sensor] = vEgo
          kwargs['objIsCW_%s'        %sensor] = cwTrack

        workspaceDetDist.add(**kwargs)
        batch.add_entry(workspaceDetDist, self.NONE)
    return
