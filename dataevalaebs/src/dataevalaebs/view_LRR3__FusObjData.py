import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"fus.ObjData_TC.FusObj.i0.Handle": ("ECU", "fus.ObjData_TC.FusObj.i0.Handle"),
                 "fus.ObjData_TC.FusObj.i1.Handle": ("ECU", "fus.ObjData_TC.FusObj.i1.Handle"),
                 "fus.ObjData_TC.FusObj.i10.Handle": ("ECU", "fus.ObjData_TC.FusObj.i10.Handle"),
                 "fus.ObjData_TC.FusObj.i11.Handle": ("ECU", "fus.ObjData_TC.FusObj.i11.Handle"),
                 "fus.ObjData_TC.FusObj.i12.Handle": ("ECU", "fus.ObjData_TC.FusObj.i12.Handle"),
                 "fus.ObjData_TC.FusObj.i13.Handle": ("ECU", "fus.ObjData_TC.FusObj.i13.Handle"),
                 "fus.ObjData_TC.FusObj.i14.Handle": ("ECU", "fus.ObjData_TC.FusObj.i14.Handle"),
                 "fus.ObjData_TC.FusObj.i15.Handle": ("ECU", "fus.ObjData_TC.FusObj.i15.Handle"),
                 "fus.ObjData_TC.FusObj.i16.Handle": ("ECU", "fus.ObjData_TC.FusObj.i16.Handle"),
                 "fus.ObjData_TC.FusObj.i17.Handle": ("ECU", "fus.ObjData_TC.FusObj.i17.Handle"),
                 "fus.ObjData_TC.FusObj.i18.Handle": ("ECU", "fus.ObjData_TC.FusObj.i18.Handle"),
                 "fus.ObjData_TC.FusObj.i19.Handle": ("ECU", "fus.ObjData_TC.FusObj.i19.Handle"),
                 "fus.ObjData_TC.FusObj.i2.Handle": ("ECU", "fus.ObjData_TC.FusObj.i2.Handle"),
                 "fus.ObjData_TC.FusObj.i20.Handle": ("ECU", "fus.ObjData_TC.FusObj.i20.Handle"),
                 "fus.ObjData_TC.FusObj.i21.Handle": ("ECU", "fus.ObjData_TC.FusObj.i21.Handle"),
                 "fus.ObjData_TC.FusObj.i22.Handle": ("ECU", "fus.ObjData_TC.FusObj.i22.Handle"),
                 "fus.ObjData_TC.FusObj.i23.Handle": ("ECU", "fus.ObjData_TC.FusObj.i23.Handle"),
                 "fus.ObjData_TC.FusObj.i24.Handle": ("ECU", "fus.ObjData_TC.FusObj.i24.Handle"),
                 "fus.ObjData_TC.FusObj.i25.Handle": ("ECU", "fus.ObjData_TC.FusObj.i25.Handle"),
                 "fus.ObjData_TC.FusObj.i26.Handle": ("ECU", "fus.ObjData_TC.FusObj.i26.Handle"),
                 "fus.ObjData_TC.FusObj.i27.Handle": ("ECU", "fus.ObjData_TC.FusObj.i27.Handle"),
                 "fus.ObjData_TC.FusObj.i28.Handle": ("ECU", "fus.ObjData_TC.FusObj.i28.Handle"),
                 "fus.ObjData_TC.FusObj.i29.Handle": ("ECU", "fus.ObjData_TC.FusObj.i29.Handle"),
                 "fus.ObjData_TC.FusObj.i3.Handle": ("ECU", "fus.ObjData_TC.FusObj.i3.Handle"),
                 "fus.ObjData_TC.FusObj.i30.Handle": ("ECU", "fus.ObjData_TC.FusObj.i30.Handle"),
                 "fus.ObjData_TC.FusObj.i31.Handle": ("ECU", "fus.ObjData_TC.FusObj.i31.Handle"),
                 "fus.ObjData_TC.FusObj.i32.Handle": ("ECU", "fus.ObjData_TC.FusObj.i32.Handle"),
                 "fus.ObjData_TC.FusObj.i4.Handle": ("ECU", "fus.ObjData_TC.FusObj.i4.Handle"),
                 "fus.ObjData_TC.FusObj.i5.Handle": ("ECU", "fus.ObjData_TC.FusObj.i5.Handle"),
                 "fus.ObjData_TC.FusObj.i6.Handle": ("ECU", "fus.ObjData_TC.FusObj.i6.Handle"),
                 "fus.ObjData_TC.FusObj.i7.Handle": ("ECU", "fus.ObjData_TC.FusObj.i7.Handle"),
                 "fus.ObjData_TC.FusObj.i8.Handle": ("ECU", "fus.ObjData_TC.FusObj.i8.Handle"),
                 "fus.ObjData_TC.FusObj.i9.Handle": ("ECU", "fus.ObjData_TC.FusObj.i9.Handle"),
                 "fus.ObjData_TC.FusObj.i0.dxv": ("ECU", "fus.ObjData_TC.FusObj.i0.dxv"),
                 "fus.ObjData_TC.FusObj.i1.dxv": ("ECU", "fus.ObjData_TC.FusObj.i1.dxv"),
                 "fus.ObjData_TC.FusObj.i10.dxv": ("ECU", "fus.ObjData_TC.FusObj.i10.dxv"),
                 "fus.ObjData_TC.FusObj.i11.dxv": ("ECU", "fus.ObjData_TC.FusObj.i11.dxv"),
                 "fus.ObjData_TC.FusObj.i12.dxv": ("ECU", "fus.ObjData_TC.FusObj.i12.dxv"),
                 "fus.ObjData_TC.FusObj.i13.dxv": ("ECU", "fus.ObjData_TC.FusObj.i13.dxv"),
                 "fus.ObjData_TC.FusObj.i14.dxv": ("ECU", "fus.ObjData_TC.FusObj.i14.dxv"),
                 "fus.ObjData_TC.FusObj.i15.dxv": ("ECU", "fus.ObjData_TC.FusObj.i15.dxv"),
                 "fus.ObjData_TC.FusObj.i16.dxv": ("ECU", "fus.ObjData_TC.FusObj.i16.dxv"),
                 "fus.ObjData_TC.FusObj.i17.dxv": ("ECU", "fus.ObjData_TC.FusObj.i17.dxv"),
                 "fus.ObjData_TC.FusObj.i18.dxv": ("ECU", "fus.ObjData_TC.FusObj.i18.dxv"),
                 "fus.ObjData_TC.FusObj.i19.dxv": ("ECU", "fus.ObjData_TC.FusObj.i19.dxv"),
                 "fus.ObjData_TC.FusObj.i2.dxv": ("ECU", "fus.ObjData_TC.FusObj.i2.dxv"),
                 "fus.ObjData_TC.FusObj.i20.dxv": ("ECU", "fus.ObjData_TC.FusObj.i20.dxv"),
                 "fus.ObjData_TC.FusObj.i21.dxv": ("ECU", "fus.ObjData_TC.FusObj.i21.dxv"),
                 "fus.ObjData_TC.FusObj.i22.dxv": ("ECU", "fus.ObjData_TC.FusObj.i22.dxv"),
                 "fus.ObjData_TC.FusObj.i23.dxv": ("ECU", "fus.ObjData_TC.FusObj.i23.dxv"),
                 "fus.ObjData_TC.FusObj.i24.dxv": ("ECU", "fus.ObjData_TC.FusObj.i24.dxv"),
                 "fus.ObjData_TC.FusObj.i25.dxv": ("ECU", "fus.ObjData_TC.FusObj.i25.dxv"),
                 "fus.ObjData_TC.FusObj.i26.dxv": ("ECU", "fus.ObjData_TC.FusObj.i26.dxv"),
                 "fus.ObjData_TC.FusObj.i27.dxv": ("ECU", "fus.ObjData_TC.FusObj.i27.dxv"),
                 "fus.ObjData_TC.FusObj.i28.dxv": ("ECU", "fus.ObjData_TC.FusObj.i28.dxv"),
                 "fus.ObjData_TC.FusObj.i29.dxv": ("ECU", "fus.ObjData_TC.FusObj.i29.dxv"),
                 "fus.ObjData_TC.FusObj.i3.dxv": ("ECU", "fus.ObjData_TC.FusObj.i3.dxv"),
                 "fus.ObjData_TC.FusObj.i30.dxv": ("ECU", "fus.ObjData_TC.FusObj.i30.dxv"),
                 "fus.ObjData_TC.FusObj.i31.dxv": ("ECU", "fus.ObjData_TC.FusObj.i31.dxv"),
                 "fus.ObjData_TC.FusObj.i32.dxv": ("ECU", "fus.ObjData_TC.FusObj.i32.dxv"),
                 "fus.ObjData_TC.FusObj.i4.dxv": ("ECU", "fus.ObjData_TC.FusObj.i4.dxv"),
                 "fus.ObjData_TC.FusObj.i5.dxv": ("ECU", "fus.ObjData_TC.FusObj.i5.dxv"),
                 "fus.ObjData_TC.FusObj.i6.dxv": ("ECU", "fus.ObjData_TC.FusObj.i6.dxv"),
                 "fus.ObjData_TC.FusObj.i7.dxv": ("ECU", "fus.ObjData_TC.FusObj.i7.dxv"),
                 "fus.ObjData_TC.FusObj.i8.dxv": ("ECU", "fus.ObjData_TC.FusObj.i8.dxv"),
                 "fus.ObjData_TC.FusObj.i9.dxv": ("ECU", "fus.ObjData_TC.FusObj.i9.dxv"),
                 "fus.ObjData_TC.FusObj.i0.dyv": ("ECU", "fus.ObjData_TC.FusObj.i0.dyv"),
                 "fus.ObjData_TC.FusObj.i1.dyv": ("ECU", "fus.ObjData_TC.FusObj.i1.dyv"),
                 "fus.ObjData_TC.FusObj.i10.dyv": ("ECU", "fus.ObjData_TC.FusObj.i10.dyv"),
                 "fus.ObjData_TC.FusObj.i11.dyv": ("ECU", "fus.ObjData_TC.FusObj.i11.dyv"),
                 "fus.ObjData_TC.FusObj.i12.dyv": ("ECU", "fus.ObjData_TC.FusObj.i12.dyv"),
                 "fus.ObjData_TC.FusObj.i13.dyv": ("ECU", "fus.ObjData_TC.FusObj.i13.dyv"),
                 "fus.ObjData_TC.FusObj.i14.dyv": ("ECU", "fus.ObjData_TC.FusObj.i14.dyv"),
                 "fus.ObjData_TC.FusObj.i15.dyv": ("ECU", "fus.ObjData_TC.FusObj.i15.dyv"),
                 "fus.ObjData_TC.FusObj.i16.dyv": ("ECU", "fus.ObjData_TC.FusObj.i16.dyv"),
                 "fus.ObjData_TC.FusObj.i17.dyv": ("ECU", "fus.ObjData_TC.FusObj.i17.dyv"),
                 "fus.ObjData_TC.FusObj.i18.dyv": ("ECU", "fus.ObjData_TC.FusObj.i18.dyv"),
                 "fus.ObjData_TC.FusObj.i19.dyv": ("ECU", "fus.ObjData_TC.FusObj.i19.dyv"),
                 "fus.ObjData_TC.FusObj.i2.dyv": ("ECU", "fus.ObjData_TC.FusObj.i2.dyv"),
                 "fus.ObjData_TC.FusObj.i20.dyv": ("ECU", "fus.ObjData_TC.FusObj.i20.dyv"),
                 "fus.ObjData_TC.FusObj.i21.dyv": ("ECU", "fus.ObjData_TC.FusObj.i21.dyv"),
                 "fus.ObjData_TC.FusObj.i22.dyv": ("ECU", "fus.ObjData_TC.FusObj.i22.dyv"),
                 "fus.ObjData_TC.FusObj.i23.dyv": ("ECU", "fus.ObjData_TC.FusObj.i23.dyv"),
                 "fus.ObjData_TC.FusObj.i24.dyv": ("ECU", "fus.ObjData_TC.FusObj.i24.dyv"),
                 "fus.ObjData_TC.FusObj.i25.dyv": ("ECU", "fus.ObjData_TC.FusObj.i25.dyv"),
                 "fus.ObjData_TC.FusObj.i26.dyv": ("ECU", "fus.ObjData_TC.FusObj.i26.dyv"),
                 "fus.ObjData_TC.FusObj.i27.dyv": ("ECU", "fus.ObjData_TC.FusObj.i27.dyv"),
                 "fus.ObjData_TC.FusObj.i28.dyv": ("ECU", "fus.ObjData_TC.FusObj.i28.dyv"),
                 "fus.ObjData_TC.FusObj.i29.dyv": ("ECU", "fus.ObjData_TC.FusObj.i29.dyv"),
                 "fus.ObjData_TC.FusObj.i3.dyv": ("ECU", "fus.ObjData_TC.FusObj.i3.dyv"),
                 "fus.ObjData_TC.FusObj.i30.dyv": ("ECU", "fus.ObjData_TC.FusObj.i30.dyv"),
                 "fus.ObjData_TC.FusObj.i31.dyv": ("ECU", "fus.ObjData_TC.FusObj.i31.dyv"),
                 "fus.ObjData_TC.FusObj.i32.dyv": ("ECU", "fus.ObjData_TC.FusObj.i32.dyv"),
                 "fus.ObjData_TC.FusObj.i4.dyv": ("ECU", "fus.ObjData_TC.FusObj.i4.dyv"),
                 "fus.ObjData_TC.FusObj.i5.dyv": ("ECU", "fus.ObjData_TC.FusObj.i5.dyv"),
                 "fus.ObjData_TC.FusObj.i6.dyv": ("ECU", "fus.ObjData_TC.FusObj.i6.dyv"),
                 "fus.ObjData_TC.FusObj.i7.dyv": ("ECU", "fus.ObjData_TC.FusObj.i7.dyv"),
                 "fus.ObjData_TC.FusObj.i8.dyv": ("ECU", "fus.ObjData_TC.FusObj.i8.dyv"),
                 "fus.ObjData_TC.FusObj.i9.dyv": ("ECU", "fus.ObjData_TC.FusObj.i9.dyv"),
                 "fus.ObjData_TC.FusObj.i0.vxv": ("ECU", "fus.ObjData_TC.FusObj.i0.vxv"),
                 "fus.ObjData_TC.FusObj.i1.vxv": ("ECU", "fus.ObjData_TC.FusObj.i1.vxv"),
                 "fus.ObjData_TC.FusObj.i10.vxv": ("ECU", "fus.ObjData_TC.FusObj.i10.vxv"),
                 "fus.ObjData_TC.FusObj.i11.vxv": ("ECU", "fus.ObjData_TC.FusObj.i11.vxv"),
                 "fus.ObjData_TC.FusObj.i12.vxv": ("ECU", "fus.ObjData_TC.FusObj.i12.vxv"),
                 "fus.ObjData_TC.FusObj.i13.vxv": ("ECU", "fus.ObjData_TC.FusObj.i13.vxv"),
                 "fus.ObjData_TC.FusObj.i14.vxv": ("ECU", "fus.ObjData_TC.FusObj.i14.vxv"),
                 "fus.ObjData_TC.FusObj.i15.vxv": ("ECU", "fus.ObjData_TC.FusObj.i15.vxv"),
                 "fus.ObjData_TC.FusObj.i16.vxv": ("ECU", "fus.ObjData_TC.FusObj.i16.vxv"),
                 "fus.ObjData_TC.FusObj.i17.vxv": ("ECU", "fus.ObjData_TC.FusObj.i17.vxv"),
                 "fus.ObjData_TC.FusObj.i18.vxv": ("ECU", "fus.ObjData_TC.FusObj.i18.vxv"),
                 "fus.ObjData_TC.FusObj.i19.vxv": ("ECU", "fus.ObjData_TC.FusObj.i19.vxv"),
                 "fus.ObjData_TC.FusObj.i2.vxv": ("ECU", "fus.ObjData_TC.FusObj.i2.vxv"),
                 "fus.ObjData_TC.FusObj.i20.vxv": ("ECU", "fus.ObjData_TC.FusObj.i20.vxv"),
                 "fus.ObjData_TC.FusObj.i21.vxv": ("ECU", "fus.ObjData_TC.FusObj.i21.vxv"),
                 "fus.ObjData_TC.FusObj.i22.vxv": ("ECU", "fus.ObjData_TC.FusObj.i22.vxv"),
                 "fus.ObjData_TC.FusObj.i23.vxv": ("ECU", "fus.ObjData_TC.FusObj.i23.vxv"),
                 "fus.ObjData_TC.FusObj.i24.vxv": ("ECU", "fus.ObjData_TC.FusObj.i24.vxv"),
                 "fus.ObjData_TC.FusObj.i25.vxv": ("ECU", "fus.ObjData_TC.FusObj.i25.vxv"),
                 "fus.ObjData_TC.FusObj.i26.vxv": ("ECU", "fus.ObjData_TC.FusObj.i26.vxv"),
                 "fus.ObjData_TC.FusObj.i27.vxv": ("ECU", "fus.ObjData_TC.FusObj.i27.vxv"),
                 "fus.ObjData_TC.FusObj.i28.vxv": ("ECU", "fus.ObjData_TC.FusObj.i28.vxv"),
                 "fus.ObjData_TC.FusObj.i29.vxv": ("ECU", "fus.ObjData_TC.FusObj.i29.vxv"),
                 "fus.ObjData_TC.FusObj.i3.vxv": ("ECU", "fus.ObjData_TC.FusObj.i3.vxv"),
                 "fus.ObjData_TC.FusObj.i30.vxv": ("ECU", "fus.ObjData_TC.FusObj.i30.vxv"),
                 "fus.ObjData_TC.FusObj.i31.vxv": ("ECU", "fus.ObjData_TC.FusObj.i31.vxv"),
                 "fus.ObjData_TC.FusObj.i32.vxv": ("ECU", "fus.ObjData_TC.FusObj.i32.vxv"),
                 "fus.ObjData_TC.FusObj.i4.vxv": ("ECU", "fus.ObjData_TC.FusObj.i4.vxv"),
                 "fus.ObjData_TC.FusObj.i5.vxv": ("ECU", "fus.ObjData_TC.FusObj.i5.vxv"),
                 "fus.ObjData_TC.FusObj.i6.vxv": ("ECU", "fus.ObjData_TC.FusObj.i6.vxv"),
                 "fus.ObjData_TC.FusObj.i7.vxv": ("ECU", "fus.ObjData_TC.FusObj.i7.vxv"),
                 "fus.ObjData_TC.FusObj.i8.vxv": ("ECU", "fus.ObjData_TC.FusObj.i8.vxv"),
                 "fus.ObjData_TC.FusObj.i9.vxv": ("ECU", "fus.ObjData_TC.FusObj.i9.vxv"),
                 "fus.ObjData_TC.FusObj.i0.axv": ("ECU", "fus.ObjData_TC.FusObj.i0.axv"),
                 "fus.ObjData_TC.FusObj.i1.axv": ("ECU", "fus.ObjData_TC.FusObj.i1.axv"),
                 "fus.ObjData_TC.FusObj.i10.axv": ("ECU", "fus.ObjData_TC.FusObj.i10.axv"),
                 "fus.ObjData_TC.FusObj.i11.axv": ("ECU", "fus.ObjData_TC.FusObj.i11.axv"),
                 "fus.ObjData_TC.FusObj.i12.axv": ("ECU", "fus.ObjData_TC.FusObj.i12.axv"),
                 "fus.ObjData_TC.FusObj.i13.axv": ("ECU", "fus.ObjData_TC.FusObj.i13.axv"),
                 "fus.ObjData_TC.FusObj.i14.axv": ("ECU", "fus.ObjData_TC.FusObj.i14.axv"),
                 "fus.ObjData_TC.FusObj.i15.axv": ("ECU", "fus.ObjData_TC.FusObj.i15.axv"),
                 "fus.ObjData_TC.FusObj.i16.axv": ("ECU", "fus.ObjData_TC.FusObj.i16.axv"),
                 "fus.ObjData_TC.FusObj.i17.axv": ("ECU", "fus.ObjData_TC.FusObj.i17.axv"),
                 "fus.ObjData_TC.FusObj.i18.axv": ("ECU", "fus.ObjData_TC.FusObj.i18.axv"),
                 "fus.ObjData_TC.FusObj.i19.axv": ("ECU", "fus.ObjData_TC.FusObj.i19.axv"),
                 "fus.ObjData_TC.FusObj.i2.axv": ("ECU", "fus.ObjData_TC.FusObj.i2.axv"),
                 "fus.ObjData_TC.FusObj.i20.axv": ("ECU", "fus.ObjData_TC.FusObj.i20.axv"),
                 "fus.ObjData_TC.FusObj.i21.axv": ("ECU", "fus.ObjData_TC.FusObj.i21.axv"),
                 "fus.ObjData_TC.FusObj.i22.axv": ("ECU", "fus.ObjData_TC.FusObj.i22.axv"),
                 "fus.ObjData_TC.FusObj.i23.axv": ("ECU", "fus.ObjData_TC.FusObj.i23.axv"),
                 "fus.ObjData_TC.FusObj.i24.axv": ("ECU", "fus.ObjData_TC.FusObj.i24.axv"),
                 "fus.ObjData_TC.FusObj.i25.axv": ("ECU", "fus.ObjData_TC.FusObj.i25.axv"),
                 "fus.ObjData_TC.FusObj.i26.axv": ("ECU", "fus.ObjData_TC.FusObj.i26.axv"),
                 "fus.ObjData_TC.FusObj.i27.axv": ("ECU", "fus.ObjData_TC.FusObj.i27.axv"),
                 "fus.ObjData_TC.FusObj.i28.axv": ("ECU", "fus.ObjData_TC.FusObj.i28.axv"),
                 "fus.ObjData_TC.FusObj.i29.axv": ("ECU", "fus.ObjData_TC.FusObj.i29.axv"),
                 "fus.ObjData_TC.FusObj.i3.axv": ("ECU", "fus.ObjData_TC.FusObj.i3.axv"),
                 "fus.ObjData_TC.FusObj.i30.axv": ("ECU", "fus.ObjData_TC.FusObj.i30.axv"),
                 "fus.ObjData_TC.FusObj.i31.axv": ("ECU", "fus.ObjData_TC.FusObj.i31.axv"),
                 "fus.ObjData_TC.FusObj.i32.axv": ("ECU", "fus.ObjData_TC.FusObj.i32.axv"),
                 "fus.ObjData_TC.FusObj.i4.axv": ("ECU", "fus.ObjData_TC.FusObj.i4.axv"),
                 "fus.ObjData_TC.FusObj.i5.axv": ("ECU", "fus.ObjData_TC.FusObj.i5.axv"),
                 "fus.ObjData_TC.FusObj.i6.axv": ("ECU", "fus.ObjData_TC.FusObj.i6.axv"),
                 "fus.ObjData_TC.FusObj.i7.axv": ("ECU", "fus.ObjData_TC.FusObj.i7.axv"),
                 "fus.ObjData_TC.FusObj.i8.axv": ("ECU", "fus.ObjData_TC.FusObj.i8.axv"),
                 "fus.ObjData_TC.FusObj.i9.axv": ("ECU", "fus.ObjData_TC.FusObj.i9.axv"),},]

