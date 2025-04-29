from pyutils.orderedset import OrderedSet
import trw_active_faults
from camera_sensor_status import flc20_sensor_status_dict
from lane_quality_state import lane_quality_dict
from fused_state import fused_dict
from fcw_state import fcw_state_dict
from aebs_state import aebs_state_dict
from paebs_state import paebs_state_dict
from ldws_state import ldws_state_dict
from daytime import daytime_dict
from aebs_classif import all_labels as aebs_warning_causes
from paebs_classif import all_labels as paebs_warning_causes
from line_props import line_type_dict

default = {
    'standard': (
        False,
        ['valid', 'missed', 'invalid'],
    ),
    'general': (
        False,
        ['class-%d' % i for i in xrange(10)],
    ),
    'relevance': (
        True,
        ['relevant', 'irrelevant', 'false event'],
    ),
    'sensor': (
        False,
        ['CVR2', 'CVR3', 'AC100', 'ESR', 'IBEO', 'S-Cam', 'Iteris'],
    ),
    'sensor type': (
        False,
        ['radar', 'lidar', 'laser', 'camera', 'infrared camera'],
    ),
    'vehicle type': (
        True,
        ['car', 'truck', 'bus', 'agricultural', 'trailer', 'motorcycle', 'bike'],
    ),
    'manoeuvre type': (
        True,
        ['cut-in', 'cut-out', 'cut-through', 'overtaking',
         'left turn', 'right turn', 'sharp turn', 'u-turn',
         'left lane change', 'right lane change', 'lane change',
         'straight driving',
         'unclassifiable', ],
    ),
    'moving state': (
        False,
        ['moving', 'stopped', 'stationary', 'unclassified'],
    ),
    'moving direction': (
        False,
        ['oncoming', 'ongoing'],
    ),
    'lane': (
        False,
        ['left', 'same', 'right', 'uncorrelated left', 'uncorrelated right'],
    ),
    'tracking': (
        False,
        ['stable', 'missing', 'ghost', 'late', 'dropout', 'jumping'],
    ),
    'asso problem': (
        False,
        ['late', 'quick', 'reunion', 'replaced', 'dropout', 'missing', 'wrong'],
    ),
    'asso problem main cause': (
        False,
        ['disappearance', 'solver', 'gate', 'filter', 'unknown'],
    ),
    'asso problem detailed cause': (
        False,
        ['angle', 'occlusion', 'dx', 'dx far range', 'counter', 'invttc'],
    ),
    'asso state': (
        False,
        ['radar only', 'camera only', 'fused'],
    ),
    'asso afterlife': (
        True,
        ['new pair', 'original pair', 'lonely', 'no'],
    ),
    'asso breakup reason': (
        True,
        ['radar loss', 'video loss', 'both loss', 'unknown'],
    ),
    'sensors involved': (
        True,
        ['radar', 'camera', 'both', 'neither'],
    ),
    'OHY object': (
        True,
        [str(i) for i in xrange(40)],
    ),
    'FUS object': (
        True,
        [str(i) for i in xrange(33)],
    ),
    'FUS VID object': (
        True,
        [str(i) for i in xrange(10)],
    ),
    'AC100 track': (
        True,
        [str(i) for i in xrange(21)],
    ),
    'S-Cam obstacle data': (
        True,
        [str(i) for i in xrange(1, 11)],
    ),
    'S-Cam object': (
        True,
        [str(i) for i in xrange(1, 128)],
    ),
    'daytime': (
        True,
        list(OrderedSet(daytime_dict.itervalues())),
    ),
    'availability': (
        True,
        ['available', 'n/a'],
    ),
    'sensor n/a': (
        False,
        ['CVR2', 'CVR3', 'AC100', 'ESR', 'IBEO', 'S-Cam', 'Iteris'],
    ),
    'false warning reduction': (
        False,
        ['fw red with sdf'],
    ),
    'sels warning': (
        False,
        ['CVR3W sels w/o SDF'],
    ),
    'false warning cause': (  # deprecated; use 'AEBS event cause' instead
        False,
        ['bridge', 'tunnel', 'infrastructure', 'parking car', 'road exit',
         'high curvature', 'traffic island', 'approaching curve', 'straight road',
         'construction site', 'braking fw vehicle', 'overtaking',
         'passing by', 'sharp turn', 'overhead sign', 'crossing traffic'],
    ),
    'AEBS event cause': (
        True,
        aebs_warning_causes,
    ),
    'ACC issue type': (
        True,
        ['KB Issue', 'Conti Issue']
    ),
    'ACC event cause': (
        True,
        ['Late target detection', 'Wrong lane assignment', 'Object detection', 'Target loss', 'braking', 'torque limit',
         'No Issue Found']
    ),
    'DMT driver monitoring': (
        False,
        ['driver active', 'accel pedal', 'brake pedal', 'steering wheel', 'indicator'],
    ),
    'OHY object detection': (
        True,
        ['yes', 'no'],
    ),
    'road type': (
        True,
        ['ego stopped', 'city', 'rural', 'highway'],
    ),
    'engine running': (
        True,
        ['yes', 'no', 'n/a'],
    ),
    'is_file_corrupt': (
        True,
        ['yes', 'no'],
    ),
    'AEBS algo': (
        True,
        ['Avoidance', 'Mitigation10', 'Mitigation20', 'KB AEBS', 'KB ASF Avoidance',
         'CVR2 Warning', 'CVR3 Warning', 'AC100 Warning', 'FLR20 Prop Warning',
         'FLR20 Warning', 'TRW CM', 'Autobox Warning', 'SIL KB AEBS',
         'FLR20 RadarOnly Warning',
         'FLR21 Prop Warning', 'FLR21 Warning', 'FLR21 RadarOnly Warning',
         'Wabco Warning', 'ARS430 Warning', 'FLR25 Warning'],
    ),
    'FLR25 events': (
        True,
        ['Radar Reset']
    ),
    'FLR20 object': (
        True,
        [str(i) for i in xrange(0, 21)],
    ),
    'FLC25 CEM TPF Old ID': (
        True,
        [str(i) for i in xrange(0, 100)],
    ),
    'FLC25 CEM TPF New ID': (
        True,
        [str(i) for i in xrange(0, 100)],
    ),
    'FLC25 CEM TPF Object Info': (
        True,
        [str(i) for i in xrange(0, 100)],
    ),
    'FLC25 events': (
        True,
        ['Lane Drops', 'Lane Merge ego_left-ego_center', 'Lane Merge ego_left-ego_right',
         'Lane Merge ego_right-ego_center', 'Object Jump', 'Object Track SwitchOver', 'Object Lane Change',
         'left lane quality is around 50%',
         'right lane quality is around 50%', 'Not realistic lane width', 'left lane is not within range'
                                                                         'right lane is not within range',
         'strong distance change', '0..25', '26..50', '51..75', '76..100',
         'Left Lane Quality drop', 'Right Lane Quality drop', 'ACC Unstable tracking', 'Camera Reset', 'YAW Statistics',
         'LD during ego lane change', 'LD dropouts on HW',
         'NumOfDetectedObjects', 'Worst Left Lane Detection', 'Worst Right Lane Detection', 'Left Lane C0 Jump',
         'Right Lane C0 Jump',
         'deactivated by driver', 'ready', 'warning', 'imminent_left_0->1', 'imminent_right_0->1',
         'Left_lane_C0 Above Threshold', 'Right_lane_C0 Above Threshold', 'worst lane drop',
         'LD Construction Site', ]
    ),

    'Fusion3 Data Mining': (
        True,
        ['FDA Low Speed']
    ),
    'AEBS problem': (
        False,
        ['warning w/o object']),
    'Bendix event': (
        True,
        ['1-AEB breaking', '2-AEB warning', '3-ACC activity',
         '4-Stationary object alert', '5-ACC Mode 6', '6-ESP', '7-Distance alert',
         '8-Sensor blocked', '9-UMO candidate qualified', '10-Unclassified',
         '11-Fault', '12-Message does not exists', '13-LDW', '14-TSR warning'],
    ),
    'AEBS cascade phase': (
        True,
        ['warning', 'partial\n braking', 'emergency\n braking', 'in-crash\n braking',
         'pre-crash\n intervention', 'full\n cascade'],
    ),
    'AEBS Usecase': (
        True,
        ['AEBS Usecase eval'],
    ),
    'Trailer': (
        True,
        ['WL active', 'ABS_and_RSP active', 'p21_or_p22_diff.', 'no braking event', 'wheelspeed suspicious',
         'ilvl_out_of_driving_level', 'RSP_Active', 'VrefFilter>2100AND(RSPStep1Enable=0ORRSPStep2=0)',
         'ABS(AyFilt)>2500', 'ABS(AyCalc)>2000', 'delta(AyLimLeft)<>0', 'delta(AyLimRight)<>0',
         'delta(AyOffset)<>0', 'RSPTestedLifted=1', 'RSPLowMuSide>0', 'RSPVDCActive=1', 'RSPPlauError>0',
         'Rsptestactive=1', 'RspStep1Active=1', 'RspStep2Active=1', 'NearlyRSP=1',
         'RSPtUnstabA>=0', 'RSPtUnstabB>=0', 'RSPtUnstabC>=0', 'RSPtUnstabD>=0', 'RSPtUnstabE>=0', 'RSPtUnstabF>=0']
    ),
    'LDWS system status': (
        True,
        ['warning', 'ready', 'deactivate by driver'],
    ),
    'AEBS resim phase': (
        True,
        ['warning,\n stationary target', "partial braking,\n stationary target",
         "emergency braking,\n stationary target",
         "warning,\n moving target", "partial braking,\n moving target", "emergency braking,\n moving target"],
    ),
    'Delta report data': (
        True,
        ["Measurement\n Event", "Resimulation\n Event", "Common\n Event", "Baseline", "Retest"],
    ),
    'Function deactivation check': (
        True,
        ["Function Deactivated"],
    ),
    'FCW cascade phase': (
        True,
        ['preliminary warning', 'collision warning'],
    ),
    'sensor check': (
        True,
        ['valid', 'invalid']
    ),
    'AEBS event rating scale': (
        True,
        ['1-False alarm', '2-Questionable false alarm', '3-Questionable',
         '4-Questionable mitigation', '5-Mitigation']
    ),
    'event severity': (
        True,
        ['1-False alarm', '2-Questionable false alarm', '3-Questionable',
         '4-Questionable justified', '5-Justified']
    ),
    'resim event severity': (
        True,
        ['1-False_alarm', '2-Questionable_false_alarm', '3-Questionable',
         '4-Questionable_justified', '5-Justified']
    ),
    'resim useCaseMode severity': (
        True,
        ['1-Passed', '2-Passed_with_restrictions', '3-Failed', '4-Canceled']
    ),
    'cm system status': (
        True,
        ['0-Not allowed', '1-Allowed', '2-Warning', '3-Braking', '4-Waiting'],
    ),
    'track selection': (
        False,
        ['AEB', 'ACC'],
    ),
    'improvable': (
        True,
        ['yes', 'no', 'maybe', 'no (would be worse)', 'improvement not needed'],
    ),
    'KB AEBS suppression': (
        False,
        ['cm_allow_entry_global_conditions', 'cm_cancel_global_conditions',
         'cmb_allow_entry', 'cmb_cancel', 'cw_allow_entry', 'cw_cancel',
         'direction indicator', 'steering wheel', 'extrapolated track',
         'smaller lane width'],
    ),
    'KB AEBS suppression phase': (
        True,
        ['cancelled', 'warning', 'partial braking', 'emergency braking'],
    ),
    'TRW active fault': (  # deprecated; use 'FLR21 fault' instead
        True,
        trw_active_faults.trw_active_faults,
    ),
    'FLR21 fault': (
        False,
        trw_active_faults.dtc2label.values() + ['UNKNOWN'],
    ),
    'FLR21 antenna type': (
        False,
        ['unknown (0)', 'IVQ830', 'IVQ831', 'unknown (3)'],
    ),
    'camera status': (
        True,
        list(OrderedSet(flc20_sensor_status_dict.itervalues())),
    ),
    'AEBS state': (
        True,
        list(OrderedSet(aebs_state_dict.itervalues())),
    ),
    'PAEBS state': (
        True,
        list(OrderedSet(paebs_state_dict.itervalues())),
    ),
    'FLC25 LDWS': (
        True,
        ['FLC25 ldws left', 'FLC25 ldws right', 'FLC20 ldws left', 'FLC20 ldws right', 'Not Available', 'Available',
         'LeftLaneNotAvailable', 'RightLaneNotAvailable', 'ConstructionSiteAvailable', 'LeftLaneDepartureWarning',
         'RightLaneDepartureWarning','LaneWidthJump']
    ),
    'FLC25 LDWS state': (
        True,
        ['not ready', 'temp. not avail', 'deact. by driver', 'ready', 'driver override', 'warning', 'error']
    ),
    'FLC20 LDWS state': (
        True,
        ['not ready', 'temp. not avail', 'deact. by driver', 'ready', 'driver override', 'warning', 'error']
    ),
    'FLC25 Sensor state': (
        True,
        ['CAMERA DEGRADED', 'RADAR DEGRADED']
    ),
    'FLC25 Blockage state': (
        True,
        ['CB_UNKNOWN_STATUS', 'CB_NO_BLOCKAGE', 'CB_CONDENSATION', 'CB_TOP_PART_BLOCKAGE', 'CB_BOTTOM_PART_BLOCKAGE',
         'CB_BLOCKAGE', 'CB_LEFT_PART_BLOCKAGE', 'CB_RIGHT_PART_BLOCKAGE']
    ),
    'FLC25 CEM state': (
        True,
        [
            'CEMState_FAILURE'
        ]
    ),
    'FLC25 keep alive': (
        True,
        [
            'KeepAlive_Left', 'KeepAlive_Right'
        ]
    ),
    'FLC25 eSign Status': (
        True,
        [
            'TPF AL_SIG_STATE_INIT', 'TPF AL_SIG_STATE_INVALID', 'LD AL_SIG_STATE_INIT', 'LD AL_SIG_STATE_INVALID',
        ]
    ),
    'FLC25 lane state': (
        True,
        list(OrderedSet(lane_quality_dict.itervalues())),
    ),
    'FLC25 fused state': (
        True,
        list(OrderedSet(fused_dict.itervalues())),
    ),
    'FCW state': (
        True,
        list(OrderedSet(fcw_state_dict.itervalues())),
    ),
    'LDWS state': (
        True,
        list(OrderedSet(ldws_state_dict.itervalues())),
    ),
    'result': (
        False,
        ['passed', 'failed', 'inconclusive']
    ),
    'fusion dropout cause': (
        False,
        ['camera track loss', 'dx mismatch', 'angle mismatch', 'vx mismatch',
         'occlusion', 'ambiguous situation', 'extrapolated radar track', 'unknown',
         'camera status']
    ),
    'overtaking type': (
        True,
        ['far', 'near', 'left line', 'steering wheel']
    ),
    'overtake information': (
        True,
        ['overtake', 'not enough st. wh.', 'long check', 'timeout']
    ),
    'line type': (
        True,
        list(OrderedSet(line_type_dict.itervalues())),
    ),
    'Time': (
        True,
        ['Day', 'Twilight', 'Night']
    ),
    'Road Type': (
        True,
        ['City', 'Country Road', 'Motorway']
    ),
    'Vehicle Headlamp': (
        True,
        ['Halogen', 'LED', 'Xenon', 'Laser']
    ),
    'Weather Conditions': (
        True,
        ['Clear', 'Cloudy', 'Rain', 'Snow fall', 'Fog', 'Hail', 'Heavy Sun Glaring']
    ),
    'CAN_Signal_group': (
        True,
        ['TSR_SpeedLimit1_E8_sE8', 'TSSDetectedValue', '999']
    ),
    'TSR Remark': (
        True,
        ['Duplicate True Positive']
    ),
    'Road edge': (
        True,
        ['Flat', 'Continuous Elevated', 'Discrete Elevated', 'Trench or Cliff', 'Curbstone']
    ),
    'Street Objects': (
        True,
        ['Bad road conditions', 'Fishbone lane marker', 'Zigzag lane  marker', 'Street Island']
    ),
    'Object on side of Road': (
        True,
        ['Tunnel', 'Under Bridge']
    ),
    'Traffic Event': (
        True,
        ['Construction', 'Traffic jam', 'Country Border', 'Overtaking scenario', 'Roundabout',
         'Interesting traffic situation']
    ),
    'Moving Objects': (
        True,
        ['Crossing scenarios', 'Children', 'Unusual shaped vehicle', 'Vehicle transport', 'Tram', 'Unusual taillights',
         'Hazard lights', 'Animals', 'Motorbike', 'Bicycle']
    ),
    'Country Code': (
        True,
        ['DEU', 'AUT', 'BEL', 'HUN', 'LUX', 'NLD', 'USA', 'CAN', 'KOR', 'CHN', 'JPN', 'GBR', 'IRL', 'FRA', 'ITA', 'ESP',
         'PRT', 'MLT', 'CYP', 'CZE', 'POL', 'ROU', 'BGR', 'SWE']
    ),
    'ACC event': (
        True,
        ['Red Dirk Activate', 'Green Dirk Activate', 'Economic Driving', 'Strong Brake Request', 'ACC brake overheat',
         'Unexpected strong brake', 'ACC shutdown', 'ACC jerk', 'Take Over Request',
         'ACC Overreaction', 'Brakepedal Override', 'Torque Limit Above Threshold', 'ACC Target Present',
         'Pedestrian Go Suppression Target Present', 'Pedestrian Stop Intervention', 'High Speed Cut-In']
    ),
    'ACTL event': (
        True,
        ['Not_Equal_To_Normal']
    ),
    'DM1 event': (
        True,
        ['DM1 AmberWarningLamp', 'DM1 FailureModeIdentifier', 'FLR25 DTC active', 'FLC25 DTC active']
    ),
    'DTC event': (
        True,
        ['DM1 AmberWarningLamp', 'DM1 FailureModeIdentifier', 'FLR25 DTC active', 'FLC25 DTC active']
    ),
    'TPF TRW Compare': (
        True,
        ['MissingObjectsInTPF', 'False Prediction']
    ),
    'PAEBS algo': (
        True,
        ['FLC25 Warning'],
    ),
    'PAEBS problem': (
        False,
        ['warning w/o object']),
    'PAEBS cascade phase': (
        True,
        ['warning', 'partial braking', 'emergency braking', 'in-crash braking',
         'pre-crash intervention', 'full cascade'],
    ),
    'PAEBS resim phase': (
        True,
        ['warning,\n crossing', 'partial braking,\n crossing', 'emergency braking,\n crossing',
         'warning,\n not crossing', 'partial braking,\n not crossing', 'emergency braking,\n not crossing'],
    ),
    'PAEBS event cause': (
        True,
        paebs_warning_causes,
    ),
    'PAEBS moving state': (
        False,
        ['pedestrian crossing',
         'pedestrian not crossing',
         'bicyclist crossing',
         'bicyclist not crossing',
         'undefined',
         ],
    ),
    'PAEBS source': (
        False,
        ['Fused',
         'Camera only',
         'Radar only',
         'Unknown',
         'N/A',
         ],
    ),
    'TSR event': (
        True,
        ['TSR event'],
    ),
    'Sys_Bitfield event': (
        True,
        ['sys_bitfield_event'],
    ),
    'TSR verdict': (
        True,
        ['False Positive Type 1', 'False Positive Type 2', 'False Positive Type 3', "False Negative", "True Negative",
         "True Positive"],
    ),
    'YACA Verdict': (
        True,
        ['PASS', 'FAIL'],
    ),
    'Status': (
        True,
        ['new'],
    ),
    'Trigger': (
        True,
        ['COLLISION_WARNING', 'AEB_PARTIAL_BRAKING', 'AEB_WARNING'],
    ),
    'BSIS Event': (
        True,
        ['BSM_ACTIVE', 'VEHICLE_DETECTED_ON_RIGHT', 'SRR_WARNING_FRONT', 'SRR_WARNING_RIGHT', 'Information Warning',
         'VDP Warning','Collision Warning','NA Status','Error State', 'LCDA Information Warning',
         'LCDA VDP Warning','LCDA Collision Warning','LCDA NA Status','LCDA Error State'],
    ),
}
""":type: dict
{ labelgroup<str> : (exclusive<bool>, labels<list>) }"""
