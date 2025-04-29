# -*- dataeval: init -*-

import numpy as np

import interface
import measparser

REALY_IMPORTANT_NUMBER = 10

# obsolated
SignalGroups =  [{'dummy': ['obstacle_0_info','Distance_to_Obstacle_0']}, ]
# obsolated

class cFill(interface.iObjectFill):
  def check(self):
    SignalGroups = []
    Aliases = 'Distance_to_Obstacle', 'Angle_to_obstacle', 'Relative_velocity_to_obstacle'
    for i in xrange(REALY_IMPORTANT_NUMBER):
      try:
        DeviceName, = interface.Source.getDeviceNames("Distance_to_Obstacle_%d"%i)
      except ValueError:
        raise measparser.signalgroup.SignalGroupError('No device for Distance_to_Obstacle_%d' %i)
      SignalGroup = {}
      for Alias in Aliases:
        SignalGroup[Alias] = DeviceName, '%s_%i' %(Alias, i)
      SignalGroups.append(SignalGroup)
    Groups, Errors = interface.Source._filterSignalGroups(SignalGroups)
    measparser.signalgroup.check_allvalid(Groups, Errors, len(Aliases))
    return Groups
    
  def fill(self, Groups):
    Signals = measparser.signalgroup.extract_signals(Groups)
    scaletime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    Objects=[]
    for i in xrange(REALY_IMPORTANT_NUMBER):
      Group = Groups[i]
      o={}
      time, distance = interface.Source.getSignalFromSignalGroup(Group, 'Distance_to_Obstacle',          ScaleTime=scaletime)
      angle          = interface.Source.getSignalFromSignalGroup(Group, 'Angle_to_obstacle',             ScaleTime=scaletime)[1]
      rangerate      = interface.Source.getSignalFromSignalGroup(Group, 'Relative_velocity_to_obstacle', ScaleTime=scaletime)[1]
      o={}
      o["time"]             =time
      o["dx"]               =distance*np.cos(angle*(np.pi/180.0))
      o["dy"]               =-distance*np.sin(angle*(np.pi/180.0))
      o["rangerate"]        =rangerate
      o["label"]            ="MobilEye_%d"%i
      
      o["type"] = self.get_grouptype('MOBILEYE')
      
      w = np.reshape(np.repeat(o["rangerate"] < 0, 3), (-1,3))
      o["color"] = np.where(w,[255, 0, 0],[0, 255, 0])
      o["label"] = "MobilEye_%d"%i
      Objects.append(o)
    return scaletime, Objects
