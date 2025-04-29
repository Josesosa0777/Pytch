import numpy as np

from interface import iCalc
from aebs_c import AEBS_C_wrapper


NORMING_VALS =\
[
  (np.float32(AEBS_C_wrapper._N_dSW_ub),
   ['dxv', 'dyv', 'dxSecure', 'dxStartICB']),
  (np.float32(AEBS_C_wrapper._N_vSW_uw),
   ['vxv', 'vyv', 'vRef', 'vEgoMaxStartWarning', 'vEgoMinStartWarning',
    'vRelMaxStartWarning', 'vRelStartICB']),
  (np.float32(AEBS_C_wrapper._N_aSW_uw),
   ['aRef', 'axv', 'aComfortSwingOut', 'aRelMin', 'axvBrakingLimit',
    'axvEmergencyBraking', 'axvPartialBraking']),
  (np.float32(AEBS_C_wrapper._N_nUW_ub),
   ['EngineSpeed', 'EngineSpeedMinEnable']),
  (np.float32(AEBS_C_wrapper._N_GPPosUW_uw),
   ['GPPos', 'pAccelMinStop', 'pAccelMinStopICB']),
  (np.float32(AEBS_C_wrapper._N_BPPosUW_uw),
   ['BPPos', 'pBrakeMinStop']),
  (np.float32(AEBS_C_wrapper._N_alpSteeringWheelSW_uw),
   ['alpSteeringWheel', 'alpSteeringWheelDeltaMinStop']),
  (np.float32(AEBS_C_wrapper._N_fak1UB_uw),
   ['SAMBrakingSkillMinLeavePInt', 'SAMBrakingSkillWMinLeavePInt',
    'SAMSteeringSkillMinLeavePInt', 'SASBrakingSkillMinLeavePInt',
    'SASBrakingSkillWMinLeavePInt', 'SASSteeringSkillMinLeavePInt']),
  (np.float32(AEBS_C_wrapper._N_alpDtSteeringWheelSW_uw),
   ['alpDtSteeringWheelMinStop']),
  (np.float32(AEBS_C_wrapper._N_tUW_uw),
   ['alpStwFilterT', 'tBlockingTimeDueToOverride', 'tBrakeDelay1',
    'tBrakeDelay2', 'tDirIndMaxSuppress', 'tMaxEmergencyBrakingTime',
    'tPartialBrakingTime', 'tStopDueToAP', 'tStopDueToBP', 'tWarningTime']),
  (np.float32(AEBS_C_wrapper._N_GPPosDeltaSW_uw),
   ['pAccelDeltaMinStop']),
  (np.float32(AEBS_C_wrapper._N_GPPosDtSW_ub),
   ['pDtAccelMinStop']),
  (np.float32(20),
   ['AEBS1_ttc']),
  (np.float32(2048),
   ['XBR_Demand']),
]

SGN_UNITS =\
[
  ('m', ['dxv', 'dyv']),
  ('m/s', ['vxv', 'vyv', 'vRef']),
  ('m/s/s', ['aRef', 'axv', 'XBR_Demand']),
  ('rpm', ['EngineSpeed']),
  ('rad', ['alpSteeringWheel']),
  ('%', ['GPPos', 'BPPos', 'TSC1_TorqueLimitation']),
  ('s', ['AEBS1_ttc']),
]


