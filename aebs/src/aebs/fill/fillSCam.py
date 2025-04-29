# -*- dataeval: init -*-

import numpy as np

import interface
import measparser

SCAM_OBS_NUM = 10

STATUS_STANDING = 1
STATUS_ONCOMING = 4
STATUS_PARKED   = 5

signalGroups = [{'baseTimeSignal' : ('Obstacle_Status', 'Num_Obstacles')},]

# assumption: these signals are all from "Obstacle_[01-10]_Data_A" messages
signalNames = 'ID',\
              'Pos_X',\
              'Pos_Y',\
              'Vel_X',\
              'Status'
groupLen = len(signalNames)
# create message signal groups
messageSignalGroups = []
for k in xrange(1, SCAM_OBS_NUM+1):
  signalGroup = {}
  ShortDeviceName = 'Obstacle_%02d_Data_A' %k
  for signalName in signalNames:
    signalGroup[signalName] = (ShortDeviceName, signalName)
  messageSignalGroups.append(signalGroup)
                     
  
class cFill(interface.iObjectFill):
  def check(self):
    # process signal groups
    baseGroup = interface.Source.selectSignalGroup(signalGroups)
    groups, errors = interface.Source._filterSignalGroups(messageSignalGroups)
    measparser.signalgroup.check_onevalid(groups, errors, groupLen)
    return baseGroup, groups

  def fill(self, baseGroup, groups):
    signalsExtr = measparser.signalgroup.extract_signals(signalGroups)
    scaleTime = interface.Source.selectScaleTime(signalsExtr, interface.StrictlyGrowingTimeCheck)
    objects = []
    # put all signals to common message time
    messageTime = interface.Source.getSignalFromSignalGroup(baseGroup, 'baseTimeSignal')[0]
    for k, group in enumerate(groups):
      # skip track if its signals are not present
      if len(group) != groupLen:
        continue
      # convert signals to common message time
      signals = {} # { signalName<str> : signalOnCommonMessageTime<ndarrray> }
      timeOrig, id = interface.Source.getSignalFromSignalGroup(group, 'ID')
      for signalName in signalNames:
        signalOrig = interface.Source.getSignalFromSignalGroup(group, signalName)[1]
        if timeOrig is not messageTime:
          indices = measparser.signalproc.mapTimeToScaleTime(messageTime, timeOrig)
          signalNew  = np.zeros_like(messageTime, dtype=signalOrig.dtype)
          signalNew[indices] = signalOrig
        else:
          signalNew = signalOrig
        signals[signalName] = signalNew
      # rescale all signals
      rescaledSignals = {} # { signalName<str> : signalRescaled<ndarrray> }
      for signalName, signalNew in signals.iteritems():
        _, signal = measparser.signalproc.rescale(messageTime, signalNew, scaleTime)
        rescaledSignals[signalName] = signal
      # create objects
      id     = rescaledSignals['ID']
      status = rescaledSignals['Status']
      o = {}
      o["id"] = id
      labelList  = map(lambda index: "S-CAM_%d" %index, id)
      o["label"] = np.array(labelList)
      o["dx"]  = rescaledSignals['Pos_X']
      o["dy"]  = rescaledSignals['Pos_Y']
      o["dvx"] = rescaledSignals['Vel_X']
      # calculate signal used for selection
      maskStat = (status == STATUS_STANDING) | (status == STATUS_PARKED)
      maskOnco = status == STATUS_ONCOMING
      o["type"] = np.where( maskStat, 
                            self.get_grouptype('SCAM_STAT'), 
                            self.get_grouptype('SCAM_MOV'))
      # colors: moving-green    stat-red    ongoing-blue
      maskStat3D = np.repeat(maskStat[:,np.newaxis], 3, axis=1)
      maskOnco3D = np.repeat(maskOnco[:,np.newaxis], 3, axis=1)
      o["color"] = np.where( maskStat3D, (255, 0, 0), (0, 255, 0) )
      o["color"] = np.where( maskOnco3D, (0, 0, 255), o["color"]  )
      objects.append(o)
    return scaleTime, objects
