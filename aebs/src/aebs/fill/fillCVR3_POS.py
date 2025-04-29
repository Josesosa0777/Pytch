# -*- dataeval: init -*-

import numpy as np

import interface
import measparser

FUS_OBJ_NUM = 32
SIT_INTRO_OBJECTLIST_LEN = 6 # might be 8

Aliases = 'dxv', 'dyv', 'vxv', 'vyv', 'axv', 'Handle', 'b.b.Stand_b'

DeviceNames = "MRR1plus", "RadarFC"          
SignalGroupsDict = {}
for dn in DeviceNames:
  SignalGroupsDict[dn] = []
  for i in xrange(FUS_OBJ_NUM):
    SignalGroup = {}
    for Alias in Aliases:
      SignalGroup[Alias] = dn, 'fus.ObjData_TC.FusObj.i%d.%s' %(i, Alias)
    SignalGroupsDict[dn].append(SignalGroup)

ObjectSignalGroupsDict = {}
for dn in DeviceNames:
  ObjectSignalGroupsDict[dn] = []
  for i in xrange(SIT_INTRO_OBJECTLIST_LEN):
    SignalGroup = {'ObjectList': (dn, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i%d' %i)}
    ObjectSignalGroupsDict[dn].append(SignalGroup)

IntroSignalGroupsDict = {}
for dn in DeviceNames:        
  IntroSignalGroupsDict[dn] = [{'Intro': (dn, 'sit.IntroFinder_TC.Intro.i0.ObjectList.i0')}]

PSSSignalGroupsDict = {}
for dn in DeviceNames:        
  PSSSignalGroupsDict[dn] = [ {'Warning': (dn, "repprew.__b_Rep.__b_RepBase.status")}]
  
labelCrossTable = (("LeftLane_near",  (  0,255,  0)),
                   ("SameLane_near",  (255,  0,255)),
                   ("RightLane_near", (  0,255,  0)),
                   ("LeftLane_far",   (100,255,100)),
                   ("SameLane_far",   (  0,  0,255)),
                   ("RightLane_far",  (100,255,100)))

                   
class cCreateFUSMatrix:
  def __init__(self, Groups, scaletime):
    self.Groups = Groups  
    self.scaletime = scaletime
    
  def createFiller(self):
    len_scaletime = len(self.scaletime)
    id_matrix       = np.zeros((FUS_OBJ_NUM, len_scaletime), dtype=int)
    dx_matrix       = np.zeros((FUS_OBJ_NUM, len_scaletime))
    dy_matrix       = np.zeros((FUS_OBJ_NUM, len_scaletime))
    dv_matrix       = np.zeros((FUS_OBJ_NUM, len_scaletime))
    vy_matrix       = np.zeros((FUS_OBJ_NUM, len_scaletime))
    ax_matrix       = np.zeros((FUS_OBJ_NUM, len_scaletime))
    Stand_b_matrix  = np.zeros((FUS_OBJ_NUM, len_scaletime), dtype=bool)
    
    for i in xrange(FUS_OBJ_NUM):
      Group = self.Groups[i]
      dx_matrix[:][i]      = interface.Source.getSignalFromSignalGroup(Group, 'dxv',         ScaleTime=self.scaletime)[1]
      dy_matrix[:][i]      = interface.Source.getSignalFromSignalGroup(Group, 'dyv',         ScaleTime=self.scaletime)[1]
      dv_matrix[:][i]      = interface.Source.getSignalFromSignalGroup(Group, 'vxv',         ScaleTime=self.scaletime)[1]
      vy_matrix[:][i]      = interface.Source.getSignalFromSignalGroup(Group, 'vyv',         ScaleTime=self.scaletime)[1]
      ax_matrix[:][i]      = interface.Source.getSignalFromSignalGroup(Group, 'axv',         ScaleTime=self.scaletime)[1]
      id_matrix[:][i]      = interface.Source.getSignalFromSignalGroup(Group, 'Handle',      ScaleTime=self.scaletime)[1]
      Stand_b_matrix[:][i] = interface.Source.getSignalFromSignalGroup(Group, 'b.b.Stand_b', ScaleTime=self.scaletime)[1]
    return cFillObjectsFromFUSMatrix(len_scaletime, dx_matrix, dy_matrix, dv_matrix, vy_matrix, ax_matrix, id_matrix, Stand_b_matrix)
    
class cFillObjectsFromFUSMatrix:
  def __init__(self, len_scaletime, dx_matrix, dy_matrix, dv_matrix, vy_matrix, ax_matrix, id_matrix, Stand_b_matrix):
    self.len_scaletime = len_scaletime
    self.dx_matrix = dx_matrix
    self.dy_matrix = dy_matrix
    self.dv_matrix = dv_matrix
    self.vy_matrix = vy_matrix
    self.ax_matrix = ax_matrix
    self.id_matrix = id_matrix
    self.Stand_b_matrix = Stand_b_matrix
    
  def __call__(self, handle):
    o={}
    o["dx"] = np.zeros(self.len_scaletime)
    o["dy"] = np.zeros(self.len_scaletime)
    o["vx"] = np.zeros(self.len_scaletime)
    o["vy"] = np.zeros(self.len_scaletime)
    o["id"] = np.zeros(self.len_scaletime, dtype=int)
    o["ax"] = np.zeros(self.len_scaletime)
    o["stand"] = np.zeros(self.len_scaletime, dtype=bool)
    
    for x in xrange(FUS_OBJ_NUM):
      mask = self.id_matrix[:][x]==handle
      o["dx"][mask] = self.dx_matrix[:][x][mask]
      o["dy"][mask] = self.dy_matrix[:][x][mask]
      o["vx"][mask] = self.dv_matrix[:][x][mask]
      o["vy"][mask] = self.vy_matrix[:][x][mask]
      o["id"][mask] = self.id_matrix[:][x][mask]
      o["ax"][mask] = self.ax_matrix[:][x][mask]
      o["stand"][mask] = self.Stand_b_matrix[:][x][mask]
    return o

    
class cFill(interface.iObjectFill):
  def check(self):
    filtsglist = []
    filtobjsglist = []
    filtintrosglist = []
    filtpsssglist = []
    for dn in DeviceNames:
      filtsglist.append(interface.Source._filterSignalGroups(SignalGroupsDict[dn]))
      filtobjsglist.append(interface.Source._filterSignalGroups(ObjectSignalGroupsDict[dn]))
      filtintrosglist.append(interface.Source._filterSignalGroups(IntroSignalGroupsDict[dn]))
      filtpsssglist.append(interface.Source._filterSignalGroups(PSSSignalGroupsDict[dn]))
    Groups = measparser.signalgroup.select_sgl_first_allvalid(filtsglist, len(Aliases))
    ObjectGroups = measparser.signalgroup.select_sgl_first_allvalid(filtobjsglist, 1)
    IntroGroups = measparser.signalgroup.select_sgl_first_allvalid(filtintrosglist, 1)
    PSSGroups = measparser.signalgroup.select_sgl_first_allvalid(filtpsssglist, 1)
    return Groups, ObjectGroups, IntroGroups, PSSGroups

  def fill(self, Groups, ObjectGroups, IntroGroups, PSSGroups):
    Signals = measparser.signalgroup.extract_signals(Groups, ObjectGroups)
    scaletime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)

    FusMatrix = cCreateFUSMatrix(Groups, scaletime)
    ObjectFiller = FusMatrix.createFiller()  
    
    Objects=[]
    for i in xrange(SIT_INTRO_OBJECTLIST_LEN):
      Group = ObjectGroups[i]
      handle = interface.Source.getSignalFromSignalGroup(Group, 'ObjectList', ScaleTime=scaletime)[1]
      o = ObjectFiller(handle)
        
      o["type"]  = np.where(o["stand"],
                            self.get_grouptype('CVR3_POS_STAT'), 
                            self.get_grouptype('CVR3_POS_MOV'))
      o["label"] = labelCrossTable[i][0]
      w = np.reshape(np.repeat(o["stand"] == 1, 3), (-1,3))
      o["color"] = np.where(
        w,
        [0, 0, 0],
        labelCrossTable[i][1])
      
      Objects.append(o)
      
    # Add intro and warning:
    Group = IntroGroups[0]
    handle = interface.Source.getSignalFromSignalGroup(Group, 'Intro', ScaleTime=scaletime)[1]
    o = ObjectFiller(handle)
    o["type"]  = self.get_grouptype('CVR3_POS_INTRO')
    o["label"] = "Intro"
    o["color"] = (255,  0,255)
    Objects.append(o)
    
    warning = interface.Source.getSignalFromSignalGroup(PSSGroups[0], 'Warning', ScaleTime=scaletime)[1]
    o = ObjectFiller(handle)
    o["label"] = "Warning"
    o["type"]  = np.where(warning == 6,
                          self.get_grouptype('CVR3_ASF_WARNING'), 
                          self.get_grouptype('NONE_TYPE'))
    Objects.append(o)
    
    return scaletime, Objects
