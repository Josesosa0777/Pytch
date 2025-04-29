# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

from interface import iCalc


class TA_BSM_WarningAreas(object):
    # def __init__(self, time, dy_info, dy_hazard, dx_hazard_front, dx_hazard_rear):
    #     self.time = time
    #     self.dy_info = dy_info
    #     self.dy_hazard = dy_hazard
    #     self.dx_hazard_front = dx_hazard_front
    #     self.dx_hazard_rear = dx_hazard_rear
    #
    #     self.info_mask = self.dy_info != 0.0
    #     self.hazard_mask = self.dy_hazard != 0.0
    #
    #     return

    def __init__(self, time):
        self.time = time

        self.cam = self.get_cam_vertices()
        self.ls = self.get_ls_vertices()
        self.hs = self.get_hs_vertices()
        self.drad_long = self.get_drad_long_vertices()
        self.drad_lat = self.get_drad_lat_vertices()
        self.mask = np.ones(self.time.shape)

    def bsm_cam_vertices(self, index):
        return self.cam[index]

    def bsm_ls_vertices(self, index):
        return self.ls[index]

    def bsm_hs_vertices(self, index):
        return self.hs[index]

    def bsm_drad_long_vertices(self, index):
        return self.drad_long[index]

    def bsm_drad_lat_vertices(self, index):
        return self.drad_lat[index]

    def get_cam_vertices(self):
        vertices = np.zeros((self.time.shape[0], 4, 2))
        vertices[:, 0, 0] = CAM_VERTICES["ymax"]
        vertices[:, 0, 1] = CAM_VERTICES["xmax"]
        vertices[:, 1, 0] = CAM_VERTICES["ymax"]
        vertices[:, 1, 1] = CAM_VERTICES["xmin"]
        vertices[:, 2, 0] = CAM_VERTICES["ymin"]
        vertices[:, 2, 1] = CAM_VERTICES["xmin"]
        vertices[:, 3, 0] = CAM_VERTICES["ymin"]
        vertices[:, 3, 1] = CAM_VERTICES["xmax"]
        return vertices

    def get_ls_vertices(self):
        vertices = np.zeros((self.time.shape[0], 4, 2))
        vertices[:, 0, 0] = LS_VERTICES["ymax"]
        vertices[:, 0, 1] = LS_VERTICES["xmax"]
        vertices[:, 1, 0] = LS_VERTICES["ymax"]
        vertices[:, 1, 1] = LS_VERTICES["xmin"]
        vertices[:, 2, 0] = LS_VERTICES["ymin"]
        vertices[:, 2, 1] = LS_VERTICES["xmin"]
        vertices[:, 3, 0] = LS_VERTICES["ymin"]
        vertices[:, 3, 1] = LS_VERTICES["xmax"]
        return vertices

    def get_hs_vertices(self):
        vertices = np.zeros((self.time.shape[0], 4, 2))
        vertices[:, 0, 0] = HS_VERTICES["ymax"]
        vertices[:, 0, 1] = HS_VERTICES["xmax"]
        vertices[:, 1, 0] = HS_VERTICES["ymax"]
        vertices[:, 1, 1] = HS_VERTICES["xmin"]
        vertices[:, 2, 0] = HS_VERTICES["ymin"]
        vertices[:, 2, 1] = HS_VERTICES["xmin"]
        vertices[:, 3, 0] = HS_VERTICES["ymin"]
        vertices[:, 3, 1] = HS_VERTICES["xmax"]
        return vertices

    def get_drad_long_vertices(self):
        vertices = np.zeros((self.time.shape[0], 4, 2))
        vertices[:, 0, 0] = DRAD_LONG_VERTICES["ymax"]
        vertices[:, 0, 1] = DRAD_LONG_VERTICES["xmax"]
        vertices[:, 1, 0] = DRAD_LONG_VERTICES["ymax"]
        vertices[:, 1, 1] = DRAD_LONG_VERTICES["xmin"]
        vertices[:, 2, 0] = DRAD_LONG_VERTICES["ymin"]
        vertices[:, 2, 1] = DRAD_LONG_VERTICES["xmin"]
        vertices[:, 3, 0] = DRAD_LONG_VERTICES["ymin"]
        vertices[:, 3, 1] = DRAD_LONG_VERTICES["xmax"]
        return vertices

    def get_drad_lat_vertices(self):
        vertices = np.zeros((self.time.shape[0], 4, 2))
        vertices[:, 0, 0] = DRAD_LAT_VERTICES["ymax"]
        vertices[:, 0, 1] = DRAD_LAT_VERTICES["xmax"]
        vertices[:, 1, 0] = DRAD_LAT_VERTICES["ymax"]
        vertices[:, 1, 1] = DRAD_LAT_VERTICES["xmin"]
        vertices[:, 2, 0] = DRAD_LAT_VERTICES["ymin"]
        vertices[:, 2, 1] = DRAD_LAT_VERTICES["xmin"]
        vertices[:, 3, 0] = DRAD_LAT_VERTICES["ymin"]
        vertices[:, 3, 1] = DRAD_LAT_VERTICES["xmax"]
        return vertices


# used only to get the time array
signals = [{
    "x": ("SRR_OBJ_00_C", "fDistX_SrrRLObj00_SRR_OBJ_00_C_CAN2"),
    },
    {
    "x": ("SRR_OBJ_00_C", "fDistX_SrrRLObj00"),
    }
]

# the coordinates of the vertices defining the monitoring areas
CAM_VERTICES = {
    "ymin" : -1.5,
    "ymax" : 0,
    "xmin" : -4,
    "xmax" : 2,
}

LS_VERTICES = {
    "ymin" : -5,
    "ymax" : 0,
    "xmin" : -10,
    "xmax" : 2,
}

HS_VERTICES = {
    "ymin" : -6,
    "ymax" : 0,
    "xmin" : -12,
    "xmax" : 4,
}

DRAD_LONG_VERTICES = {
    "ymin" : -7.25,
    "ymax" : -1.25,
    "xmin" : -32.5,
    "xmax" : 17.5,
}

DRAD_LAT_VERTICES = {
    "ymin" : -11.25,
    "ymax" : -1.25,
    "xmin" : -7.5,
    "xmax" : 10.5,
}

class Calc(iCalc):
    def check(self):
        group = self.source.selectSignalGroup(signals)
        time, _ = group.get_signal("x")
        # overwrite the dictionaries here, if the area boundaries come from the measurement
        return TA_BSM_WarningAreas(time)
