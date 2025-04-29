import datavis
import measparser
import interface
import numpy as np

class cParameter(interface.iParameter):
  def __init__(self, posMatrixIndex):
    self.posMatrixIndex = posMatrixIndex
    self.genKeys()
    pass
# instantiation of module parameters
SIT_L1 = cParameter(0)
SIT_S1 = cParameter(1)
SIT_R1 = cParameter(2)
SIT_L2 = cParameter(3)
SIT_S2 = cParameter(4)
SIT_R2 = cParameter(5)

SignalGroups = []
sg = {}
fusIndices = xrange(0, 32)
sitFiltObjIndices = xrange(0,6)
sitFiltObjNames = ["L1", "S1", "R1", "L2", "S2", "R2"]
# fusIndices = (23,)

for i in fusIndices:
  sg["fus.ObjData_TC.FusObj.i%i.Handle" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.Handle" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.dxv" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.dxv" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.vxv" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.vxv" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.axv" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.axv" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.dyv" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.dyv" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.b.b.DriveInvDir_b" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.b.b.DriveInvDir_b" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.b.b.Hist_b" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.b.b.Hist_b" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.b.b.Measured_b" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.b.b.Measured_b" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.b.b.Stand_b" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.b.b.Stand_b" % (i))
  sg["fus.ObjData_TC.FusObj.i%i.b.b.Stopped_b" % (i)] = ("MRR1plus", "fus.ObjData_TC.FusObj.i%i.b.b.Stopped_b" % (i))
for i in sitFiltObjIndices:
  sg["sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i%i"%(i)] = ("MRR1plus", "sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i%i"%(i))

SignalGroups.append(sg)

class cView(interface.iView):
  @classmethod
  def view(cls, Param):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      Time = interface.Source.getSignalFromSignalGroup(Group,  "sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i0")[0]
      i =  Param.posMatrixIndex
      handle = interface.Source.getSignalFromSignalGroup(Group,  "sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i%i"%(i))[1]
      dx = np.zeros(handle.shape, dtype='float64')    
      dy = np.zeros(handle.shape, dtype='float64')    
      vx = np.zeros(handle.shape, dtype='float64')
      fDriveIvDir = np.zeros(handle.shape, dtype='int32')
      fHist = np.zeros(handle.shape, dtype='int32')   
      fMeasured  = np.zeros(handle.shape, dtype='int32')
      fStand = np.zeros(handle.shape, dtype='int32')     
      fStopped = np.zeros(handle.shape, dtype='int32')
      for j in fusIndices:
        fusHandle = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%i.Handle"%(j))[1]
        fusDx = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%i.dxv"%(j))[1]
        fusDy = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%i.dyv"%(j))[1]
        fusVx = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%i.vxv"%(j))[1]
        fusDriveIvDir = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%i.b.b.DriveInvDir_b"%(j))[1]
        fusHist = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%i.b.b.Hist_b"%(j))[1]
        fusMeasured = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%i.b.b.Measured_b"%(j))[1]
        fusStand = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%i.b.b.Stand_b"%(j))[1]
        fusStopped = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%i.b.b.Stopped_b"%(j))[1]
        mask = np.logical_and(handle > 0, handle == fusHandle)
        dx[mask] = fusDx[mask]
        dy[mask] = fusDy[mask]
        vx[mask] = fusVx[mask]
        fDriveIvDir[mask] = fusDriveIvDir[mask]
        fHist[mask] = fusHist[mask]
        fMeasured[mask] = fusMeasured[mask]
        fStand[mask] = fusStand[mask]
        fStopped[mask] = fusStopped[mask]
      Client = datavis.cPlotNavigator(title="Posmatrix %s" % (sitFiltObjNames[i]), figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "%s Handle" % (sitFiltObjNames[i]), Time, handle, unit="-")
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "%s Dx" % (sitFiltObjNames[i]), Time, dx, unit="m")
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "%s Dy" % (sitFiltObjNames[i]), Time, dy, unit="m")
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "%s Vx" % (sitFiltObjNames[i]), Time, vx, unit="m/s")
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "%s DriveIvDir" % (sitFiltObjNames[i]), Time, fDriveIvDir, unit="-")
      Client.addSignal2Axis(Axis, "%s Hist" % (sitFiltObjNames[i]), Time, fHist, unit="-")
      Client.addSignal2Axis(Axis, "%s Measured" % (sitFiltObjNames[i]), Time, fMeasured, unit="-")
      Client.addSignal2Axis(Axis, "%s Stand" % (sitFiltObjNames[i]), Time, fStand, unit="-")
      Client.addSignal2Axis(Axis, "%s Stopped" % (sitFiltObjNames[i]), Time, fStopped, unit="-")
  pass
