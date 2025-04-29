import datavis
import interface
import numpy as np

DefParam = interface.NullParam

SignalGroups = [{"roadCurvatureACCsens_BASIS": ("ACCrefInfo_BASE", "roadCurvatureACCsens_BASIS"),
                 "ACCstatusDistSens_BASE": ("ACCrefInfo_BASE", "ACCstatusDistSens_BASE"),
                 "yawRate_BASIS": ("VDC2_BASIS", "yawRate_BASIS"),
                 "Distance2Vehicle1_BASIS": ("ACCvehicle1_BASIS", "Distance2Vehicle1_BASIS"),
                 "azimuthVeh1ACC_BASE": ("ACCvehicle1_BASIS", "azimuthVeh1ACC_BASE"),
                 "relSpeedOfVehicle1_BASIS": ("ACCvehicle1_BASIS", "relSpeedOfVehicle1_BASIS"),
                 "vehicleAccel1_BASIS": ("ACCvehicle1_BASIS", "vehicleAccel1_BASIS"),
                 "frontAxleSpeed_BASIS": ("EBC2_VAR1", "frontAxleSpeed_BASIS"),
                 "vehicleSpeedFromRadar_BASIS": ("ACCrefInfo_BASE", "vehicleSpeedFromRadar_BASIS"),},]

class cView(interface.iView):
  def check(self):
    Group = interface.Source.selectSignalGroup(SignalGroups)
    return Group
    
  def fill(self, Group):
    return Group

  def view(cls, Param, Group):
    Client = datavis.cPlotNavigator(title="PN", figureNr=None)
    interface.Sync.addClient(Client)

    # ego vehicle speed
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "frontAxleSpeed_BASIS")
    Client.addSignal2Axis(Axis, "frontAxleSpeed_BASIS", Time, Value, unit="kph")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vehicleSpeedFromRadar_BASIS")
    Client.addSignal2Axis(Axis, "vehicleSpeedFromRadar_BASIS", Time, Value, unit="kph")

    # yaw rate
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "yawRate_BASIS")
    Client.addSignal2Axis(Axis, "yawRate_BASIS", Time, Value, unit="")
    
    # curvature 
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "roadCurvatureACCsens_BASIS")
    Client.addSignal2Axis(Axis, "roadCurvatureACCsens_BASIS", Time, Value, unit="")
    
    #Axis = Client.addAxis()
    #Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ACCstatusDistSens_BASE")
    #Client.addSignal2Axis(Axis, "ACCstatusDistSens_BASE", Time, Value, unit="")
    
    
    # ACC Vehicle 1 Object

    # dx     
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Distance2Vehicle1_BASIS")
    Value = np.copy(Value)
    mask = Value > 6000.0
    Value[mask]     = np.zeros_like(Value)[mask]
    Client.addSignal2Axis(Axis, "Distance2Vehicle1_BASIS", Time, Value, unit="")
    
    # vRel
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "relSpeedOfVehicle1_BASIS")
    Value = np.copy(Value)
    mask = np.logical_or(Value < -3200.5,Value > 6200.5)
    Value[mask]     = np.zeros_like(Value)[mask]
    Client.addSignal2Axis(Axis, "relSpeedOfVehicle1_BASIS", Time, Value, unit="")
    
    # ax
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vehicleAccel1_BASIS")
    Value = np.copy(Value)
    mask = np.logical_or(Value < -12.5, Value > 12.5)
    Value[mask]     = np.zeros_like(Value)[mask]
    Client.addSignal2Axis(Axis, "vehicleAccel1_BASIS", Time, Value, unit="")

    # azimuth
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "azimuthVeh1ACC_BASE")
    Value = np.copy(Value)
    mask = np.logical_or(Value < -12.5, Value > 12.5)
    Value[mask]     = np.zeros_like(Value)[mask]
    Client.addSignal2Axis(Axis, "azimuthVeh1ACC_BASE", Time, Value, unit="")
   
    return


