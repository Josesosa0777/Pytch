# -*- dataeval: init -*-

import sys

import interface
import measproc
import measparser
import fillAC100

Alias  = 'CW_track'
SignalGroups = []
for k in xrange(fillAC100.N_AC100_TR):
  SignalGroup = {Alias: ('Tracks', 'tr%d_%s' %(k, Alias))}
  SignalGroups.append(SignalGroup)

WarningSignalGroups = [{ "cm_collision_warning":  ("General_radar_status", "cm_collision_warning"),
                         "cm_mitigation_braking": ("General_radar_status", "cm_mitigation_braking"),
                         "cm_emergency_braking":  ("General_radar_status", "cm_emergency_braking"),}]

class cFill(interface.iObjectFill):
  dep = 'fillAC100',
  def check(self):
    Groups, Errors = interface.Source._filterSignalGroups(SignalGroups)
    measparser.signalgroup.check_onevalid(Groups, Errors, 1)
    return Groups

  def fill(self, Groups):
    Keys = 'dx', 'dy', 'vx', 'vy', 'ax', 'type', 'aeb_track', 'color', 'id', 'stand'
    Time, Objects = interface.Objects.fill('fillAC100')
    CWO =  measproc.Object.initObject(Objects[0], Keys, type=self.get_grouptype('NONE_TYPE'))
    CWO['label'] = 'AC100_CO'
    for Object in Objects:
      Track = Object['track']
      Group = Groups[Track]
      CW = interface.Source.getSignalFromSignalGroup(Group, Alias, ScaleTime=Time)[1]
      MaskCW = CW == 1
      measproc.Object.copyObject(Object, CWO, MaskCW, Keys, type=self.get_grouptype('AC100_CO'))
    colwar = None
    try:
      WarningGroup = interface.Source.selectSignalGroup(WarningSignalGroups)
    except measparser.signalgroup.SignalGroupError:
      print >> sys.stderr, 'AC100 warnings cannot be displayed due to missing signals.'
    else:
      colwar =  measproc.Object.initObject(CWO, Keys, type=self.get_grouptype('NONE_TYPE'))
      CMW  = interface.Source.getSignalFromSignalGroup(WarningGroup, 'cm_collision_warning', ScaleTime=Time)[1]
      CMM  = interface.Source.getSignalFromSignalGroup(WarningGroup, 'cm_mitigation_braking', ScaleTime=Time)[1]
      CME  = interface.Source.getSignalFromSignalGroup(WarningGroup, 'cm_emergency_braking', ScaleTime=Time)[1]
      colwar['label'] = 'AC100_CW'
      Mask = ((CMW == 1) | (CMM == 1) | (CME == 1))
      measproc.Object.copyObject(CWO, colwar, Mask, Keys, type=self.get_grouptype('AC100_CW'))
      colwar['cw'] = CMW
      colwar['pb'] = CMM
      colwar['eb'] = CME
      CWO['cw'] = CMW
      CWO['pb'] = CMM
      CWO['eb'] = CME
    if colwar is not None:
      CWObjects = [CWO, colwar]
    else:
      CWObjects = [CWO]
    return Time, CWObjects
