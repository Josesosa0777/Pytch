# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from collections import OrderedDict

import numpy as np

from primitives.bases import PrimitiveCollection
from metatrack import ObjectFromMessage
import calc_mb79_common_time
from interface import iCalc

X0 = 0.0  # -2.69
Y0 = 0.0  # 1.25
ANGLE0 = -120.0  # -115.0

#NOTE: based on: PrivateCAN_MB79_NONASR_100Detection_complex_data_KB_change_0x101.dbc

# MB79_TARGET_DETECTION_100A
#     WRange10DB              0 to 9600   [m]      10 dB width of detection in range dimension (in m)
#     WDoppler10DB            0 to 28000  [m/s]    10 dB width of detection in Doppler dimension (in m/s)
#     Infrastructure          0 or 1      [1]      Target is stationary (infrastructure)
#     NoInfrastructure        0 or 1      [1]      Target is moving (with high confidence)
#     ValidXBeam              0 or 1      [1]      Validated by detection in other beam/measurement
#     ValidXBeamIndex         0 to 1023   [1]      Corresponding Index in detection list of other beam
#     Detected_beam_number    0 to 3      [1]      In which beam the corresponding detection was found
#     StdDoppler              0 to 1000   [m/s]    Standard deviation of Doppler measurement (in m/s)
#     StdRange                0 to 1000   [m]      Standard deviation of range measurement (m)

# MB79_TARGET_DETECTION_100B
#     PowerDB                 0 to 255    [dB]     Power of detection in dB
#!!   CoGRange    !!        0.0 to 96.0   [m]      Center of gravity range (in m)
#!!   CoGDoppler  !!     -140.0 to 14.0   [m/s]    Center of gravity Doppler (in m/s)
#!!   Azimuth     !!        -pi to pi     [deg]    Azimuth angle of detection (in degree in driving direction coordinate system)
#     StdAzimuth              0 to 255    [°]      Standard deviation of azimuth (in °)

# MB79_TARGET_DETECTION_100C !! Note: This message is transmitted only when requested
#     Complex1_Re
#     Complex1_Im
#     Complex2_Re
#     Complex2_Re

# MB79_TARGET_DETECTION_100D !! Note: This message is transmitted only when requested
#     Complex3_Re       -32768 to 3267 [1]    Complex FFT data (Re, Im) Rx channel 1
#     Complex3_Im       -32768 to 3267 [1]    Complex FFT data (Re, Im) Rx channel 1
#     Complex4_Re       -32768 to 3267 [1]    Complex FFT data (Re, Im) Rx channel 1
#     Complex4_Im       -32768 to 3267 [1]    Complex FFT data (Re, Im) Rx channel 1

MSG_ST_IDX = 1 # start index of messages

signals_template = (
  ('MB79_TARGET_DETECTION_%dB', 'CoGRange_%d'),
  ('MB79_TARGET_DETECTION_%dB', 'CoGDoppler_%d'),
  ('MB79_TARGET_DETECTION_%dB', 'Azimuth_%d'),
  ('MB79_TARGET_DETECTION_%dB', 'PowerDB_%d'),
  ('MB79_TARGET_DETECTION_%dB', 'StdAzimuth_%d'),
  ('MB79_TARGET_DETECTION_%dA', 'WRange10DB_%d'),
  ('MB79_TARGET_DETECTION_%dA', 'WDoppler10DB_%d'),
  ('MB79_TARGET_DETECTION_%dA', 'Infrastructure_%d'),
  ('MB79_TARGET_DETECTION_%dA', 'NoInfrastructure_%d'),
  ('MB79_TARGET_DETECTION_%dA', 'StdDoppler_%d'),
  ('MB79_TARGET_DETECTION_%dA', 'StdRange_%d'),
)

cut_signame = lambda sigtempl : sigtempl.split('_')[0]

class Mb79Target(ObjectFromMessage):
  _attribs = tuple( cut_signame(sigtempl) for devtempl,sigtempl in signals_template )

  # sensor position & orientation in reference (front bumper) coordinate frame
  # TODO: update with actual values
  dx0 = X0
  dy0 = Y0
  angle0_deg = ANGLE0

  def __init__(self, id, common_time, group, **kwargs):
    dir_corr = None # no direction correction
    source = None # source unnecessary as signals can be loaded directly from signal group
    super(Mb79Target, self).__init__(id, common_time, source, dir_corr, **kwargs)
    self._group = group
    return

  def _create(self, signame):
    arr = self._group.get_value(signame, ScaleTime=self._msgTime, Order='valid', InvalidValue=0)
    out = self._rescale(arr)
    return out

  def rescale(self, scaleTime, **kwargs):
    return Mb79Target(self._id, self._msgTime, self._group, scaleTime=scaleTime, **kwargs)

  def id(self):
    data = np.empty(self.range.size, dtype=np.uint8)
    data.fill(self._id)
    mask = self.range.mask
    return np.ma.masked_array(data, mask)

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
    return self.range_rate*np.cos(np.deg2rad(self._Azimuth + self.angle0_deg))  # approximation (angle_rate = 0.0)

  def vy(self):
    return self.range_rate*np.sin(np.deg2rad(self._Azimuth + self.angle0_deg))  # approximation (angle_rate = 0.0)


class Calc(iCalc):
  dep = 'calc_mb79_common_time',

  def check(self):
    common_time_group = self.source.selectSignalGroup(calc_mb79_common_time.sgs)
    num_targets = common_time_group.get_value("NumOfDetectionsTransmitted")
    max_num_targets = num_targets.max()
    groups = OrderedDict()
    # exclude even-numbered detections as their data is unusable
    # NumOfDetectionsTransmitted signal counts only the odd-numbered detections
    for msg_num in xrange(MSG_ST_IDX, 2*max_num_targets, 2):
      sg = { cut_signame(sigtempl) : (devtempl %msg_num, sigtempl %msg_num) for devtempl, sigtempl in signals_template }
      groups[msg_num] = self.source.selectSignalGroup( [sg] )
    return groups, num_targets

  def fill(self, groups, num_targets):
    common_time = self.modules.fill(self.dep[0])
    targets = PrimitiveCollection(common_time)
    for id, group in groups.iteritems():
      targets[id] = Mb79Target(id, common_time, group)
    # attach additional signals to collection
    targets.num_targets = num_targets
    return targets


if __name__ == '__main__':
  from config.Config import init_dataeval

  meas_path = r'\\corp.knorr-bremse.com\str\measure1\DAS\Turning_Assist\internal\06xB365\2016-06-21_MB79_SDS_Tracker_300detections\B365__2016-06-21_15-52-12.MF4'
  config, manager, manager_modules = init_dataeval(['-m', meas_path])
  mb79_targets = manager_modules.calc('calc_mb79_raw_targets@aebs.fill', manager)
  dummy_id, dummy_target = mb79_targets.iteritems().next()
  print dummy_id
  print dummy_target.range
