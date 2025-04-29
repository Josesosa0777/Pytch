# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from collections import OrderedDict

import numpy as np

from primitives.bases import PrimitiveCollection
from metatrack import ObjectFromMessage
from interface import iCalc

from pyutils.enum import enum

TARGET_TYPE = enum(STATIONARY_CONT=0, MOVING_CONT=1, STATIONARY=2, MOVING=3)

mask_signal = "Existence_of_TG%d"

alive_sgs = {
    "Existence_of_TG0":           ("RadarID_%d_alive", "RadarID_%d_Existence_of_TG0"),
    "Existence_of_TG1":           ("RadarID_%d_alive", "RadarID_%d_Existence_of_TG1"),
    "Existence_of_TG2":           ("RadarID_%d_alive", "RadarID_%d_Existence_of_TG2"),
    "Existence_of_TG3":           ("RadarID_%d_alive", "RadarID_%d_Existence_of_TG3"),
    "Existence_of_TG4":           ("RadarID_%d_alive", "RadarID_%d_Existence_of_TG4"),
    "Existence_of_TG5":           ("RadarID_%d_alive", "RadarID_%d_Existence_of_TG5"),
    "Existence_of_TG6":           ("RadarID_%d_alive", "RadarID_%d_Existence_of_TG6"),
    "Existence_of_TG7":           ("RadarID_%d_alive", "RadarID_%d_Existence_of_TG7"),
    "Existence_of_TG8":           ("RadarID_%d_alive", "RadarID_%d_Existence_of_TG8"),
    "Existence_of_TG9":           ("RadarID_%d_alive", "RadarID_%d_Existence_of_TG9"),
    "Sync_counter":               ("RadarID_%d_alive", "RadarID_%d_Sync_counter"),
    "Timestamp":                  ("RadarID_%d_alive", "RadarID_%d_Timestamp"),
    "Error_flag":                 ("RadarID_%d_alive", "RadarID_%d_Error_flag"),
}

sgs_temp = {
    "Sync_counter":    ("RadarID_%d_target_%d", "RadarID_%d_target_%d_Sync_counter"),
    "AMP":             ("RadarID_%d_target_%d", "RadarID_%d_target_%d_AMP"),
    "X":               ("RadarID_%d_target_%d", "RadarID_%d_target_%d_X"),
    "Y":               ("RadarID_%d_target_%d", "RadarID_%d_target_%d_Y"),
    "VY":              ("RadarID_%d_target_%d", "RadarID_%d_target_%d_VY"),
    "VX":              ("RadarID_%d_target_%d", "RadarID_%d_target_%d_VX"),
    "Type":            ("RadarID_%d_target_%d", "RadarID_%d_target_%d_Type"),
}


class FurukawaTargets(ObjectFromMessage):
    _attribs = sgs_temp.keys()

    #TODO: fill with actual values
    dx0 = 0.0
    dy0 = 0.0
    angle0_deg = 0.0

    def __init__(self, _id, common_time, group, mask, **kwargs):
        dir_corr = None     # no direction correction
        source = None       # source unnecessary as signals can be loaded directly from signal group
        super(FurukawaTargets, self).__init__(_id, common_time, source, dir_corr, **kwargs)
        self._group = group
        self._mask = mask
        return

    def _create(self, signame):
        arr = self._group.get_value(signame, ScaleTime=self._msgTime, Order='valid', InvalidValue=0)
        out = self._rescale(arr)
        return np.ma.masked_array(out, self._mask)

    def rescale(self, scaleTime, **kwargs):
        return FurukawaTargets(self._id, self._msgTime, self._group, self._mask, scaleTime=scaleTime, **kwargs)

    def id(self):
        data = np.empty(len(self._mask), dtype=np.uint8)
        data.fill(self._id)
        return np.ma.masked_array(data, self._mask)

    def dx(self):
        return self._X + self.dx0

    def dy(self):
        return -(self._Y + self.dy0)

    def range(self):
        return np.sqrt(np.square(self.dx) + np.square(self.dy))

    def angle(self):
        return np.arctan2(self.dy, self.dx)

    def vx(self):
        return self._VX

    def vy(self):
        return self._VY

    def mov_state(self):
        # TODO: implement moving state?
        return


class Calc(iCalc):
    def check(self):
        alive_groups = OrderedDict()
        for radar_id in xrange(1, 5):  # radar ids are between 1-4 according to dbc file
            head_sgs = {alias: (dev % radar_id, sig % radar_id) for alias, (dev, sig) in alive_sgs.iteritems()}
            head_group = self.source.selectSignalGroup([head_sgs])
            if head_group:
                alive_groups[radar_id] = head_group
        return alive_groups

    def fill(self, alive_groups):
        # get the common time
        time_group = alive_groups.itervalues().next()
        common_time = time_group.get_time(time_group.iterkeys().next())

        targets = PrimitiveCollection(common_time)
        for radar_id, group in alive_groups.iteritems():
            for target_no in xrange(10):
                existence = group.get_value(mask_signal % target_no)
                mask = existence != 1
                if False in mask:
                    sg_group = {alias: (dev % (radar_id, target_no), sig % (radar_id, target_no))
                                      for alias, (dev, sig) in sgs_temp.iteritems()}
                    target_group = self.source.selectSignalGroup([sg_group])
                    target_id = radar_id * 10 + target_no
                    targets[target_id] = FurukawaTargets(target_id, common_time, target_group, mask)
        return targets

if __name__ == '__main__':
  from config.Config import init_dataeval

  meas_path = r'\\file.corp.knorr-bremse.com\knorr\Project\DAS\07_Information\70_TA\SensorPosition\Test\Furukawa\m01.mdf'
  config, manager, manager_modules = init_dataeval(['-m', meas_path])
  furukawa_targets = manager_modules.calc('calc_furukawa_targets@aebs.fill', manager)
  dummy_id, dummy_target = furukawa_targets.iteritems().next()
  print dummy_id
  print dummy_target.range
