# -*- dataeval: init -*-

import numpy as np

import interface
import measparser


SignalGroups =  [ { 'PO_target_range_OFC':        ('Iteris_object_follow', 'PO_target_range_OFC'),
                    'PO_right_azimuth_angle_OFC': ('Iteris_object_follow', 'PO_right_azimuth_angle_OFC'),
                    'OI_PO_target_speed':         ('OI_PO',                'target_speed')
                  },
                ]

class cFill(interface.iObjectFill):
  def check(self):
    SignalGroup = interface.Source.selectSignalGroup(SignalGroups)
    return SignalGroup

  def fill(self, SignalGroup):
    Signals = measparser.signalgroup.extract_signals(SignalGroup)
    scaletime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    #---data from Iteris
    time, target_range  = interface.Source.getSignalFromSignalGroup(SignalGroup, 'PO_target_range_OFC',        ScaleTime=scaletime)
    time, angle         = interface.Source.getSignalFromSignalGroup(SignalGroup, 'PO_right_azimuth_angle_OFC', ScaleTime=scaletime)
    #----data from LRR3
    time, rangerate     = interface.Source.getSignalFromSignalGroup(SignalGroup, 'OI_PO_target_speed',         ScaleTime=scaletime)
    #----
    o={}
    #o["time"]=time_Iteris
    o["dx"]=target_range*np.cos(angle*(np.pi/180.0))
    o["dy"]=target_range*np.sin(angle*(np.pi/180.0))
    o["rangerate"]=rangerate
    o["label"]="Iteris_PO"
    o["type"]=self.get_grouptype('ITERIS')
    w = np.reshape(np.repeat(o["rangerate"] < 0, 3), (-1,3))
    o["color"] = np.where(w,[255, 0, 0],[0, 255, 0])

    Objects=[]
    Objects.append(o)
    return scaletime, Objects
