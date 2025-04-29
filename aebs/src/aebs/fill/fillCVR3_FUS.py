# -*- dataeval: init -*-

import numpy as np

import interface
import measparser

FUS_OBJ_NUM = 33 # 0..31: regular, 32: external fus object
OHY_OBJ_NUM = 40
VID_OBJ_NUM = 10

RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)

fusOldTemplate       = "CVR3_FUS_%d"
fusRadarOnlyTemplate = "CVR3_FUS_%d_r%d"
fusVideoOnlyTemplate = "CVR3_FUS_%d_v%d"
fusAssoLabelTemplate = "CVR3_FUS_%d_r%d_v%d"
fusUnknown           = "CVR3_FUS_%d_?"

aliases = 'dxv',\
          'dyv',\
          'vxv',\
          'vyv',\
          'Handle',\
          'b.b.Stand_b',\
          'b.b.DriveInvDir_b',\
          'wExistProbBase'
# optional signals (object index must be after signal name)
optaliases = 'fus_asso_mat.LrrObjIdx',\
             'fus_s_asso_mat.VidObjIdx'

devicenames = "MRR1plus", "RadarFC"

SignalGroupsDict = {}
OptGroupsDict = {}
for dn in devicenames:
  sglist  = []
  optlist = []
  for i in xrange(FUS_OBJ_NUM):
    # mandatory signals
    signalGroup = {}
    for alias in aliases: 
      signalGroup[alias] = dn, 'fus.ObjData_TC.FusObj.i%d.%s' %(i, alias)
    sglist.append(signalGroup)
    # optional signals
    optGroup = {}
    if i == FUS_OBJ_NUM-1:
      # external (video-only) fus object
      optGroup['ExtVidObjIdx'] = dn, 'fus_s_asso_mat.ExtVidObjIdx'
      optGroup['Handle'] = dn, 'fus.ObjData_TC.FusObj.i%d.Handle' %i # unused, but declared since num of signals in optGroup-s must agree
    else:
      # regular (radar-only or associated) fus object
      for alias in optaliases:
        optGroup[alias] = dn, '%s.i%d' %(alias, i)
    optlist.append(optGroup)
  SignalGroupsDict[dn] = sglist
  OptGroupsDict[dn]    = optlist

def prepareLabel(fusIndex, lrrIndex, vidIndex):
  if lrrIndex < OHY_OBJ_NUM:
    if vidIndex < VID_OBJ_NUM:
      # associated objects
      fusLabel = fusAssoLabelTemplate %(fusIndex, lrrIndex, vidIndex)
    else:
      # radar-only
      fusLabel = fusRadarOnlyTemplate %(fusIndex, lrrIndex)
  else:
    if vidIndex < VID_OBJ_NUM:
      # video only
      fusLabel = fusVideoOnlyTemplate %(fusIndex, vidIndex)
    else:
      # unknown
      fusLabel = fusUnknown %fusIndex
  return fusLabel

class cFill(interface.iObjectFill):
  def check(self):
    # mandatory signals
    filtsglist = []
    for dn, signalgroups in SignalGroupsDict.iteritems():
      filtsglist.append( interface.Source._filterSignalGroups(signalgroups) )
    groups = measparser.signalgroup.select_sgl_first_allvalid(filtsglist, len(aliases))
    
    # optional signals
    filtoptlist = []
    for dn, signalgroups in OptGroupsDict.iteritems():
      filtoptlist.append( interface.Source._filterSignalGroups(signalgroups) )
    try:
      optgroups = measparser.signalgroup.select_sgl_first_allvalid(filtoptlist, len(optaliases))
    except measparser.signalgroup.SignalGroupError, error:
      optgroups = None
    
    return groups, optgroups
    
  def fill(self, groups, optgroups):
    Signals = measparser.signalgroup.extract_signals(groups)
    scaletime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    kwargs = dict(ScaleTime=scaletime)
    objects=[]
    for i in xrange(FUS_OBJ_NUM):
      group = groups[i]
      o = {}
      o["dx"]  = interface.Source.getSignalFromSignalGroup(group, 'dxv',    **kwargs)[1]
      o["dy"]  = interface.Source.getSignalFromSignalGroup(group, 'dyv',    **kwargs)[1]
      o["dvx"] = interface.Source.getSignalFromSignalGroup(group, 'vxv',    **kwargs)[1]
      o["dvy"] = interface.Source.getSignalFromSignalGroup(group, 'vyv',    **kwargs)[1]
      o["id"]  = interface.Source.getSignalFromSignalGroup(group, 'Handle', **kwargs)[1]
      o["dv"]  = o["dvx"]
      
      Stand_b        = interface.Source.getSignalFromSignalGroup(group, 'b.b.Stand_b',       **kwargs)[1]
      DriveInvDir_b  = interface.Source.getSignalFromSignalGroup(group, 'b.b.DriveInvDir_b', **kwargs)[1]
      wExistProbBase = interface.Source.getSignalFromSignalGroup(group, 'wExistProbBase',    **kwargs)[1]
      statmask = Stand_b == 1
      
      if optgroups:
        # association signals available
        optgroup = optgroups[i]
        if i == FUS_OBJ_NUM-1:
          # external (video-only) fus object
          VidObjIdx = interface.Source.getSignalFromSignalGroup(optgroup, 'ExtVidObjIdx', **kwargs)[1]
          LrrObjIdx = np.ones_like(VidObjIdx, dtype=np.int16)*OHY_OBJ_NUM # invalid radar ids
          objtype = np.where(statmask, self.get_grouptype('CVR3_FUS_VIDEO_ONLY_STAT'), self.get_grouptype('CVR3_FUS_VIDEO_ONLY_MOV'))
          color = BLUE
        else:
          # regular (radar-only or associated) fus object
          LrrObjIdx = interface.Source.getSignalFromSignalGroup(optgroup, 'fus_asso_mat.LrrObjIdx',   **kwargs)[1]
          VidObjIdx = interface.Source.getSignalFromSignalGroup(optgroup, 'fus_s_asso_mat.VidObjIdx', **kwargs)[1]
          radarOnlyMask = (LrrObjIdx < OHY_OBJ_NUM) & (VidObjIdx >= VID_OBJ_NUM)
          objtype = np.where(radarOnlyMask,
                             np.where(statmask, self.get_grouptype('CVR3_FUS_RADAR_ONLY_STAT'), self.get_grouptype('CVR3_FUS_RADAR_ONLY_MOV')),
                             np.where(statmask, self.get_grouptype('CVR3_FUS_FUSED_STAT'), self.get_grouptype('CVR3_FUS_FUSED_MOV')))
          radarOnlyMask3d = np.resize(radarOnlyMask, (3, radarOnlyMask.size))
          color = np.where(radarOnlyMask3d.T, GREEN, RED)
        # regular, associated or external object
        labelList  = [prepareLabel(i, r, v) for r, v in zip(LrrObjIdx, VidObjIdx)]
        label = np.array(labelList)
      else:
        # association signals not available (radar-only object)
        objtype = np.where(statmask, self.get_grouptype('CVR3_FUS_RADAR_ONLY_STAT'), self.get_grouptype('CVR3_FUS_RADAR_ONLY_MOV'))
        # FUS index as simple label
        label = fusOldTemplate %i
        color = GREEN
      o["type"] = objtype
      o["label"] = label
      o["color"] = color
      
      objects.append(o)
    return scaletime, objects
