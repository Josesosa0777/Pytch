# -*- dataeval: init -*-

import numpy as np

from interface import iCalc
from primitives.bases import PrimitiveCollection
from measparser.signalgroup import select_allvalid_sgs
from metatrack import ObjectFromMessage
from flr20_raw_tracks_base import template2signame
from calc_flr20_egomotion import is_left_positive

__version__ = 'A087MB_V3.2_MH8_truck' # reference to dbc file

N_AC100_TARGETS = 26

# optional track signal templates (not all the tracks might be present)
ac100signalTemplates = (
  'ta%d_angle_LSB',
  'ta%d_angle_MSB',
  'ta%d_FSK_relative_velocitiy',
  'ta%d_power',
  'ta%d_primary_FSK_range',
  'ta%d_range',
  'ta%d_range_flags',
  'ta%d_relative_velocitiy',
  'ta%d_secondary_FSK_range',
  'ta%d_target_flags_LSB',
  'ta%d_target_flags_MSB',
  'ta%d_target_status',
  'ta%d_tracking_flags',
)

signalCorrection = {
  'angle_LSB'        : dict(dtype='>u1'), # wrongly recorded as signed integer # TODO: newer A087 dbc file is fixed - correction should be removed
  'target_flags_MSB' : dict(factor=2**5), # LSB-length (5bit) up-shift needed
}

messageGroups = []
for m in xrange(N_AC100_TARGETS):
  messageGroup = {}
  for signalTemplate in ac100signalTemplates:
    fullName = signalTemplate %m
    shortName = template2signame(signalTemplate)
    messageGroup[shortName] = ('Targets', fullName)
  messageGroups.append(messageGroup)

sgs = [
  {"number_of_targets": ("General_radar_status", "number_of_targets"),},
]


class Flr20Target(ObjectFromMessage):
  _attribs = tuple(template2signame(tmpl) for tmpl in ac100signalTemplates)

  def __init__(self, id, msgTime, source, dirCorr, group, num_targets,
               scaleTime=None, **kwargs):
    super(Flr20Target, self).__init__(id, msgTime, source, dirCorr,
                                      scaleTime=scaleTime, **kwargs)
    self._group = group
    self._num_targets = num_targets
    self._is_not_available = (id >= num_targets.data) | num_targets.mask
    return

  def _create(self, signalName):
    # keyword arguments to override signal parsing
    kwargs = signalCorrection[signalName] if signalName in signalCorrection else {}
    # load signal
    arr = self._source.getSignalFromSignalGroup(self._group, signalName,
            ScaleTime=self._msgTime, Order='valid', InvalidValue=0, **kwargs)[1]
    arr.mask &= self._is_not_available # invalid target slot might be sent on CAN
    out = self._rescale(arr)
    return out

  def rescale(self, scaleTime, **kwargs):
    return Flr20Target(self._id, self._msgTime, self._source, self._dirCorr,
                       self._group, self._num_targets, scaleTime=scaleTime, **kwargs)

  def id(self):
    data = np.repeat( np.uint8(self._id), self.time.size )
    arr = np.ma.masked_array(data, mask=self.range.mask)
    return arr

  def angle(self):
    return self._dirCorr * np.deg2rad( self._angle_MSB + self._angle_LSB )

  def range(self):
    return self._range

  def dx(self):
    return self.range * np.cos(self.angle)

  def dy(self):
    return self.range * np.sin(self.angle)

  def vx(self):
    return self.range_rate  # approximation

  def range_rate(self):
    return self._relative_velocitiy

  def power(self):
    return self._power

  def target_flags(self):
    return self._target_flags_LSB + self._target_flags_MSB


class cFill(iCalc):
  dep = 'calc_flr20_common_time',

  def check(self):
    commonTime = self.modules.fill('calc_flr20_common_time')
    filtgroups = self.source.filterSignalGroups(messageGroups)
    optgroups = select_allvalid_sgs(filtgroups, len(ac100signalTemplates),
                                    message='Missing radar target data!')
    group = self.source.selectSignalGroup(sgs)
    return commonTime, optgroups, group

  def fill(self, msgTime, optgroups, group):
    # check for y coord axis direction correction
    dirCorr = 1 if is_left_positive(self.source) else -1
    num = self.source.getSignalFromSignalGroup(group, "number_of_targets",
            ScaleTime=msgTime, Order='valid', InvalidValue=0)[1]
    # create empty targets
    targets = PrimitiveCollection(msgTime)
    for id, optgroup in enumerate(optgroups):
      targets[id] = Flr20Target(id, msgTime, self.source, dirCorr, optgroup, num)
    return targets
