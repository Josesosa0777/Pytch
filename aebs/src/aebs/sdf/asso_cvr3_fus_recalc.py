""" Associates the tracks of radar and camera for a given measurement 
using the same algorithm as in CVR3 FUS component.
This allows easy benchmark of different parameter sets and assignment solver methods.
"""

from collections import OrderedDict

import numpy as np

from asso_cvr3_fus_result import OHL_OBJ_NUM, VID_OBJ_NUM, getVidInvalidHandle,\
                                 devnames, pattern, getSwVersion
from asso_cvr3_asofus import defpars, norms, FLOAT32_0, normParams, checkInputParams,\
                             fix2float, calcCurrentAssoProb, calcFilterAssoProb, Cvr3fusTransf
import asso

OHL_OBJ_NUM_RANGE = xrange(OHL_OBJ_NUM)
VID_OBJ_NUM_RANGE = xrange(VID_OBJ_NUM)

dLongOffsetObjToVidCoordSys_def = 0.1953125 # default value of transf data (if not recorded)

videoAttrib2signal = {
  "VidObj.i%d.handle"       : "fus.SVidBasicInput_TC.VidObj.i%d.Handle",
  "VidObj.i%d.alpRightEdge" : "fus.SVidBasicInput_TC.VidObj.i%d.alpRightEdge",
  "VidObj.i%d.alpLeftEdge"  : "fus.SVidBasicInput_TC.VidObj.i%d.alpLeftEdge",
  "VidObj.i%d.dx"           : "fus.SVidBasicInput_TC.VidObj.i%d.dxv",
  "VidObj.i%d.invttc"       : "fus.SVidBasicInput_TC.VidObj.i%d.invTTtipc",
  "VidObj.i%d.measured_b"   : "fus.SVidBasicInput_TC.VidObj.i%d.b.b.Measured_b",
  "VidObj.i%d.historical_b" : "fus_s_vid_hist.Hist.i%d",
  "VidObj.i%d.countAlive"   : "fus.SVidBasicInput_TC.VidObj.i%d.countAlive",
}

radarAttrib2signal = {
  "OhlObj.i%d.dx"                : "ohy.ObjData_TC.OhlObj.i%d.dx",
  "OhlObj.i%d.dy"                : "ohy.ObjData_TC.OhlObj.i%d.dy",
  "OhlObj.i%d.vx"                : "ohy.ObjData_TC.OhlObj.i%d.vx",
  "OhlObj.i%d.valid_b"           : "ohy.ObjData_TC.OhlObj.i%d.c.c.Valid_b",
  "OhlObj.i%d.measured_b"        : "ohy.ObjData_TC.OhlObj.i%d.c.c.Meas_b",
  "OhlObj.i%d.historical_b"      : "ohy.ObjData_TC.OhlObj.i%d.c.c.Hist_b",
  "OhlObj.i%d.existProb"         : "ohy.ObjData_TC.OhlObj.i%d.wExistProb",
  "OhlObj.i%d.obstacleProb"      : "ohy.ObjData_TC.OhlObj.i%d.probClass.i0",
  "OhlObj.i%d.stationary_b"      : "ohy.ObjData_TC.OhlObj.i%d.c.c.Stand_b",
  "OhlObj.i%d.stopped_b"         : "ohy.ObjData_TC.OhlObj.i%d.c.c.Stopped_b",
  "OhlObj.i%d.notClassified_b"   : "ohy.ObjData_TC.OhlObj.i%d.c.c.NotClassified_b",
  # useful but not necessary attributes
  "OhlObj.i%d.ongoing_b"         : "ohy.ObjData_TC.OhlObj.i%d.c.c.Drive_b",
  "OhlObj.i%d.oncoming_b"        : "ohy.ObjData_TC.OhlObj.i%d.c.c.DriveInvDir_b",
  "OhlObj.i%d.oncomingStopped_b" : "ohy.ObjData_TC.OhlObj.i%d.c.c.StoppedInvDir_b",
}

