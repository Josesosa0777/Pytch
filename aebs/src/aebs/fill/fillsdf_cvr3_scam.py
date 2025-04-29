# -*- dataeval: init -*-

import numpy as np

import interface
import measparser
from aebs.sdf import asso_cvr3_sCam, fuse_cvr3_sCam

sdfLabelTemplate = 'sdf_i%d_id%d'

NO_ASSO_POSITION  = (0., 0.)
NO_ASSO_INDEX = 255
NO_ASSO_LABEL = ''

def extendObjIndices(l, maxNumOfObjs):
  mylist = list(l)
  mylist.extend( [(NO_ASSO_INDEX, NO_ASSO_INDEX)] *(maxNumOfObjs-len(l)))
  return  mylist
  
def prepareLabel(p):
  return NO_ASSO_LABEL if NO_ASSO_INDEX in p else sdfLabelTemplate %(p[0],p[1])

class cFill(interface.iObjectFill):
  def check(self):
    group = interface.Source.selectSignalGroup(asso_cvr3_sCam.signalGroups) 
    return group

  def fill(self, group):
    signals = measparser.signalgroup.extract_signals(group)
    scaletime = interface.Source.selectScaleTime(signals, True)
    Objects=[]
    # track-to-track association
    assoObj = asso_cvr3_sCam.AssoCvr3SCam(interface.Source, scaleTime=scaletime)
    assoObj.calc()
    maxNumOfObjs = assoObj.maxNumOfAssociations
    # track-to-track fusion
    fuseObj = fuse_cvr3_sCam.FusObject(assoObj)
    fuseObj.calc(isDiag=True)
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
    # nested function for moving state copy
    def copyMovingStates(tk, i, j):
      if i == NO_ASSO_INDEX or j == NO_ASSO_INDEX:
        return self.get_grouptype('NONE_TYPE')
      else:
        index = fuseObj.indices[i,j][tk]
        stationary = fuseObj.movingState[i,j][index] 
        return self.get_grouptype('SDF_CVR3_SCAM_STAT') if stationary else gtps.get_type('SDF_CVR3_SCAM_MOV')
    # loop through associations
    for k in xrange(maxNumOfObjs):
      o = {}
      arr = assoArray[:,k] # shape (N,2)
      dxdyList = [copyStates(m,i,j) for m, (i,j) in enumerate(arr)]
      dxdyArr  = np.array(dxdyList)
      o["dx"]  = dxdyArr[:,0]
      o["dy"]  = dxdyArr[:,1]
      labelList  = [prepareLabel(a) for a in arr]
      typeList   = [copyMovingStates(m,i,j) for m, (i,j) in enumerate(arr)]
      # array creation needed (for video overlay)
      o["label"] = np.array(labelList)
      o["type"]  = np.array(typeList)
      Objects.append(o)
    return scaletime, Objects
