import sys

import numpy

import measparser
import interface
import measproc

import aebs
from aebs.sdf import asso_cvr3_ac100
from aebs.par import grouptypes

DefParam = interface.NullParam

FUS_OBJ_MAX = 32
FUS_HANDLE_MAX = 64
sg = {}
for i in range(FUS_OBJ_MAX):
  sg["fus.ObjData_TC.FusObj.i%d.Handle" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%d.Handle" % (i))
  sg["fus_asso_mat.LrrObjIdx.i%d" % (i)] = ("MRR1plus", "fus_asso_mat.LrrObjIdx.i%d" % (i))
sg["evi.General_TC.vxvRef"] = ("ECU", "evi.General_TC.vxvRef")
sg["evi.General_T20.psiDtOpt"] = ("ECU", "evi.General_T20.psiDtOpt")
SignalGroups = [sg]

class cSearch(interface.iSearch):
  dep = 'fillAC100@aebs.fill', 'fillAC100_POS@aebs.fill', \
        'fillCVR3_POS@aebs.fill', 'fillCVR3_OHL@aebs.fill'
  def check(self):
    Source = self.get_source('main')
    # Check and select own groups
    Group = Source.selectSignalGroup(SignalGroups)
    # Check association groups
    Source.selectSignalGroup(asso_cvr3_ac100.signalGroups)
    return Group

  def fill(self, Group):
    Modules = self.get_modules()
    Time, AC100Objects = Modules.fill("fillAC100@aebs.fill")
    AC100Time, AC100PosObjects = Modules.fill("fillAC100_POS@aebs.fill")
    print >> sys.stderr, AC100PosObjects[0].keys()
    AC100PosObjects = measproc.Object.rescaleObjects(AC100PosObjects, AC100Time, Time)
    print >> sys.stderr, AC100PosObjects[0].keys()
    try:
      Time = Modules.ScaleTime
    except AttributeError:
      Modules.ScaleTime = Time

    CVR3PosObjects = Modules.fill("fillCVR3_POS@aebs.fill")[1]
    CVR3OhlObjects = Modules.fill("fillCVR3_OHL@aebs.fill")[1]
    # Asso scaletime, reliability threshold and AC100 credibility mapping
    Source = self.get_source('main')
    assoObj = asso_cvr3_ac100.AssoCvr3Ac100(Source, Time, reliabilityLimit=0.4, mapAc100credib=lambda x:numpy.where(x<0.1, 4*x, 2./3.*x+1./3.))
    return Group, Time, assoObj, AC100Objects, AC100PosObjects, CVR3PosObjects, CVR3OhlObjects

  def search(self, Param, Group, Time, assoObj, AC100Objects, AC100PosObjects, CVR3PosObjects, CVR3OhlObjects):
    Source = self.get_source('main')
    Batch = self.get_batch()
    # Calculate association (cost matrix calculation and track-to-track association)
    assoObj.calc()

    # Select position matrix elements
    # PositionsCVR3 = ["LeftLane_near", "SameLane_near", "RightLane_near", "SameLane_far"]
    PositionsCVR3 = ["SameLane_near"]
    CVR3PosHandle = {}
    for o in CVR3PosObjects:
      for s in  PositionsCVR3:
        if o["label"] == s:
          CVR3PosHandle[s] = o["id"]
    # PositionsAC100 = ["NIV_L", "ACC", "NIV_R", "IIV"]
    PositionsAC100 = ["ACC"]
    AC100PosHandle = {}
    for o in AC100PosObjects:
      for s in PositionsAC100:
        if o["label"] == s:
          AC100PosHandle[s] = numpy.ones_like(Time) * -1
          mask = o["type"] == grouptypes.AC100_ACC
          AC100PosHandle[s][mask] = o["id"][mask]

    # Handle to OHL cross table calculation
    HandlesToOhl = {}
    for h in range(1, FUS_HANDLE_MAX):
      hto = numpy.zeros_like(Time, dtype=int)
      for i in range(FUS_OBJ_MAX):
        Handle = Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%d.Handle" % (i), ScaleTime = Time)[1]
        OhlIndex = Source.getSignalFromSignalGroup(Group, "fus_asso_mat.LrrObjIdx.i%d" % (i), ScaleTime = Time)[1]
        mask = h == Handle
        hto[mask] = OhlIndex[mask]
      # ind1, = numpy.where(hto == 255)
      # ind2 = ind1 + 1
      # if ind2[-1] > hto.size:
        # ind2[-1] -= 1
      # hto[ind1] = hto[ind2]
      HandlesToOhl[h] = hto

    # Get vehicle data for filtering
    Velocity = Source.getSignalFromSignalGroup(Group, "evi.General_TC.vxvRef", ScaleTime = Time)[1]
    YawRate = Source.getSignalFromSignalGroup(Group, "evi.General_T20.psiDtOpt", ScaleTime = Time)[1]
    # Create mask for fiter inrelevant data
    VxvRef = Source.getSignalFromSignalGroup(Group, "evi.General_TC.vxvRef", ScaleTime = Time)[1]
    FilterMask = VxvRef < (15. / 3.6)

    # AssoMasked = numpy.array(assoObj.objectPairs, dtype=numpy.object)[mask]
    IntroAssociatedCVR3 = {}
    for key in CVR3PosHandle.iterkeys():
      IntroAssociatedCVR3[key] = numpy.ones_like(Time) * -2
    IntroAssociatedAC100 = {}
    for key in AC100PosHandle.iterkeys():
      IntroAssociatedAC100[key] = numpy.ones_like(Time) * -2
    for k, assoList in enumerate(assoObj.objectPairs):
      # Search where AC100 object is associated with CVR3 position matrix element
      for key, value in CVR3PosHandle.iteritems():
        if value[k] < 1:
          IntroAssociatedCVR3[key][k] =  -1
        else:
          for asso in assoList:
            if HandlesToOhl[value[k]][k] == asso[0]:
              IntroAssociatedCVR3[key][k] = asso[1]
      # Search where CVR3 object is associated with AC100 position matrix element
      for key, value in AC100PosHandle.iteritems():
        if value[k] < 0:
          IntroAssociatedAC100[key][k] =  -1
        else:
          for asso in assoList:
            if value[k] == asso[1]:
              IntroAssociatedAC100[key][k] = asso[0]


    # Create reports
    for key in CVR3PosHandle.iterkeys():
      NoAssociationCVR3 = IntroAssociatedCVR3[key] == -2
      NoAssociationCVR3_Filtered = numpy.where(FilterMask, False, NoAssociationCVR3)
      Intervals = Source.compare(Time, NoAssociationCVR3_Filtered, measproc.equal, True)
      Title = "CVR3_%s" % (key)
      Report = measproc.cIntervalListReport(Intervals, Title)
      Batch.add_entry(Report, self.NONE)
    #Get and plot AC100 and associated CVR3 data
    for key in AC100PosHandle.iterkeys():
      NoAssociationAC100 = IntroAssociatedAC100[key] == -2
      NoAssociationAC100_Filtered = numpy.where(FilterMask, False, NoAssociationAC100)
      Intervals = Source.compare(Time, NoAssociationAC100_Filtered, measproc.equal, True)
      Title = "AC100_%s" % (key)
      Report = measproc.cIntervalListReport(Intervals, Title)
      Batch.add_entry(Report, self.NONE)

    return