optsignals = "fus.SVidBasicInput_TC.dLongOffsetObjToVidCoordSys",
sgs = []
optsgs = []
for devname in devnames:
  # required signal group
  sg = { "fus.SVidBasicInput_TC.dMountOffsetVid" : (devname, "fus.SVidBasicInput_TC.dMountOffsetVid") }
  for k in OHL_OBJ_NUM_RANGE:
    for aliastemplate, signaltemplate in radarAttrib2signal.iteritems():
      sg[aliastemplate %k] = devname, signaltemplate%k
  for l in VID_OBJ_NUM_RANGE:
    for aliastemplate, signaltemplate in videoAttrib2signal.iteritems():
      sg[aliastemplate %l] = devname, signaltemplate%l
    for k in OHL_OBJ_NUM_RANGE:
      sg["ProbAssoMat.i%d.i%d" %(k,l)] = devname, "fus_s_asso_mat.ProbAssoMat.probability.i%d.i%d" %(k,l)
  sgs.append(sg)
  # optional signal group (signals might not be recorded in older measurements)
  optsg = {}
  for signalname in optsignals:
    optsg[signalname] = devname, signalname
  optsgs.append(optsg)

def getOptGroup(source, signalgroups):
  optgroups = source.filterSignalGroups(signalgroups)
  for optgroup in optgroups:
    if len(optgroup) == len(optsignals):
      break
  else:
    # optional signals are NOT present
    optgroup = None
  return optgroup

def prob2cost(p):
  return 1 - p

# transformations
def getTransf(source, group, optgroup):
  if optgroup:
    dLongOffsetObjToVidCoordSys = source.getSignalFromSignalGroup(optgroup, "fus.SVidBasicInput_TC.dLongOffsetObjToVidCoordSys")[1]
  else:
    dLongOffsetObjToVidCoordSys = dLongOffsetObjToVidCoordSys_def, # make it iterable for later sclicing
  dMountOffsetVid = source.getSignalFromSignalGroup(group, "fus.SVidBasicInput_TC.dMountOffsetVid")[1]
  # assumption: transformation values are constant
  transf = Cvr3fusTransf(dLongOffsetObjToVidCoordSys = np.float32( dLongOffsetObjToVidCoordSys[0] ),
                         dMountOffsetVid = np.float32( dMountOffsetVid[0] ) )
  return transf

# sensor track creation
def createRadarTracks(source, group):
  tracks = OrderedDict() # { objnum<int> : {attribname<str> : value<ndarray>}, }
  for i in OHL_OBJ_NUM_RANGE:
    obj = {}
    for aliaspattern in radarAttrib2signal:
      attrib = aliaspattern.split('.')[-1]
      signal = source.getSignalFromSignalGroup(group, aliaspattern %i)[1]
      if 'prob' in attrib.lower() and signal.dtype.kind != 'f':
        # probability signal is not normalized
        signal = fix2float( signal, norms['N_prob1UW_uw'] )
      if signal.dtype == np.float64:
        signal = signal.astype(np.float32)
      elif attrib.endswith('_b'):
        signal = signal.astype(np.bool)
      obj[attrib] = signal
    tracks[i] = obj
  return tracks

def createVideoTracks(source, group):
  tracks = OrderedDict() # { objnum<int> : {attribname<str> : value<ndarray>}, }
  for j in VID_OBJ_NUM_RANGE:
    obj = {}
    for aliaspattern in videoAttrib2signal:
      attrib = aliaspattern.split('.')[-1]
      signal = source.getSignalFromSignalGroup(group, aliaspattern %j)[1]
      if signal.dtype == np.float64:
        signal = signal.astype(np.float32)
      elif attrib.endswith('_b'):
        signal = signal.astype(np.bool)
      obj[attrib] = signal
    tracks[j] = obj
  return tracks

def getFilteredAssoProbInit(source, group):
  filteredAssoProbInit = np.zeros(shape=(OHL_OBJ_NUM, VID_OBJ_NUM), dtype=np.float32)
  for i in OHL_OBJ_NUM_RANGE:
    for j in VID_OBJ_NUM_RANGE:
      filteredAssoProb = source.getSignalFromSignalGroup(group, "ProbAssoMat.i%d.i%d" %(i,j))[1]
      if filteredAssoProb.dtype.kind != 'f':
        # normalization needed
        filteredAssoProb = fix2float( filteredAssoProb, norms['N_prob1UW_uw'] )
      filteredAssoProbInit[i,j] = filteredAssoProb[0]
  return filteredAssoProbInit


