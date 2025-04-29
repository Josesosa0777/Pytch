import numpy

import datavis
import interface

# radar constants
N_prob1UW_uw = 32768
OHY_OBJ_NUM = 40
FUS_OBJ_NUM = 32
VID_OBJ_NUM = 10
VID_INVALID_ID = 0xFF

# script constants
INVALID_VALUE = 0xFF

DefParam = interface.NullParam

sg = {}
for i in xrange(OHY_OBJ_NUM):
  sg["ohy.ObjData_TC.OhlObj.i%d.dx" % i] = ("RadarFC", "ohy.ObjData_TC.OhlObj.i%d.dx" % i)
  sg["ohy.ObjData_TC.OhlObj.i%d.dy" % i] = ("RadarFC", "ohy.ObjData_TC.OhlObj.i%d.dy" % i)
  sg["ohy.ObjData_TC.OhlObj.i%d.vx" % i] = ("RadarFC", "ohy.ObjData_TC.OhlObj.i%d.vx" % i)
  sg["ohy.ObjData_TC.OhlObj.i%d.wExistProb" % i] = ("RadarFC", "ohy.ObjData_TC.OhlObj.i%d.wExistProb" % i)
  sg["fus_s_asso_mat.VidToLrrIdx.i%d" % i] = ("RadarFC", "fus_s_asso_mat.VidToLrrIdx.i%d" % i)
  for j in xrange(VID_OBJ_NUM):
    sg["fus_s_asso_mat.ProbAssoMat.probability.i%d.i%d" % (i, j)] = ("RadarFC", "fus_s_asso_mat.ProbAssoMat.probability.i%d.i%d" % (i, j))
for i in xrange(VID_OBJ_NUM):
  sg["fus.SVidBasicInput_TC.VidObj.i%d.dxv"          % i] = ("RadarFC", "fus.SVidBasicInput_TC.VidObj.i%d.dxv" % i)
  sg["fus.SVidBasicInput_TC.VidObj.i%d.dyv"          % i] = ("RadarFC", "fus.SVidBasicInput_TC.VidObj.i%d.dyv" % i)
  sg["fus.SVidBasicInput_TC.VidObj.i%d.alpLeftEdge"  % i] = ("RadarFC", "fus.SVidBasicInput_TC.VidObj.i%d.alpLeftEdge" % i)
  sg["fus.SVidBasicInput_TC.VidObj.i%d.alpRightEdge" % i] = ("RadarFC", "fus.SVidBasicInput_TC.VidObj.i%d.alpRightEdge" % i)
  sg["fus.SVidBasicInput_TC.VidObj.i%d.invTTtipc"    % i] = ("RadarFC", "fus.SVidBasicInput_TC.VidObj.i%d.invTTtipc" % i)
  sg["fus.SVidBasicInput_TC.VidObj.i%d.wExistProb"   % i] = ("RadarFC", "fus.SVidBasicInput_TC.VidObj.i%d.wExistProb" % i)
for i in xrange(FUS_OBJ_NUM):
  sg["fus_asso_mat.LrrObjIdx.i%d"    % i] = ("RadarFC", "fus_asso_mat.LrrObjIdx.i%d"    % i)
  sg["fus_s_asso_mat.VidObjIdx.i%d"  % i] = ("RadarFC", "fus_s_asso_mat.VidObjIdx.i%d"  % i)
  sg["fus.ObjData_TC.FusObj.i%d.dyv" % i] = ("RadarFC", "fus.ObjData_TC.FusObj.i%d.dyv" % i)
  sg["fus.ObjData_TC.FusObj.i%d.wExistProb" % i] = ("RadarFC", "fus.ObjData_TC.FusObj.i%d.wExistProb" % i)
sgs = [sg,]

def reverseIndices(indexMatrix, maxIndex, invalidValue, retInvalidValue=INVALID_VALUE):
  """
  Reverse index matrix.
  
  Example:
    `indexMatrix` contains the VID object indices (less than `maxIndex`) for every FUS object for all timestamps:
      obj \ time | t0 | t1 | t2 | ... | tn
      -----------+----+----+----+-----+-----
          0      | 9  | 9  | 8  | ... | invalid
          1      | 7  | 6  | 6  | ... | 6
          ...    |         ...
          31     | 0  | 0  | 0  | ... | 0
    
    The reversed matrix (with elements less than FUS_OBJ_NUM) contains the FUS object indices for every VID object for all timestamps:
      obj \ time | t0 | t1 | t2 | ... | tn
      -----------+----+----+----+-----+-----
          0      | 31 | 31 | 31 | ... | 31
          1      |         ...
          ...    |         ...
          9      | 0  | 0  | ...| ... | retInvalid
  """
  indexMatrixT = indexMatrix.transpose()
  reversedT_ll = [[numpy.where(indexRow == i)[0] if i in indexRow else retInvalidValue for i in xrange(maxIndex)] for indexRow in indexMatrixT]
  reversed = numpy.array(reversedT_ll).transpose()
  return reversed