ccp_input_groups = [
{
  "AdditionalSensorAssociated_b": ("CCP", "kbaebsInaebs.AdditionalSensorAssociated_b"),
  "BPAct_b": ("CCP", "kbaebsInaebs.BPAct_b"),
  "BPPos": ("CCP", "kbaebsInaebs.BPPos"),
  "CMAllowEntry_b": ("CCP", "kbaebsInaebs.CMAllowEntry_b"),
  "CMBAllowEntry_b": ("CCP", "kbaebsInaebs.CMBAllowEntry_b"),
  "CMBCancel_b": ("CCP", "kbaebsInaebs.CMBCancel_b"),
  "CMCancel_b": ("CCP", "kbaebsInaebs.CMCancel_b"),
  "CWAllowEntry_b": ("CCP", "kbaebsInaebs.CWAllowEntry_b"),
  "CWCancel_b": ("CCP", "kbaebsInaebs.CWCancel_b"),
  "ControlledIrrevOffRaised_b": ("CCP", "kbaebsInaebs.ControlledIrrevOffRaised_b"),
  "ControlledRevOffRaised_b": ("CCP", "kbaebsInaebs.ControlledRevOffRaised_b"),
  "DirIndL_b": ("CCP", "kbaebsInaebs.DirIndL_b"),
  "DirIndR_b": ("CCP", "kbaebsInaebs.DirIndR_b"),
  "Drive_b": ("CCP", "kbaebsInaebs.Drive_b"),
  "DriverActivationDemand_b": ("CCP", "kbaebsInaebs.DriverActivationDemand_b"),
  "EngineSpeed": ("CCP", "kbaebsInaebs.EngineSpeed"),
  "FusionOperational_b": ("CCP", "kbaebsInaebs.FusionOperational_b"),
  "GPKickdown_B": ("CCP", "kbaebsInaebs.GPKickdown_B"),
  "GPPos": ("CCP", "kbaebsInaebs.GPPos"),
  "ImmediateIrrevOffRaised_b": ("CCP", "kbaebsInaebs.ImmediateIrrevOffRaised_b"),
  "ImmediateRevOffRaised_b": ("CCP", "kbaebsInaebs.ImmediateRevOffRaised_b"),
  "ReducedPerformance_b": ("CCP", "kbaebsInaebs.ReducedPerformance_b"),
  "ReverseGearDetected_b": ("CCP", "kbaebsInaebs.ReverseGearDetected_b"),
  "Stand_b": ("CCP", "kbaebsInaebs.Stand_b"),
  "Stopped_b": ("CCP", "kbaebsInaebs.Stopped_b"),
  "Valid_b": ("CCP", "kbaebsInaebs.Valid_b"),
  "aRef": ("CCP", "kbaebsInaebs.aRef"),
  "alpSteeringWheel": ("CCP", "kbaebsInaebs.alpSteeringWheel"),
  "axv": ("CCP", "kbaebsInaebs.axv"),
  "dxv": ("CCP", "kbaebsInaebs.dxv"),
  "dyv": ("CCP", "kbaebsInaebs.dyv"),
  "vRef": ("CCP", "kbaebsInaebs.vRef"),
  "vxv": ("CCP", "kbaebsInaebs.vxv"),
  "vyv": ("CCP", "kbaebsInaebs.vyv"),
},
]

ccp_output_groups = [
{
  "AEBS1_BendOff": ("CCP", "kbaebsOutaebs.AEBS1_BendOff"),
  "AEBS1_RelevantObjectDetected": ("CCP", "kbaebsOutaebs.AEBS1_RelevantObjectDetected"),
  "AEBS1_SystemState": ("CCP", "kbaebsOutaebs.AEBS1_SystemState"),
  "AEBS1_WarningLevel": ("CCP", "kbaebsOutaebs.AEBS1_WarningLevel"),
  "AEBS1_request": ("CCP", "kbaebsOutaebs.AEBS1_request"),
  "AEBS1_ttc": ("CCP", "kbaebsOutaebs.AEBS1_ttc"),
  "TSC1_TorqueLimitation": ("CCP", "kbaebsOutaebs.TSC1_TorqueLimitation"),
  "TSC1_request": ("CCP", "kbaebsOutaebs.TSC1_request"),
  "XBR_Demand": ("CCP", "kbaebsOutaebs.XBR_Demand"),
  "XBR_request": ("CCP", "kbaebsOutaebs.XBR_request"),
},
]

