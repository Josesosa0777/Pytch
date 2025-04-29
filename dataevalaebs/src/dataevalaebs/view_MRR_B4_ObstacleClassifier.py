import datavis
import interface
import numpy as np

class cParameter(interface.iParameter):
  def __init__(self, fusIndex):
    self.fusIndex = fusIndex
    self.genKeys()
    pass
# instantiation of module parameters
FUS_00 = cParameter(0)
FUS_01 = cParameter(1)
FUS_02 = cParameter(2)
FUS_03 = cParameter(3)
FUS_04 = cParameter(4)
FUS_05 = cParameter(5)
FUS_06 = cParameter(6)
FUS_07 = cParameter(7)
FUS_08 = cParameter(8)
FUS_09 = cParameter(9)
FUS_10 = cParameter(10)
FUS_11 = cParameter(11)
FUS_12 = cParameter(12)
FUS_13 = cParameter(13)
FUS_14 = cParameter(14)
FUS_15 = cParameter(15)
FUS_16 = cParameter(16)
FUS_17 = cParameter(17)
FUS_18 = cParameter(18)
FUS_19 = cParameter(19)
FUS_20 = cParameter(20)
FUS_21 = cParameter(21)
FUS_22 = cParameter(22)
FUS_23 = cParameter(23)
FUS_24 = cParameter(24)
FUS_25 = cParameter(25)
FUS_26 = cParameter(26)
FUS_27 = cParameter(27)
FUS_28 = cParameter(28)
FUS_29 = cParameter(29)
FUS_30 = cParameter(30)
FUS_31 = cParameter(31)

SignalGroups = []
sg = {}
fusIndices = xrange(0, 32)

for i in fusIndices:
  sg["fus.ObjData_TC.FusObj.i%i.Handle" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.Handle" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.dxv" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.dxv" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.wClassObstacleNear" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.wClassObstacleNear" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.wClassObstacle" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.wClassObstacle" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.qClass" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.qClass" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.wConstElem" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.wConstElem" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.dVarYvBase" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.dVarYvBase" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.wObstacle" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.wObstacle" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.wExistProb" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.wExistProb" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.dLength" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.dLength" % (i))

SignalGroups.append(sg)

class cView(interface.iView):
  @classmethod
  def view(cls, Param):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except ValueError, error:
      print __file__
      print error.message
    else:
      j =  Param.fusIndex
      Client = datavis.cPlotNavigator(title="FUS Object %i Obstacle Classification" % (j), figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()     
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%i.dxv"%(j))      
      Client.addSignal2Axis(Axis, "Dx", Time, Value, unit="m")
      Axis = Client.addAxis()     
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%i.wExistProb"%(j))      
      Client.addSignal2Axis(Axis, "wExistProb", Time, Value, unit="m")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%i.wClassObstacle"%(j))      
      Client.addSignal2Axis(Axis, "wClassObstacle", Time, Value, unit="-")
      Axis.axhspan(0.0, 0.5, facecolor="r", alpha=.4)
      Axis = Client.addAxis()     
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%i.dLength"%(j))      
      Client.addSignal2Axis(Axis, "dLength", Time, Value, unit="m")
      Axis.axhspan(0.0, 1.0, facecolor="r", alpha=.4)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%i.wConstElem"%(j))      
      Client.addSignal2Axis(Axis, "wConstElem", Time, Value, unit="-")
      Axis.axhspan(0.003, 1.0, facecolor="r", alpha=.4)
      Axis = Client.addAxis()     
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%i.dVarYvBase"%(j))      
      Client.addSignal2Axis(Axis, "dVarYvBase", Time, Value, unit="m2")
      Axis.axhspan(0.5, 20.0, facecolor="r", alpha=.4)
      Axis = Client.addAxis()     
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%i.wClassObstacleNear"%(j))
      Client.addSignal2Axis(Axis, "wClassObstacleNear", Time, Value, unit="-")
      Axis.axhspan(0.0, 0.7, facecolor="r", alpha=.4)
      Axis = Client.addAxis()     
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%i.qClass"%(j))      
      Client.addSignal2Axis(Axis, "qClass", Time, Value, unit="m")
      Axis.axhspan(0.0, 0.7, facecolor="r", alpha=.4)
  pass
