import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1121Sa0x0B_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1121Sa0x0B_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1243Sa0x0B_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1243Sa0x0B_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1480Sa0xFE": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1480Sa0xFE"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1480Sa0xFE2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1480Sa0xFE2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1480Sa0xFE3": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1480Sa0xFE3"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1481Sa0x0B": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1481Sa0x0B"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1715Sa0xFE": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1715Sa0xFE"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1715Sa0xFE2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1715Sa0xFE2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1715Sa0xFE3": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1715Sa0xFE3"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn171Sa0xFF": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn171Sa0xFF"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1760Sa0x0B": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1760Sa0x0B"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1807Sa0xFF": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1807Sa0xFF"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1808Sa0xFF": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1808Sa0xFF"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1816Sa0xFF_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1816Sa0xFF_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1817Sa0xFF_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1817Sa0xFF_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1818Sa0xFF_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1818Sa0xFF_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1819Sa0xFF_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1819Sa0xFF_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn190Sa0x00": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn190Sa0x00"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn2917Sa0x0B_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn2917Sa0x0B_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn2918Sa0x0B_B4": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn2918Sa0x0B_B4"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn2919Sa0x0B_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn2919Sa0x0B_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn2921Sa0x0B": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn2921Sa0x0B"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn3839Sa0x0B_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn3839Sa0x0B_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn43500Sa0xE8_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn43500Sa0xE8_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn43501Sa0xE8_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn43501Sa0xE8_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn43502Sa0xE8_B4": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn43502Sa0xE8_B4"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn45001Sa0x21_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn45001Sa0x21_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn45002Sa0x21_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn45002Sa0x21_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn51000Sa0xFF_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn51000Sa0xFF_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn512Sa0x00": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn512Sa0x00"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn513Sa0x00": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn513Sa0x00"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn514Sa0x00": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn514Sa0x00"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn520Sa0xFE": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn520Sa0xFE"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn520Sa0xFE2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn520Sa0xFE2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn520Sa0xFE3": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn520Sa0xFE3"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn521Sa0x0B": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn521Sa0x0B"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn523Sa0x03": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn523Sa0x03"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn524Sa0x03": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn524Sa0x03"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn526Sa0x03": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn526Sa0x03"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn544Sa0x00": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn544Sa0x00"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn556Sa0xFF": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn556Sa0xFF"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn556Sa0xFF2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn556Sa0xFF2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn556Sa0xFF3": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn556Sa0xFF3"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn558Sa0xFF_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn558Sa0xFF_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn561Sa0x0B_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn561Sa0x0B_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn562Sa0x0B_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn562Sa0x0B_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn563Sa0x0B_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn563Sa0x0B_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn574Sa0x03_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn574Sa0x03_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn575Sa0x0B_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn575Sa0x0B_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn595Sa0xFF_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn595Sa0xFF_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn596Sa0xFF_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn596Sa0xFF_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn597Sa0xFF_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn597Sa0xFF_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn598Sa0xFF_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn598Sa0xFF_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn600Sa0xFF_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn600Sa0xFF_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn601Sa0xFF_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn601Sa0xFF_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn602Sa0xFF_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn602Sa0xFF_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn70Sa0xFF_B2": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn70Sa0xFF_B2"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn84Sa0xFF": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn84Sa0xFF"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn900Sa0xFE2_B4": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn900Sa0xFE2_B4"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn900Sa0xFE3_B4": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn900Sa0xFE3_B4"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn900Sa0xFE_B4": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn900Sa0xFE_B4"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn901Sa0xFF2_B4": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn901Sa0xFF2_B4"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn901Sa0xFF3_B4": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn901Sa0xFF3_B4"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn901Sa0xFF_B4": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn901Sa0xFF_B4"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn904Sa0x0B": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn904Sa0x0B"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn905Sa0x0B": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn905Sa0x0B"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn906Sa0x0B": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn906Sa0x0B"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn907Sa0x0B": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn907Sa0x0B"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn908Sa0x0B": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn908Sa0x0B"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn917Sa0xFF": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn917Sa0xFF"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn91Sa0xFF": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn91Sa0xFF"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn959Sa0xFF": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn959Sa0xFF"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn960Sa0xFF": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn960Sa0xFF"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn961Sa0xFF": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn961Sa0xFF"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn962Sa0xFF": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn962Sa0xFF"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn963Sa0xFF": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn963Sa0xFF"),
                 "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn964Sa0xFF": ("ECU", "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn964Sa0xFF"),},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except ValueError, error:
      print __file__
      print error.message
    else:
      Client = datavis.cPlotNavigator(title="PN", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1121Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1121Sa0x0B_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1243Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1243Sa0x0B_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1480Sa0xFE")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1480Sa0xFE", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1480Sa0xFE2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1480Sa0xFE2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1480Sa0xFE3")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1480Sa0xFE3", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1481Sa0x0B")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1481Sa0x0B", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1715Sa0xFE")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1715Sa0xFE", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1715Sa0xFE2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1715Sa0xFE2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1715Sa0xFE3")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1715Sa0xFE3", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn171Sa0xFF")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn171Sa0xFF", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1760Sa0x0B")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1760Sa0x0B", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1807Sa0xFF")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1807Sa0xFF", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1808Sa0xFF")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1808Sa0xFF", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1816Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1816Sa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1817Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1817Sa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1818Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1818Sa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1819Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn1819Sa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn190Sa0x00")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn190Sa0x00", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn2917Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn2917Sa0x0B_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn2918Sa0x0B_B4")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn2918Sa0x0B_B4", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn2919Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn2919Sa0x0B_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn2921Sa0x0B")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn2921Sa0x0B", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn3839Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn3839Sa0x0B_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn43500Sa0xE8_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn43500Sa0xE8_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn43501Sa0xE8_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn43501Sa0xE8_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn43502Sa0xE8_B4")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn43502Sa0xE8_B4", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn45001Sa0x21_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn45001Sa0x21_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn45002Sa0x21_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn45002Sa0x21_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn51000Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn51000Sa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn512Sa0x00")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn512Sa0x00", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn513Sa0x00")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn513Sa0x00", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn514Sa0x00")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn514Sa0x00", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn520Sa0xFE")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn520Sa0xFE", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn520Sa0xFE2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn520Sa0xFE2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn520Sa0xFE3")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn520Sa0xFE3", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn521Sa0x0B")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn521Sa0x0B", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn523Sa0x03")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn523Sa0x03", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn524Sa0x03")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn524Sa0x03", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn526Sa0x03")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn526Sa0x03", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn544Sa0x00")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn544Sa0x00", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn556Sa0xFF")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn556Sa0xFF", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn556Sa0xFF2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn556Sa0xFF2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn556Sa0xFF3")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn556Sa0xFF3", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn558Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn558Sa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn561Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn561Sa0x0B_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn562Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn562Sa0x0B_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn563Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn563Sa0x0B_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn574Sa0x03_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn574Sa0x03_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn575Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn575Sa0x0B_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn595Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn595Sa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn596Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn596Sa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn597Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn597Sa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn598Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn598Sa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn600Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn600Sa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn601Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn601Sa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn602Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn602Sa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn70Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn70Sa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn84Sa0xFF")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn84Sa0xFF", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn900Sa0xFE2_B4")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn900Sa0xFE2_B4", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn900Sa0xFE3_B4")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn900Sa0xFE3_B4", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn900Sa0xFE_B4")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn900Sa0xFE_B4", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn901Sa0xFF2_B4")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn901Sa0xFF2_B4", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn901Sa0xFF3_B4")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn901Sa0xFF3_B4", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn901Sa0xFF_B4")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn901Sa0xFF_B4", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn904Sa0x0B")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn904Sa0x0B", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn905Sa0x0B")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn905Sa0x0B", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn906Sa0x0B")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn906Sa0x0B", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn907Sa0x0B")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn907Sa0x0B", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn908Sa0x0B")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn908Sa0x0B", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn917Sa0xFF")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn917Sa0xFF", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn91Sa0xFF")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn91Sa0xFF", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn959Sa0xFF")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn959Sa0xFF", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn960Sa0xFF")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn960Sa0xFF", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn961Sa0xFF")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn961Sa0xFF", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn962Sa0xFF")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn962Sa0xFF", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn963Sa0xFF")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn963Sa0xFF", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn964Sa0xFF")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.CanRxRawData.RawValues.Spn964Sa0xFF", Time, Value, unit="")
      pass
    pass


