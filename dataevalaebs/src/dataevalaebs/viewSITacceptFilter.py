import numpy as np

import interface
import measparser
import datavis

FUS_OBJ_NUM = 32
INVALID_FUS_2_OHL_ASSOC = 255

posElements = {'L1': 0,
               'S1': 1,
               'R1': 2,
               'L2': 3,
               'S2': 4,
               'R2': 5}
SignalGroups = []
for dn in ("MRR1plus", "RadarFC"):
  MRR1signalGroup = {}
  for i in xrange(FUS_OBJ_NUM):
    MRR1signalGroup["%d_handle"              %i] = (dn, "fus.ObjData_TC.FusObj.i%d.Handle"              %i)
    MRR1signalGroup["%d_dxv"                 %i] = (dn, "fus.ObjData_TC.FusObj.i%d.dxv"                 %i)
    MRR1signalGroup["%d_dVarYvBase"          %i] = (dn, "fus.ObjData_TC.FusObj.i%d.dVarYvBase"          %i)
    MRR1signalGroup["%d_wObstacle"           %i] = (dn, "fus.ObjData_TC.FusObj.i%d.wObstacle"           %i)
    MRR1signalGroup["%d_wClassObstacle"      %i] = (dn, "fus.ObjData_TC.FusObj.i%d.wClassObstacle"      %i)
    MRR1signalGroup["%d_wClassObstacleNear"  %i] = (dn, "fus.ObjData_TC.FusObj.i%d.wClassObstacleNear"  %i)
    MRR1signalGroup["%d_qClass"              %i] = (dn, "fus.ObjData_TC.FusObj.i%d.qClass"              %i)
    MRR1signalGroup["%d_wExistProb"          %i] = (dn, "fus.ObjData_TC.FusObj.i%d.wExistProb"          %i)
    MRR1signalGroup["%d_wGroundReflex"       %i] = (dn, "fus.ObjData_TC.FusObj.i%d.wGroundReflex"       %i)
    MRR1signalGroup["%d_wConstElem"          %i] = (dn, "fus.ObjData_TC.FusObj.i%d.wConstElem"          %i)
    MRR1signalGroup["%d_b.b.NotClassified_b" %i] = (dn, "fus.ObjData_TC.FusObj.i%d.b.b.NotClassified_b" %i)
    MRR1signalGroup['%d_dLength'             %i] = (dn, "fus.ObjData_TC.FusObj.i%d.dLength"             %i)
    MRR1signalGroup['fus.i%d_to_ohl_assoc'   %i] = (dn, 'fus_asso_mat.LrrObjIdx.i%d'                    %i)
  for posName, posID in posElements.items():
    MRR1signalGroup['%s_Object'        %posName] = (dn, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i%d' %posID)
  SignalGroups.append(MRR1signalGroup)
  
class cParameter(interface.iParameter):
  def __init__(self, fusIndex):
    self.fusIndex = fusIndex
    self.genKeys()
    pass
# instantiation of module parameters
FUS_INDEX_00 = cParameter(0)
FUS_INDEX_01 = cParameter(1)
FUS_INDEX_02 = cParameter(2)
FUS_INDEX_03 = cParameter(3)
FUS_INDEX_04 = cParameter(4)
FUS_INDEX_05 = cParameter(5)
FUS_INDEX_06 = cParameter(6)
FUS_INDEX_07 = cParameter(7)
FUS_INDEX_08 = cParameter(8)
FUS_INDEX_09 = cParameter(9)
FUS_INDEX_10 = cParameter(10)
FUS_INDEX_11 = cParameter(11)
FUS_INDEX_12 = cParameter(12)
FUS_INDEX_13 = cParameter(13)
FUS_INDEX_14 = cParameter(14)
FUS_INDEX_15 = cParameter(15)
FUS_INDEX_16 = cParameter(16)
FUS_INDEX_17 = cParameter(17)
FUS_INDEX_18 = cParameter(18)
FUS_INDEX_19 = cParameter(19)
FUS_INDEX_20 = cParameter(20)
FUS_INDEX_21 = cParameter(21)
FUS_INDEX_22 = cParameter(22)
FUS_INDEX_23 = cParameter(23)
FUS_INDEX_24 = cParameter(24)
FUS_INDEX_25 = cParameter(25)
FUS_INDEX_26 = cParameter(26)
FUS_INDEX_27 = cParameter(27)
FUS_INDEX_28 = cParameter(28)
FUS_INDEX_29 = cParameter(29)
FUS_INDEX_30 = cParameter(30)
FUS_INDEX_31 = cParameter(31)

class cView(interface.iView):
  @classmethod
  def view(cls, Param):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      i = Param.fusIndex
      Client = datavis.cPlotNavigator(title="FUS object %d" %i, figureNr=None)
      
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "%d_handle"              %i)
      
      Axis = Client.addAxis()
      for posName, posID in posElements.items():
        posHandle = interface.Source.getSignalFromSignalGroup(Group, '%s_Object'        %posName, ScaleTime=Time)[1]
        posElemMask = Value == posHandle
        Client.addSignal2Axis(Axis, posName, Time, posElemMask, unit='-')
      
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "handle", Time, Value, unit='-')
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, 'fus.i%d_to_ohl_assoc'   %i)
      mask = (Value==INVALID_FUS_2_OHL_ASSOC)
      Value = np.where(mask, np.NaN, Value)
      Client.addSignal2Axis(Axis, "ohl_assoc", Time, Value, unit='-')
      
      Axis = Client.addAxis()
      Time, dx = interface.Source.getSignalFromSignalGroup(Group, "%d_dxv"                 %i)
      PhysUnit    = interface.Source.getPhysicalUnitFromSignalGroup(Group, "%d_dxv"           %i)
      Client.addSignal2Axis(Axis, "dx", Time, dx, unit=PhysUnit)
      
      Axis = Client.addAxis()
      Time, dVarYvBase = interface.Source.getSignalFromSignalGroup(Group, "%d_dVarYvBase"          %i)
      PhysUnit    = interface.Source.getPhysicalUnitFromSignalGroup(Group, "%d_dVarYvBase"    %i)
      Client.addSignal2Axis(Axis, "dVarYvBase", Time, dVarYvBase, unit=PhysUnit)
      
      Axis = Client.addAxis()
      Time, wObstacle = interface.Source.getSignalFromSignalGroup(Group, "%d_wObstacle"           %i)
      Client.addSignal2Axis(Axis, "wObstacle", Time, wObstacle, unit='-')
      Time, wClassObstacle = interface.Source.getSignalFromSignalGroup(Group, "%d_wClassObstacle"      %i)
      Client.addSignal2Axis(Axis, "wClassObstacle", Time, wClassObstacle, unit='-')
      Time, wClassObstacleNear = interface.Source.getSignalFromSignalGroup(Group, "%d_wClassObstacleNear"  %i)
      Client.addSignal2Axis(Axis, "wClassObstacleNear", Time, wClassObstacleNear, unit='-')
      Time, qClass = interface.Source.getSignalFromSignalGroup(Group, "%d_qClass"              %i)
      Client.addSignal2Axis(Axis, "qClass", Time, qClass, unit='-')
      
      Axis = Client.addAxis()
      Time, wExistProb = interface.Source.getSignalFromSignalGroup(Group, "%d_wExistProb"          %i)
      Client.addSignal2Axis(Axis, "wExistProb", Time, wExistProb, unit='-')
      Time, wGroundReflex = interface.Source.getSignalFromSignalGroup(Group, "%d_wGroundReflex"       %i)
      Client.addSignal2Axis(Axis, "wGroundReflex", Time, wGroundReflex, unit='-')
      Time, wConstElem = interface.Source.getSignalFromSignalGroup(Group, "%d_wConstElem" %i)
      Client.addSignal2Axis(Axis, "wConstElem", Time, wConstElem, unit='-')
      Time, NotClassified_b = interface.Source.getSignalFromSignalGroup(Group, "%d_b.b.NotClassified_b" %i)
      Client.addSignal2Axis(Axis, "NotClassified_b", Time, NotClassified_b, unit='-')

      Axis = Client.addAxis()
      Time, dLength = interface.Source.getSignalFromSignalGroup(Group, "%d_dLength"             %i)
      Client.addSignal2Axis(Axis, "dLength", Time, dLength, unit='-')

      # Valid parameter values of 1.2.1.8 release
      P_dVarYLimitStationary_uw = 1.0 # K1 is 1.0 as well
      P_wExistStationary_uw = 0.8 # K1 is 0.8 as well
      P_wGroundReflex_ub = 0.1  
      
      ObstacleIsValid = (wExistProb >= P_wExistStationary_uw) &\
        (dVarYvBase <= P_dVarYLimitStationary_uw) &\
        (wGroundReflex <= P_wGroundReflex_ub)
        
      # Relevant parameter values of 1.2.1.8 release
      P_dOutOfSightSO_sw = 100.0
      P_wObstacleProbFar_uw = 0.5
      P_wObstacleNear_uw = 0.7
      P_wObstacleNearQClass_uw = 0.7
      P_dLengthFar_sw = 1.0
      P_wConstructionElementFar_ub = 0.003
      P_dVarYLimitFar_uw = 0.5
      
      # Check if the stationary object is a relevant obstacle.
      # If one of the classifieres (near or far) and for near also the qClass value
      # is above the threshold, the obstacle is relevant.
      ObstacleIsRelevant = (dx <= P_dOutOfSightSO_sw) &\
        (
        (wClassObstacle >= P_wObstacleProbFar_uw) &\
        (wConstElem < P_wConstructionElementFar_ub) &\
        (dLength > P_dLengthFar_sw) &\
        (dVarYvBase < P_dVarYLimitFar_uw)
        ) |\
        (\
        (wClassObstacleNear	>= P_wObstacleNearQClass_uw) &\
        (qClass		>= P_wObstacleNearQClass_uw)\
        )

      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "Valid & Relevant", Time, (ObstacleIsRelevant & ObstacleIsValid), unit='-')
        
      interface.Sync.addClient(Client)
      pass
    pass