ccp_param_groups = [
{
  "ConfigChannel": ("CCP", "kbaebsParaebs.ConfigChannel"),
  "EmergencyBrakingEnableVideoValidationSAS": ("CCP", "kbaebsParaebs.EmergencyBrakingEnableVideoValidationSAS"),
  "EnableStandstillBraking": ("CCP", "kbaebsParaebs.EnableStandstillBraking"),
  "EngineSpeedMinEnable": ("CCP", "kbaebsParaebs.EngineSpeedMinEnable"),
  "FillAEBS1ObstData": ("CCP", "kbaebsParaebs.FillAEBS1ObstData"),
  "PartialBrakingEnableVideoValidationSAS": ("CCP", "kbaebsParaebs.PartialBrakingEnableVideoValidationSAS"),
  "SAMBrakingSkillMinLeavePInt": ("CCP", "kbaebsParaebs.SAMBrakingSkillMinLeavePInt"),
  "SAMBrakingSkillWMinLeavePInt": ("CCP", "kbaebsParaebs.SAMBrakingSkillWMinLeavePInt"),
  "SAMSteeringSkillMinLeavePInt": ("CCP", "kbaebsParaebs.SAMSteeringSkillMinLeavePInt"),
  "SASBrakingSkillMinLeavePInt": ("CCP", "kbaebsParaebs.SASBrakingSkillMinLeavePInt"),
  "SASBrakingSkillWMinLeavePInt": ("CCP", "kbaebsParaebs.SASBrakingSkillWMinLeavePInt"),
  "SASSteeringSkillMinLeavePInt": ("CCP", "kbaebsParaebs.SASSteeringSkillMinLeavePInt"),
  "UseAccelerationInfo": ("CCP", "kbaebsParaebs.UseAccelerationInfo"),
  "WarningEnableVideoValidationSAS": ("CCP", "kbaebsParaebs.WarningEnableVideoValidationSAS"),
  "aComfortSwingOut": ("CCP", "kbaebsParaebs.aComfortSwingOut"),
  "aRelMin": ("CCP", "kbaebsParaebs.aRelMin"),
  "alpDtSteeringWheelMinStop": ("CCP", "kbaebsParaebs.alpDtSteeringWheelMinStop"),
  "alpSteeringWheelDeltaMinStop": ("CCP", "kbaebsParaebs.alpSteeringWheelDeltaMinStop"),
  "alpStwFilterT": ("CCP", "kbaebsParaebs.alpStwFilterT"),
  "axvBrakingLimit": ("CCP", "kbaebsParaebs.axvBrakingLimit"),
  "axvEmergencyBraking": ("CCP", "kbaebsParaebs.axvEmergencyBraking"),
  "axvPartialBraking": ("CCP", "kbaebsParaebs.axvPartialBraking"),
  "dxSecure": ("CCP", "kbaebsParaebs.dxSecure"),
  "dxStartICB": ("CCP", "kbaebsParaebs.dxStartICB"),
  "pAccelDeltaMinStop": ("CCP", "kbaebsParaebs.pAccelDeltaMinStop"),
  "pAccelMinStop": ("CCP", "kbaebsParaebs.pAccelMinStop"),
  "pAccelMinStopICB": ("CCP", "kbaebsParaebs.pAccelMinStopICB"),
  "pBrakeMinStop": ("CCP", "kbaebsParaebs.pBrakeMinStop"),
  "pDtAccelMinStop": ("CCP", "kbaebsParaebs.pDtAccelMinStop"),
  "tBlockingTimeDueToOverride": ("CCP", "kbaebsParaebs.tBlockingTimeDueToOverride"),
  "tBrakeDelay1": ("CCP", "kbaebsParaebs.tBrakeDelay1"),
  "tBrakeDelay2": ("CCP", "kbaebsParaebs.tBrakeDelay2"),
  "tDirIndMaxSuppress": ("CCP", "kbaebsParaebs.tDirIndMaxSuppress"),
  "tMaxEmergencyBrakingTime": ("CCP", "kbaebsParaebs.tMaxEmergencyBrakingTime"),
  "tPartialBrakingTime": ("CCP", "kbaebsParaebs.tPartialBrakingTime"),
  "tStopDueToAP": ("CCP", "kbaebsParaebs.tStopDueToAP"),
  "tStopDueToBP": ("CCP", "kbaebsParaebs.tStopDueToBP"),
  "tWarningTime": ("CCP", "kbaebsParaebs.tWarningTime"),
  "vEgoMaxStartWarning": ("CCP", "kbaebsParaebs.vEgoMaxStartWarning"),
  "vEgoMinStartWarning": ("CCP", "kbaebsParaebs.vEgoMinStartWarning"),
  "vRelMaxStartWarning": ("CCP", "kbaebsParaebs.vRelMaxStartWarning"),
  "vRelStartICB": ("CCP", "kbaebsParaebs.vRelStartICB"),
  "WarningEnabledInReducedPerformaceSAM": ("CCP", "kbaebsParaebs.WarningEnabledInReducedPerformaceSAM"),
},
]

