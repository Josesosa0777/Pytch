""" Associates the tracks of radar and camera for a given measurement
using existing association results of CVR3 FUS component.
"""
from datavis import pyglet_workaround  # necessary as early as possible (#164)
import re

import numpy as np

import asso

OHL_OBJ_NUM = 40
VID_OBJ_NUM = 10
VID_INTERNAL_OBJ_NUM = 64
INVALID_INDEX = 255

devnames = "RadarFC", # prepare for device name change in future
sgs = []
for devname in devnames:
  sg = {}
  for k in xrange(OHL_OBJ_NUM):
    sg["VidToLrrIdx.i%d" %k] = devname, "fus_s_asso_mat.VidToLrrIdx.i%d"        %k
    sg["Valid.i%d"       %k] = devname, "ohy.ObjData_TC.OhlObj.i%d.c.c.Valid_b" %k
    sg["Hist.i%d"        %k] = devname, "ohy.ObjData_TC.OhlObj.i%d.c.c.Hist_b"  %k
  for l in xrange(VID_OBJ_NUM):
    sg["VidObj.i%d.Handle" %l] = devname, "fus.SVidBasicInput_TC.VidObj.i%d.Handle"     %l
    sg["VidObj.i%d.Hist"   %l] = devname, "fus.SVidBasicInput_TC.VidObj.i%d.b.b.Hist_b" %l
  sgs.append(sg)

pattern = r'sw:.*CP\D*(\d+)\D*(\d+)\D*(\d+)\D*(\d+)' # regexp pattern of sw version in meas file comment

def getSwVersion(source, pattern):
  # handle sw version differences
  comment = source.getFileComment()
  m = re.search(pattern, comment)
  try:
    version = '.'.join( m.groups() )
  except (AttributeError, ValueError):
    version = None
  return version

def getVidInvalidHandle(swversion):
  if swversion >= '1.2.1.14':
    vid_invalid_handle = 64 # after bugfix
  else:
    vid_invalid_handle = 0  # before bugfix
  return vid_invalid_handle

class AssoCvr3fusResult(asso.interface.AssoObject):
  def __init__(self, source, useVideoHandle=False):
    """
    :Parameters:
        source : measparser.cSignalSource
          Measurement signal source
        useVideoHandle : bool, optional
          Use video handle in association results. If True, the internal object id (handle) is utilized,
          otherwise the video object indices are used. Default is False.
    :Exceptions:
      measparser.signalgroup.SignalGroupError : if required signals are not present
    """
    asso.interface.AssoObject.__init__(self)

    self.group = source.selectSignalGroup(sgs)
    self.scaleTime = source.getSignalFromSignalGroup(self.group, "VidToLrrIdx.i0")[0]
    self.useVideoHandle = useVideoHandle
    self.N = self.scaleTime.size
    self.K = OHL_OBJ_NUM
    self.L = VID_INTERNAL_OBJ_NUM if useVideoHandle else VID_OBJ_NUM
    self.isAssoSuccessful = np.zeros(self.N, dtype=np.bool)
    self.assoMask = np.zeros(shape=(self.N, OHL_OBJ_NUM), dtype=np.bool)
    """:type: ndarray
    Bool mask indicating association of radar objects"""
    self.masks = {}
    """:type: dict
    Bool masks indicating validity of objects in associated pairs (video indices are used)"""
    self.videoHist = {}
    """:type: dict
    Bool masks indicating historical flag of video objects (video indices are used)"""
    self.radarHist = {}
    """:type: dict
    Bool masks indicating historical flag of radar objects"""
    self.videoValid = {}
    """:type: dict
    Bool masks indicating validity of video objects (video indices are used)"""
    self.radarValid = {}
    """:type: dict
    Bool masks indicating validity of radar objects"""
    self.radar2vid = {}
    """:type: dict
    {radarIdx<int> : associatedVideoIdx<ndarray>} """
    self.vidHandles = {}
    """:type: dict
    {videoIdx<int> : videoHandle<ndarray>} """
    # handle sw version differences
    self.swversion = getSwVersion(source, pattern)
    self.vid_invalid_handle = getVidInvalidHandle(self.swversion)
    for l in xrange(VID_OBJ_NUM):
      self.vidHandles[l] = source.getSignalFromSignalGroup(self.group, "VidObj.i%d.Handle" %l)[1]
      videoHist          = source.getSignalFromSignalGroup(self.group, "VidObj.i%d.Hist"   %l)[1]
      self.videoHist[l]  = np.asarray(videoHist, dtype=np.bool)
    for k in xrange(OHL_OBJ_NUM):
      radar2vidIdx = source.getSignalFromSignalGroup(self.group, "VidToLrrIdx.i%d" %k)[1]
      radarHist    = source.getSignalFromSignalGroup(self.group, "Hist.i%d"        %k)[1]
      self.radarHist[k]  = np.asarray(radarHist, dtype=np.bool)
      self.assoMask[:,k] = radar2vidIdx != INVALID_INDEX
      self.radar2vid[k]  = radar2vidIdx
      mask_k = source.getSignalFromSignalGroup(self.group, "Valid.i%d" %k)[1] > 0
      self.radarValid[k] = mask_k
      for l in xrange(VID_OBJ_NUM):
        if l in radar2vidIdx:
          mask_l = self.vidHandles[l] != self.vid_invalid_handle
          self.videoValid[l] = mask_l
          mask = mask_k & mask_l
          if np.any(mask):
            self.masks[k,l] = mask
    return

  def calc(self):
    if not self.isAssoDone:
      # time loop
      for n in xrange(self.N):
        pairs = []
        assomask = self.assoMask[n]
        if np.any(assomask):
          # at least one radar object was associated in this cycle
          radarObjs, = np.where(assomask)
          # loop on associated radar objects
          for i in radarObjs:
            l = self.radar2vid[i][n]
            j = self.vidHandles[l][n] if self.useVideoHandle else l
            pair = ( int(i),int(j) ) # store pair as regular python integers
            pairs.append(pair)
            timeIndices = self.assoData.setdefault(pair, [])
            timeIndices.append(n)
          self.isAssoSuccessful[n] = True
          pairs.sort(cmp=self.cmp) # in-place sort of tuple elements
        self.objectPairs.append(pairs)
      self.maxNumOfAssociations = np.max( map(len, self.objectPairs) )
      self.isAssoDone = True
    return

if __name__ == '__main__':
  import sys

  import measparser
  import fusutils

  measPath = sys.argv[1]
  source = measparser.cSignalSource(measPath)
  try:
    # asso object init (track inits using signal queries)
    assoObj = AssoCvr3fusResult(source)
  except measparser.signalgroup.SignalGroupError, error:
    # in case signals are not present
    print error.message
  else:
    # cost matrix calculation and track-to-track association
    assoObj.calc()
    if '-v' in sys.argv:
      # print out association result
      for k, assoList in enumerate(assoObj.objectPairs):
        print k, '%.2f' %assoObj.scaleTime[k], assoList
      # check if all base class attributes are set
      missings = fusutils.debug.checkAttributes(assoObj)
      if missings:
        print 'Attribute(s) might be unset: %s' %missings
  # close resources
  source.save()