class cView(interface.iView):
  def check(self):
    Group = interface.Source.selectSignalGroup(SignalGroups)
    return Group
    
  def fill(self, Group):
    return Group

  def view(cls, Param, Group):
    Client = datavis.cPlotNavigator(title="Overview LRR3 FUS objects", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i0.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i0.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i1.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i1.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i2.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i2.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i3.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i3.Handle", Time, Value, unit="", color="-")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i31.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i4.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i4.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i5.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i5.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i6.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i6.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i7.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i7.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i8.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i8.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i9.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i9.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i10.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i10.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i11.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i11.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i12.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i12.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i13.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i13.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i14.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i14.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i15.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i15.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i16.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i16.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i17.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i17.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i18.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i18.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i19.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i19.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i20.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i20.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i21.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i21.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i22.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i22.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i23.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i23.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i24.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i24.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i25.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i25.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i26.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i26.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i27.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i27.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i28.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i28.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i29.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i29.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i30.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i30.Handle", Time, Value, unit="", color="-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i31.Handle")
    Axis = Client.addAxis(ylim=(0, 200))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i0.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i0.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i1.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i1.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i2.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i2.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i3.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i3.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i4.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i4.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i5.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i5.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i6.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i6.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i7.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i7.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i8.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i8.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i9.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i9.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i10.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i10.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i11.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i11.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i12.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i12.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i13.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i13.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i14.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i14.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i15.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i15.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i16.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i16.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i17.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i17.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i18.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i18.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i19.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i19.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i20.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i20.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i21.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i21.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i22.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i22.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i23.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i23.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i24.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i24.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i25.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i25.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i26.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i26.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i27.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i27.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i28.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i28.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i29.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i29.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i30.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i30.dxv", Time, Value, unit="m", color=".")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i31.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i31.dxv", Time, Value, unit="m", color=".")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 00", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i0.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i0.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i0.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i0.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i0.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i0.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i0.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i0.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i0.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i0.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 01", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i1.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i1.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i1.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i1.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i1.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i1.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i1.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i1.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i1.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i1.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 02", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i2.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i2.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i2.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i2.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i2.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i2.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i2.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i2.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i2.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i2.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 03", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i3.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i3.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i3.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i3.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i3.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i3.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i3.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i3.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i3.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i3.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 04", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i4.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i4.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i4.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i4.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i4.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i4.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i4.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i4.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i4.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i4.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 05", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i5.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i5.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i5.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i5.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i5.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i5.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i5.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i5.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i5.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i5.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 06", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i6.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i6.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i6.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i6.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i6.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i6.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i6.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i6.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i6.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i6.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 07", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i7.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i7.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i7.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i7.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i7.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i7.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i7.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i7.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i7.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i7.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 08", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i8.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i8.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i8.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i8.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i8.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i8.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i8.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i8.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i8.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i8.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 09", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i9.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i9.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i9.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i9.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i9.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i9.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i9.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i9.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i9.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i9.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 10", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i10.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i10.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i10.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i10.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i10.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i10.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i10.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i10.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i10.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i10.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 11", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i11.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i11.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i11.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i11.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i11.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i11.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i11.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i11.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i11.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i11.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 12", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i12.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i12.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i12.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i12.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i12.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i12.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i12.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i12.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i12.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i12.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 13", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i13.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i13.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i13.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i13.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i13.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i13.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i13.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i13.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i13.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i13.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 14", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i14.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i14.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i14.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i14.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i14.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i14.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i14.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i14.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i14.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i14.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 15", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i15.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i15.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i15.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i15.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i15.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i15.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i15.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i15.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i15.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i15.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 16", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i16.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i16.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i16.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i16.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i16.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i16.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i16.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i16.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i16.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i16.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 17", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i17.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i17.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i17.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i17.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i17.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i17.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i17.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i17.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i17.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i17.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 18", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i18.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i18.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i18.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i18.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i18.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i18.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i18.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i18.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i18.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i18.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 19", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i19.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i19.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i19.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i19.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i19.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i19.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i19.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i19.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i19.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i19.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 20", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i20.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i20.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i20.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i20.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i20.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i20.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i20.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i20.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i20.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i20.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 21", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i21.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i21.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i21.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i21.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i21.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i21.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i21.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i21.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i21.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i21.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 22", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i22.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i22.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i22.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i22.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i22.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i22.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i22.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i22.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i22.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i22.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 23", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i23.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i23.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i23.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i23.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i23.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i23.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i23.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i23.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i23.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i23.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 24", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i24.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i24.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i24.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i24.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i24.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i24.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i24.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i24.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i24.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i24.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 25", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i25.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i25.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i25.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i25.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i25.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i25.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i25.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i25.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i25.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i25.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 26", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i26.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i26.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i26.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i26.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i26.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i26.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i26.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i26.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i26.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i26.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 27", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i27.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i27.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i27.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i27.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i27.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i27.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i27.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i27.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i27.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i27.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 28", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i28.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i28.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i28.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i28.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i28.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i28.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i28.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i28.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i28.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i28.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 29", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i29.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i29.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i29.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i29.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i29.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i29.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i29.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i29.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i29.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i29.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 30", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i30.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i30.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i30.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i30.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i30.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i30.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i30.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i30.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i30.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i30.axv", Time, Value, unit="m/s^2", color="-")
    Client = datavis.cPlotNavigator(title="LRR3 FUS 31", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(0, 50))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i31.Handle")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i31.Handle", Time, Value, unit="", color="-")
    Axis = Client.addAxis(ylim=(0, 150))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i31.dxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i31.dxv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-10, 10))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i31.dyv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i31.dyv", Time, Value, unit="m", color="-")
    Axis = Client.addAxis(ylim=(-15, 15))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i31.vxv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i31.vxv", Time, Value, unit="m/s", color="-")
    Axis = Client.addAxis(ylim=(-5, 5))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i31.axv")
    Client.addSignal2Axis(Axis, "fus.ObjData_TC.FusObj.i31.axv", Time, Value, unit="m/s^2", color="-")
    return

