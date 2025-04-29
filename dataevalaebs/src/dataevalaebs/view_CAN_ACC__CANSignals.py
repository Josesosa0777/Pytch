import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"ACCDistanceAlertSignal": ("ACC1", "ACCDistanceAlertSignal"),
                 "ACCMode": ("ACC1", "ACCMode"),
                 "ACCSetDistanceMode": ("ACC1", "ACCSetDistanceMode"),
                 "ACCSetSpeed": ("ACC1", "ACCSetSpeed"),
                 "ACCSystemShutoff": ("ACC1", "ACCSystemShutoff"),
                 "ACCTargetDetected": ("ACC1", "ACCTargetDetected"),
                 "DistanceToFrowardVehicle": ("ACC1", "DistanceToFrowardVehicle"),
                 "ForwardCollisionWarning": ("ACC1", "ForwardCollisionWarning"),
                 "MANDummyBits": ("ACC1", "MANDummyBits"),
                 "MANDummyByte": ("ACC1", "MANDummyByte"),
                 "RoadCurvature": ("ACC1", "RoadCurvature"),
                 "SpeedOfForwardVehicle": ("ACC1", "SpeedOfForwardVehicle"),
                 "AmbientAirTemperature": ("AMB", "AmbientAirTemperature"),
                 "BrakeSwitch": ("CCVS", "BrakeSwitch"),
                 "CCAccelSwitch": ("CCVS", "CCAccelSwitch"),
                 "CCActive": ("CCVS", "CCActive"),
                 "CCCoastSwitch": ("CCVS", "CCCoastSwitch"),
                 "CCEnableSwitch": ("CCVS", "CCEnableSwitch"),
                 "CCPauseSwitch": ("CCVS", "CCPauseSwitch"),
                 "CCResumeSwitch": ("CCVS", "CCResumeSwitch"),
                 "ClutchSwitch": ("CCVS", "ClutchSwitch"),
                 "ParkingBrakeSwitch": ("CCVS", "ParkingBrakeSwitch"),
                 "WheelBasedVehicleSpeed": ("CCVS", "WheelBasedVehicleSpeed"),
                 "GrossCombinationVehicleWeight": ("CVW", "GrossCombinationVehicleWeight"),
                 "DFM_Cnt_green_button": ("DIRK", "DFM_Cnt_green_button"),
                 "DFM_Cnt_red_button": ("DIRK", "DFM_Cnt_red_button"),
                 "DFM_green_button": ("DIRK", "DFM_green_button"),
                 "DFM_red_button": ("DIRK", "DFM_red_button"),
                 "ABSActive": ("EBC1", "ABSActive"),
                 "ABSFullyOperational": ("EBC1", "ABSFullyOperational"),
                 "ABSOffroadSwitch": ("EBC1", "ABSOffroadSwitch"),
                 "ASRBrakeControllerActive": ("EBC1", "ASRBrakeControllerActive"),
                 "ASREngineControllerActive": ("EBC1", "ASREngineControllerActive"),
                 "BrakePedalPosition": ("EBC1", "BrakePedalPosition"),
                 "EBSBrakeSwitch": ("EBC1", "EBSBrakeSwitch"),
                 "SourceAddressOfControllingDeviceForBrakeControl": ("EBC1", "SourceAddressOfControllingDeviceForBrakeControl"),
                 "FrontAxleSpeed": ("EBC2", "FrontAxleSpeed"),
                 "RelativeSpeedFrontLeft": ("EBC2", "RelativeSpeedFrontLeft"),
                 "RelativeSpeedFrontRight": ("EBC2", "RelativeSpeedFrontRight"),
                 "RelativeSpeedRearLeft": ("EBC2", "RelativeSpeedRearLeft"),
                 "RelativeSpeedRearRight": ("EBC2", "RelativeSpeedRearRight"),
                 "BrakeTemperatureWarning": ("EBC5", "BrakeTemperatureWarning"),
                 "FoundationBrakeUse": ("EBC5", "FoundationBrakeUse"),
                 "XBRAccelerationLimit": ("EBC5", "XBRAccelerationLimit"),
                 "XBRActiveControlMode": ("EBC5", "XBRActiveControlMode"),
                 "XBRSystemState": ("EBC5", "XBRSystemState"),
                 "EngineReferenceTorque": ("EC1", "EngineReferenceTorque"),
                 "ActualEnginePercentTorque": ("EEC1", "ActualEnginePercentTorque"),
                 "DriversDemandPercentTorque": ("EEC1", "DriversDemandPercentTorque"),
                 "EngineSpeed": ("EEC1", "EngineSpeed"),
                 "AccelPedalLowIdleSwitch": ("EEC2", "AccelPedalLowIdleSwitch"),
                 "AccelPedalPosition": ("EEC2", "AccelPedalPosition"),
                 "NominalFrictionPercentTorque": ("EEC3", "NominalFrictionPercentTorque"),
                 "ActualRetarderPercentTorque": ("ERC1", "ActualRetarderPercentTorque"),
                 "DriversDemandRetarderPercentTorque": ("ERC1", "DriversDemandRetarderPercentTorque"),
                 "RetarderTorqueMode": ("ERC1", "RetarderTorqueMode"),
                 "SourceAddressOfControllingDeviceForRetarderControl": ("ERC1", "SourceAddressOfControllingDeviceForRetarderControl"),
                 "TransmissionShiftInProcess": ("ETC1", "TransmissionShiftInProcess"),
                 "CurrentGear": ("ETC2", "CurrentGear"),
                 "SelectedGear": ("ETC2", "SelectedGear"),
                 "TransmissionActualGearRatio": ("ETC2", "TransmissionActualGearRatio"),
                 "ReferenceRetarderTorque": ("RC", "ReferenceRetarderTorque"),
                 "RetarderType": ("RC", "RetarderType"),
                 "Day": ("TD", "Day"),
                 "Hour": ("TD", "Hour"),
                 "Minute": ("TD", "Minute"),
                 "Month": ("TD", "Month"),
                 "Second": ("TD", "Second"),
                 "Year": ("TD", "Year"),
                 "TSC1EngineOverrideControlMode": ("TSC1", "TSC1EngineOverrideControlMode"),
                 "TSC1EngineOverrideControlModePriority": ("TSC1", "TSC1EngineOverrideControlModePriority"),
                 "TSC1EngineRequestedSpeed": ("TSC1", "TSC1EngineRequestedSpeed"),
                 "TSC1EngineRequestedTorque": ("TSC1", "TSC1EngineRequestedTorque"),
                 "ROPBrakeActive": ("VDC1", "ROPBrakeActive"),
                 "ROPEngineActive": ("VDC1", "ROPEngineActive"),
                 "YCBrakeActive": ("VDC1", "YCBrakeActive"),
                 "YCEngineActive": ("VDC1", "YCEngineActive"),
                 "SteeringWheelAngle": ("VDC2", "SteeringWheelAngle"),
                 "YawRate": ("VDC2", "YawRate"),
                 "HighResolutionVehicleDistance": ("VDHR", "HighResolutionVehicleDistance"),
                 "ExtAccelerationDemand": ("XBR", "ExtAccelerationDemand"),
                 "XBRControlMode": ("XBR", "XBRControlMode"),
                 "XBREBIMode": ("XBR", "XBREBIMode"),
                 "XBRPriority": ("XBR", "XBRPriority"),
                 "XBRUrgency": ("XBR", "XBRUrgency"),},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except ValueError, error:
      print __file__
      print error.message
    else:
      Client = datavis.cPlotNavigator(title="ACC1", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ACCDistanceAlertSignal")
      Client.addSignal2Axis(Axis, "ACCDistanceAlertSignal", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ACCMode")
      Client.addSignal2Axis(Axis, "ACCMode", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ACCSetDistanceMode")
      Client.addSignal2Axis(Axis, "ACCSetDistanceMode", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ACCSetSpeed")
      Client.addSignal2Axis(Axis, "ACCSetSpeed", Time, Value, unit="km/h")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ACCSystemShutoff")
      Client.addSignal2Axis(Axis, "ACCSystemShutoff", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ACCTargetDetected")
      Client.addSignal2Axis(Axis, "ACCTargetDetected", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "DistanceToFrowardVehicle")
      Client.addSignal2Axis(Axis, "DistanceToFrowardVehicle", Time, Value, unit="m")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ForwardCollisionWarning")
      Client.addSignal2Axis(Axis, "ForwardCollisionWarning", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "RoadCurvature")
      Client.addSignal2Axis(Axis, "RoadCurvature", Time, Value, unit="1/km")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "SpeedOfForwardVehicle")
      Client.addSignal2Axis(Axis, "SpeedOfForwardVehicle", Time, Value, unit="km/h")
      Client = datavis.cPlotNavigator(title="AMB", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "AmbientAirTemperature")
      Client.addSignal2Axis(Axis, "AmbientAirTemperature", Time, Value, unit="C")
      Client = datavis.cPlotNavigator(title="CCVS1", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "BrakeSwitch")
      Client.addSignal2Axis(Axis, "BrakeSwitch", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ClutchSwitch")
      Client.addSignal2Axis(Axis, "ClutchSwitch", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ParkingBrakeSwitch")
      Client.addSignal2Axis(Axis, "ParkingBrakeSwitch", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "CCEnableSwitch")
      Client.addSignal2Axis(Axis, "CCEnableSwitch", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "CCActive")
      Client.addSignal2Axis(Axis, "CCActive", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "CCAccelSwitch")
      Client.addSignal2Axis(Axis, "CCAccelSwitch", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "CCCoastSwitch")
      Client.addSignal2Axis(Axis, "CCCoastSwitch", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "CCPauseSwitch")
      Client.addSignal2Axis(Axis, "CCPauseSwitch", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "CCResumeSwitch")
      Client.addSignal2Axis(Axis, "CCResumeSwitch", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "WheelBasedVehicleSpeed")
      Client.addSignal2Axis(Axis, "WheelBasedVehicleSpeed", Time, Value, unit="km/h")
      Client = datavis.cPlotNavigator(title="CVW", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "GrossCombinationVehicleWeight")
      Client.addSignal2Axis(Axis, "GrossCombinationVehicleWeight", Time, Value, unit="kg")
      Client = datavis.cPlotNavigator(title="DIRK", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "DFM_green_button")
      Client.addSignal2Axis(Axis, "DFM_green_button", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "DFM_red_button")
      Client.addSignal2Axis(Axis, "DFM_red_button", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "DFM_Cnt_green_button")
      Client.addSignal2Axis(Axis, "DFM_Cnt_green_button", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "DFM_Cnt_red_button")
      Client.addSignal2Axis(Axis, "DFM_Cnt_red_button", Time, Value, unit="")
      Client = datavis.cPlotNavigator(title="EBC1", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ABSFullyOperational")
      Client.addSignal2Axis(Axis, "ABSFullyOperational", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ABSOffroadSwitch")
      Client.addSignal2Axis(Axis, "ABSOffroadSwitch", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ABSActive")
      Client.addSignal2Axis(Axis, "ABSActive", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ASRBrakeControllerActive")
      Client.addSignal2Axis(Axis, "ASRBrakeControllerActive", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ASREngineControllerActive")
      Client.addSignal2Axis(Axis, "ASREngineControllerActive", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "EBSBrakeSwitch")
      Client.addSignal2Axis(Axis, "EBSBrakeSwitch", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "BrakePedalPosition")
      Client.addSignal2Axis(Axis, "BrakePedalPosition", Time, Value, unit="%")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "SourceAddressOfControllingDeviceForBrakeControl")
      Client.addSignal2Axis(Axis, "SourceAddressOfControllingDeviceForBrakeControl", Time, Value, unit="")
      Client = datavis.cPlotNavigator(title="EBC2", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "FrontAxleSpeed")
      Client.addSignal2Axis(Axis, "FrontAxleSpeed", Time, Value, unit="km/h")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "RelativeSpeedFrontLeft")
      Client.addSignal2Axis(Axis, "RelativeSpeedFrontLeft", Time, Value, unit="km/h")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "RelativeSpeedFrontRight")
      Client.addSignal2Axis(Axis, "RelativeSpeedFrontRight", Time, Value, unit="km/h")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "RelativeSpeedRearLeft")
      Client.addSignal2Axis(Axis, "RelativeSpeedRearLeft", Time, Value, unit="km/h")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "RelativeSpeedRearRight")
      Client.addSignal2Axis(Axis, "RelativeSpeedRearRight", Time, Value, unit="km/h")
      Client = datavis.cPlotNavigator(title="EBC5", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "BrakeTemperatureWarning")
      Client.addSignal2Axis(Axis, "BrakeTemperatureWarning", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "FoundationBrakeUse")
      Client.addSignal2Axis(Axis, "FoundationBrakeUse", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "XBRActiveControlMode")
      Client.addSignal2Axis(Axis, "XBRActiveControlMode", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "XBRSystemState")
      Client.addSignal2Axis(Axis, "XBRSystemState", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "XBRAccelerationLimit")
      Client.addSignal2Axis(Axis, "XBRAccelerationLimit", Time, Value, unit="m/s^2")
      Axis = Client.addAxis()
      Client = datavis.cPlotNavigator(title="EC1", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "EngineReferenceTorque")
      Client.addSignal2Axis(Axis, "EngineReferenceTorque", Time, Value, unit="Nm")
      Client = datavis.cPlotNavigator(title="EEC1", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ActualEnginePercentTorque")
      Client.addSignal2Axis(Axis, "ActualEnginePercentTorque", Time, Value, unit="%")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "DriversDemandPercentTorque")
      Client.addSignal2Axis(Axis, "DriversDemandPercentTorque", Time, Value, unit="%")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "EngineSpeed")
      Client.addSignal2Axis(Axis, "EngineSpeed", Time, Value, unit="1/min")
      Client = datavis.cPlotNavigator(title="EEC2", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "AccelPedalLowIdleSwitch")
      Client.addSignal2Axis(Axis, "AccelPedalLowIdleSwitch", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "AccelPedalPosition")
      Client.addSignal2Axis(Axis, "AccelPedalPosition", Time, Value, unit="%")
      Client = datavis.cPlotNavigator(title="EEC3", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "NominalFrictionPercentTorque")
      Client.addSignal2Axis(Axis, "NominalFrictionPercentTorque", Time, Value, unit="%")
      Client = datavis.cPlotNavigator(title="ERC1", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ActualRetarderPercentTorque")
      Client.addSignal2Axis(Axis, "ActualRetarderPercentTorque", Time, Value, unit="%")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "DriversDemandRetarderPercentTorque")
      Client.addSignal2Axis(Axis, "DriversDemandRetarderPercentTorque", Time, Value, unit="%")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "RetarderTorqueMode")
      Client.addSignal2Axis(Axis, "RetarderTorqueMode", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "SourceAddressOfControllingDeviceForRetarderControl")
      Client.addSignal2Axis(Axis, "SourceAddressOfControllingDeviceForRetarderControl", Time, Value, unit="")
      Client = datavis.cPlotNavigator(title="ETC1", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "TransmissionShiftInProcess")
      Client.addSignal2Axis(Axis, "TransmissionShiftInProcess", Time, Value, unit="")
      Client = datavis.cPlotNavigator(title="ETC2", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "CurrentGear")
      Client.addSignal2Axis(Axis, "CurrentGear", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "SelectedGear")
      Client.addSignal2Axis(Axis, "SelectedGear", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "TransmissionActualGearRatio")
      Client.addSignal2Axis(Axis, "TransmissionActualGearRatio", Time, Value, unit="")
      Client = datavis.cPlotNavigator(title="RC", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "RetarderType")
      Client.addSignal2Axis(Axis, "RetarderType", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ReferenceRetarderTorque")
      Client.addSignal2Axis(Axis, "ReferenceRetarderTorque", Time, Value, unit="Nm")
      Client = datavis.cPlotNavigator(title="TD", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Year")
      Client.addSignal2Axis(Axis, "Year", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Month")
      Client.addSignal2Axis(Axis, "Month", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Day")
      Client.addSignal2Axis(Axis, "Day", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Hour")
      Client.addSignal2Axis(Axis, "Hour", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Minute")
      Client.addSignal2Axis(Axis, "Minute", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Second")
      Client.addSignal2Axis(Axis, "Second", Time, Value, unit="")
      Client = datavis.cPlotNavigator(title="TSC1", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "TSC1EngineOverrideControlMode")
      Client.addSignal2Axis(Axis, "TSC1EngineOverrideControlMode", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "TSC1EngineOverrideControlModePriority")
      Client.addSignal2Axis(Axis, "TSC1EngineOverrideControlModePriority", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "TSC1EngineRequestedSpeed")
      Client.addSignal2Axis(Axis, "TSC1EngineRequestedSpeed", Time, Value, unit="1/min")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "TSC1EngineRequestedTorque")
      Client.addSignal2Axis(Axis, "TSC1EngineRequestedTorque", Time, Value, unit="%")
      Client = datavis.cPlotNavigator(title="VDC1", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ROPBrakeActive")
      Client.addSignal2Axis(Axis, "ROPBrakeActive", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ROPEngineActive")
      Client.addSignal2Axis(Axis, "ROPEngineActive", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "YCBrakeActive")
      Client.addSignal2Axis(Axis, "YCBrakeActive", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "YCEngineActive")
      Client.addSignal2Axis(Axis, "YCEngineActive", Time, Value, unit="")
      Client = datavis.cPlotNavigator(title="VDC2", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "SteeringWheelAngle")
      Client.addSignal2Axis(Axis, "SteeringWheelAngle", Time, Value, unit="rad")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "YawRate")
      Client.addSignal2Axis(Axis, "YawRate", Time, Value, unit="rad/s")
      Client = datavis.cPlotNavigator(title="VDHR", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "HighResolutionVehicleDistance")
      Client.addSignal2Axis(Axis, "HighResolutionVehicleDistance", Time, Value, unit="km")
      Client = datavis.cPlotNavigator(title="XBR", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ExtAccelerationDemand")
      Client.addSignal2Axis(Axis, "ExtAccelerationDemand", Time, Value, unit="m/s^2")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "XBRControlMode")
      Client.addSignal2Axis(Axis, "XBRControlMode", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "XBREBIMode")
      Client.addSignal2Axis(Axis, "XBREBIMode", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "XBRPriority")
      Client.addSignal2Axis(Axis, "XBRPriority", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "XBRUrgency")
      Client.addSignal2Axis(Axis, "XBRUrgency", Time, Value, unit="%")
      pass
    pass