class AssoCvr3fusCore(asso.interface.AssoObject):
  def __init__(self, source, Solver=asso.greedy.Greedy):
    asso.interface.AssoObject.__init__(self)
    
    # handle signal groups
    group = source.selectSignalGroup(sgs)
    optgroup = getOptGroup(source, optsgs)
    # asso interface attributes
    self.solver = Solver()
    self.scaleTime = source.getSignalFromSignalGroup(group, "ProbAssoMat.i0.i0")[0]
    self.K = OHL_OBJ_NUM
    self.L = VID_OBJ_NUM
    self.N = self.scaleTime.size
    # handle sw version differences
    self.swversion = getSwVersion(source, pattern)
    vid_invalid_handle = getVidInvalidHandle(self.swversion)
    # algorithm inputs
    self.transf = getTransf(source, group, optgroup)
    self.radarTracks = createRadarTracks(source, group)
    self.videoTracks = createVideoTracks(source, group)
    self.masks = self._createMasks(vid_invalid_handle)
    # extend radar tracks with angle and invttc
    self._extendRadarTracksWithAngle()
    self._extendRadarTracksWithInvttc()
    # initial condition for filter
    self.filteredAssoProbInit = getFilteredAssoProbInit(source, group)
    # set association parameters to default
    self.params = defpars
    return

  def update(self, usedefault=True, **params):
    """ Update parameters

    :Parameters:
        usedefault : bool, optional
          If set to True (default), the parameters are updated based on the
          default parameter set, otherwise based on the last set (iterative update).
    :Keywords:
      parameter name=value pairs
    :Exceptions:
      AssertionError
        invalid association algorithm parameter name or value (outside range)
    """
    checkInputParams(params)
    self._updateParams(params, usedefault=usedefault)
    if self.isAssoDone:
      self._resetAssoResults()
    return

  def _createMasks(self, vid_invalid_handle):
    masks = np.zeros(shape=(self.N, self.K, self.L), dtype=np.bool)
    # object loop
    for i, radarTrack in self.radarTracks.iteritems():
        mask_i = radarTrack['valid_b']
        for j, videoTrack in self.videoTracks.iteritems():
            mask_j = videoTrack['handle'] != vid_invalid_handle
            mask = mask_i & mask_j
            masks[:,i,j] = mask
    masks.flags.writeable = False # safety
    return masks

  def _updateParams(self, params, usedefault=True):
    # update params
    normedparams = normParams(params)
    if self.params and not usedefault:
      # update current params with the new ones
      self.params = self.params._replace(**normedparams)
    else:
      # update default params with the new ones
      self.params = defpars._replace(**normedparams)
    return

  def _extendRadarTracksWithAngle(self):
    # transf
    t_dxLrrVid_f = self.transf.dLongOffsetObjToVidCoordSys
    t_dyLrrVid_f = self.transf.dMountOffsetVid
    # object loop
    for radar in self.radarTracks.itervalues():
      mask = radar['valid_b']
      # object attributes
      t_dxLrr_f = radar['dx'][mask]
      t_dyLrr_f = radar['dy'][mask]
      # set lrr object dx-dy to camera coordinate system
      t_dxLrr_f = t_dxLrr_f + t_dxLrrVid_f
      t_dyLrr_f = t_dyLrr_f - t_dyLrrVid_f
      # calculate lrr object angle
      t_phiLrr_f = np.arctan2(t_dyLrr_f, t_dxLrr_f)
      # mask valid values
      angle = np.zeros_like(mask, dtype=t_phiLrr_f.dtype)
      angle[mask] = t_phiLrr_f
      # save radar object angle
      radar['angle'] = angle
    return

  def _extendRadarTracksWithInvttc(self):
    # transf
    t_dxLrrVid_f = self.transf.dLongOffsetObjToVidCoordSys
    # object loop
    for radar in self.radarTracks.itervalues():
      mask = radar['valid_b']
      # object attributes
      t_dxLrr_f = radar['dx'][mask]
      t_vxLrr_f = radar['vx'][mask]
      #  set lrr object dx to camera coordinate system
      t_dxLrr_f = t_dxLrr_f + t_dxLrrVid_f
      #  calculate lrr inverse ttc
      maskDxValid = t_dxLrr_f > FLOAT32_0
      t_invTtcLrr_f = np.where( maskDxValid,
                                -t_vxLrr_f/t_dxLrr_f,
                                FLOAT32_0 )
      # mask valid values
      invttc = np.zeros_like(mask, dtype=t_invTtcLrr_f.dtype)
      invttc[mask] = t_invTtcLrr_f
      #  save radar inverse ttc
      radar['invttc'] = invttc
    return

  def _resetAssoResults(self):
    self.objectPairs = []
    self.isAssoDone = False
    return

  def _createCostMatrix(self):
    currentAssoProb_uint32 = self._calcCurrentAssoProb()
    filteredAssoProb = calcFilterAssoProb(currentAssoProb_uint32,
                                          self.filteredAssoProbInit,
                                          self.radarTracks,
                                          self.videoTracks,
                                          self.masks,
                                          self.params)
    self.C = prob2cost( filteredAssoProb )
    return
  
  def _calcCurrentAssoProb(self):
    currentAssoProb_uint32, _ = calcCurrentAssoProb(self.radarTracks,
                                                    self.videoTracks,
                                                    self.masks,
                                                    self.params,
                                                    self.transf)
    return currentAssoProb_uint32

  def _calcGate(self):
    self.gate = prob2cost( self.params.prob1AsoProbLimit )
    return
  
  def _register(self, n, Ccut, validRows, validCols, indices):
    assoObjIndices = []
    for rowNum, colNum in indices:
      # filter invalid association
      if not np.allclose(Ccut[rowNum, colNum], self.invalidAssoCost):
        i = validRows[rowNum]
        j = validCols[colNum]
        assoObjIndices.append( (i,j) )
    if assoObjIndices:
      assoObjIndices.sort(cmp=self.cmp) # in-place sort of tuple elements
    self.objectPairs.append(assoObjIndices)
    return


