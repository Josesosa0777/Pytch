import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"cis_x_can_signals.ABSOffroadSwitchEBC1Sa0x0B_B2": ("ECU", "cis_x_can_signals.ABSOffroadSwitchEBC1Sa0x0B_B2"),
                 "cis_x_can_signals.ABSactiveEBC1Sa0x0B_B2": ("ECU", "cis_x_can_signals.ABSactiveEBC1Sa0x0B_B2"),
                 "cis_x_can_signals.ASRBrkCtrlActEBC1Sa0x0B_B2": ("ECU", "cis_x_can_signals.ASRBrkCtrlActEBC1Sa0x0B_B2"),
                 "cis_x_can_signals.ASREngCtrlActEBC1Sa0x0B_B2": ("ECU", "cis_x_can_signals.ASREngCtrlActEBC1Sa0x0B_B2"),
                 "cis_x_can_signals.AbsFullyOperationalEBC1Sa0x0B_B": ("ECU", "cis_x_can_signals.AbsFullyOperationalEBC1Sa0x0B_B"),
                 "cis_x_can_signals.AccelPed1LoIdleSwitchEEC2Sa0xFF": ("ECU", "cis_x_can_signals.AccelPed1LoIdleSwitchEEC2Sa0xFF"),
                 "cis_x_can_signals.AccelPedalPos1EEC2Sa0xFF": ("ECU", "cis_x_can_signals.AccelPedalPos1EEC2Sa0xFF"),
                 "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE": ("ECU", "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE"),
                 "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE2": ("ECU", "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE2"),
                 "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE3": ("ECU", "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE3"),
                 "cis_x_can_signals.ActualEnginePercentTorqueEEC1Sa": ("ECU", "cis_x_can_signals.ActualEnginePercentTorqueEEC1Sa"),
                 "cis_x_can_signals.AmbientAirTempAMBSa0xFF": ("ECU", "cis_x_can_signals.AmbientAirTempAMBSa0xFF"),
                 "cis_x_can_signals.BrakePedalPositionEBC1Sa0x0B": ("ECU", "cis_x_can_signals.BrakePedalPositionEBC1Sa0x0B"),
                 "cis_x_can_signals.BrkSwitchCCVSSa0xFF_B2": ("ECU", "cis_x_can_signals.BrkSwitchCCVSSa0xFF_B2"),
                 "cis_x_can_signals.BrkTempWarnEBC5Sa0x0B_B2": ("ECU", "cis_x_can_signals.BrkTempWarnEBC5Sa0x0B_B2"),
                 "cis_x_can_signals.CCAccelSwitchCCVSSa0xFF_B2": ("ECU", "cis_x_can_signals.CCAccelSwitchCCVSSa0xFF_B2"),
                 "cis_x_can_signals.CCCoastSwitchCCVSSa0xFF_B2": ("ECU", "cis_x_can_signals.CCCoastSwitchCCVSSa0xFF_B2"),
                 "cis_x_can_signals.CCEnableSwitchCCVSSa0xFF_B2": ("ECU", "cis_x_can_signals.CCEnableSwitchCCVSSa0xFF_B2"),
                 "cis_x_can_signals.CCPauseSwitchCCVSSa0xFF_B2": ("ECU", "cis_x_can_signals.CCPauseSwitchCCVSSa0xFF_B2"),
                 "cis_x_can_signals.CCResumeSwitchCCVSSa0xFF_B2": ("ECU", "cis_x_can_signals.CCResumeSwitchCCVSSa0xFF_B2"),
                 "cis_x_can_signals.ClutchSwitchCCVSSa0xFF_B2": ("ECU", "cis_x_can_signals.ClutchSwitchCCVSSa0xFF_B2"),
                 "cis_x_can_signals.CurrentGearETC2Sa0x03": ("ECU", "cis_x_can_signals.CurrentGearETC2Sa0x03"),
                 "cis_x_can_signals.DayTDSa0xFF": ("ECU", "cis_x_can_signals.DayTDSa0xFF"),
                 "cis_x_can_signals.DirIndLPROPAUXSTZBR3Sa0x21_B2": ("ECU", "cis_x_can_signals.DirIndLPROPAUXSTZBR3Sa0x21_B2"),
                 "cis_x_can_signals.DirIndRPROPAUXSTZBR3Sa0x21_B2": ("ECU", "cis_x_can_signals.DirIndRPROPAUXSTZBR3Sa0x21_B2"),
                 "cis_x_can_signals.DriversDemandEnginePercentTrqEE": ("ECU", "cis_x_can_signals.DriversDemandEnginePercentTrqEE"),
                 "cis_x_can_signals.DrvrsDemRetPercTrqERC1Sa0xFE": ("ECU", "cis_x_can_signals.DrvrsDemRetPercTrqERC1Sa0xFE"),
                 "cis_x_can_signals.DrvrsDemRetPercTrqERC1Sa0xFE2": ("ECU", "cis_x_can_signals.DrvrsDemRetPercTrqERC1Sa0xFE2"),
                 "cis_x_can_signals.DrvrsDemRetPercTrqERC1Sa0xFE3": ("ECU", "cis_x_can_signals.DrvrsDemRetPercTrqERC1Sa0xFE3"),
                 "cis_x_can_signals.EBSBrkSwitchEBC1Sa0x0B_B2": ("ECU", "cis_x_can_signals.EBSBrkSwitchEBC1Sa0x0B_B2"),
                 "cis_x_can_signals.FoundationBrakeUseEBC5Sa0x0B_B2": ("ECU", "cis_x_can_signals.FoundationBrakeUseEBC5Sa0x0B_B2"),
                 "cis_x_can_signals.HighResTotalVehDisVDHRSa0xFF": ("ECU", "cis_x_can_signals.HighResTotalVehDisVDHRSa0xFF"),
                 "cis_x_can_signals.HourTDSa0xFF": ("ECU", "cis_x_can_signals.HourTDSa0xFF"),
                 "cis_x_can_signals.MinuteTDSa0xFF": ("ECU", "cis_x_can_signals.MinuteTDSa0xFF"),
                 "cis_x_can_signals.MonthTDSa0xFF": ("ECU", "cis_x_can_signals.MonthTDSa0xFF"),
                 "cis_x_can_signals.NominalFrictionPercentTorqueEEC": ("ECU", "cis_x_can_signals.NominalFrictionPercentTorqueEEC"),
                 "cis_x_can_signals.ParkingBrkSwitchCCVSSa0xFF_B2": ("ECU", "cis_x_can_signals.ParkingBrkSwitchCCVSSa0xFF_B2"),
                 "cis_x_can_signals.ROPBrkActVDC1Sa0xFF_B2": ("ECU", "cis_x_can_signals.ROPBrkActVDC1Sa0xFF_B2"),
                 "cis_x_can_signals.ROPEngActVDC1Sa0xFF_B2": ("ECU", "cis_x_can_signals.ROPEngActVDC1Sa0xFF_B2"),
                 "cis_x_can_signals.RetTrqModeERC1Sa0xFE2_B4": ("ECU", "cis_x_can_signals.RetTrqModeERC1Sa0xFE2_B4"),
                 "cis_x_can_signals.RetTrqModeERC1Sa0xFE3_B4": ("ECU", "cis_x_can_signals.RetTrqModeERC1Sa0xFE3_B4"),
                 "cis_x_can_signals.RetTrqModeERC1Sa0xFE_B4": ("ECU", "cis_x_can_signals.RetTrqModeERC1Sa0xFE_B4"),
                 "cis_x_can_signals.RetTypeRCSa0xFF2_B4": ("ECU", "cis_x_can_signals.RetTypeRCSa0xFF2_B4"),
                 "cis_x_can_signals.RetTypeRCSa0xFF3_B4": ("ECU", "cis_x_can_signals.RetTypeRCSa0xFF3_B4"),
                 "cis_x_can_signals.RetTypeRCSa0xFF_B4": ("ECU", "cis_x_can_signals.RetTypeRCSa0xFF_B4"),
                 "cis_x_can_signals.SAofCtrlDeviceForBrakeCtrlEBC1S": ("ECU", "cis_x_can_signals.SAofCtrlDeviceForBrakeCtrlEBC1S"),
                 "cis_x_can_signals.SAofCtrlDeviceForRetarderCtrlER": ("ECU", "cis_x_can_signals.SAofCtrlDeviceForRetarderCtrlER"),
                 "cis_x_can_signals.SAofCtrlDeviceForRetarderCtrlER_s0": ("ECU", "cis_x_can_signals.SAofCtrlDeviceForRetarderCtrlER_s0"),
                 "cis_x_can_signals.SAofCtrlDeviceForRetarderCtrlER_s1": ("ECU", "cis_x_can_signals.SAofCtrlDeviceForRetarderCtrlER_s1"),
                 "cis_x_can_signals.SecondTDSa0xFF": ("ECU", "cis_x_can_signals.SecondTDSa0xFF"),
                 "cis_x_can_signals.SelectedGearETC2Sa0x03": ("ECU", "cis_x_can_signals.SelectedGearETC2Sa0x03"),
                 "cis_x_can_signals.TMShiftInProcessETC1Sa0x03_B2": ("ECU", "cis_x_can_signals.TMShiftInProcessETC1Sa0x03_B2"),
                 "cis_x_can_signals.VehCcActiveCCVSSa0xFF_B2": ("ECU", "cis_x_can_signals.VehCcActiveCCVSSa0xFF_B2"),
                 "cis_x_can_signals.XbrActCtrlModeEBC5Sa0x0B_B4": ("ECU", "cis_x_can_signals.XbrActCtrlModeEBC5Sa0x0B_B4"),
                 "cis_x_can_signals.XbrSysStateEBC5Sa0x0B_B2": ("ECU", "cis_x_can_signals.XbrSysStateEBC5Sa0x0B_B2"),
                 "cis_x_can_signals.YCBrkActVDC1Sa0xFF_B2": ("ECU", "cis_x_can_signals.YCBrkActVDC1Sa0xFF_B2"),
                 "cis_x_can_signals.YCEngActVDC1Sa0xFF_B2": ("ECU", "cis_x_can_signals.YCEngActVDC1Sa0xFF_B2"),
                 "cis_x_can_signals.YearTDSa0xFF": ("ECU", "cis_x_can_signals.YearTDSa0xFF"),
                 "cis_x_can_signals.aLimitXbrEBC5Sa0x0B": ("ECU", "cis_x_can_signals.aLimitXbrEBC5Sa0x0B"),
                 "cis_x_can_signals.alpSteeringWheelVDC2Sa0xFF": ("ECU", "cis_x_can_signals.alpSteeringWheelVDC2Sa0xFF"),
                 "cis_x_can_signals.iActGearETC2Sa0x03": ("ECU", "cis_x_can_signals.iActGearETC2Sa0x03"),
                 "cis_x_can_signals.mGrossCombCVWSa0x0B": ("ECU", "cis_x_can_signals.mGrossCombCVWSa0x0B"),
                 "cis_x_can_signals.nMotEEC1Sa0x00": ("ECU", "cis_x_can_signals.nMotEEC1Sa0x00"),
                 "cis_x_can_signals.psiDtVDC2Sa0xFF": ("ECU", "cis_x_can_signals.psiDtVDC2Sa0xFF"),
                 "cis_x_can_signals.trqRefEngEC1Sa0x00": ("ECU", "cis_x_can_signals.trqRefEngEC1Sa0x00"),
                 "cis_x_can_signals.trqRetRefRCSa0xFF": ("ECU", "cis_x_can_signals.trqRetRefRCSa0xFF"),
                 "cis_x_can_signals.trqRetRefRCSa0xFF2": ("ECU", "cis_x_can_signals.trqRetRefRCSa0xFF2"),
                 "cis_x_can_signals.trqRetRefRCSa0xFF3": ("ECU", "cis_x_can_signals.trqRetRefRCSa0xFF3"),
                 "cis_x_can_signals.vxvWheelBasedCCVSSa0xFF": ("ECU", "cis_x_can_signals.vxvWheelBasedCCVSSa0xFF"),
                 "cis_x_can_signals.vxwFrontAxleEBC2Sa0x0B": ("ECU", "cis_x_can_signals.vxwFrontAxleEBC2Sa0x0B"),
                 "cis_x_can_signals.vxwRelativeFrontLeftEBC2Sa0x0B": ("ECU", "cis_x_can_signals.vxwRelativeFrontLeftEBC2Sa0x0B"),
                 "cis_x_can_signals.vxwRelativeFrontRightEBC2Sa0x0B": ("ECU", "cis_x_can_signals.vxwRelativeFrontRightEBC2Sa0x0B"),
                 "cis_x_can_signals.vxwRelativeRear1LeftEBC2Sa0x0B": ("ECU", "cis_x_can_signals.vxwRelativeRear1LeftEBC2Sa0x0B"),
                 "cis_x_can_signals.vxwRelativeRear1RightEBC2Sa0x0B": ("ECU", "cis_x_can_signals.vxwRelativeRear1RightEBC2Sa0x0B"),},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except ValueError, error:
      print __file__
      print error.message
    else:
      Client = datavis.cPlotNavigator(title="EBC1", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.AbsFullyOperationalEBC1Sa0x0B_B")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.AbsFullyOperationalEBC1Sa0x0B_B", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ABSOffroadSwitchEBC1Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ABSOffroadSwitchEBC1Sa0x0B_B2", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ABSactiveEBC1Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ABSactiveEBC1Sa0x0B_B2", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ASRBrkCtrlActEBC1Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ASRBrkCtrlActEBC1Sa0x0B_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ASREngCtrlActEBC1Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ASREngCtrlActEBC1Sa0x0B_B2", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.EBSBrkSwitchEBC1Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.EBSBrkSwitchEBC1Sa0x0B_B2", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.BrakePedalPositionEBC1Sa0x0B")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.BrakePedalPositionEBC1Sa0x0B", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.SAofCtrlDeviceForBrakeCtrlEBC1S")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.SAofCtrlDeviceForBrakeCtrlEBC1S", Time, Value, unit="")
      Client = datavis.cPlotNavigator(title="EEC2", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.AccelPed1LoIdleSwitchEEC2Sa0xFF")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.AccelPed1LoIdleSwitchEEC2Sa0xFF", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.AccelPedalPos1EEC2Sa0xFF")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.AccelPedalPos1EEC2Sa0xFF", Time, Value, unit="%", factor=0.00152587890625)
      Client = datavis.cPlotNavigator(title="ERC1", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE", Time, Value, unit="%", factor=0.006103515625)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE2", Time, Value, unit="%", factor=0.006103515625)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE3")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE3", Time, Value, unit="%", factor=0.006103515625)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.DrvrsDemRetPercTrqERC1Sa0xFE")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.DrvrsDemRetPercTrqERC1Sa0xFE", Time, Value, unit="%", factor=0.006103515625)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.DrvrsDemRetPercTrqERC1Sa0xFE2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.DrvrsDemRetPercTrqERC1Sa0xFE2", Time, Value, unit="%", factor=0.006103515625)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.DrvrsDemRetPercTrqERC1Sa0xFE3")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.DrvrsDemRetPercTrqERC1Sa0xFE3", Time, Value, unit="%", factor=0.006103515625)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.RetTrqModeERC1Sa0xFE_B4")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.RetTrqModeERC1Sa0xFE_B4", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.RetTrqModeERC1Sa0xFE2_B4")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.RetTrqModeERC1Sa0xFE2_B4", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.RetTrqModeERC1Sa0xFE3_B4")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.RetTrqModeERC1Sa0xFE3_B4", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.SAofCtrlDeviceForRetarderCtrlER")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.SAofCtrlDeviceForRetarderCtrlER", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.SAofCtrlDeviceForRetarderCtrlER_s0")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.SAofCtrlDeviceForRetarderCtrlER_s0", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.SAofCtrlDeviceForRetarderCtrlER_s1")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.SAofCtrlDeviceForRetarderCtrlER_s1", Time, Value, unit="")
      Client = datavis.cPlotNavigator(title="AMB", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.AmbientAirTempAMBSa0xFF")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.AmbientAirTempAMBSa0xFF", Time, Value, unit="C", factor=0.00390625)
      Client = datavis.cPlotNavigator(title="CCVS1", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.BrkSwitchCCVSSa0xFF_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.BrkSwitchCCVSSa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ClutchSwitchCCVSSa0xFF_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ClutchSwitchCCVSSa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ParkingBrkSwitchCCVSSa0xFF_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ParkingBrkSwitchCCVSSa0xFF_B2", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.CCEnableSwitchCCVSSa0xFF_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.CCEnableSwitchCCVSSa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.VehCcActiveCCVSSa0xFF_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.VehCcActiveCCVSSa0xFF_B2", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.CCAccelSwitchCCVSSa0xFF_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.CCAccelSwitchCCVSSa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.CCCoastSwitchCCVSSa0xFF_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.CCCoastSwitchCCVSSa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.CCPauseSwitchCCVSSa0xFF_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.CCPauseSwitchCCVSSa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.CCResumeSwitchCCVSSa0xFF_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.CCResumeSwitchCCVSSa0xFF_B2", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.vxvWheelBasedCCVSSa0xFF")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.vxvWheelBasedCCVSSa0xFF", Time, Value, unit="m/s")
      Client = datavis.cPlotNavigator(title="ETC2", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.CurrentGearETC2Sa0x03")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.CurrentGearETC2Sa0x03", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.SelectedGearETC2Sa0x03")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.SelectedGearETC2Sa0x03", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.iActGearETC2Sa0x03")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.iActGearETC2Sa0x03", Time, Value, unit="-")
      Client = datavis.cPlotNavigator(title="TD", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.YearTDSa0xFF")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.YearTDSa0xFF", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.MonthTDSa0xFF")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.MonthTDSa0xFF", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.DayTDSa0xFF")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.DayTDSa0xFF", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.HourTDSa0xFF")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.HourTDSa0xFF", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.MinuteTDSa0xFF")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.MinuteTDSa0xFF", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.SecondTDSa0xFF")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.SecondTDSa0xFF", Time, Value, unit="")
      Client = datavis.cPlotNavigator(title="PROP AUX ST ZBR", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.DirIndLPROPAUXSTZBR3Sa0x21_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.DirIndLPROPAUXSTZBR3Sa0x21_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.DirIndRPROPAUXSTZBR3Sa0x21_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.DirIndRPROPAUXSTZBR3Sa0x21_B2", Time, Value, unit="")
      Client = datavis.cPlotNavigator(title="EEC1", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ActualEnginePercentTorqueEEC1Sa")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ActualEnginePercentTorqueEEC1Sa", Time, Value, unit="%", factor=0.006103515625)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.DriversDemandEnginePercentTrqEE")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.DriversDemandEnginePercentTrqEE", Time, Value, unit="%", factor=0.006103515625)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.nMotEEC1Sa0x00")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.nMotEEC1Sa0x00", Time, Value, unit="1/min")
      Client = datavis.cPlotNavigator(title="VDHR", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.HighResTotalVehDisVDHRSa0xFF")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.HighResTotalVehDisVDHRSa0xFF", Time, Value, unit="")
      Client = datavis.cPlotNavigator(title="EEC3", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.NominalFrictionPercentTorqueEEC")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.NominalFrictionPercentTorqueEEC", Time, Value, unit="%", factor=0.006103515625)
      Client = datavis.cPlotNavigator(title="VDC1", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ROPBrkActVDC1Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ROPBrkActVDC1Sa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ROPEngActVDC1Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ROPEngActVDC1Sa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.YCBrkActVDC1Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.YCBrkActVDC1Sa0xFF_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.YCEngActVDC1Sa0xFF_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.YCEngActVDC1Sa0xFF_B2", Time, Value, unit="")
      Client = datavis.cPlotNavigator(title="RC", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.RetTypeRCSa0xFF_B4")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.RetTypeRCSa0xFF_B4", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.RetTypeRCSa0xFF2_B4")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.RetTypeRCSa0xFF2_B4", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.RetTypeRCSa0xFF3_B4")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.RetTypeRCSa0xFF3_B4", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.trqRetRefRCSa0xFF")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.trqRetRefRCSa0xFF", Time, Value, unit="Nm")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.trqRetRefRCSa0xFF2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.trqRetRefRCSa0xFF2", Time, Value, unit="Nm")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.trqRetRefRCSa0xFF3")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.trqRetRefRCSa0xFF3", Time, Value, unit="Nm")
      Client = datavis.cPlotNavigator(title="ETC1", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.TMShiftInProcessETC1Sa0x03_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.TMShiftInProcessETC1Sa0x03_B2", Time, Value, unit="")
      Client = datavis.cPlotNavigator(title="EBC5", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.BrkTempWarnEBC5Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.BrkTempWarnEBC5Sa0x0B_B2", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.FoundationBrakeUseEBC5Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.FoundationBrakeUseEBC5Sa0x0B_B2", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.XbrActCtrlModeEBC5Sa0x0B_B4")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.XbrActCtrlModeEBC5Sa0x0B_B4", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.XbrSysStateEBC5Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.XbrSysStateEBC5Sa0x0B_B2", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.aLimitXbrEBC5Sa0x0B")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.aLimitXbrEBC5Sa0x0B", Time, Value, unit="m/s^2")
      Client = datavis.cPlotNavigator(title="CVW", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.mGrossCombCVWSa0x0B")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.mGrossCombCVWSa0x0B", Time, Value, unit="kg")
      Client = datavis.cPlotNavigator(title="VDC2", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.alpSteeringWheelVDC2Sa0xFF")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.alpSteeringWheelVDC2Sa0xFF", Time, Value, unit="rad")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.psiDtVDC2Sa0xFF")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.psiDtVDC2Sa0xFF", Time, Value, unit="1/s")
      Client = datavis.cPlotNavigator(title="EC1", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.trqRefEngEC1Sa0x00")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.trqRefEngEC1Sa0x00", Time, Value, unit="Nm")
      Client = datavis.cPlotNavigator(title="EBC2", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.vxwFrontAxleEBC2Sa0x0B")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.vxwFrontAxleEBC2Sa0x0B", Time, Value, unit="m/s")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.vxwRelativeFrontLeftEBC2Sa0x0B")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.vxwRelativeFrontLeftEBC2Sa0x0B", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.vxwRelativeFrontRightEBC2Sa0x0B")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.vxwRelativeFrontRightEBC2Sa0x0B", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.vxwRelativeRear1LeftEBC2Sa0x0B")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.vxwRelativeRear1LeftEBC2Sa0x0B", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.vxwRelativeRear1RightEBC2Sa0x0B")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.vxwRelativeRear1RightEBC2Sa0x0B", Time, Value, unit="m/s")
      pass
    pass


