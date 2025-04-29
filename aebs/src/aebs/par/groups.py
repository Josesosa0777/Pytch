import grouptypes as gtps
from config.parameter import GroupParams
from datavis.GroupParam import cGroupParam as Param

Not_guardrail = Param(gtps.NOT_GUARDRAIL, "U", False, False)
mk = "9"
sk = "0"
fill_prj = "@aebs.fill"

Groups = GroupParams(
    {
        "fillLRR3_FUS%s"
        % fill_prj: {
            "LRR3_FUS": Param(gtps.LRR3_FUS, "1", False, False),
            "moving": Param(gtps.LRR3_FUS_MOV, mk, False, False),
            "stationary": Param(gtps.LRR3_FUS_STAT, sk, False, False),
        },
        "fillCVR3_ATS%s"
        % fill_prj: {
            "CVR3_ATS": Param(gtps.CVR3_ATS, "A", False, False),
            "moving": Param(gtps.CVR3_ATS_MOV, mk, False, False),
            "stationary": Param(gtps.CVR3_ATS_STAT, sk, False, False),
        },
        "fillAC100%s"
        % fill_prj: {
            "AC100": Param(gtps.AC100, "2", False, False),
            "moving": Param(gtps.AC100_MOV, mk, False, False),
            "stationary": Param(gtps.AC100_STAT, sk, False, False),
        },
        "fillAC100_POS%s"
        % fill_prj: {
            "AC100_POS": Param(gtps.AC100_POS, "J", False, False),
        },
        "fillAC100_CW%s"
        % fill_prj: {
            "AC100_CW": Param(gtps.AC100_W, "D", False, False),
        },
        "fillAC100_TargetFlags%s"
        % fill_prj: {
            "AC100_TF": Param(gtps.AC100_TARGET_FLAG, "T", False, False),
        },
        "fillAC100_TargetStatus%s"
        % fill_prj: {
            "AC100_TS": Param(gtps.AC100_TARGET_STATUS, "S", False, False),
        },
        "fillAC100_TrackingFlag%s"
        % fill_prj: {
            "AC100_TRF": Param(gtps.AC100_TRACKING_FLAG, "R", False, False),
        },
        "fillSCam%s"
        % fill_prj: {
            "S-Cam": Param(gtps.SCAM, "C", False, False),
        },
        "fillESR%s"
        % fill_prj: {
            "ESR": Param(gtps.ESR, "3", False, False),
            "moving": Param(gtps.ESR_MOV, mk, False, False),
            "stationary": Param(gtps.ESR_STAT, sk, False, False),
        },
        "fillIBEO%s"
        % fill_prj: {
            "IBEO": Param(gtps.IBEO, "4", False, False),
            "moving": Param(gtps.IBEO_MOV, mk, False, False),
            "stationary": Param(gtps.IBEO_STAT, sk, False, False),
        },
        "fillVFP%s"
        % fill_prj: {
            "VFP": Param(gtps.VFP, "5", False, False),
            "moving": Param(gtps.VFP_MOV, mk, False, False),
            "stationary": Param(gtps.VFP_STAT, sk, False, False),
        },
        "fillIteris%s"
        % fill_prj: {
            "Iteris": Param(gtps.ITERIS, "6", False, False),
            "moving": Param(gtps.ITERIS, mk, False, False),
        },
        "fillMobilEye%s"
        % fill_prj: {
            "MobilEye": Param(gtps.MOBILEYE, "7", False, False),
            "moving": Param(gtps.MOBILEYE, mk, False, False),
        },
        "fillLRR3_SIT-LRR3%s"
        % fill_prj: {
            "LRR3_SIT": Param(gtps.LRR3_SIT, "N", False, False),
            "moving": Param(gtps.LRR3_SIT_MOV, mk, False, False),
            "stationary": Param(gtps.LRR3_SIT_STAT, sk, False, False),
        },
        "fillLRR3_ASF%s"
        % fill_prj: {
            "LRR3_ASF": Param(gtps.LRR3_ASF, "M", False, False),
        },
        "fillCVR3_LOC%s"
        % fill_prj: {
            "CVR3_LOC": Param(gtps.CVR3_LOC, "X", False, False),
            "CVR3_LOC_invalid": Param(gtps.CVR3_LOC_INVALID, "Q", False, False),
        },
        "fillCVR3_OHL%s"
        % fill_prj: {
            "CVR3_OHL": Param(gtps.CVR3_OHL, "O", False, False),
            "moving": Param(gtps.CVR3_OHL_MOV, mk, False, False),
            "stationary": Param(gtps.CVR3_OHL_STAT, sk, False, False),
        },
        "fillCVR3_POS%s"
        % fill_prj: {
            "CVR3_POS": Param(gtps.CVR3_POS, "P", False, False),
            "moving": Param(gtps.CVR3_POS_MOV, mk, False, False),
            "stationary": Param(gtps.CVR3_POS_STAT, sk, False, False),
        },
        "fillLRR3_POS%s"
        % fill_prj: {
            "LRR3_POS": Param(gtps.LRR3_POS, "B", False, False),
            "moving": Param(gtps.LRR3_POS_MOV, mk, False, False),
            "stationary": Param(gtps.LRR3_POS_STAT, sk, False, False),
        },
        "fillLRR3_OHL%s"
        % fill_prj: {
            "LRR3_OHL": Param(gtps.LRR3_OHL, "K", False, False),
            "moving": Param(gtps.LRR3_OHL_MOV, mk, False, False),
            "stationary": Param(gtps.LRR3_OHL_STAT, sk, False, False),
        },
        "fillLRR3_SIT-CVR3%s"
        % fill_prj: {
            "CVR3_SIT": Param(gtps.CVR3_SIT, "H", False, False),
            "moving": Param(gtps.CVR3_SIT_MOV, mk, False, False),
            "stationary": Param(gtps.CVR3_SIT_STAT, sk, False, False),
        },
        "fillLRR3_ATS%s"
        % fill_prj: {
            "LRR3_ATS": Param(gtps.LRR3_ATS, "8", False, False),
            "moving": Param(gtps.LRR3_ATS_MOV, mk, False, False),
            "stationary": Param(gtps.LRR3_ATS_STAT, sk, False, False),
        },
        "fillCVR3_FUS%s"
        % fill_prj: {
            "CVR3 FUS fused": Param(gtps.CVR3_FUS_FUSED, "F", False, False),
            "moving": Param(gtps.CVR3_FUS_FUSED_MOV, mk, False, False),
            "stationary": Param(gtps.CVR3_FUS_FUSED_STAT, sk, False, False),
            "CVR3 FUS radar-only": Param(gtps.CVR3_FUS_RADAR_ONLY, "L", False, False),
            "CVR3 FUS video-only": Param(gtps.CVR3_FUS_VIDEO_ONLY, "G", False, False),
        },
        "fillCVR3_FUS_VID%s"
        % fill_prj: {
            "CVR3_FUS_VID": Param(gtps.CVR3_FUS_VID, "U", False, False),
        },
        "fillLRR3_LOC%s"
        % fill_prj: {
            "LRR3_LOC": Param(gtps.LRR3_LOC, "Y", False, False),
            "LRR3_LOC_invalid": Param(gtps.LRR3_LOC_INVALID, "W", False, False),
        },
        "fillSDF_LRR3_CVR3_OHL%s"
        % fill_prj: {
            "SDF_LRR3_CVR3_OHL": Param(gtps.SDF_LRR3_CVR3_OHL, "E", False, False),
        },
        "fillsdf_cvr3_scam_cipv%s"
        % fill_prj: {
            "SDF_CVR3_SCam_CIPV": Param(gtps.SDF_CVR3_SCAM_CIPV, "Z", False, False),
        },
        "fillsdf_cvr3_scam%s"
        % fill_prj: {
            "SDF_CVR3_SCAM": Param(gtps.SDF_CVR3_SCAM, "V", False, False),
        },
        "fillCVR3_OHL_Guardrail%s"
        % fill_prj: {
            "CVR3_OHL_Guardrail": Param(gtps.OHL_GUARDRAILS, "L", False, True),
            "Not_guardrail": Not_guardrail,
        },
        "fillCVR3_FUS_Guardrail%s"
        % fill_prj: {
            "CVR3_FUS_Guardrail": Param(gtps.FUS_GUARDRAILS, "G", False, True),
            "Not_guardrail": Not_guardrail,
        },
        "fillMBL2_Target%s"
        % fill_prj: {
            "MBL2 targets": Param(gtps.MBL2_TARGET, "B", False, False),
        },
        "fillMBL2_Track%s"
        % fill_prj: {
            "MBL2 tracks": Param(gtps.MBL2_TRACK, "N", False, False),
        },
        "fillMB79_Target-FRONT_BUMPER%s"
        % fill_prj: {
            "MB79 targets": Param(gtps.MB79_TARGET, "B", False, False),
        },
        "fillMB79_Target-FRONT_RIGHT_CORNER%s"
        % fill_prj: {
            "MB79 targets": Param(gtps.MB79_TARGET, "B", False, False),
        },
        "fillMB79_KB_Target-FRONT_BUMPER%s"
        % fill_prj: {
            "KB targets": Param(gtps.KB_TARGET, "D", False, False),
        },
        "fillMB79_KB_Target-FRONT_RIGHT_CORNER%s"
        % fill_prj: {
            "KB targets": Param(gtps.KB_TARGET, "D", False, False),
        },
        "fillMB79_KB_Detection_Repr-FRONT_BUMPER%s"
        % fill_prj: {
            "KB repr detection": Param(gtps.MB79_DET_REPR, "C", False, False),
        },
        "fillMB79_KB_Detection_Repr-FRONT_RIGHT_CORNER%s"
        % fill_prj: {
            "KB repr detection": Param(gtps.MB79_DET_REPR, "C", False, False),
        },
        "fillMB79_Track-FRONT_BUMPER%s"
        % fill_prj: {
            "MB79 tracks": Param(gtps.MB79_TRACK, "A", False, False),
            "moving": Param(gtps.MB79_TRACK_MOV, mk, False, False),
            "stationary": Param(gtps.MB79_TRACK_STAT, sk, False, False),
        },
        "fillMB79_Track-FRONT_RIGHT_CORNER%s"
        % fill_prj: {
            "MB79 tracks": Param(gtps.MB79_TRACK, "A", False, False),
            "moving": Param(gtps.MB79_TRACK_MOV, mk, False, False),
            "stationary": Param(gtps.MB79_TRACK_STAT, sk, False, False),
        },
        "fillMB79_KB_Track-FRONT_BUMPER%s"
        % fill_prj: {
            "KB tracks": Param(gtps.KB_TRACK, "K", False, False),
            "moving": Param(gtps.KB_TRACK_MOV, mk, False, False),
            "stationary": Param(gtps.KB_TRACK_STAT, sk, False, False),
            "stopped": Param(gtps.KB_TRACK_STOP, "2", False, False),
            "unknown": Param(gtps.KB_TRACK_UNK, "3", False, False),
        },
        "fillMB79_KB_Track-FRONT_RIGHT_CORNER%s"
        % fill_prj: {
            "KB tracks": Param(gtps.KB_TRACK, "K", False, False),
            "moving": Param(gtps.KB_TRACK_MOV, mk, False, False),
            "stationary": Param(gtps.KB_TRACK_STAT, sk, False, False),
            "stopped": Param(gtps.KB_TRACK_STOP, "2", False, False),
            "unknown": Param(gtps.KB_TRACK_UNK, "3", False, False),
        },
        "fillMB79_KB_Warning_Track-FRONT_BUMPER%s"
        % fill_prj: {
            "MB79_KB_WARNING_TRACK": Param(
                gtps.MB79_KB_WARNING_TRACK, "4", False, False
            ),
        },
        "fillMB79_KB_Warning_Track-FRONT_RIGHT_CORNER%s"
        % fill_prj: {
            "MB79_KB_WARNING_TRACK": Param(
                gtps.MB79_KB_WARNING_TRACK, "4", False, False
            ),
        },
        "fillMB79_KB_Info_Area%s"
        % fill_prj: {"KB Info Area": Param(gtps.KB_INFO_AREA, "5", False, False)},
        "fillMB79_KB_Hazard_Area%s"
        % fill_prj: {"KB Hazard Area": Param(gtps.KB_HAZARD_AREA, "6", False, False)},
        "fillMB79_KB_Clusters%s"
        % fill_prj: {"KB Clusters": Param(gtps.KB_CLUSTERS, "7", False, False)},
        "fillFurukawa_Targets%s"
        % fill_prj: {
            "Furukawa Targets": Param(gtps.FURUKAWA_TARGETS, "8", False, False)
        },
        "fillContiARS430%s"
        % fill_prj: {
            "ContiARS430": Param(gtps.CONTI_ARS430, "A", False, False),
            "moving": Param(gtps.CONTI_ARS430_MOVING, mk, False, False),
            "stopped": Param(gtps.CONTI_ARS430_STOPPED, "1", False, False),
            "stationary": Param(gtps.CONTI_ARS430_STAT, sk, False, False),
        },
        "fillContiSRR320%s"
        % fill_prj: {
            "ContiSRR320": Param(gtps.CONTI_SRR320, "C", False, False),
        },
        "fillContiARS430_AEBS%s"
        % fill_prj: {
            "Conti_AEBS": Param(gtps.CONTI_AEBS_WARNING, "B", False, False),
        },
        "fillContiARS440%s"
        % fill_prj: {
            "ContiARS440": Param(gtps.CONTI_ARS440, "S", False, False),
            "moving": Param(gtps.CONTI_ARS440_MOVING, mk, False, False),
            "stopped": Param(gtps.CONTI_ARS440_STOPPED, "3", False, False),
            "stationary": Param(gtps.CONTI_ARS440_STAT, sk, False, False),
        },
        "fillFLR20%s"
        % fill_prj: {
            "FLR20": Param(gtps.FLR20, "2", False, False),
            "moving": Param(gtps.FLR20_MOV, mk, False, False),
            "stationary": Param(gtps.FLR20_STAT, sk, False, False),
        },
        "fillFLR20_AEB%s"
        % fill_prj: {
            "FLR20_AEB": Param(gtps.FLR20_AEB, "3", False, False),
        },
        "fillFLR20_ACC%s"
        % fill_prj: {
            "FLR20_ACC": Param(gtps.FLR20_ACC, "4", False, False),
        },
        "fillFLR20_FUS%s"
        % fill_prj: {
            "FLR20_FUS": Param(gtps.FLR20_FUS, "5", False, False),
            "FLR20_FUSED": Param(gtps.FLR20_FUSED, "L", False, False),
            "FLR20_RADAR_ONLY": Param(gtps.FLR20_RADAR_ONLY, "G", False, False),
            "moving": Param(gtps.FLR20_FUS_MOV, mk, False, False),
            "stationary": Param(gtps.FLR20_FUS_STAT, sk, False, False),
        },
        "fillFLR20_Target%s"
        % fill_prj: {
            "FLR20_TARGET": Param(gtps.FLR20_TARGET, "6", False, False),
        },
        "fillFLC20%s"
        % fill_prj: {
            "FLC20": Param(gtps.FLC20, "C", False, False),
            "moving": Param(gtps.FLC20_MOV, mk, False, False),
            "stationary": Param(gtps.FLC20_STAT, sk, False, False),
        },
        "fillFLC25_CEM_TPF%s"
        % fill_prj: {
            "FLC25_CEM_TPF": Param(gtps.FLC25_CEM_TPF, "N", False, False),
            "moving": Param(gtps.FLC25_CEM_TPF_MOV, mk, False, False),
            "stationary": Param(gtps.FLC25_CEM_TPF_STAT, sk, False, False),
        },
        "fillFLC25_CEM_TPF_MG_AOA_ACC%s"
        % fill_prj: {
          "FLC25_CEM_TPF_MG_AOA_ACC": Param(gtps.FLC25_CEM_TPF_MG_AOA_ACC, "V", False, False),
          "moving"       : Param(gtps.FLC25_CEM_TPF_MG_AOA_ACC_MOV, mk, False, False),
          "stationary"   : Param(gtps.FLC25_CEM_TPF_MG_AOA_ACC_STAT, sk, False, False),
        },
        "fillFLC25_CAN%s"
        % fill_prj: {
            "FLC25_CAN": Param(gtps.FLC25_CAN, "P", False, False),
            "moving": Param(gtps.FLC25_CAN_MOV, mk, False, False),
            "stationary": Param(gtps.FLC25_CAN_STAT, sk, False, False),
        },
        "fillFLC25_ARS_FCU%s"
        % fill_prj: {
            "FLC25_ARS_FCU": Param(gtps.FLC25_ARS_FCU, "Z", False, False),
            "moving": Param(gtps.FLC25_ARS_FCU_MOV, mk, False, False),
            "stationary": Param(gtps.FLC25_ARS_FCU_STAT, sk, False, False),
        },
        "fillFLC25_ARS620%s"
        % fill_prj: {
            "FLC25_ARS620": Param(gtps.FLC25_ARS620, "Y", False, False),
            "moving": Param(gtps.FLC25_ARS620_MOV, mk, False, False),
            "stationary": Param(gtps.FLC25_ARS620_STAT, sk, False, False),
        },
        "fillFLC25_EM%s"
        % fill_prj: {
            "FLC25_EM": Param(gtps.FLC25_EM, "W", False, False),
            "moving": Param(gtps.FLC25_EM_MOV, mk, False, False),
            "stationary": Param(gtps.FLC25_EM_STAT, sk, False, False),
        },
        "fillFLC25_TSR%s"
        % fill_prj: {
            "FLC25_TSR": Param(gtps.FLC25_TSR, "T", False, False),
            "stationary": Param(gtps.FLC25_TSR_STAT, sk, False, False),
        },
        "fillFLC25_TSR_SHORTLISTED%s"
        % fill_prj: {
            "FLC25_TSR_SHORTLISTED": Param(
                gtps.FLC25_TSR_SHORTLISTED, "Q", False, False
            ),
            "stationary": Param(gtps.FLC25_TSR_STAT, sk, False, False),
        },
        "fillFLR20_AEBS_Warning-kb%s"
        % fill_prj: {
            "FLR20_AEBS_Warning-KB": Param(
                gtps.FLR20_AEBS_WARNING_KB, "Q", False, False
            ),
        },
        "fillFLR20_AEBS_Warning-trw%s"
        % fill_prj: {
            "FLR20_AEBS_Warning-TRW": Param(
                gtps.FLR20_AEBS_WARNING_TRW, "W", False, False
            ),
        },
        "fillFLR20_AEBS_Warning-flr20%s"
        % fill_prj: {
            "FLR20_AEBS_Warning-FLR20": Param(
                gtps.FLR20_AEBS_WARNING_FLR20, "E", False, False
            ),
        },
        "fillFLR20_AEBS_Warning-autobox%s"
        % fill_prj: {
            "FLR20_AEBS_Warning-AUTOBOX": Param(
                gtps.FLR20_AEBS_WARNING_AUTOBOX, "R", False, False
            ),
        },
        "fillFLR20_AEBS_Warning-sil%s"
        % fill_prj: {
            "FLR20_AEBS_Warning-SIL": Param(
                gtps.FLR20_AEBS_WARNING_SIL, "T", False, False
            ),
        },
        "fillVBOX_OBJ%s"
        % fill_prj: {
            "VBox Object": Param(gtps.VBOX_OBJ, "V", False, False),
        },
        "fillFLR25%s"
        % fill_prj: {
            "FLR25": Param(gtps.FLR25, "8", False, False),
            "moving": Param(gtps.FLR25_MOV, mk, False, False),
            "stopped": Param(gtps.FLR25_STOPPED, "7", False, False),
            "stationary": Param(gtps.FLR25_STAT, sk, False, False),
        },
        "fillFLR25_AEB%s"
        % fill_prj: {
            "FLR25_AEB": Param(gtps.FLR25_AEB, "3", False, False),
        },
        "fillFLR25_AEBS_RETEST_RESIM%s"
        % fill_prj: {
            "FLR25_AEB_RETEST_RESIM": Param(gtps.FLR25_AEB_RETEST_RESIM, "3", False, False),
        },
        "fillFLR25_AEBS_BASELINE_RESIM%s"
        % fill_prj: {
            "FLR25_AEB_BASELINE_RESIM": Param(gtps.FLR25_AEB_BASELINE_RESIM, "R", False, False),
        },
        "fillFLC25_AEBS_FIRST_OBJ%s"
        % fill_prj: {
            "FLC25_AEBS_FIRST_OBJ": Param(gtps.FLC25_AEBS_FIRST_OBJ, "3", False, False),
        },
       "fillFLC25_AEBS_SECOND_OBJ%s"
        % fill_prj: {
            "FLC25_AEBS_SECOND_OBJ": Param(gtps.FLC25_AEBS_SECOND_OBJ, "4", False, False),
        },
       "fillFLC25_AEBS_THIRD_OBJ%s"
        % fill_prj: {
            "FLC25_AEBS_THIRD_OBJ": Param(gtps.FLC25_AEBS_THIRD_OBJ, "5", False, False),
        },
        "fillFLC25_MLAEB_LEFT_FIRST_OBJ%s"
                % fill_prj: {
                    "FLC25_MLAEB_LEFT_FIRST_OBJ": Param(gtps.FLC25_MLAEB_LEFT_FIRST_OBJ, "6", False, False),
                },
        "fillFLC25_MLAEB_LEFT_SECOND_OBJ%s"
                % fill_prj: {
                    "FLC25_MLAEB_LEFT_SECOND_OBJ": Param(gtps.FLC25_MLAEB_LEFT_SECOND_OBJ, "7", False, False),
                },
        "fillFLC25_MLAEB_LEFT_THIRD_OBJ%s"
                % fill_prj: {
                    "FLC25_MLAEB_LEFT_THIRD_OBJ": Param(gtps.FLC25_MLAEB_LEFT_THIRD_OBJ, "8", False, False),
                },
        "fillFLC25_MLAEB_RIGHT_FIRST_OBJ%s"
                % fill_prj: {
                    "FLC25_MLAEB_RIGHT_FIRST_OBJ": Param(gtps.FLC25_MLAEB_RIGHT_FIRST_OBJ, "T", False, False),
                },
        "fillFLC25_MLAEB_RIGHT_SECOND_OBJ%s"
                % fill_prj: {
                    "FLC25_MLAEB_RIGHT_SECOND_OBJ": Param(gtps.FLC25_MLAEB_RIGHT_SECOND_OBJ, "S", False, False),
                },
        "fillFLC25_MLAEB_RIGHT_THIRD_OBJ%s"
                % fill_prj: {
                    "FLC25_MLAEB_RIGHT_THIRD_OBJ": Param(gtps.FLC25_MLAEB_RIGHT_THIRD_OBJ, "R", False, False),
                },
        "fillFLR25_AEBS_RESIM%s"
        % fill_prj: {
            "FLR25_AEB_RESIM": Param(gtps.FLR25_AEB_RESIM, "R", False, False),
        },
        "fillFLR25_ACC_PED%s"
        % fill_prj: {
            "FLR25_ACC_PED": Param(gtps.FLR25_ACC_PED, "7", False, False),
        },
        "fillFLR25_ACC_PED_STOP%s"
        % fill_prj: {
            "FLR25_ACC_PED_STOP": Param(gtps.FLR25_ACC_PED_STOP, "7", False, False),
        },
        "fillFLR25_ACC%s"
        % fill_prj: {
            "FLR25_ACC": Param(gtps.FLR25_ACC, "6", False, False),
            "moving": Param(gtps.FLR25_ACC_MOV, mk, False, False),
            "stopped": Param(gtps.FLR25_ACC_STOPPED, "7", False, False),
            "stationary": Param(gtps.FLR25_ACC_STAT, sk, False, False),
        },
        "fillFLR25_ACC_GO_SUPP_PED%s"
        % fill_prj: {
            "FLR25_ACC_GO_SUPP_PED": Param(
                gtps.FLR25_ACC_GO_SUPP_PED, "8", False, False
            ),
            "moving": Param(gtps.FLR25_ACC_GO_SUPP_PED_MOV, mk, False, False),
            "stopped": Param(gtps.FLR25_ACC_GO_SUPP_PED_STOPPED, "7", False, False),
            "stationary": Param(gtps.FLR25_ACC_GO_SUPP_PED_STAT, sk, False, False),
        },
        "fillGROUND_TRUTH%s"
        % fill_prj: {
            "GT_FREEBOARD": Param(gtps.GT_FREEBOARD, "Y", False, False),
        },
        "fillGROUND_TRUTH_DELTA%s"
        % fill_prj: {
            "GT_DELTA": Param(gtps.GT_DELTA, "J", False, False),
        },
        "fillFLC25_PAEBS_AOAOUTPUT%s"
        % fill_prj: {
            "FLC25_PAEBS_AOAOUTPUT": Param(gtps.FLC25_PAEBS_AOAOUTPUT, "A", False, False),
            "moving": Param(gtps.FLC25_PAEBS_AOAOUTPUT_MOV, mk, False, False),
            "stationary": Param(gtps.FLC25_PAEBS_AOAOUTPUT_STAT, sk, False, False),
        },
        "fillFLC25_PAEBS_AOAOUTPUT_RESIM%s"
        % fill_prj: {
            "FLC25_PAEBS_AOAOUTPUT_RESIM": Param(gtps.FLC25_PAEBS_AOAOUTPUT_RESIM, "Y", False, False),
            "moving": Param(gtps.FLC25_PAEBS_AOAOUTPUT_MOV_RESIM, mk, False, False),
            "stationary": Param(gtps.FLC25_PAEBS_AOAOUTPUT_STAT_RESIM, sk, False, False),
        },
        "fillFLC25_PAEBS_DEBUG%s"
        % fill_prj: {
            "FLC25_PAEBS_DEBUG": Param(gtps.FLC25_PAEBS_DEBUG, "C", False, False),
            # "crossing": Param(gtps.FLC25_PAEBS_DEBUG_PED_CROSS.union(gtps.FLC25_PAEBS_DEBUG_BIC_CROSS), mk, False, False),
            # "not crossing": Param(gtps.FLC25_PAEBS_DEBUG_PED_NOT_CROSS.union(gtps.FLC25_PAEBS_DEBUG_BIC_NOT_CROSS), sk, False, False),
            # "undefined": Param(gtps.FLC25_PAEBS_DEBUG_UNDEFINED, "W", False, False),
        },
        "fillFLC25_PAEBS_LAUSCH%s"
        % fill_prj: {
            "FLC25_PAEBS_LAUSCH": Param(gtps.FLC25_PAEBS_LAUSCH, "V", False, False),
        },
        "fillFLC25_PAEBS_CAN%s"
        % fill_prj: {
            "FLC25_PAEBS_CAN": Param(gtps.FLC25_PAEBS_CAN, "B", False, False),
            "moving": Param(gtps.FLC25_PAEBS_CAN_MOV, mk, False, False),
            "stationary": Param(gtps.FLC25_PAEBS_CAN_STAT, sk, False, False),
        },
        "fillFLC25_AOA_AEBS%s"
        % fill_prj: {
            "FLC25_AOA_AEBS": Param(gtps.FLC25_AOA_AEBS, "X", False, False),
            "moving": Param(gtps.FLC25_AOA_AEBS_MOV, mk, False, False),
            "stationary": Param(gtps.FLC25_AOA_AEBS_STAT, sk, False, False),
        },
        "fillFLC25_AOA_ACC%s"
        % fill_prj: {
            "FLC25_AOA_ACC": Param(gtps.FLC25_AOA_ACC, "Y", False, False),
            "moving": Param(gtps.FLC25_AOA_ACC_MOV, mk, False, False),
            "stationary": Param(gtps.FLC25_AOA_ACC_STAT, sk, False, False),
        },
        "fillSLR25_RFB%s"
        % fill_prj: {
            "SLR25_RFB": Param(gtps.SLR25_RFB, "I", False, False),
            "moving"       : Param(gtps.SLR25_RFB_MOV, mk, False, False),
            "stationary"   : Param(gtps.SLR25_RFB_STAT, sk, False, False),
        },
        "fillSLR25_RFF%s"
        % fill_prj: {
            "SLR25_RFF": Param(gtps.SLR25_RFF, "Y", False, False),
            "moving"       : Param(gtps.SLR25_RFF_MOV, mk, False, False),
            "stationary"   : Param(gtps.SLR25_RFF_STAT, sk, False, False),
        },
        "fillSLR25_Front%s"
        % fill_prj: {
            "SLR25_Front": Param(gtps.SLR25_Front, "J", False, False),
            "moving"       : Param(gtps.SLR25_Front_MOV, mk, False, False),
            "stationary"   : Param(gtps.SLR25_Front_STAT, sk, False, False),
        },
    }
)
"""type : GroupParams
{StatusName<str>: {GroupName<str> : GroupParam<Param>}, }"""
