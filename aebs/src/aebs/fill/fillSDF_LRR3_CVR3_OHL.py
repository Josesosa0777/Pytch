# -*- dataeval: init -*-

import numpy as np

import interface
import measparser
from aebs.par import grouptypes
from aebs.sdf import assoOHL
from aebs.sdf import fuseOHL

NO_ASSO_POSITION  = (0., 0.)
NO_ASSO_INDEX = 255
NO_ASSO_LABEL = ''

sdfLabelTemplate = 'OHL_L%d_C%d'

SignalGroups = assoOHL.signalGroups

def extendObjIndices(l, maxNumOfObjs):
  mylist = list(l)
  mylist.extend( [(NO_ASSO_INDEX, NO_ASSO_INDEX)] *(maxNumOfObjs-len(l)))
  return  mylist
  
def prepareLabel(p):
  return NO_ASSO_LABEL if NO_ASSO_INDEX in p else sdfLabelTemplate %(p[0],p[1])

class cFill(interface.iObjectFill):
  def check(self):
    Group = interface.Source.selectSignalGroup(SignalGroups) 
    return Group

  def fill(self, Group):
    Signals = measparser.signalgroup.extract_signals(Group)
    scaletime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    Objects=[]
    # track-to-track association
    assoObj = assoOHL.AssoOHL(interface.Source, scaleTime=scaletime)
    assoObj.calc()
    maxNumOfObjs = assoObj.maxNumOfAssociations
    # track-to-track fusion
    fuseObj = fuseOHL.FuseOHL(assoObj)
    fuseObj.calc()
    # share object references
    interface.assoObj = assoObj
    interface.fuseObj = fuseObj
    # extend original object index lists to maxNumOfObjs size
    objectPairs = [extendObjIndices(elem, maxNumOfObjs) for elem in assoObj.objectPairs]
    assoArray = np.array(objectPairs) # shape (N, maxNumOfObjs, 2)
    # nested function for state copy
    def copyStates(tk, i, j):
      if i == NO_ASSO_INDEX or j == NO_ASSO_INDEX:
        return NO_ASSO_POSITION
      else:
        index = fuseObj.indices[i,j][tk]
        xfus, _ = fuseObj.tracks[i,j]
        return xfus[index,0], xfus[index,1]
    # loop through associations
    for k in xrange(maxNumOfObjs):
      o = {}
      arr = assoArray[:,k]
      dxdyList = [copyStates(m,i,j) for m, (i,j) in enumerate(arr)]
      dxdyArr  = np.array(dxdyList)
      o["dx"]  = dxdyArr[:,0]
      o["dy"]  = dxdyArr[:,1]
      labelList  = [prepareLabel(a) for a in arr]
      o["label"] = np.array(labelList) # array creation needed (for video overlay)
      o["type"] = np.where(o["dx"] == NO_ASSO_POSITION[0],
                           self.get_grouptype('NONE_TYPE'),
                           self.get_grouptype('SDF_LRR3_CVR3_OHL'))
      Objects.append(o)
    return scaletime, Objects
