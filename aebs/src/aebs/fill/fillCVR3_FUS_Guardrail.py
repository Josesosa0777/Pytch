# -*- dataeval: init -*-

import numpy as np

import interface
import measparser
import cluster

# FUS specific variables
FUS_OBJ_NUM = 32
COMPONENT_NAME = 'FUS'
GUARDRAIL_P_LIMIT = 14/255.0 # 14 is the limit in the CVR3 code for construction element probability decrementation, 
                             # 255 is the max value

Aliases = 'dxv', 'dyv', 'wConstElem'

SignalGroups = []
for i in xrange(FUS_OBJ_NUM):
  SignalGroup = {}
  for Alias in Aliases:
    SignalGroup[Alias] = 'MRR1plus', 'fus.ObjData_TC.FusObj.i%d.%s' %(i, Alias)
  SignalGroups.append(SignalGroup)

class cFill(interface.iObjectFill, cluster.aCluster):
  def check(self):
    Groups, Errors = interface.Source._filterSignalGroups(SignalGroups)
    measparser.signalgroup.check_allvalid(Groups, Errors, len(Aliases))
    return Groups
  
  def fill(self, Groups):
    Signals = measparser.signalgroup.extract_signals(Groups)
    scaletime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    # extract 0th object's signals
    Group = Groups[0]
    Time, dx = interface.Source.getSignalFromSignalGroup(Group, 'dxv',        ScaleTime=scaletime)
    Time, dy = interface.Source.getSignalFromSignalGroup(Group, 'dyv',        ScaleTime=scaletime)
    Time, p  = interface.Source.getSignalFromSignalGroup(Group, 'wConstElem', ScaleTime=scaletime)
    # preallocate memory
    len_scaletime = len(scaletime)
    dxArray = np.zeros(shape=(FUS_OBJ_NUM, len_scaletime), dtype=dx.dtype)
    dyArray = np.zeros(shape=(FUS_OBJ_NUM, len_scaletime), dtype=dy.dtype)
    pArray = np.zeros(shape=(FUS_OBJ_NUM,  len_scaletime), dtype=p.dtype)
    
    dxArray[0] = dx
    dyArray[0] = dy
    pArray[0] = p
    
    for i in xrange(1, FUS_OBJ_NUM):     
      Group = Groups[i]
      Time, dx = interface.Source.getSignalFromSignalGroup(Group, 'dxv',        ScaleTime=scaletime)
      Time, dy = interface.Source.getSignalFromSignalGroup(Group, 'dyv',        ScaleTime=scaletime)
      Time, p  = interface.Source.getSignalFromSignalGroup(Group, 'wConstElem', ScaleTime=scaletime)
      dxArray[i] = dx
      dyArray[i] = dy
      pArray[i] = p

    # start = time.time()
    
    # run clustering algorithm
    gtps = self.get_grouptypes()
    prj_name = self.get_prj_name()
    clusterArray, dxArraySorted, dyArraySorted, pArraySorted = \
    self.clusterGuardrail(dxArray, dyArray, pArray, COMPONENT_NAME, gtps, prj_name)
    
    # end = time.time()
    # elapsed = end-start
    # print 'Clustering algorithm on %(num)d %(compName)s objects, %(time)d time steps.\n\tElapsed time: %(timeElaps)f sec' \
    # %{'num':FUS_OBJ_NUM, 'compName':COMPONENT_NAME, 'time':len_scaletime, 'timeElaps':elapsed}
    
    Objects=[]
    # fill the Objects list
    for k in xrange(FUS_OBJ_NUM):
      o = {}
      o["dx"] = dxArraySorted[k]
      o["dy"] = dyArraySorted[k]
      o["type"] = clusterArray[k]         
      
      o["label"] = "CVR3_FUS_?" # FIXME: labels should be also sorted, but it would change with time
      
      o["alpha"] = np.where(pArraySorted[k] < GUARDRAIL_P_LIMIT, 0., pArraySorted[k]) # alpha channel: 0...1

      Objects.append(o)
    return scaletime, Objects
    
      
