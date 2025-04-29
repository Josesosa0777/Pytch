default = {
    'general': [
        'quantity-%d' % i for i in xrange(10)
    ],
    "general": ["quantity-%d" % i for i in xrange(10)],
    "ego vehicle": [
        "speed",
        "speed start",
        "speed end",
        "speed min",
        "speed max",
        "yaw rate",
        "yaw rate start",
        "yaw rate end",
        "yaw rate min",
        "yaw rate max",
        "acceleration",
        "lateral acceleration",
        "driven distance",
        "gps lat start",
        "gps long start",
        "gps alt start",
        "steering wheel speed",
        "appos",
        "appos speed",
        "lateral speed",
        "lateral speed start",
        "mileage",
        "sw version",
        "event start time diff",
    ],
    "target": [
        "dx min",
        "dx max",
        "dx start",
        "dx end",
        "dx aeb",
        "dx paeb",
        "dy start",
        "dy error avg",
        "dy error max",
        "dy corrected avg (radar-only)",
        "dy corrected avg (lane fusion)",
        "vx",
        "vx start",
        "vx end",
        "ax",
        "ax start",
        "ax end",
        "ax min",
        "ax max",
        "ax avg",
        "ax std",
        "confidence avg",
        "length duty",
        "dy var duty",
        "infrastruct prob duty",
        "obstacle prob duty",
        "near obstacle prob duty",
        "classif quality duty",
        "aeb duty",
        "pure aeb duration",
        "paeb duty",
        "pure paeb duration",
        "fused duty",
        "ttc min",
    ],
    "lane": [
        "left line view range avg",
        "right line view range avg",
        "left line view range start",
        "right line view range start",
        "left line offset start",
        "right line offset start",  # offset from vehicle centerline
        "left line distance start",
        "right line distance start",  # distance from vehicle (wheel)
        "line distance start",
    ],
    "AEBS": [  # deprecated; use 'intervention'
        "speed reduction",
    ],
    "AEBS resim": [
        "ego_velocity_x",
        "obj_width",
        "obj_length",
        "obj_distance_x",
        "obj_distance_y",
        "obj_relative_velocity_x",
        "obj_relative_velocity_y",
        "object_id",
        "e_dynamic_property",
        "ui_stopped_confidence",
    ],
    "AEBS Usecase check": [
        "ego_vx_at_warning",
        "aebs_obj_vx_at_warning",
        "dx_warning",
        "dx_braking",
        "dx_emergency",
        "t_warning",
        "dx_stopping",
        "ego_vx_stopping",
    ],
    "pyon": [
        "foo",
        "bar",
    ],
    "association": [
        "online duty",
        "offline duty",
    ],
    "date": [
        "year",
        "month",
        "day",
        "hour",
        "minute",
        "second",
    ],
    'CVR3 sensor check': [
        "absTimeDer_max", "absTimeDer_mean", "absTimeDer_min",
        "absTime_max", "absTime_min",
        "cntAlive_max", "cntAlive_mean",
        "egoDrivenDistance", "egoSpeed_mean", "egoYawRate_max", "egoYawRate_mean",
        "fov_dx_max", "fov_dx_mean", "fov_dy_max", "fov_dy_mean",
        "fusMeasErrors", "fusMissedVidUpdates",
        "invalidTimeCount",
        "objCreationRate_mean",
        "posObjectCount",
        "receivedPower_mean",
        "tcCycleCount", "tcCycleTime_max", "tcCycleTime_mean", "tcCycleTime_std",
    ],
    'CANape sensor check': [
        "videoAvailability",
        "videoFps_mean", "videoFps_min",
        "videoTimeDer_max", "videoTimeDer_mean", "videoTimeDer_min",
    ],
    'S-Cam sensor check': [
        'timeTotal', 'timeAvailable', 'availability',
        'minTime', 'maxTime', 'meanCT', 'numOfLongLapse',
    ],
    'intervention': [
        'speed reduction', 'accel demand min', 'accel demand max',
    ],
    'path prediction': [
        'rms error avg', 'other rms error avg',
        'lane valid duty', 'moving radar valid duty',
    ],
    'ecu performance': [
        'processor load min', 'processor load max', 'processor load avg',
        'cycle time min', 'cycle time max', 'cycle time avg',
    ],
    'mobileye': [
        'frame start', 'frame end',
    ],
    'conf fusion': [
        'video conf min', 'video conf max', 'video conf start', 'video conf end'
    ],
    'fault identifier': [
        'ID', 'DTC', 'SPN', 'FMI',
    ],
    'AC100 sensor check': [
        'blindness min', 'blindness max', 'covi min', 'covi max',
        'yaw rate offset min', 'yaw rate offset max', 'dfil min', 'dfil max',
        'fov count left min', 'fov count left max', 'fov count centre min',
        'fov count centre max', 'fov count right min', 'fov count right max',
    ],
    'FLR25 radar check': [
        'Cat2LastResetReason', 'Address', 'ResetCounter', 'Return Address'
    ],
    'FLC25 camera check': [
        'ResetReason', 'ResetCounter'
    ],
    'FLC25 ACAL YAW Statistics': [
        'Count', 'Mean','Std','Min','Max','Sum','Violation'
    ],
    'FLC25 LD check': [
        'construction site detected'
    ],
    'TPF TRW Compare': [
        'timestamp', 'trw_dx', 'trw_dy', 'trw_track_id', 'trw_alive_time', 'nearest_tpf_track_id',
        'nearest_tpf_delta_vx', 'nearest_tpf_distance', 'nearest_tpf_alive_time'
    ],
    'ACC check': [
        'dirk_red_button', 'dirk_green_button', 'economic_driving', 'strong brake request', 'ACC Brake overheat', 'unexp strong brake','ACC Shutdown','ACC Jerk', 'take over request',
        'acc overreaction', 'brakepedal override', 'torque limit above threshold',
        'acc target present(dx)', 'pedestrian go suppression target present(dx)', 'verdict', 'brake request'
    ],
    'DM1 signals check': [
        'AmberWarningLamp', 'FailureModeIdentifier'
    ],
    'FLC25 check': [
        'obj_distx_jump', 'obj_id', 'obj_distx_val', 'measured_by', 'obj_disty_jump', 'obj_disty_val', 'C0_left_wheel',
        'C0_right_wheel'
    ],
    'FLC25 Object SwitchOver check': [
        'Old Track End(vx)', 'Old Track End(vx_abs)', 'Old Track End(dx)', 'Old Track End(dy)',
        'New Track St(vx)', 'New Track St(vx_abs)', 'New Track St(dx)', 'New Track St(dy)'
    ],
    'FLC25 Object LaneChange check': [
        'Object Info(current_id)',
        'Object Info(previous_index)', 'Object Info(current_index)',
        'Object Info(previous_lane)', 'Object Info(current_lane)',
        'Object Info(previous_time)', 'Object Info(current_time)',
        'Object Distance X'

    ],
    'DTC event check': [
        'AmberWarningLamp', 'DTC1', 'DTC2', 'DTC3', 'DTC4', 'DTC5', 'DTC occurence counter1', 'DTC occurence counter2',
        'DTC occurence counter3', 'DTC occurence counter4', 'DTC occurence counter5', 'DTC ID', 'DTC counter',
        'DTC timestamp', 'DTC history ID','DTC in HEX','DTC in DEC',
        'DTC history counter', 'DTC history timestamp', 'DEM events', 'DEM event ids'
    ],
    'ACC PED STOP': [
        'vehicle_in_accped_speed_range'
    ],
    'Function Deactivation Check': [
        'CAN XBR', 'AEBS brake acceleration demand', 'CAN AEBSState'
    ],
    'TSR': [
        'sign_class_id', 'sign_class_name', 'postmarker_Lane_ref', 'value', 'quantity', 'uid', "TP", "FP", "Total_GT",
        "FN", "conti_uid",
        "AutoHighLowBeamControl", "TSSCurrentRegion", "TSSDetectedStatus", "TSSDetectedUoM", "TSSDetectedValue",
        "TSSLifeTime", "TSSOverspeedAlert", "conti_duration",
        # For KBKPI report
        "CAN_FP1", "CAN_FP2", "CAN_FP3", "CAN_TP", "CAN_TN", "CAN_FP", "CAN_FN", "can_duration", "CAN_sign_class_id",
        "CAN_AutoHighLowBeamControl", "CAN_TSSCurrentRegion", "CAN_TSSDetectedStatus", "CAN_TSSDetectedUoM",
        "CAN_TSSDetectedValue", "CAN_TSSLifeTime", "CAN_TSSOverspeedAlert",
        "CAN_GT_existance_true", "CAN_GT_existance_false", "CAN_Total_GT"
        , "TSR_SpeedLimit1_E8_sE8", "TSR_SpeedLimit1Supplementary_E8_sE8", "TSR_SpeedLimit2_E8_sE8",
        "TSR_SpeedLimitElectronic_E8_sE8", "TSR_NoPassingRestriction_E8_sE8","TSR_CountryCode_E8_sE8"
    ],
    "PAEBS Debug": [
        "collision probability",
        "ttc",
        "path distance",
        "cascade distance",
        "internal state",
        "lane",
        "vx_ref",
        "dx",
        "motion state",
        "object type",
        "source",
        "probability of existance",
        "lane confidence",
        "classification confidence",
    ],
    "PAEBS LAUSCH": [
        "collision probability",
        "ttc",
        "path distance",
        "cascade distance",
        "internal state",
        "lane",
        "vx_ref",
        "dx",
        "motion state",
        "object type",
        "source",
        "probability of existance",
        "lane confidence",
        "classification confidence",
    ],
    'FLC25 LDWS': [
        "Not Available",
        "Available",
        "FrontAxleSpeed"
    ],
    'Trailer': [
        "AyFilt_max_value", "AyCalc_max_value", 'AyLimLeft_max_value', 'AyLimRight_max_value'
    ],
    'BSIS Event' :
        ['LonDispMIOPassSide','LatDispMIOPassSide', 'LatDispMIOFront','LonDispMIOFront',
         'LatDispMIORightSide', 'LonDispMIORightSide', 'BSIS', 'MOIS', 'VDP', 'LCDA', 'FNA'],
}
""":type: dict
{groupname<str>: [valuename<str>]}"""
