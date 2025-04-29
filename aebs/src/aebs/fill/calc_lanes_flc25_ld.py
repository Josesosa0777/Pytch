# -*- dataeval: init -*-

import copy
import logging

import interface
from primitives.lane import LaneData, PolyClothoid, VideoLineProp
from pyutils.cache_manager import get_modules_cache, store_modules_cache

logger = logging.getLogger('calc_lanes_flc25_abd')
signal_group = [
    {
        "ego_left_clothoidNear_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_offset"),
        "ego_left_clothoidNear_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_yawAngle"),
        "ego_left_clothoidNear_curvature": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_curvature"),
        "ego_left_clothoidNear_curvatureRate": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_curvatureRate"),
        "ego_left_clothoidNear_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_validTo"),
        "ego_left_clothoidFar_curvature": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidFar_curvature"),
        "ego_left_clothoidFar_curvatureRate": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidFar_curvatureRate"),
        "ego_left_clothoidFar_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidFar_validTo"),
        "ego_left_clothoidFar_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidFar_offset"),
        "ego_left_clothoidFar_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidFar_yawAngle"),
        "ego_left_available": ("LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_available"),
        "ego_right_clothoidNear_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_offset"),
        "ego_right_clothoidNear_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_yawAngle"),
        "ego_right_clothoidNear_curvature": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_curvature"),
        "ego_right_clothoidNear_curvatureRate": ("LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_curvatureRate"),
        "ego_right_clothoidNear_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_validTo"),
        "ego_right_clothoidFar_curvature": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidFar_curvature"),
        "ego_right_clothoidFar_curvatureRate": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidFar_curvatureRate"),
        "ego_right_clothoidFar_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidFar_validTo"),
        "ego_right_clothoidFar_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidFar_offset"),
        "ego_right_clothoidFar_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidFar_yawAngle"),
        "ego_right_available": ("LdOutput",
                                "MFC5xx_Device_LD_LdOutput_road_ego_right_available"),
        "leftI0I_left_clothoidNear_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_left_clothoidNear_offset"),
        "leftI0I_left_clothoidNear_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_left_clothoidNear_yawAngle"),
        "leftI0I_left_clothoidNear_curvature": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_left_clothoidNear_curvature"),
        "leftI0I_left_clothoidNear_curvatureRate": ("LdOutput",
                                                    "MFC5xx_Device_LD_LdOutput_road_leftI0I_left_clothoidNear_curvatureRate"),
        "leftI0I_left_clothoidNear_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_left_clothoidNear_validTo"),
        "leftI0I_left_clothoidFar_curvature": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_left_clothoidFar_curvature"),
        "leftI0I_left_clothoidFar_curvatureRate": ("LdOutput",
                                                   "MFC5xx_Device_LD_LdOutput_road_leftI0I_left_clothoidFar_curvatureRate"),
        "leftI0I_left_clothoidFar_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_left_clothoidFar_validTo"),
        "leftI0I_left_clothoidFar_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_left_clothoidFar_offset"),
        "leftI0I_left_clothoidFar_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_left_clothoidFar_yawAngle"),
        "leftI0I_left_available": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_left_available"),
        "leftI0I_right_clothoidNear_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_right_clothoidNear_offset"),
        "leftI0I_right_clothoidNear_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_right_clothoidNear_yawAngle"),
        "leftI0I_right_clothoidNear_curvature": ("LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_leftI0I_right_clothoidNear_curvature"),
        "leftI0I_right_clothoidNear_curvatureRate": ("LdOutput",
                                                     "MFC5xx_Device_LD_LdOutput_road_leftI0I_right_clothoidNear_curvatureRate"),
        "leftI0I_right_clothoidNear_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_right_clothoidNear_validTo"),
        "leftI0I_right_clothoidFar_curvature": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_right_clothoidFar_curvature"),
        "leftI0I_right_clothoidFar_curvatureRate": ("LdOutput",
                                                    "MFC5xx_Device_LD_LdOutput_road_leftI0I_right_clothoidFar_curvatureRate"),
        "leftI0I_right_clothoidFar_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_right_clothoidFar_validTo"),
        "leftI0I_right_clothoidFar_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_right_clothoidFar_offset"),
        "leftI0I_right_clothoidFar_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_right_clothoidFar_yawAngle"),
        "leftI0I_right_available": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_right_available"),
        "leftI1I_left_clothoidNear_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI1I_left_clothoidNear_offset"),
        "leftI1I_left_clothoidNear_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI1I_left_clothoidNear_yawAngle"),
        "leftI1I_left_clothoidNear_curvature": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI1I_left_clothoidNear_curvature"),
        "leftI1I_left_clothoidNear_curvatureRate": ("LdOutput",
                                                    "MFC5xx_Device_LD_LdOutput_road_leftI1I_left_clothoidNear_curvatureRate"),
        "leftI1I_left_clothoidNear_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI1I_left_clothoidNear_validTo"),
        "leftI1I_left_clothoidFar_curvature": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI1I_left_clothoidFar_curvature"),
        "leftI1I_left_clothoidFar_curvatureRate": ("LdOutput",
                                                   "MFC5xx_Device_LD_LdOutput_road_leftI1I_left_clothoidFar_curvatureRate"),
        "leftI1I_left_clothoidFar_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI1I_left_clothoidFar_validTo"),
        "leftI1I_left_clothoidFar_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI1I_left_clothoidFar_offset"),
        "leftI1I_left_clothoidFar_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI1I_left_clothoidFar_yawAngle"),
        "leftI1I_left_available": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI1I_left_available"),
        "leftI1I_right_clothoidNear_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI1I_right_clothoidNear_offset"),
        "leftI1I_right_clothoidNear_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI1I_right_clothoidNear_yawAngle"),
        "leftI1I_right_clothoidNear_curvature": ("LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_leftI1I_right_clothoidNear_curvature"),
        "leftI1I_right_clothoidNear_curvatureRate": ("LdOutput",
                                                     "MFC5xx_Device_LD_LdOutput_road_leftI1I_right_clothoidNear_curvatureRate"),
        "leftI1I_right_clothoidNear_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI1I_right_clothoidNear_validTo"),
        "leftI1I_right_clothoidFar_curvature": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI1I_right_clothoidFar_curvature"),
        "leftI1I_right_clothoidFar_curvatureRate": ("LdOutput",
                                                    "MFC5xx_Device_LD_LdOutput_road_leftI1I_right_clothoidFar_curvatureRate"),
        "leftI1I_right_clothoidFar_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI1I_right_clothoidFar_validTo"),
        "leftI1I_right_clothoidFar_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI1I_right_clothoidFar_offset"),
        "leftI1I_right_clothoidFar_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI1I_right_clothoidFar_yawAngle"),
        "leftI1I_right_available": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI1I_right_available"),
        "rightI0I_left_clothoidNear_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI0I_left_clothoidNear_offset"),
        "rightI0I_left_clothoidNear_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI0I_left_clothoidNear_yawAngle"),
        "rightI0I_left_clothoidNear_curvature": ("LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_rightI0I_left_clothoidNear_curvature"),
        "rightI0I_left_clothoidNear_curvatureRate": ("LdOutput",
                                                     "MFC5xx_Device_LD_LdOutput_road_rightI0I_left_clothoidNear_curvatureRate"),
        "rightI0I_left_clothoidNear_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI0I_left_clothoidNear_validTo"),
        "rightI0I_left_clothoidFar_curvature": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI0I_left_clothoidFar_curvature"),
        "rightI0I_left_clothoidFar_curvatureRate": ("LdOutput",
                                                    "MFC5xx_Device_LD_LdOutput_road_rightI0I_left_clothoidFar_curvatureRate"),
        "rightI0I_left_clothoidFar_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI0I_left_clothoidFar_validTo"),
        "rightI0I_left_clothoidFar_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI0I_left_clothoidFar_offset"),
        "rightI0I_left_clothoidFar_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI0I_left_clothoidFar_yawAngle"),
        "rightI0I_left_available": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI0I_left_available"),
        "rightI0I_right_clothoidNear_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI0I_right_clothoidNear_offset"),
        "rightI0I_right_clothoidNear_yawAngle": ("LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_rightI0I_right_clothoidNear_yawAngle"),
        "rightI0I_right_clothoidNear_curvature": ("LdOutput",
                                                  "MFC5xx_Device_LD_LdOutput_road_rightI0I_right_clothoidNear_curvature"),
        "rightI0I_right_clothoidNear_curvatureRate": ("LdOutput",
                                                      "MFC5xx_Device_LD_LdOutput_road_rightI0I_right_clothoidNear_curvatureRate"),
        "rightI0I_right_clothoidNear_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI0I_right_clothoidNear_validTo"),
        "rightI0I_right_clothoidFar_curvature": ("LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_rightI0I_right_clothoidFar_curvature"),
        "rightI0I_right_clothoidFar_curvatureRate": ("LdOutput",
                                                     "MFC5xx_Device_LD_LdOutput_road_rightI0I_right_clothoidFar_curvatureRate"),
        "rightI0I_right_clothoidFar_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI0I_right_clothoidFar_validTo"),
        "rightI0I_right_clothoidFar_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI0I_right_clothoidFar_offset"),
        "rightI0I_right_clothoidFar_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI0I_right_clothoidFar_yawAngle"),
        "rightI0I_right_available": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI0I_right_available"),
        "rightI1I_left_clothoidNear_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI1I_left_clothoidNear_offset"),
        "rightI1I_left_clothoidNear_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI1I_left_clothoidNear_yawAngle"),
        "rightI1I_left_clothoidNear_curvature": ("LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_rightI1I_left_clothoidNear_curvature"),
        "rightI1I_left_clothoidNear_curvatureRate": ("LdOutput",
                                                     "MFC5xx_Device_LD_LdOutput_road_rightI1I_left_clothoidNear_curvatureRate"),
        "rightI1I_left_clothoidNear_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI1I_left_clothoidNear_validTo"),
        "rightI1I_left_clothoidFar_curvature": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI1I_left_clothoidFar_curvature"),
        "rightI1I_left_clothoidFar_curvatureRate": ("LdOutput",
                                                    "MFC5xx_Device_LD_LdOutput_road_rightI1I_left_clothoidFar_curvatureRate"),
        "rightI1I_left_clothoidFar_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI1I_left_clothoidFar_validTo"),
        "rightI1I_left_clothoidFar_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI1I_left_clothoidFar_offset"),
        "rightI1I_left_clothoidFar_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI1I_left_clothoidFar_yawAngle"),
        "rightI1I_left_available": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI1I_left_available"),
        "rightI1I_right_clothoidNear_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI1I_right_clothoidNear_offset"),
        "rightI1I_right_clothoidNear_yawAngle": ("LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_rightI1I_right_clothoidNear_yawAngle"),
        "rightI1I_right_clothoidNear_curvature": ("LdOutput",
                                                  "MFC5xx_Device_LD_LdOutput_road_rightI1I_right_clothoidNear_curvature"),
        "rightI1I_right_clothoidNear_curvatureRate": ("LdOutput",
                                                      "MFC5xx_Device_LD_LdOutput_road_rightI1I_right_clothoidNear_curvatureRate"),
        "rightI1I_right_clothoidNear_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI1I_right_clothoidNear_validTo"),
        "rightI1I_right_clothoidFar_curvature": ("LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_rightI1I_right_clothoidFar_curvature"),
        "rightI1I_right_clothoidFar_curvatureRate": ("LdOutput",
                                                     "MFC5xx_Device_LD_LdOutput_road_rightI1I_right_clothoidFar_curvatureRate"),
        "rightI1I_right_clothoidFar_validTo": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI1I_right_clothoidFar_validTo"),
        "rightI1I_right_clothoidFar_offset": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI1I_right_clothoidFar_offset"),
        "rightI1I_right_clothoidFar_yawAngle": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI1I_right_clothoidFar_yawAngle"),
        "rightI1I_right_available": (
            "LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI1I_right_available"),
    },
    {
        "ego_left_clothoidNear_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_offset"),
        "ego_left_clothoidNear_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_yawAngle"),
        "ego_left_clothoidNear_curvature": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_curvature"),
        "ego_left_clothoidNear_curvatureRate": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_curvatureRate"),
        "ego_left_clothoidNear_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_validTo"),
        "ego_left_clothoidFar_curvature": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidFar_curvature"),
        "ego_left_clothoidFar_curvatureRate": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidFar_curvatureRate"),
        "ego_left_clothoidFar_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidFar_validTo"),
        "ego_left_clothoidFar_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidFar_offset"),
        "ego_left_clothoidFar_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidFar_yawAngle"),
        "ego_left_available": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_available"),
        "ego_right_clothoidNear_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_offset"),
        "ego_right_clothoidNear_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_yawAngle"),
        "ego_right_clothoidNear_curvature": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_curvature"),
        "ego_right_clothoidNear_curvatureRate": ("MFC5xx Device.LD.LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_curvatureRate"),
        "ego_right_clothoidNear_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_validTo"),
        "ego_right_clothoidFar_curvature": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidFar_curvature"),
        "ego_right_clothoidFar_curvatureRate": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidFar_curvatureRate"),
        "ego_right_clothoidFar_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidFar_validTo"),
        "ego_right_clothoidFar_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidFar_offset"),
        "ego_right_clothoidFar_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidFar_yawAngle"),
        "ego_right_available": ("MFC5xx Device.LD.LdOutput",
                                "MFC5xx_Device_LD_LdOutput_road_ego_right_available"),
        "leftI0I_left_clothoidNear_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_left_clothoidNear_offset"),
        "leftI0I_left_clothoidNear_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_left_clothoidNear_yawAngle"),
        "leftI0I_left_clothoidNear_curvature": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_left_clothoidNear_curvature"),
        "leftI0I_left_clothoidNear_curvatureRate": ("MFC5xx Device.LD.LdOutput",
                                                    "MFC5xx_Device_LD_LdOutput_road_left0_left_clothoidNear_curvatureRate"),
        "leftI0I_left_clothoidNear_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_left_clothoidNear_validTo"),
        "leftI0I_left_clothoidFar_curvature": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_left_clothoidFar_curvature"),
        "leftI0I_left_clothoidFar_curvatureRate": ("MFC5xx Device.LD.LdOutput",
                                                   "MFC5xx_Device_LD_LdOutput_road_left0_left_clothoidFar_curvatureRate"),
        "leftI0I_left_clothoidFar_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_left_clothoidFar_validTo"),
        "leftI0I_left_clothoidFar_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_left_clothoidFar_offset"),
        "leftI0I_left_clothoidFar_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_left_clothoidFar_yawAngle"),
        "leftI0I_left_available": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_left_available"),
        "leftI0I_right_clothoidNear_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_right_clothoidNear_offset"),
        "leftI0I_right_clothoidNear_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_right_clothoidNear_yawAngle"),
        "leftI0I_right_clothoidNear_curvature": ("MFC5xx Device.LD.LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_left0_right_clothoidNear_curvature"),
        "leftI0I_right_clothoidNear_curvatureRate": ("MFC5xx Device.LD.LdOutput",
                                                     "MFC5xx_Device_LD_LdOutput_road_left0_right_clothoidNear_curvatureRate"),
        "leftI0I_right_clothoidNear_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_right_clothoidNear_validTo"),
        "leftI0I_right_clothoidFar_curvature": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_right_clothoidFar_curvature"),
        "leftI0I_right_clothoidFar_curvatureRate": ("MFC5xx Device.LD.LdOutput",
                                                    "MFC5xx_Device_LD_LdOutput_road_left0_right_clothoidFar_curvatureRate"),
        "leftI0I_right_clothoidFar_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_right_clothoidFar_validTo"),
        "leftI0I_right_clothoidFar_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_right_clothoidFar_offset"),
        "leftI0I_right_clothoidFar_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_right_clothoidFar_yawAngle"),
        "leftI0I_right_available": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_right_available"),
        "leftI1I_left_clothoidNear_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left1_left_clothoidNear_offset"),
        "leftI1I_left_clothoidNear_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left1_left_clothoidNear_yawAngle"),
        "leftI1I_left_clothoidNear_curvature": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left1_left_clothoidNear_curvature"),
        "leftI1I_left_clothoidNear_curvatureRate": ("MFC5xx Device.LD.LdOutput",
                                                    "MFC5xx_Device_LD_LdOutput_road_left1_left_clothoidNear_curvatureRate"),
        "leftI1I_left_clothoidNear_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left1_left_clothoidNear_validTo"),
        "leftI1I_left_clothoidFar_curvature": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left1_left_clothoidFar_curvature"),
        "leftI1I_left_clothoidFar_curvatureRate": ("MFC5xx Device.LD.LdOutput",
                                                   "MFC5xx_Device_LD_LdOutput_road_left1_left_clothoidFar_curvatureRate"),
        "leftI1I_left_clothoidFar_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left1_left_clothoidFar_validTo"),
        "leftI1I_left_clothoidFar_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left1_left_clothoidFar_offset"),
        "leftI1I_left_clothoidFar_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left1_left_clothoidFar_yawAngle"),
        "leftI1I_left_available": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left1_left_available"),
        "leftI1I_right_clothoidNear_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left1_right_clothoidNear_offset"),
        "leftI1I_right_clothoidNear_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left1_right_clothoidNear_yawAngle"),
        "leftI1I_right_clothoidNear_curvature": ("MFC5xx Device.LD.LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_left1_right_clothoidNear_curvature"),
        "leftI1I_right_clothoidNear_curvatureRate": ("MFC5xx Device.LD.LdOutput",
                                                     "MFC5xx_Device_LD_LdOutput_road_left1_right_clothoidNear_curvatureRate"),
        "leftI1I_right_clothoidNear_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left1_right_clothoidNear_validTo"),
        "leftI1I_right_clothoidFar_curvature": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left1_right_clothoidFar_curvature"),
        "leftI1I_right_clothoidFar_curvatureRate": ("MFC5xx Device.LD.LdOutput",
                                                    "MFC5xx_Device_LD_LdOutput_road_left1_right_clothoidFar_curvatureRate"),
        "leftI1I_right_clothoidFar_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left1_right_clothoidFar_validTo"),
        "leftI1I_right_clothoidFar_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left1_right_clothoidFar_offset"),
        "leftI1I_right_clothoidFar_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left1_right_clothoidFar_yawAngle"),
        "leftI1I_right_available": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left1_right_available"),
        "rightI0I_left_clothoidNear_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right0_left_clothoidNear_offset"),
        "rightI0I_left_clothoidNear_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right0_left_clothoidNear_yawAngle"),
        "rightI0I_left_clothoidNear_curvature": ("MFC5xx Device.LD.LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_right0_left_clothoidNear_curvature"),
        "rightI0I_left_clothoidNear_curvatureRate": ("MFC5xx Device.LD.LdOutput",
                                                     "MFC5xx_Device_LD_LdOutput_road_right0_left_clothoidNear_curvatureRate"),
        "rightI0I_left_clothoidNear_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right0_left_clothoidNear_validTo"),
        "rightI0I_left_clothoidFar_curvature": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right0_left_clothoidFar_curvature"),
        "rightI0I_left_clothoidFar_curvatureRate": ("MFC5xx Device.LD.LdOutput",
                                                    "MFC5xx_Device_LD_LdOutput_road_right0_left_clothoidFar_curvatureRate"),
        "rightI0I_left_clothoidFar_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right0_left_clothoidFar_validTo"),
        "rightI0I_left_clothoidFar_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right0_left_clothoidFar_offset"),
        "rightI0I_left_clothoidFar_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right0_left_clothoidFar_yawAngle"),
        "rightI0I_left_available": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right0_left_available"),
        "rightI0I_right_clothoidNear_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right0_right_clothoidNear_offset"),
        "rightI0I_right_clothoidNear_yawAngle": ("MFC5xx Device.LD.LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_right0_right_clothoidNear_yawAngle"),
        "rightI0I_right_clothoidNear_curvature": ("MFC5xx Device.LD.LdOutput",
                                                  "MFC5xx_Device_LD_LdOutput_road_right0_right_clothoidNear_curvature"),
        "rightI0I_right_clothoidNear_curvatureRate": ("MFC5xx Device.LD.LdOutput",
                                                      "MFC5xx_Device_LD_LdOutput_road_right0_right_clothoidNear_curvatureRate"),
        "rightI0I_right_clothoidNear_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right0_right_clothoidNear_validTo"),
        "rightI0I_right_clothoidFar_curvature": ("MFC5xx Device.LD.LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_right0_right_clothoidFar_curvature"),
        "rightI0I_right_clothoidFar_curvatureRate": ("MFC5xx Device.LD.LdOutput",
                                                     "MFC5xx_Device_LD_LdOutput_road_right0_right_clothoidFar_curvatureRate"),
        "rightI0I_right_clothoidFar_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right0_right_clothoidFar_validTo"),
        "rightI0I_right_clothoidFar_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right0_right_clothoidFar_offset"),
        "rightI0I_right_clothoidFar_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right0_right_clothoidFar_yawAngle"),
        "rightI0I_right_available": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right0_right_available"),
        "rightI1I_left_clothoidNear_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right1_left_clothoidNear_offset"),
        "rightI1I_left_clothoidNear_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right1_left_clothoidNear_yawAngle"),
        "rightI1I_left_clothoidNear_curvature": ("MFC5xx Device.LD.LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_right1_left_clothoidNear_curvature"),
        "rightI1I_left_clothoidNear_curvatureRate": ("MFC5xx Device.LD.LdOutput",
                                                     "MFC5xx_Device_LD_LdOutput_road_right1_left_clothoidNear_curvatureRate"),
        "rightI1I_left_clothoidNear_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right1_left_clothoidNear_validTo"),
        "rightI1I_left_clothoidFar_curvature": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right1_left_clothoidFar_curvature"),
        "rightI1I_left_clothoidFar_curvatureRate": ("MFC5xx Device.LD.LdOutput",
                                                    "MFC5xx_Device_LD_LdOutput_road_right1_left_clothoidFar_curvatureRate"),
        "rightI1I_left_clothoidFar_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right1_left_clothoidFar_validTo"),
        "rightI1I_left_clothoidFar_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right1_left_clothoidFar_offset"),
        "rightI1I_left_clothoidFar_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right1_left_clothoidFar_yawAngle"),
        "rightI1I_left_available": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right1_left_available"),
        "rightI1I_right_clothoidNear_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right1_right_clothoidNear_offset"),
        "rightI1I_right_clothoidNear_yawAngle": ("MFC5xx Device.LD.LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_right1_right_clothoidNear_yawAngle"),
        "rightI1I_right_clothoidNear_curvature": ("MFC5xx Device.LD.LdOutput",
                                                  "MFC5xx_Device_LD_LdOutput_road_right1_right_clothoidNear_curvature"),
        "rightI1I_right_clothoidNear_curvatureRate": ("MFC5xx Device.LD.LdOutput",
                                                      "MFC5xx_Device_LD_LdOutput_road_right1_right_clothoidNear_curvatureRate"),
        "rightI1I_right_clothoidNear_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right1_right_clothoidNear_validTo"),
        "rightI1I_right_clothoidFar_curvature": ("MFC5xx Device.LD.LdOutput",
                                                 "MFC5xx_Device_LD_LdOutput_road_right1_right_clothoidFar_curvature"),
        "rightI1I_right_clothoidFar_curvatureRate": ("MFC5xx Device.LD.LdOutput",
                                                     "MFC5xx_Device_LD_LdOutput_road_right1_right_clothoidFar_curvatureRate"),
        "rightI1I_right_clothoidFar_validTo": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right1_right_clothoidFar_validTo"),
        "rightI1I_right_clothoidFar_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right1_right_clothoidFar_offset"),
        "rightI1I_right_clothoidFar_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right1_right_clothoidFar_yawAngle"),
        "rightI1I_right_available": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right1_right_available"),
    },
    {
        "ego_left_clothoidNear_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.left.clothoidNear.offset"),
        "ego_left_clothoidNear_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.left.clothoidNear.yawAngle"),
        "ego_left_clothoidNear_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.left.clothoidNear.curvature"),
        "ego_left_clothoidNear_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.left.clothoidNear.curvatureRate"),
        "ego_left_clothoidNear_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.left.clothoidNear.validTo"),
        "ego_left_clothoidFar_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.left.clothoidFar.curvature"),
        "ego_left_clothoidFar_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.left.clothoidFar.curvatureRate"),
        "ego_left_clothoidFar_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.left.clothoidFar.validTo"),
        "ego_left_clothoidFar_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.left.clothoidFar.offset"),
        "ego_left_clothoidFar_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.left.clothoidFar.yawAngle"),
        "ego_left_available": ("MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.left.available"),
        "ego_right_clothoidNear_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.right.clothoidNear.offset"),
        "ego_right_clothoidNear_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.right.clothoidNear.yawAngle"),
        "ego_right_clothoidNear_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.right.clothoidNear.curvature"),
        "ego_right_clothoidNear_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.right.clothoidNear.curvatureRate"),
        "ego_right_clothoidNear_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.right.clothoidNear.validTo"),
        "ego_right_clothoidFar_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.right.clothoidFar.curvature"),
        "ego_right_clothoidFar_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.right.clothoidFar.curvatureRate"),
        "ego_right_clothoidFar_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.right.clothoidFar.validTo"),
        "ego_right_clothoidFar_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.right.clothoidFar.offset"),
        "ego_right_clothoidFar_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.right.clothoidFar.yawAngle"),
        "ego_right_available": ("MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.right.available"),
        "leftI0I_left_clothoidNear_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].left.clothoidNear.offset"),
        "leftI0I_left_clothoidNear_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].left.clothoidNear.yawAngle"),
        "leftI0I_left_clothoidNear_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].right.clothoidNear.curvature"),
        "leftI0I_left_clothoidNear_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].right.clothoidNear.curvatureRate"),
        "leftI0I_left_clothoidNear_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].left.clothoidNear.validTo"),
        "leftI0I_left_clothoidFar_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].right.clothoidFar.curvature"),
        "leftI0I_left_clothoidFar_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].right.clothoidFar.curvatureRate"),
        "leftI0I_left_clothoidFar_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].left.clothoidFar.validTo"),
        "leftI0I_left_clothoidFar_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].left.clothoidFar.offset"),
        "leftI0I_left_clothoidFar_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].left.clothoidFar.yawAngle"),
        "leftI0I_left_available": ("MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].available"),
        "leftI0I_right_clothoidNear_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].right.clothoidNear.offset"),
        "leftI0I_right_clothoidNear_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].right.clothoidNear.yawAngle"),
        "leftI0I_right_clothoidNear_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].right.clothoidNear.curvature"),
        "leftI0I_right_clothoidNear_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].right.clothoidNear.curvatureRate"),
        "leftI0I_right_clothoidNear_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].right.clothoidNear.validTo"),
        "leftI0I_right_clothoidFar_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].right.clothoidFar.curvature"),
        "leftI0I_right_clothoidFar_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].right.clothoidFar.curvatureRate"),
        "leftI0I_right_clothoidFar_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].right.clothoidFar.validTo"),
        "leftI0I_right_clothoidFar_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].right.clothoidFar.offset"),
        "leftI0I_right_clothoidFar_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].right.clothoidFar.yawAngle"),
        "leftI0I_right_available": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[0].right.available"),
        "leftI1I_left_clothoidNear_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].left.clothoidNear.offset"),
        "leftI1I_left_clothoidNear_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].left.clothoidNear.yawAngle"),
        "leftI1I_left_clothoidNear_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].right.clothoidNear.curvature"),
        "leftI1I_left_clothoidNear_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].right.clothoidNear.curvatureRate"),
        "leftI1I_left_clothoidNear_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].left.clothoidNear.validTo"),
        "leftI1I_left_clothoidFar_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].left.clothoidFar.curvature"),
        "leftI1I_left_clothoidFar_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].left.clothoidFar.curvatureRate"),
        "leftI1I_left_clothoidFar_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].left.clothoidFar.validTo"),
        "leftI1I_left_clothoidFar_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].left.clothoidFar.offset"),
        "leftI1I_left_clothoidFar_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].left.clothoidFar.yawAngle"),
        "leftI1I_left_available": ("MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].available"),
        "leftI1I_right_clothoidNear_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].right.clothoidNear.offset"),
        "leftI1I_right_clothoidNear_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].right.clothoidNear.yawAngle"),
        "leftI1I_right_clothoidNear_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].right.clothoidNear.curvature"),
        "leftI1I_right_clothoidNear_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].right.clothoidNear.curvatureRate"),
        "leftI1I_right_clothoidNear_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].right.clothoidNear.validTo"),
        "leftI1I_right_clothoidFar_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].right.clothoidFar.curvature"),
        "leftI1I_right_clothoidFar_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].right.clothoidFar.curvatureRate"),
        "leftI1I_right_clothoidFar_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].right.clothoidFar.validTo"),
        "leftI1I_right_clothoidFar_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].right.clothoidFar.offset"),
        "leftI1I_right_clothoidFar_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].right.clothoidFar.yawAngle"),
        "leftI1I_right_available": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.left[1].right.available"),
        "rightI0I_left_clothoidNear_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].left.clothoidNear.offset"),
        "rightI0I_left_clothoidNear_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].left.clothoidNear.yawAngle"),
        "rightI0I_left_clothoidNear_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].left.clothoidNear.curvature"),
        "rightI0I_left_clothoidNear_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].left.clothoidNear.curvatureRate"),
        "rightI0I_left_clothoidNear_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].left.clothoidNear.validTo"),
        "rightI0I_left_clothoidFar_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].left.clothoidFar.curvature"),
        "rightI0I_left_clothoidFar_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].left.clothoidFar.curvatureRate"),
        "rightI0I_left_clothoidFar_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].left.clothoidFar.validTo"),
        "rightI0I_left_clothoidFar_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].left.clothoidFar.offset"),
        "rightI0I_left_clothoidFar_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].left.clothoidFar.yawAngle"),
        "rightI0I_left_available": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].left.available"),
        "rightI0I_right_clothoidNear_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].right.clothoidNear.offset"),
        "rightI0I_right_clothoidNear_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].right.clothoidNear.yawAngle"),
        "rightI0I_right_clothoidNear_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].left.clothoidNear.curvature"),
        "rightI0I_right_clothoidNear_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].left.clothoidNear.curvatureRate"),
        "rightI0I_right_clothoidNear_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].right.clothoidNear.validTo"),
        "rightI0I_right_clothoidFar_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].left.clothoidFar.curvature"),
        "rightI0I_right_clothoidFar_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].left.clothoidFar.curvatureRate"),
        "rightI0I_right_clothoidFar_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].right.clothoidFar.validTo"),
        "rightI0I_right_clothoidFar_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].left.clothoidFar.offset"),
        "rightI0I_right_clothoidFar_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].right.clothoidFar.yawAngle"),
        "rightI0I_right_available": ("MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[0].available"),
        "rightI1I_left_clothoidNear_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].left.clothoidNear.offset"),
        "rightI1I_left_clothoidNear_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].left.clothoidNear.yawAngle"),
        "rightI1I_left_clothoidNear_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].left.clothoidNear.curvature"),
        "rightI1I_left_clothoidNear_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].left.clothoidNear.curvatureRate"),
        "rightI1I_left_clothoidNear_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].left.clothoidNear.validTo"),
        "rightI1I_left_clothoidFar_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].left.clothoidFar.curvature"),
        "rightI1I_left_clothoidFar_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].left.clothoidFar.curvatureRate"),
        "rightI1I_left_clothoidFar_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].left.clothoidFar.validTo"),
        "rightI1I_left_clothoidFar_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].left.clothoidFar.offset"),
        "rightI1I_left_clothoidFar_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].left.clothoidFar.yawAngle"),
        "rightI1I_left_available": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].left.available"),
        "rightI1I_right_clothoidNear_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].right.clothoidNear.offset"),
        "rightI1I_right_clothoidNear_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].right.clothoidNear.yawAngle"),
        "rightI1I_right_clothoidNear_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].right.clothoidNear.curvature"),
        "rightI1I_right_clothoidNear_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].right.clothoidNear.curvatureRate"),
        "rightI1I_right_clothoidNear_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].right.clothoidNear.validTo"),
        "rightI1I_right_clothoidFar_curvature": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].right.clothoidFar.curvature"),
        "rightI1I_right_clothoidFar_curvatureRate": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].right.clothoidFar.curvatureRate"),
        "rightI1I_right_clothoidFar_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].right.clothoidFar.validTo"),
        "rightI1I_right_clothoidFar_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].right.clothoidFar.offset"),
        "rightI1I_right_clothoidFar_yawAngle": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].right.clothoidFar.yawAngle"),
        "rightI1I_right_available": ("MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.right[1].available"),

    },
]


