import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"acc.XStates_TC.ActivationPreventionConditions.Moving.b.CrashOccurred_b": ("ECU", "acc.XStates_TC.ActivationPreventionConditions.Moving.b.CrashOccurred_b"),
                 "acc.XStates_TC.ActivationPreventionConditions.Moving.b.DriveAwayPreventionConditionFul": ("ECU", "acc.XStates_TC.ActivationPreventionConditions.Moving.b.DriveAwayPreventionConditionFul"),
                 "acc.XStates_TC.ActivationPreventionConditions.Moving.b.HardwareCheckNotSuccessful_b": ("ECU", "acc.XStates_TC.ActivationPreventionConditions.Moving.b.HardwareCheckNotSuccessful_b"),
                 "acc.XStates_TC.ActivationPreventionConditions.Moving.b.SwitchOffConditionFulfilled_b": ("ECU", "acc.XStates_TC.ActivationPreventionConditions.Moving.b.SwitchOffConditionFulfilled_b"),
                 "acc.XStates_TC.ActivationPreventionConditions.Moving.b.TransportModeActive_b": ("ECU", "acc.XStates_TC.ActivationPreventionConditions.Moving.b.TransportModeActive_b"),
                 "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.CrashOccurred_b": ("ECU", "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.CrashOccurred_b"),
                 "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.EPBTightened_b": ("ECU", "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.EPBTightened_b"),
                 "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.HardwareCheckNotSuccessful_b": ("ECU", "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.HardwareCheckNotSuccessful_b"),
                 "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.SwitchOffConditionFulfilled_b": ("ECU", "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.SwitchOffConditionFulfilled_b"),
                 "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.TransportModeActive_b": ("ECU", "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.TransportModeActive_b"),
                 "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.VehicleStandsStill_b": ("ECU", "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.VehicleStandsStill_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Moving.b.BrakePedalPressed_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Moving.b.BrakePedalPressed_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Moving.b.Failure_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Moving.b.Failure_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Moving.b.HigherLevelSwitchOffRequest_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Moving.b.HigherLevelSwitchOffRequest_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Moving.b.MainSwitchOff_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Moving.b.MainSwitchOff_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.BrakePedalPressed_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.BrakePedalPressed_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.Cancel_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.Cancel_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.CrashOccurred_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.CrashOccurred_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.EPBActuated_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.EPBActuated_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.Failure_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.Failure_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.HDCStandBy_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.HDCStandBy_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.HigherLevelSwitchOffRequest_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.HigherLevelSwitchOffRequest_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.MainSwitchOff_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.MainSwitchOff_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.RoadSlopeTooLarge_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.RoadSlopeTooLarge_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.SecureStandstillNotReached_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.SecureStandstillNotReached_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.StandstillSecured_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.StandstillSecured_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.StandstillSlipping_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.StandstillSlipping_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.StartStopEngineOff_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.StartStopEngineOff_b"),
                 "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.WrongGearLeverPosition_b": ("ECU", "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.WrongGearLeverPosition_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.ABSActive_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.ABSActive_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.ADSActive_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.ADSActive_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.ASRActive_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.ASRActive_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.Cancel_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.Cancel_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.CarMovingBackwards_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.CarMovingBackwards_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.CrashOccurred_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.CrashOccurred_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.EPBActuated_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.EPBActuated_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.ESPActive_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.ESPActive_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.EngineOff_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.EngineOff_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.Failure_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.Failure_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.FollowObjectLostCloseRange_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.FollowObjectLostCloseRange_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.HDCStandBy_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.HDCStandBy_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.MSRActive_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.MSRActive_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.NMotTooHighInMPosition_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.NMotTooHighInMPosition_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.RoadSlopeTooLarge_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.RoadSlopeTooLarge_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.Slipping_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.Slipping_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.TrailerStabilisationActive_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.TrailerStabilisationActive_b"),
                 "acc.XStates_TC.SoftSwitchOffConditions.l.WrongGearLeverPosition_b": ("ECU", "acc.XStates_TC.SoftSwitchOffConditions.l.WrongGearLeverPosition_b"),
                 "acc.XStates_TC.Conditions.w.ActivationConditionsFulfilled_b": ("ECU", "acc.XStates_TC.Conditions.w.ActivationConditionsFulfilled_b"),
                 "acc.XStates_TC.Conditions.w.AutomaticDriveOffConditionsFulf": ("ECU", "acc.XStates_TC.Conditions.w.AutomaticDriveOffConditionsFulf"),
                 "acc.XStates_TC.Conditions.w.BrakeOnlyConditionFulfilled_b": ("ECU", "acc.XStates_TC.Conditions.w.BrakeOnlyConditionFulfilled_b"),
                 "acc.XStates_TC.Conditions.w.BrakeOnlyEndConditionFulfilled_": ("ECU", "acc.XStates_TC.Conditions.w.BrakeOnlyEndConditionFulfilled_"),
                 "acc.XStates_TC.Conditions.w.ConfirmedDriveOffConditionsFulf": ("ECU", "acc.XStates_TC.Conditions.w.ConfirmedDriveOffConditionsFulf"),
                 "acc.XStates_TC.Conditions.w.InitialisationEndConditionFulfi": ("ECU", "acc.XStates_TC.Conditions.w.InitialisationEndConditionFulfi"),
                 "acc.XStates_TC.Conditions.w.StandSecureConditionFulfilled_b": ("ECU", "acc.XStates_TC.Conditions.w.StandSecureConditionFulfilled_b"),
                 "acc.XStates_TC.Conditions.w.StandSecureEndConditionFulfille": ("ECU", "acc.XStates_TC.Conditions.w.StandSecureEndConditionFulfille"),
                 "acc.XStates_TC.Conditions.w.StandWaitConditionFulfilled_b": ("ECU", "acc.XStates_TC.Conditions.w.StandWaitConditionFulfilled_b"),
                 "acc.XStates_TC.Conditions.w.SwitchOffConditionFulfilled_b": ("ECU", "acc.XStates_TC.Conditions.w.SwitchOffConditionFulfilled_b"),
                 "acc.XStates_TC.SecureStandstillConditions.w.DriverDoorOpen_b": ("ECU", "acc.XStates_TC.SecureStandstillConditions.w.DriverDoorOpen_b"),
                 "acc.XStates_TC.SecureStandstillConditions.w.DriverSeatbeltLockOpen_b": ("ECU", "acc.XStates_TC.SecureStandstillConditions.w.DriverSeatbeltLockOpen_b"),
                 "acc.XStates_TC.SecureStandstillConditions.w.EngineOff_b": ("ECU", "acc.XStates_TC.SecureStandstillConditions.w.EngineOff_b"),
                 "acc.XStates_TC.SecureStandstillConditions.w.Failure_b": ("ECU", "acc.XStates_TC.SecureStandstillConditions.w.Failure_b"),
                 "acc.XStates_TC.SecureStandstillConditions.w.HoodOpen_b": ("ECU", "acc.XStates_TC.SecureStandstillConditions.w.HoodOpen_b"),
                 "acc.XStates_TC.SecureStandstillConditions.w.PassengerDoorOpen_b": ("ECU", "acc.XStates_TC.SecureStandstillConditions.w.PassengerDoorOpen_b"),
                 "acc.XStates_TC.SecureStandstillConditions.w.RearLeftDoorOpen_b": ("ECU", "acc.XStates_TC.SecureStandstillConditions.w.RearLeftDoorOpen_b"),
                 "acc.XStates_TC.SecureStandstillConditions.w.RearRightDoorOpen_b": ("ECU", "acc.XStates_TC.SecureStandstillConditions.w.RearRightDoorOpen_b"),
                 "acc.XStates_TC.SecureStandstillConditions.w.StandstillTimeExceeded_b": ("ECU", "acc.XStates_TC.SecureStandstillConditions.w.StandstillTimeExceeded_b"),
                 "acc.XStates_T20.SpecificState": ("ECU", "acc.XStates_T20.SpecificState"),
                 "vlc.Mea_T20.StateInternal": ("ECU", "vlc.Mea_T20.StateInternal"),},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except ValueError, error:
      print __file__
      print error.message
    else:
      Client = datavis.cPlotNavigator(title="Constraints", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.ActivationPreventionConditions.Moving.b.CrashOccurred_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.ActivationPreventionConditions.Moving.b.CrashOccurred_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.ActivationPreventionConditions.Moving.b.DriveAwayPreventionConditionFul")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.ActivationPreventionConditions.Moving.b.DriveAwayPreventionConditionFul", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.ActivationPreventionConditions.Moving.b.HardwareCheckNotSuccessful_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.ActivationPreventionConditions.Moving.b.HardwareCheckNotSuccessful_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.ActivationPreventionConditions.Moving.b.SwitchOffConditionFulfilled_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.ActivationPreventionConditions.Moving.b.SwitchOffConditionFulfilled_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.ActivationPreventionConditions.Moving.b.TransportModeActive_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.ActivationPreventionConditions.Moving.b.TransportModeActive_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.CrashOccurred_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.CrashOccurred_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.EPBTightened_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.EPBTightened_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.HardwareCheckNotSuccessful_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.HardwareCheckNotSuccessful_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.SwitchOffConditionFulfilled_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.SwitchOffConditionFulfilled_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.TransportModeActive_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.TransportModeActive_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.VehicleStandsStill_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.ActivationPreventionConditions.Standstill.b.VehicleStandsStill_b", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Moving.b.BrakePedalPressed_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Moving.b.BrakePedalPressed_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Moving.b.Failure_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Moving.b.Failure_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Moving.b.HigherLevelSwitchOffRequest_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Moving.b.HigherLevelSwitchOffRequest_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Moving.b.MainSwitchOff_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Moving.b.MainSwitchOff_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.BrakePedalPressed_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.BrakePedalPressed_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.Cancel_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.Cancel_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.CrashOccurred_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.CrashOccurred_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.EPBActuated_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.EPBActuated_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.Failure_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.Failure_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.HDCStandBy_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.HDCStandBy_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.HigherLevelSwitchOffRequest_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.HigherLevelSwitchOffRequest_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.MainSwitchOff_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.MainSwitchOff_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.RoadSlopeTooLarge_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.RoadSlopeTooLarge_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.SecureStandstillNotReached_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.SecureStandstillNotReached_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.StandstillSecured_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.StandstillSecured_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.StandstillSlipping_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.StandstillSlipping_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.StartStopEngineOff_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.StartStopEngineOff_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.WrongGearLeverPosition_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.FastSwitchOffConditions.Standstill.w.WrongGearLeverPosition_b", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.ABSActive_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.ABSActive_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.ADSActive_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.ADSActive_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.ASRActive_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.ASRActive_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.Cancel_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.Cancel_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.CarMovingBackwards_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.CarMovingBackwards_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.CrashOccurred_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.CrashOccurred_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.EPBActuated_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.EPBActuated_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.ESPActive_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.ESPActive_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.EngineOff_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.EngineOff_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.Failure_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.Failure_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.FollowObjectLostCloseRange_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.FollowObjectLostCloseRange_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.HDCStandBy_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.HDCStandBy_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.MSRActive_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.MSRActive_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.NMotTooHighInMPosition_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.NMotTooHighInMPosition_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.RoadSlopeTooLarge_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.RoadSlopeTooLarge_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.Slipping_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.Slipping_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.TrailerStabilisationActive_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.TrailerStabilisationActive_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SoftSwitchOffConditions.l.WrongGearLeverPosition_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SoftSwitchOffConditions.l.WrongGearLeverPosition_b", Time, Value, unit="")
      Client = datavis.cPlotNavigator(title="Conditions and states", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.Conditions.w.ActivationConditionsFulfilled_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.Conditions.w.ActivationConditionsFulfilled_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.Conditions.w.AutomaticDriveOffConditionsFulf")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.Conditions.w.AutomaticDriveOffConditionsFulf", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.Conditions.w.BrakeOnlyConditionFulfilled_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.Conditions.w.BrakeOnlyConditionFulfilled_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.Conditions.w.BrakeOnlyEndConditionFulfilled_")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.Conditions.w.BrakeOnlyEndConditionFulfilled_", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.Conditions.w.ConfirmedDriveOffConditionsFulf")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.Conditions.w.ConfirmedDriveOffConditionsFulf", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.Conditions.w.InitialisationEndConditionFulfi")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.Conditions.w.InitialisationEndConditionFulfi", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.Conditions.w.StandSecureConditionFulfilled_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.Conditions.w.StandSecureConditionFulfilled_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.Conditions.w.StandSecureEndConditionFulfille")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.Conditions.w.StandSecureEndConditionFulfille", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.Conditions.w.StandWaitConditionFulfilled_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.Conditions.w.StandWaitConditionFulfilled_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.Conditions.w.SwitchOffConditionFulfilled_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.Conditions.w.SwitchOffConditionFulfilled_b", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SecureStandstillConditions.w.DriverDoorOpen_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SecureStandstillConditions.w.DriverDoorOpen_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SecureStandstillConditions.w.DriverSeatbeltLockOpen_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SecureStandstillConditions.w.DriverSeatbeltLockOpen_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SecureStandstillConditions.w.EngineOff_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SecureStandstillConditions.w.EngineOff_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SecureStandstillConditions.w.Failure_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SecureStandstillConditions.w.Failure_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SecureStandstillConditions.w.HoodOpen_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SecureStandstillConditions.w.HoodOpen_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SecureStandstillConditions.w.PassengerDoorOpen_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SecureStandstillConditions.w.PassengerDoorOpen_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SecureStandstillConditions.w.RearLeftDoorOpen_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SecureStandstillConditions.w.RearLeftDoorOpen_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SecureStandstillConditions.w.RearRightDoorOpen_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SecureStandstillConditions.w.RearRightDoorOpen_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SecureStandstillConditions.w.StandstillTimeExceeded_b")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SecureStandstillConditions.w.StandstillTimeExceeded_b", Time, Value, unit="")
      Axis = Client.addAxis(ylim=(0.0, 25.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_T20.SpecificState")
      Client.addSignal2Axis(Axis, "acc.XStates_T20.SpecificState", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.Mea_T20.StateInternal")
      Client.addSignal2Axis(Axis, "vlc.Mea_T20.StateInternal", Time, Value, unit="")
      pass
    pass


