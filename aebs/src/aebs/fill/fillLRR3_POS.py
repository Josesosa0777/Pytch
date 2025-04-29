# -*- dataeval: init -*-

import numpy as np

import interface
import measparser

FUS_OBJ_NUM = 32
SIT_INTRO_OBJECTLIST_LEN = 6 # might be 8

Aliases = 'dxv', 'dyv', 'vxv', 'vyv', 'axv', 'Handle', 'b.b.Stand_b'

SignalGroups = []
for i in xrange(FUS_OBJ_NUM):
  SignalGroup = {}
  for Alias in Aliases:
    SignalGroup[Alias] = 'ECU', 'fus.ObjData_TC.FusObj.i%d.%s' %(i, Alias)
  SignalGroups.append(SignalGroup)

ObjectSignalGroups = []
for i in xrange(SIT_INTRO_OBJECTLIST_LEN):
  SignalGroup = {'ObjectList': ('ECU', 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i%d'%i)}
  ObjectSignalGroups.append(SignalGroup)
  
labelCrossTable = (("LRR3_LeftLane_near",  (255,255,100)),
                   ("LRR3_SameLane_near",  (255,255,255)),
                   ("LRR3_RightLane_near", (255,255,100)),
                   ("LRR3_LeftLane_far",   (255,255,100)),
                   ("LRR3_SameLane_far",   (255,255,255)),
                   ("LRR3_RightLane_far",  (255,255,100)))

class cFill(interface.iObjectFill):
  def check(self):
    Groups, Errors = interface.Source._filterSignalGroups(SignalGroups)
    measparser.signalgroup.check_allvalid(Groups, Errors, len(Aliases))
    ObjectGroups, Errors = interface.Source._filterSignalGroups(ObjectSignalGroups)
    measparser.signalgroup.check_allvalid(ObjectGroups, Errors, 1)
    return Groups, ObjectGroups

  def fill(self, Groups, ObjectGroups):
    Signals = measparser.signalgroup.extract_signals(Groups, ObjectGroups)
    scaletime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    Objects=[]
    len_scaletime = len(scaletime)
    
    id_matrix       = np.zeros((FUS_OBJ_NUM,len_scaletime), dtype=int)
    dx_matrix       = np.zeros((FUS_OBJ_NUM,len_scaletime))
    dy_matrix       = np.zeros((FUS_OBJ_NUM,len_scaletime))
    dv_matrix       = np.zeros((FUS_OBJ_NUM,len_scaletime))
    vy_matrix       = np.zeros((FUS_OBJ_NUM,len_scaletime))
    ax_matrix       = np.zeros((FUS_OBJ_NUM,len_scaletime))
    Stand_b_matrix  = np.zeros((FUS_OBJ_NUM,len_scaletime), dtype=bool)
    
    for i in xrange(FUS_OBJ_NUM):
      Group = Groups[i]
      dx_matrix[:][i]        = interface.Source.getSignalFromSignalGroup(Group, 'dxv',         ScaleTime=scaletime)[1]
      dy_matrix[:][i]        = interface.Source.getSignalFromSignalGroup(Group, 'dyv',         ScaleTime=scaletime)[1]
      dv_matrix[:][i]        = interface.Source.getSignalFromSignalGroup(Group, 'vxv',         ScaleTime=scaletime)[1]
      vy_matrix[:][i]        = interface.Source.getSignalFromSignalGroup(Group, 'vyv',         ScaleTime=scaletime)[1]
      ax_matrix[:][i]        = interface.Source.getSignalFromSignalGroup(Group, 'axv',         ScaleTime=scaletime)[1]
      id_matrix[:][i]        = interface.Source.getSignalFromSignalGroup(Group, 'Handle',      ScaleTime=scaletime)[1]
      Stand_b_matrix[:][i]   = interface.Source.getSignalFromSignalGroup(Group, 'b.b.Stand_b', ScaleTime=scaletime)[1]
      
    for i in xrange(SIT_INTRO_OBJECTLIST_LEN):
      Group = ObjectGroups[i]
      handle = interface.Source.getSignalFromSignalGroup(Group, 'ObjectList', ScaleTime=scaletime)[1]
      o={}
      o["dx"] = np.zeros(len_scaletime)
      o["dy"] = np.zeros(len_scaletime)
      o["vx"] = np.zeros(len_scaletime)
      o["vy"] = np.zeros(len_scaletime)
      o["id"] = np.zeros(len_scaletime, dtype=int)
      o["ax"] = np.zeros(len_scaletime)
      o["stand"] = np.zeros(len_scaletime, dtype=bool)
      
      for x in xrange(FUS_OBJ_NUM):
        mask = id_matrix[:][x]==handle
        #np.set_printoptions(threshold=sys.maxint)
        #print mask
        
        #mask:
        #   :type: <nd.array>
        #       array of True and False. Compares for each index if double is equal or not.
        #        eg: numpy.array([True,True, False, True, False, False........True,True])
        
        # POS objects get FUS object attributes for each index, where mask is True.
        # BOTH arrays have to be masked, otherwise Just the first cluster of True-values are overwritten!!!
        o["dx"][mask] = dx_matrix[:][x][mask]
        o["dy"][mask] = dy_matrix[:][x][mask]
        o["vx"][mask] = dv_matrix[:][x][mask]
        o["vy"][mask] = vy_matrix[:][x][mask]
        o["id"][mask] = id_matrix[:][x][mask]
        o["ax"][mask] = ax_matrix[:][x][mask]
        o["stand"][mask] = Stand_b_matrix[:][x][mask]
        
      o["type"]  = np.where(o["stand"] == 1,
                            self.get_grouptype('LRR3_POS_STAT'), 
                            self.get_grouptype('LRR3_POS_MOV'))
      o["label"] = labelCrossTable[i][0]
      o["color"] = labelCrossTable[i][1]
      
      Objects.append(o)
    return scaletime, Objects