version_groups = [
{
  "Version_Major": ("CCP", "kbaebsOutaebs.Version_Major"),
  "Version_Minor": ("CCP", "kbaebsOutaebs.Version_Minor"),
},
]

rail_eval_groups = [
{
  "eval_inj_fault_dtc_id_ok": ("Environment", "eval_inj_fault_dtc_id_ok"),
  "eval_inj_fault_type": ("Environment", "eval_inj_fault_type"),
  "eval_inj_fault_flag_ok": ("Environment", "eval_inj_fault_flag_ok"),
  "eval_inj_cascade_pos": ("Environment", "eval_inj_cascade_pos"),
  "set_new_conditions": ("Environment", "set_new_conditions"),
  "RaIL_test_case_id": ("Environment", "RaIL_test_case_id"),
  "RaIL_test_session_id": ("Environment", "RaIL_test_session_id"),
  "CAN_ID_msg_to_sgn_chg": ("Environment", "CAN_ID_msg_to_sgn_chg"),
  "CAN_sgn_to_chg_length": ("Environment", "CAN_sgn_to_chg_length"),
  "CAN_sgn_to_chg_startbit": ("Environment", "CAN_sgn_to_chg_startbit"),
  "CAN_sgn_to_chg_raw_value": ("Environment", "CAN_sgn_to_chg_raw_value"),
  "CAN_ID_msg_to_timeout": ("Environment", "CAN_ID_msg_to_timeout"),
  "CAN_sgn_chg_type": ("Environment", "CAN_sgn_chg_type"),
},
]

sgn_groups = [
{
  "OEL_HazardLightSw": ("OEL_21", "OEL_HazardLightSw_21"),
  "sim_ta2_angle": ("SIM_Target", "sim_ta2_angle"),
  "sim_ta2_range": ("SIM_Target", "sim_ta2_range"),
  "sim_ta3_angle": ("SIM_Target", "sim_ta3_angle"),
  "sim_ta3_range": ("SIM_Target", "sim_ta3_range"),
  "EEC1_EngSpd": ("EEC1_00", "EEC1_EngSpd_00"),
  "XBR_ExtAccelDem": ("XBR_2A", "XBR_ExtAccelDem_2A"),
  "XBR_Prio": ("XBR_2A", "XBR_Prio_2A"),
  "ACC_brake_dem": ("ACC_S05", "LCG_a_xbr_out"),
  "ACC_brake_req": ("ACC_S05", "LCG_actuation"),
},
]


def get_sgn_normed(sgn_group, sgn_name, common_time=None):
  if common_time is not None:
    time, value = sgn_group.get_signal(sgn_name, ScaleTime=common_time)
  else:
    time, value = sgn_group.get_signal(sgn_name)
  for norm, sgn_4_norm in NORMING_VALS:
    if sgn_name in sgn_4_norm:
      break
  else:
    norm = 1
  value = value / norm
  return time, value

def get_unit_for_sgn(sgn_name):
  for unit, sgn_4_unit in SGN_UNITS:
    if sgn_name in sgn_4_unit:
      break
  else:
    unit = ""
  return unit


