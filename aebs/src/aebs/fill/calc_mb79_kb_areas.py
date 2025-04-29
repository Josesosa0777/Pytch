# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

from interface import iCalc

INFO_DX_MIN = -10.0

signals = [{
  "dy_info":             ("TA", "warn_trigg_out_dy_info"),
  "dy_hazard":           ("TA", "warn_trigg_out_dy_hazard"),
  "dx_hazard_front":     ("TA", "warn_trigg_out_dx_hazard_front"),
  "dx_hazard_rear":      ("TA", "warn_trigg_out_dx_hazard_rear"),
}]


class KBInfoAndHazardAreas(object):
    def __init__(self, time, dy_info, dy_hazard, dx_hazard_front, dx_hazard_rear):
        self.time = time
        self.dy_info = dy_info
        self.dy_hazard = dy_hazard
        self.dx_hazard_front = dx_hazard_front
        self.dx_hazard_rear = dx_hazard_rear

        self.info_mask = self.dy_info != 0.0
        self.hazard_mask = self.dy_hazard != 0.0

        self.info_area = self.get_info_vertices()
        self.hazard_area = self.get_hazard_vertices()
        return

    def info_area_vertices(self, index):
        return self.info_area[index]

    def hazard_area_vertices(self, index):
        return self.hazard_area[index]

    def get_info_vertices(self):
        dx_min = np.full(self.dy_info.shape, INFO_DX_MIN)
        vertices = np.zeros((self.dy_info.shape[0], 4, 2))
        vertices[:, 1, 0] = -self.dy_info
        vertices[:, 1, 1] = self.dy_info
        vertices[:, 2, 0] = -self.dy_info
        vertices[:, 2, 1] = dx_min
        vertices[:, 3, 1] = dx_min
        return vertices

    def get_hazard_vertices(self):
        vertices = np.zeros((self.dy_hazard.shape[0], 3, 2))
        vertices[:, 1, 0] = -self.dy_hazard
        vertices[:, 1, 1] = self.dx_hazard_front
        vertices[:, 2, 0] = -self.dy_hazard
        vertices[:, 2, 1] = self.dx_hazard_rear
        return vertices


class Calc(iCalc):
    def check(self):
        group = self.source.selectSignalGroup(signals)
        time, dy_hazard = group.get_signal("dy_hazard")
        dy_info = group.get_value("dy_info")
        dx_hazard_front = group.get_value("dx_hazard_front")
        dx_hazard_rear = group.get_value("dx_hazard_rear")
        return KBInfoAndHazardAreas(time, dy_info, dy_hazard, dx_hazard_front, dx_hazard_rear)
