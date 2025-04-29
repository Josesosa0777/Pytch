# -*- dataeval: init -*-
import numpy

import interface
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList

from searchSensorCheck_CVR3 import set_sensorcheck

signalGroups = []
for device in 'MRR1plus', 'RadarFC':
  signalGroups.append({
    "multimedia": ("Multimedia", "Multimedia_1"),
    "scaletime":  (device,       "dsp.LocationData_TC.tAbsMeasTimeStamp"),
  })

QUANTITY_INFO =                 ("Unit", "Description", )
QUANTITIES = {
  "videoAvailability": (
    "1",
    "Ratio of the durations of multimedia signal and scaletime.",
  ),
  "videoFps_mean": (
    "1/s",
    "Mean value of the video frame rate.",
  ),
  "videoFps_min": (
    "1/s",
    "Minimum value of the video frame rate.",
  ),
  "videoTimeDer_max": (
    "1",
    "Maximum of the time derivative of the multimedia signal.",
  ),
  "videoTimeDer_mean": (
    "1",
    "Mean value of the time derivative of the multimedia signal.",
  ),
  "videoTimeDer_min": (
    "1",
    "Minimum of the time derivative of the multimedia signal.",
  ),
}

class cSearch(interface.iSearch):
  def check(self):
    source = self.get_source()
    group = source.selectSignalGroup(signalGroups, StrictTime=True,
                                     TimeMonGapIdx=5)
    return group

  def fill(self, group):
    NAN = float('nan')

    multimedia_time, multimedia_value = group.get_signal("multimedia")
    dtmdtm = numpy.diff(multimedia_value) / numpy.diff(multimedia_time)
    fps = 1.0 / numpy.diff(multimedia_value)

    dic = {}

    scaleTime = group.get_time('scaletime')
    if scaleTime.size > 1:
      scaleTimeDuration = scaleTime[-1] - scaleTime[0]
    else:
      scaleTimeDuration = 0.0

    if scaleTimeDuration:
      value = (multimedia_time[-1] - multimedia_time[0]) / scaleTimeDuration
    else:
      value = NAN
    isValid = 0.95 < value < 1.05
    dic['videoAvailability'] = (value, isValid)
    
    if multimedia_value.size > 1:
      value = multimedia_value.size / (multimedia_value[-1]-multimedia_value[0])
    else:
      value = NAN
    isValid = value > 5.0 and value < 60.0
    dic['videoFps_mean'] = (value, isValid)
    
    value = fps.min() if fps.size > 0 else NAN
    isValid = 4.0 < value < 60.0
    dic['videoFps_min'] = (value, isValid)
    
    value = dtmdtm.min() if dtmdtm.size > 0 else NAN
    isValid = value > 0.5
    dic['videoTimeDer_min'] = (value, isValid)
    
    value = dtmdtm.max() if dtmdtm.size > 0 else NAN
    isValid = value < 2.0
    dic['videoTimeDer_max'] = (value, isValid)
    
    if dtmdtm.size:
      value  = multimedia_value[-1] - multimedia_value[0]
      value /= multimedia_time[-1]  - multimedia_time[0]
    else:
      value = NAN
    isValid = 0.85 < value < 1.15
    dic['videoTimeDer_mean'] = (value, isValid)
    return multimedia_time, dic

  def search(self, time, dic):
    batch = self.get_batch()
    check_votes = 'sensor check'
    check_quas = 'CANape sensor check'
    votes = batch.get_labelgroups(check_votes)
    names = batch.get_quanamegroups(check_quas)
    intervals = cIntervalList(time)
    
    report = Report(intervals, 'SensorCheck', names=names, votes=votes)

    set_sensorcheck(dic, report, check_quas, check_votes, (0, time.size))
    batch.add_entry(report, tags=['CANape'])
    return