class AssoCvr3fusRecalc(AssoCvr3fusCore):
  def __init__(self, source, Solver=asso.greedy.Greedy, useVideoHandle=False):
    """
    :Parameters:
        source : measparser.cSignalSource
          Measurement signal source
        Solver : class, optional
          Assignment solver class
        useVideoHandle : bool, optional
          Use video handle in association results. If True, the internal object id (handle) is utilized,
          otherwise the video object indices are used. Default is False.
    :Exceptions:
      measparser.signalgroup.SignalGroupError
        if required signals are not present
      AssertionError
        when invalid association algorithm parameter name or value is given
      MemoryError
        there is not enough memory to do the calculations (e.g. when measurement is too long)
    """
    AssoCvr3fusCore.__init__(self, source, Solver=Solver)
    
    self.useVideoHandle = useVideoHandle
    # asso interface attributes
    self.isAssoSuccessful = np.zeros(self.N, dtype=np.bool)
    # result storage
    self.measures         = None
    self.currentAssoProb  = None
    self.filteredAssoProb = None
    return

  def _resetAssoResults(self):
    self.isAssoSuccessful = np.zeros(self.N, dtype=np.bool)
    self.measures         = None
    self.currentAssoProb  = None
    self.filteredAssoProb = None
    self.objectPairs = []
    self.assoData = {}
    self.maxNumOfAssociations = None
    self.isAssoDone = False
    return

  def _createCostMatrix(self):
    currentAssoProb_uint32 = self._calcCurrentAssoProb()
    filteredAssoProb = calcFilterAssoProb(currentAssoProb_uint32,
                                          self.filteredAssoProbInit,
                                          self.radarTracks,
                                          self.videoTracks,
                                          self.masks,
                                          self.params)
    self.C = prob2cost( filteredAssoProb )
    self.filteredAssoProb = filteredAssoProb
    return
  
  def _calcCurrentAssoProb(self):
    currentAssoProb_uint32, measures = calcCurrentAssoProb(self.radarTracks,
                                                           self.videoTracks,
                                                           self.masks,
                                                           self.params,
                                                           self.transf)
    self.measures = measures
    self.currentAssoProb = fix2float( currentAssoProb_uint32, norms['N_prob1UW_uw'] )
    return currentAssoProb_uint32
  
  def _register(self, n, Ccut, validRows, validCols, indices):
    assoObjIndices = []
    for rowNum, colNum in indices:
      # filter invalid association
      if not np.allclose(Ccut[rowNum, colNum], self.invalidAssoCost):
        i = validRows[rowNum]
        j = validCols[colNum]
        j = self.videoTracks[j]['handle'][n] if self.useVideoHandle else j
        objPair = (i,j)
        assoObjIndices.append(objPair)
        timeIndices = self.assoData.setdefault(objPair, [])
        timeIndices.append(n)
    if assoObjIndices:
      self.isAssoSuccessful[n] = True
      assoObjIndices.sort(cmp=self.cmp) # in-place sort of tuple elements
    self.objectPairs.append(assoObjIndices)
    return
  
if __name__ == '__main__':
  import sys

  import measparser

  measPath = sys.argv[1]
  signalsource = measparser.cSignalSource(measPath)
  try:
    # asso object init (signal queries)
    a = AssoCvr3fusRecalc(signalsource)
    a.calc()
  except (measparser.signalgroup.SignalGroupError, AssertionError), error:
    print error.message
  else:
    print a
  # close resources
  signalsource.save()