def convert_sensor_offset(refpoint_x, refpoint_y):
    dx0 = -refpoint_x
    dy0 = refpoint_y
    return dx0, dy0


def convert_coeffs(offset, heading, curvature, curvature_rate):
    c0 = -offset
    c1 = -heading
    c2 = -curvature
    c3 = -curvature_rate
    return c0, c1, c2, c3


def convert_view_range(view_range):
    return view_range


def create_line(time, c0, c1, c2, c3, view_range, dx0, dy0, winner):
    view_range = convert_view_range(view_range)
    line = Flc25AbdLine.from_physical_coeffs(time, c0, c1, c2, c3, view_range)
    return line


class Flc25AbdLine(PolyClothoid, VideoLineProp):
    def __init__(self, time, c0, c1, c2, c3, view_range):
        PolyClothoid.__init__(self, time, c0, c1, c2, c3)
        VideoLineProp.__init__(self, time, view_range, None, None)
        return

    def translate(self, dx, dy):
        newobj = copy.copy(self)
        newobj = PolyClothoid.translate(newobj, dx, dy)
        newobj = VideoLineProp.translate(newobj, dx, dy)
        return newobj


class Calc(interface.iCalc):
    dep = ('calc_common_time-flc25')

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(signal_group)
        return group

    def fill(self, group):
        import time
        start = time.time()
        cached_data = get_modules_cache(self.source, "calc_lanes_flc25_ld@aebs.fill")
        if cached_data is None:
            common_time = self.get_modules().fill('calc_common_time-flc25')

            # polynominal

            C0 = group.get_value('ego_left_clothoidNear_offset', ScaleTime=common_time)
            C1 = group.get_value('ego_left_clothoidNear_yawAngle', ScaleTime=common_time)
            C2 = group.get_value('ego_left_clothoidNear_curvature', ScaleTime=common_time)
            C3 = group.get_value('ego_left_clothoidNear_curvatureRate', ScaleTime=common_time)
            V_raw = group.get_value('ego_left_clothoidNear_validTo', ScaleTime=common_time)

            left_lane = create_line(common_time, C0, C1, C2, C3, V_raw, None, None, group.winner)
            # leftI0I_left
            C0 = group.get_value('leftI0I_left_clothoidNear_offset', ScaleTime=common_time)
            C1 = group.get_value('leftI0I_left_clothoidNear_yawAngle', ScaleTime=common_time)
            C2 = group.get_value('leftI0I_left_clothoidNear_curvature', ScaleTime=common_time)
            C3 = group.get_value('leftI0I_left_clothoidNear_curvatureRate', ScaleTime=common_time)
            V_raw = group.get_value('leftI0I_left_clothoidNear_validTo', ScaleTime=common_time)

            left_left_lane = create_line(common_time, C0, C1, C2, C3, V_raw, None, None, group.winner)
            # leftI0I_right
            C0 = group.get_value('leftI0I_right_clothoidNear_offset', ScaleTime=common_time)
            C1 = group.get_value('leftI0I_right_clothoidNear_yawAngle', ScaleTime=common_time)
            C2 = group.get_value('leftI0I_right_clothoidNear_curvature', ScaleTime=common_time)
            C3 = group.get_value('leftI0I_right_clothoidNear_curvatureRate', ScaleTime=common_time)
            V_raw = group.get_value('leftI0I_right_clothoidNear_validTo', ScaleTime=common_time)

            left_left_left_lane = create_line(common_time, C0, C1, C2, C3, V_raw, None, None, group.winner)

            C0 = group.get_value('ego_right_clothoidNear_offset', ScaleTime=common_time)
            C1 = group.get_value('ego_right_clothoidNear_yawAngle', ScaleTime=common_time)
            C2 = group.get_value('ego_right_clothoidNear_curvature', ScaleTime=common_time)
            C3 = group.get_value('ego_right_clothoidNear_curvatureRate', ScaleTime=common_time)
            V_raw = group.get_value('ego_right_clothoidNear_validTo', ScaleTime=common_time)

            right_lane = create_line(common_time, C0, C1, C2, C3, V_raw, None, None, group.winner)
            # rightI0I_left
            C0 = group.get_value('rightI0I_left_clothoidNear_offset', ScaleTime=common_time)
            C1 = group.get_value('rightI0I_left_clothoidNear_yawAngle', ScaleTime=common_time)
            C2 = group.get_value('rightI0I_left_clothoidNear_curvature', ScaleTime=common_time)
            C3 = group.get_value('rightI0I_left_clothoidNear_curvatureRate', ScaleTime=common_time)
            V_raw = group.get_value('rightI0I_left_clothoidNear_validTo', ScaleTime=common_time)

            right_right_lane = create_line(common_time, C0, C1, C2, C3, V_raw, None, None, group.winner)
            # rightI0I_right
            C0 = group.get_value('rightI0I_right_clothoidNear_offset', ScaleTime=common_time)
            C1 = group.get_value('rightI0I_right_clothoidNear_yawAngle', ScaleTime=common_time)
            C2 = group.get_value('rightI0I_right_clothoidNear_curvature', ScaleTime=common_time)
            C3 = group.get_value('rightI0I_right_clothoidNear_curvatureRate', ScaleTime=common_time)
            V_raw = group.get_value('rightI0I_right_clothoidNear_validTo', ScaleTime=common_time)

            right_right_right_lane = create_line(common_time, C0, C1, C2, C3, V_raw, None, None, group.winner)

            lines = LaneData(left_lane, right_lane, left_left_lane, right_right_lane)
            store_modules_cache(self.source, "calc_lanes_flc25_ld@aebs.fill", lines)
        else:
            logger.info("Loading LD Lanes from cached data")
            lines = cached_data
        done = time.time()
        elapsed = done - start
        logger.info("LD Lanes loaded in " + str(elapsed))
        return lines


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\ld_interface\meas\HMC-QZ" \
                r"-STR__2020-11-12_15-54-20.mat"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flc25_lanes = manager_modules.calc('calc_lanes_flc25_ld@aebs.fill', manager)
    print flc25_lanes
