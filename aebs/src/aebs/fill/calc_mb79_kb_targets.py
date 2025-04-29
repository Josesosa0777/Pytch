# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

from primitives.bases import PrimitiveCollection
from metatrack import ObjectFromMessage
from interface import iCalc
from aebs.fill.calc_mb79_raw_targets import X0, Y0, ANGLE0

signals = [{
    "Azimuth":      ("TA", "tracking_in_Azimuth"),
    "CoGDoppler":   ("TA", "tracking_in_CoGDoppler"),
    "PowerDB":      ("TA", "tracking_in_PowerDB"),
    "StdAzimuth":   ("TA", "tracking_in_StdAzimuth"),
    "CoGRange":     ("TA", "tracking_in_CoGRange"),
    "StdDoppler":   ("TA", "tracking_in_StdDoppler"),
    "StdRange":     ("TA", "tracking_in_StdRange"),
}]

side_signals = [{
    "NumOfDetectionsTransmitted":   ("TA", "tracking_in_NumOfDetectionsTransmitted"),
}]


class KBTargets(ObjectFromMessage):
  _attribs = tuple(signals[0].keys())

  dx0 = X0
  dy0 = Y0
  angle0_deg = ANGLE0

  def __init__(self, _id, common_time, group, mask, **kwargs):
    dir_corr = None  # no direction correction
    source = None  # source unnecessary as signals can be loaded directly from signal group
    super(KBTargets, self).__init__(_id, common_time, source, dir_corr, **kwargs)
    self._group = group
    self._mask = mask
    return

  def _create(self, signalName):
    arr = self._group.get_value(signalName)
    arr = arr[:, self._id]
    arr_copy = arr.copy()  # arr is read-only
    return np.ma.masked_array(arr_copy, mask=self._mask)

  def id(self):
    data = np.empty(self.range.shape, dtype=np.uint16)
    data.fill(self._id)
    return np.ma.masked_array(data, self._mask)

  def range(self):
    return np.sqrt(np.square(self.dx) + np.square(self.dy))

  def range_rate(self):
    return self._CoGDoppler

  def angle(self):
    return np.arctan2(self.dy, self.dx)

  def power(self):
    return self._PowerDB.astype(np.float)  # cast uint8 to float to satisfy interface dtype

  def dx(self):
    return self._CoGRange * np.cos(np.deg2rad(self._Azimuth + self.angle0_deg)) + self.dx0

  def dy(self):
    return self._CoGRange * np.sin(np.deg2rad(self._Azimuth + self.angle0_deg)) + self.dy0

  def vx(self):
    return self.range_rate * np.cos(np.deg2rad(self._Azimuth + self.angle0_deg))  # approximation (angle_rate = 0.0)

  def vy(self):
    return self.range_rate * np.sin(np.deg2rad(self._Azimuth + self.angle0_deg))  # approximation (angle_rate = 0.0)


class Calc(iCalc):
  side_sgs = side_signals
  sgs = signals

  def check(self):
    side_group = self.source.selectSignalGroup(self.side_sgs)
    group = self.source.selectSignalGroup(self.sgs)
    return group, side_group

  def fill(self, group, side_group):
    common_time, num_of_det = side_group.get_signal("NumOfDetectionsTransmitted")

    targets = PrimitiveCollection(common_time)
    for target_slot in xrange(np.max(num_of_det)):
      # '<' is used instead of '<=' because target slot index starts from 0
      mask = ~(target_slot < num_of_det)
      targets[target_slot] = KBTargets(target_slot, common_time, group, mask)
    return targets


if __name__ == '__main__':
  from config.Config import init_dataeval

  meas_path = r'\\file\Messdat\DAS\ConvertedMeas\TurningAssist\06xB365\2016-11-08-Clustering\B365__2016-11-08_11-11-31_resim_2016_12_02-11_23_53_more.mat'
  config, manager, manager_modules = init_dataeval(['-m', meas_path])
  mb79_targets = manager_modules.calc('calc_mb79_kb_targets@aebs.fill', manager)
  dummy_id, dummy_target = mb79_targets.iteritems().next()
  print dummy_id
  print dummy_target.range_rate
