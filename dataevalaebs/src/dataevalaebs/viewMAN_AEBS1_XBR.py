import datavis
import interface
import numpy as np
DefParam = interface.NullParam

SignalGroups = [{"frontAxleSpeed_BASIS": ("EBC2_VAR1", "frontAxleSpeed_BASIS"),
                 "vehicleSpeedFromRadar_BASIS": ("ACCrefInfo_BASE", "vehicleSpeedFromRadar_BASIS"),
                 "advancedEmgcyBrakingSysState_BASE": ("AEBS1_BASE", "advancedEmgcyBrakingSysState_BASE"),
                 "externalAccelerationDemand_BASIS": ("XBR_VAR4", "externalAccelerationDemand_BASIS"),
                 "XBRpriority_BASIS": ("XBR_VAR4", "XBRpriority_BASIS"),
                 "XBRcontrolMode_BASIS": ("XBR_VAR4", "XBRcontrolMode_BASIS"),},]

class cView(interface.iView):
  def check(self):
    Group = interface.Source.selectSignalGroup(SignalGroups)
    return Group
    
  def fill(self, Group):
    return Group

  def view(cls, Param, Group):
    Client = datavis.cPlotNavigator(title="PN", figureNr=None)
    interface.Sync.addClient(Client)
    
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "frontAxleSpeed_BASIS")
    Client.addSignal2Axis(Axis, "frontAxleSpeed_BASIS", Time, Value, unit="")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vehicleSpeedFromRadar_BASIS")
    Client.addSignal2Axis(Axis, "vehicleSpeedFromRadar_BASIS", Time, Value, unit="")


    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "advancedEmgcyBrakingSysState_BASE")
    Client.addSignal2Axis(Axis, "advancedEmgcyBrakingSysState_BASE", Time, Value, unit="")

    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "externalAccelerationDemand_BASIS")
    Client.addSignal2Axis(Axis, "externalAccelerationDemand_BASIS", Time, Value, unit="")

    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "XBRpriority_BASIS")
    Client.addSignal2Axis(Axis, "XBRpriority_BASIS", Time, Value, unit="")

    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "XBRcontrolMode_BASIS")
    Client.addSignal2Axis(Axis, "XBRcontrolMode_BASIS", Time, Value, unit="")
    return