def getIntervals(vector):
  """Return the intervals where the value in `vector` is constant."""
  if not vector.size:
    return []
  changes = numpy.where(numpy.diff(vector))[0] + 1
  starts = numpy.insert(changes, 0, 0)
  ends = numpy.append(changes, vector.size)
  intervals = zip(starts, ends)
  return intervals

class cView(interface.iView):
  def check(self):
    group = interface.Source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    return group

  def view(cls, param, group):
    # time
    time = interface.Source.getSignalFromSignalGroup(group, "fus_s_asso_mat.VidObjIdx.i0")[0]
    if not time.size:
      print "No data to evaluate."
      return
    # video indices
    fus2vid = numpy.ndarray((FUS_OBJ_NUM, time.size))
    for i in xrange(FUS_OBJ_NUM):
      fus2vid[i] = interface.Source.getSignalFromSignalGroup(group, "fus_s_asso_mat.VidObjIdx.i%d" % i)[1]
    vid2fus = reverseIndices(fus2vid, VID_OBJ_NUM, VID_INVALID_ID)
    # radar indices
    ohy2vid = numpy.ndarray((OHY_OBJ_NUM, time.size))
    for i in xrange(OHY_OBJ_NUM):
      ohy2vid[i] = interface.Source.getSignalFromSignalGroup(group, "fus_s_asso_mat.VidToLrrIdx.i%d" % i)[1]
    vid2ohy = reverseIndices(ohy2vid, VID_OBJ_NUM, VID_INVALID_ID)
    
    assoFound = False
    # loop on all video object positions
    for cur_id_vid, curvid2fus in enumerate(vid2fus):
      if numpy.all(curvid2fus == INVALID_VALUE):
        continue  # no asso for this video object at all
      assoFound = True
      
      dummy_array = numpy.array([numpy.NaN] * time.size)
      
      id_ohy = dummy_array.copy()
      id_fus = dummy_array.copy()
      id_vid = dummy_array.copy()
      
      wAssoProb_uw = dummy_array.copy()
      dx_ohy = dummy_array.copy()
      dx_vid = dummy_array.copy()
      dy_ohy = dummy_array.copy()
      dy_vid = dummy_array.copy()
      dy_fus = dummy_array.copy()
      vx_ohy = dummy_array.copy()
      alpLeftedge_vid  = dummy_array.copy()
      alpRightedge_vid = dummy_array.copy()
      invTTtipc_vid  = dummy_array.copy()
      wExistProb_ohy = dummy_array.copy()
      wExistProb_vid = dummy_array.copy()
      wExistProb_fus = dummy_array.copy()
      
      # loop on all association intervals for the given video index
      assoIntervals = getIntervals(curvid2fus)
      for start, end in assoIntervals:
        # current ids for the given association (constants on the whole interval - get the first elements)
        cur_id_fus = vid2fus[cur_id_vid][start]
        if cur_id_fus == INVALID_VALUE:
          continue  # no asso in this interval
        cur_id_ohy = vid2ohy[cur_id_vid][start]
        # ids
        id_ohy[start:end] = cur_id_ohy
        id_vid[start:end] = cur_id_vid
        id_fus[start:end] = cur_id_fus
        # values
        wAssoProb_uw[start:end]     = interface.Source.getSignalFromSignalGroup(group, "fus_s_asso_mat.ProbAssoMat.probability.i%d.i%d" %(cur_id_ohy, cur_id_vid))[1][start:end]
        dx_ohy[start:end]           = interface.Source.getSignalFromSignalGroup(group, "ohy.ObjData_TC.OhlObj.i%d.dx"                   % cur_id_ohy)[1][start:end]
        dx_vid[start:end]           = interface.Source.getSignalFromSignalGroup(group, "fus.SVidBasicInput_TC.VidObj.i%d.dxv"           % cur_id_vid)[1][start:end]
        dy_ohy[start:end]           = interface.Source.getSignalFromSignalGroup(group, "ohy.ObjData_TC.OhlObj.i%d.dy"                   % cur_id_ohy)[1][start:end]
        dy_vid[start:end]           = interface.Source.getSignalFromSignalGroup(group, "fus.SVidBasicInput_TC.VidObj.i%d.dyv"           % cur_id_vid)[1][start:end]
        dy_fus[start:end]           = interface.Source.getSignalFromSignalGroup(group, "fus.ObjData_TC.FusObj.i%d.dyv"                  % cur_id_fus)[1][start:end]
        vx_ohy[start:end]           = interface.Source.getSignalFromSignalGroup(group, "ohy.ObjData_TC.OhlObj.i%d.vx"                   % cur_id_ohy)[1][start:end]
        alpLeftedge_vid[start:end]  = interface.Source.getSignalFromSignalGroup(group, "fus.SVidBasicInput_TC.VidObj.i%d.alpLeftEdge"   % cur_id_vid)[1][start:end]
        alpRightedge_vid[start:end] = interface.Source.getSignalFromSignalGroup(group, "fus.SVidBasicInput_TC.VidObj.i%d.alpRightEdge"  % cur_id_vid)[1][start:end]
        invTTtipc_vid[start:end]    = interface.Source.getSignalFromSignalGroup(group, "fus.SVidBasicInput_TC.VidObj.i%d.invTTtipc"     % cur_id_vid)[1][start:end]
        wExistProb_ohy[start:end]   = interface.Source.getSignalFromSignalGroup(group, "ohy.ObjData_TC.OhlObj.i%d.wExistProb"           % cur_id_ohy)[1][start:end]
        wExistProb_vid[start:end]   = interface.Source.getSignalFromSignalGroup(group, "fus.SVidBasicInput_TC.VidObj.i%d.wExistProb"    % cur_id_vid)[1][start:end]
        wExistProb_fus[start:end]   = interface.Source.getSignalFromSignalGroup(group, "fus.ObjData_TC.FusObj.i%d.wExistProb"           % cur_id_fus)[1][start:end]
      
      # create navigator for the given video index and plot the results
      client = datavis.cPlotNavigator(title="asofus & filfus (VID%d)" % cur_id_vid, figureNr=None)
      interface.Sync.addClient(client)
      # ids
      axis49 = client.addAxis()
      client.addSignal2Axis(axis49, "ohy id", time, id_ohy, unit="")
      client.addSignal2Axis(axis49, "vid id", time, id_vid, unit="")
      client.addSignal2Axis(axis49, "fus id", time, id_fus, unit="")
      # asso prob
      axis13 = client.addAxis()
      client.addSignal2Axis(axis13, "asso prob", time, wAssoProb_uw/float(N_prob1UW_uw), unit="") # normalization
      # dx
      axis22 = client.addAxis()
      client.addSignal2Axis(axis22, "ohy dx", time, dx_ohy, unit="m")
      client.addSignal2Axis(axis22, "vid dx", time, dx_vid, unit="m")
      # angle
      axis51 = client.addAxis()
      alpMid_ohy = numpy.arctan2(dy_ohy, dx_ohy)
      client.addSignal2Axis(axis51, "ohy alpMid",   time, alpMid_ohy,       unit="rad")
      client.addSignal2Axis(axis51, "vid alpLeft",  time, alpLeftedge_vid,  unit="rad")
      client.addSignal2Axis(axis51, "vid alpRight", time, alpRightedge_vid, unit="rad")
      # inv TTipC
      axis08 = client.addAxis()
      with numpy.errstate(divide='ignore'):
        invTTtipc_ohy = -vx_ohy/dx_ohy
      client.addSignal2Axis(axis08, "ohy invTTtipc", time, invTTtipc_ohy, unit="1/s")
      client.addSignal2Axis(axis08, "vid invTTtipc", time, invTTtipc_vid, unit="1/s")
      # dy
      axis76 = client.addAxis()
      client.addSignal2Axis(axis76, "ohy dy", time, dy_ohy, unit="m")
      client.addSignal2Axis(axis76, "vid dy", time, dy_vid, unit="m")
      client.addSignal2Axis(axis76, "fus dy", time, dy_fus, unit="m")
      # exist prob
      axis34 = client.addAxis()
      client.addSignal2Axis(axis34, "ohy existProb", time, wExistProb_ohy, unit="-")
      client.addSignal2Axis(axis34, "vid existProb", time, wExistProb_vid, unit="-")
      client.addSignal2Axis(axis34, "fus existProb", time, wExistProb_fus, unit="-")
    
    if not assoFound:
      print "No association found."
    return
