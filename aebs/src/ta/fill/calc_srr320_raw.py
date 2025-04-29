# -*- dataeval: init -*-

import numpy as np

from collections import OrderedDict
from interface import iCalc
from primitives.bases import Primitive, PrimitiveCollection

signal_group = {"VY": ("SRR320_Obj%02d", "SPDY_OBJ%02d"),
                "DY": ("SRR320_Obj%02d", "DISTY_OBJ%02d"),
                "VX": ("SRR320_Obj%02d", "SPDX_OBJ%02d"),
                "DX": ("SRR320_Obj%02d", "DISTX_OBJ%02d")}

# The angle between the radar and the truck
x0 = 0
y0 = 0
angle = np.deg2rad(0)


class SRR320Objects(Primitive):
    normalize_value = 60.0

    def __init__(self, id, common_time, group):
        super(SRR320Objects, self).__init__(common_time)
        self._group = group
        self.dx = self._group.get_value("DX", ScaleTime=self.time)
        self.dy = self._group.get_value("DY", ScaleTime=self.time)
        self.vx = self._group.get_value("VX", ScaleTime=self.time)
        self.vy = self._group.get_value("VY", ScaleTime=self.time)
        self.id = id

        # self.dist_mask = np.logical_and(np.logical_and(np.abs(self.dx) < 10.0, np.abs(self.dx) > 0.5),np.logical_and(self.dx != 0.0, self.dy != 0.0))
        self.dist_mask = np.logical_and(self.dx != 0.0, self.dy != 0.0)
        self.velocity_mask = np.logical_or(self.vx == 0.0, self.vy == 0.0)
        self.mask = np.logical_and(self.dist_mask, self.velocity_mask)

        # self.dx = np.where(self.mask, 5, 0)
        # self.dy = np.where(self.mask, -1, 0)

        # coordinate transformation
        vehicle_x = self.dx * np.cos(angle) - self.dy * np.sin(angle)
        vehicle_y = self.dx * np.sin(angle) + self.dy * np.cos(angle) - y0
        self.dx = np.ma.masked_array(vehicle_x, mask=~self.mask)
        self.dy = np.ma.masked_array(vehicle_y, mask=~self.mask)

        vehicle_vx = self.vx * np.cos(angle) - self.vy * np.sin(angle)
        vehicle_vy = self.vx * np.sin(angle) + self.vy * np.cos(angle)
        self.vx = np.ma.masked_array(vehicle_vx, mask=~self.mask)
        self.vy = np.ma.masked_array(vehicle_vy, mask=~self.mask)

        return


class Calc(iCalc):

    def check(self):
        group = OrderedDict()
        for msg_num in xrange(18):
            sg = {alias: (devtempl % msg_num, sigtempl % msg_num) for alias, (devtempl, sigtempl) in
                  signal_group.iteritems()}
            group[msg_num] = self.source.selectSignalGroup([sg])
        return group

    def fill(self, groups):
        common_time = groups[0].get_time("DX")
        targets = PrimitiveCollection(common_time)
        for id, group in groups.iteritems():
            targets[id] = SRR320Objects(id, common_time, group)
        return targets


if __name__ == '__main__':
    from config.Config import init_dataeval
    meas_path = r'C:\Users\ext-dudolad\Desktop\TA-Conti\Measurements\20170614\002TA20170614.MDF'
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    srr320 = manager_modules.calc('calc_srr320_raw@aebs.fill', manager)
    dummy_id, dummy_target = srr320.iteritems().next()
    print dummy_id
    print dummy_target.dx
