# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"Visualize AEBS_C library parameters recorded by CCP"

from interface import iView
import datavis
from tceval.rail_eval_n_ccp_meas_handler import cAcquireSignals


init_params = {
  'use_DPV_alias': dict(use_dpv_alias=True),
  'not_use_DPV_alias': dict(use_dpv_alias=False),
}


sgn_names_with_dpv_alias =\
  dict([("ConfigChannel", 'CONFIG_CHANNEL'),
        ("EmergencyBrakingEnableVideoValidationSAS", 'EMERGENCY_BRAKING_ENABLE_VIDEO_VALIDATION_SAS'),
        ("EnableStandstillBraking", 'ENABLE_STANDSTILL_BRAKING'),
        ("EngineSpeedMinEnable", 'ENGINE_SPEED_MIN_ENABLE'),
        ("FillAEBS1ObstData", 'FILL_AEBS1_OBST_DATA'),
        ("PartialBrakingEnableVideoValidationSAS", 'PARTIAL_BRAKING_ENABLE_VIDEO_VALIDATION_SAS'),
        ("SAMBrakingSkillMinLeavePInt", 'SAM_BRAKING_SKILL_MIN_LEAVE_P_INT'),
        ("SAMBrakingSkillWMinLeavePInt", 'SAM_BRAKING_SKILL_W_MIN_LEAVE_P_INT'),
        ("SAMSteeringSkillMinLeavePInt", 'SAM_STEERING_SKILL_MIN_LEAVE_P_INT'),
        ("SASBrakingSkillMinLeavePInt", 'SAS_BRAKING_SKILL_MIN_LEAVE_P_INT'),
        ("SASBrakingSkillWMinLeavePInt", 'SAS_BRAKING_SKILL_W_MIN_LEAVE_P_INT'),
        ("SASSteeringSkillMinLeavePInt", 'SAS_STEERING_SKILL_MIN_LEAVE_P_INT'),
        ("UseAccelerationInfo", 'USE_ACCELERATION_INFO'),
        ("WarningEnableVideoValidationSAS", 'WARNING_ENABLE_VIDEO_VALIDATION_SAS'),
        ("aComfortSwingOut", 'A_COMFORT_SWING_OUT'),
        ("aRelMin", 'A_REL_MIN'),
        ("alpDtSteeringWheelMinStop", 'ALP_DT_STEERING_WHEEL_MIN_STOP'),
        ("alpSteeringWheelDeltaMinStop", 'ALP_STEERING_WHEEL_DELTA_MIN_STOP'),
        ("alpStwFilterT", 'ALP_STW_FILTER_T'),
        ("axvBrakingLimit", 'AXV_BRAKING_LIMIT'),
        ("axvEmergencyBraking", 'AXV_EMERGENCY_BRAKING'),
        ("axvPartialBraking", 'AXV_PARTIAL_BRAKING'),
        ("dxSecure", 'DX_SECURE'),
        ("dxStartICB", 'DX_START_ICB'),
        ("pAccelDeltaMinStop", 'P_ACCEL_DELTA_MIN_STOP'),
        ("pAccelMinStop", 'P_ACCEL_MIN_STOP'),
        ("pAccelMinStopICB", 'P_ACCEL_MIN_STOP_ICB'),
        ("pBrakeMinStop", 'P_BRAKE_MIN_STOP'),
        ("pDtAccelMinStop", 'P_DT_ACCEL_MIN_STOP'),
        ("tBlockingTimeDueToOverride", 'T_BLOCKING_TIME_DUE_TO_OVERRIDE'),
        ("tBrakeDelay1", 'T_BRAKE_DELAY1'),
        ("tBrakeDelay2", 'T_BRAKE_DELAY2'),
        ("tDirIndMaxSuppress", 'T_DIR_IND_MAX_SUPPRESS'),
        ("tMaxEmergencyBrakingTime", 'T_MAX_EMERGENCY_BRAKING_TIME'),
        ("tPartialBrakingTime", 'T_PARTIAL_BRAKING_TIME'),
        ("tStopDueToAP", 'T_STOP_DUE_TO_AP'),
        ("tStopDueToBP", 'T_STOP_DUE_TO_BP'),
        ("tWarningTime", 'T_WARNING_TIME'),
        ("vEgoMaxStartWarning", 'V_EGO_MAX_START_WARNING'),
        ("vEgoMinStartWarning", 'V_EGO_MIN_START_WARNING'),
        ("vRelMaxStartWarning", 'V_REL_MAX_START_WARNING'),
        ("vRelStartICB", 'V_REL_START_ICB'),])

ln_content = dict([('Default', sgn_names_with_dpv_alias),])


class View(iView, cAcquireSignals):
  def init(self, use_dpv_alias):
    self.use_dpv_alias = use_dpv_alias
    return
  
  def view(self):
    ln = datavis.cListNavigator(title="LN")
    self.sync.addClient(ln)
    
    for grp_name, sgn_names in ln_content.iteritems():
      req_sgn = sgn_names.keys()
      avail_signals = self.available_in_ccp_param(*req_sgn)
      ccp_params = self.get_ccp_param_sgn(*avail_signals)
      for sgn_name in sorted(sgn_names):
        dpv_alias = sgn_names[sgn_name]
        time, value = ccp_params[sgn_name]
        print_name = dpv_alias if self.use_dpv_alias else sgn_name
        ln.addsignal(print_name, (time, value), groupname=grp_name)
    return