class cAcquireSignals(iCalc):
  def check(self):
    self.ccp_input_group = self.source.selectLazySignalGroup(ccp_input_groups)
    self.ccp_output_group = self.source.selectLazySignalGroup(ccp_output_groups)
    self.ccp_param_group = self.source.selectLazySignalGroup(ccp_param_groups)
    self.rail_eval_group = self.source.selectLazySignalGroup(rail_eval_groups)
    self.sgn_group = self.source.selectLazySignalGroup(sgn_groups)
    self.version_group = self.source.selectLazySignalGroup(version_groups)
    return
  
  def available_in_ccp_input(self, *sgn_names):
    return list(set(self.ccp_input_group).intersection(set(sgn_names)))
  
  def available_in_ccp_output(self, *sgn_names):
    return list(set(self.ccp_output_group).intersection(set(sgn_names)))
  
  def available_in_ccp_param(self, *sgn_names):
    return list(set(self.ccp_param_group).intersection(set(sgn_names)))
  
  def available_in_rail_eval(self, *sgn_names):
    return list(set(self.rail_eval_group).intersection(set(sgn_names)))
  
  def available_in_sgn_group(self, *sgn_names):
    return list(set(self.sgn_group).intersection(set(sgn_names)))
  
  def get_version(self):
    if 'Version_Major' in self.version_group:
      version_major = get_sgn_normed(self.version_group, 'Version_Major')[-1][0]
    else:
      version_major = 0
    if 'Version_Minor' in self.version_group:
      version_minor = get_sgn_normed(self.version_group, 'Version_Minor')[-1][0]
    else:
      version_minor = 0
    return version_major, version_minor
  
  def _get_signal(self, sgn_grp, sgn_name, **kwargs):
    if 'common_time' in kwargs:
      common_time = kwargs['common_time']
    else:
      common_time = None
    if 'inc_units' in kwargs:
      inc_units = kwargs['inc_units']
    else:
      inc_units = False
    time, value = get_sgn_normed(sgn_grp, sgn_name, common_time=common_time)
    if common_time is not None:
      time = None
    if inc_units:
      unit = get_unit_for_sgn(sgn_name)
    else:
      unit = None
    return time, value, unit
  
  def _chk_signal_content(self, time, value, unit):
    if time is not None and unit is not None:
      sgn_tuple = (time, value, unit)
    elif time is not None:
      sgn_tuple = (time, value)
    elif unit is not None:
      sgn_tuple = (value, unit)
    else:
      sgn_tuple = value
    return sgn_tuple
  
  def get_ccp_input_sgn(self, *sgn_names, **kwargs):
    sgn_out = {}
    for sgn_name in sgn_names:
      time, value, unit = self._get_signal(self.ccp_input_group,
                                           sgn_name, **kwargs)
      sgn_tuple = self._chk_signal_content(time, value, unit)
      sgn_out.setdefault(sgn_name, sgn_tuple)
    return sgn_out
  
  def get_ccp_output_sgn(self, *sgn_names, **kwargs):
    sgn_out = {}
    for sgn_name in sgn_names:
      time, value, unit = self._get_signal(self.ccp_output_group,
                                           sgn_name, **kwargs)
      sgn_tuple = self._chk_signal_content(time, value, unit)
      sgn_out.setdefault(sgn_name, sgn_tuple)
    return sgn_out
  
  def get_ccp_param_sgn(self, *sgn_names, **kwargs):
    sgn_out = {}
    for sgn_name in sgn_names:
      time, value, unit = self._get_signal(self.ccp_param_group,
                                           sgn_name, **kwargs)
      sgn_tuple = self._chk_signal_content(time, value, unit)
      sgn_out.setdefault(sgn_name, sgn_tuple)
    return sgn_out
  
  def get_rail_eval_sgn(self, *sgn_names, **kwargs):
    sgn_out = {}
    for sgn_name in sgn_names:
      time, value, unit = self._get_signal(self.rail_eval_group,
                                           sgn_name, **kwargs)
      sgn_tuple = self._chk_signal_content(time, value, unit)
      sgn_out.setdefault(sgn_name, sgn_tuple)
    return sgn_out
  
  def get_other_sgn(self, *sgn_names, **kwargs):
    sgn_out = {}
    for sgn_name in sgn_names:
      time, value, unit = self._get_signal(self.sgn_group,
                                           sgn_name, **kwargs)
      sgn_tuple = self._chk_signal_content(time, value, unit)
      sgn_out.setdefault(sgn_name, sgn_tuple)
    return sgn_out
  
  def get_needed_signals(self, *sgn_names, **kwargs):
    sgn_out = {}
    for sgn_name in sgn_names:
      if sgn_name in self.ccp_input_group:
        sgn_group = self.ccp_input_group
      elif sgn_name in self.ccp_output_group:
        sgn_group = self.ccp_output_group
      elif sgn_name in self.ccp_param_group:
        sgn_group = self.ccp_param_group
      elif sgn_name in self.rail_eval_group:
        sgn_group = self.rail_eval_group
      elif sgn_name in self.sgn_group:
        sgn_group = self.sgn_group
      else:
        continue
      time, value, unit = self._get_signal(sgn_group, sgn_name, **kwargs)
      sgn_tuple = self._chk_signal_content(time, value, unit)
      sgn_out.setdefault(sgn_name, sgn_tuple)
    return sgn_out
