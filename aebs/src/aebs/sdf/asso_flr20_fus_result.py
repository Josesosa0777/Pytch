import numpy as np

import asso.interface

class Flr20AssoResult(asso.interface.AssoObject):
  def __init__(self, tracks):
    asso.interface.AssoObject.__init__(self)
    self.scaleTime = tracks.time
    self.tracks = tracks
    self.N = self.scaleTime.size
    self.isAssoSuccessful = np.zeros(self.N, dtype=np.bool)
    self.sensorNames = ('radar', 'video')
    return

  def calc(self):
    if self.isAssoDone:
      return
    for i, track in self.tracks.iteritems():
      for j, mask in track.video_asso_masks.iteritems():
        indices, = np.where(mask)
        self.assoData[i,j] = indices.tolist() # int32 array to python int list
        self.isAssoSuccessful |= mask
    self.objectPairs = asso.interface.occurence2pairs(self.assoData, self.N)
    self.maxNumOfAssociations = np.max( map(len, self.objectPairs) )
    self.isAssoDone = True
    return
