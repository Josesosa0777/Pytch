import numpy

import measproc
import interface
import aebs.sdf.asso_cvr3_sCam_cipv
from aebs.sdf.asso_cvr3_sCam_cipv import SCAM_MESSAGE_NUM
from measparser.signalgroup import SignalGroupList
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report

from searchSensorCheck_CVR3 import set_sensorcheck

DefParam = interface.NullParam

NAN = float('nan')

sCamSignalGroups = list(aebs.sdf.asso_cvr3_sCam_cipv.sCamSignalGroups)
sCamRefSignalGroups = [{'Refpoint_X': ('Host_Vehicle', 'Refpoint_X')}]

egoVelocitySG = []
for device in ('RadarFC', 'MRR1plus', 'ECU'):
  egoVelocitySG.append({
    'vxvRef': (device, 'evi.General_TC.vxvRef'),
  })

QUANTITY_INFO = 'Unit', 'Description'
QUANTITIES_CORE = {
  'availability': (
    '%',
    'Ratio of the time KB-Cam Advanced was actively available and the total\n'
    'time, given in percentage.',
  ),
}
QUANTITIES_REPEAT = {
  'ObstacleData%02d_maxTime': (
    's',
    'Maximum of the time signal (i.e. last time instance) of KB-Cam Advanced\n'
    ' message Obstacle_Data_%02d.',
   ),
  'ObstacleData%02d_meanCT': (
    's',
    'Average of the cycle time of KB-Cam Advanced message \n'
    'Obstacle_Data_%02d.',
  ),
  'ObstacleData%02d_minTime': (
    's',
    'Minimum of the time signal (i.e. first time instance) of KB-Cam \n'
    'Advanced message Obstacle_Data_%02d.',
  ),
  'ObstacleData%02d_numOfLongLapse': (
    '1',
    'Number of lapses/drop-outs that were longer than 3-4 cycles in KB-Cam \n'
    'Advanced message Obstacle_Data_%02d.',
  ),
}

QUANTITIES_BOUND = 1, 11
QUANTITIES = QUANTITIES_CORE.copy()
for i in xrange(*QUANTITIES_BOUND):
  for name, (unit, description) in QUANTITIES_REPEAT.iteritems():
    QUANTITIES[name % i] = unit, description % i

class cSearch(interface.iSearch):
  def check(self):
    source = self.get_source('main')
    sCamGroups = SignalGroupList.from_arbitrary(sCamSignalGroups, source)
    egoGroup = source.selectSignalGroup(egoVelocitySG)
    sCamRefGroup = source.selectSignalGroup(sCamRefSignalGroups)
    return sCamGroups, egoGroup, sCamRefGroup
    
  def fill(self, sCamGroups, egoGroup, sCamRefGroup):
    egoVehTime, egoVehVel = egoGroup.get_signal('vxvRef')
    minTime = egoVehTime.min()
    maxTime = egoVehTime.max()
    totalTime = maxTime - minTime
    
    time, value = sCamRefGroup.get_signal('Refpoint_X')
    mask = numpy.zeros(time.size, dtype=bool)
    mask[1:] = numpy.diff(time) <= 0.2
    sCamAvailables = cIntervalList.fromMask(time, mask)
    
    sCamAvailSum = 0.0
    for lower, upper in sCamAvailables:
      sCamAvailSum += (time[upper-1] - time[lower])
    sCamAvailSum = min(sCamAvailSum, totalTime)
    
    dic = {
      'timeTotal':     (totalTime, True),
      'timeAvailable': (sCamAvailSum, True),
    }

    value = (sCamAvailSum / totalTime) * 100
    isValid = (100.0 - value) <= 0.05
    dic['availability'] = (value, isValid)

    obs_dics = []
    for group in sCamGroups:
      obs_dic = {}
      t, _ = group.get_signal('Pos_X')
      dt = numpy.diff(t)
      
      value = t.min()
      valid = value - minTime <= 0.01
      obs_dic['minTime'] = value, valid

      value = t.max()
      valid = value - maxTime <= 0.01
      obs_dic['maxTime'] = value, valid

      value = dt.mean()
      valid = value < 0.2
      obs_dic['meanCT'] = value, valid

      mask = numpy.zeros(t.size, dtype=bool)
      mask[1:] = dt >= 0.6
      intervals = cIntervalList.fromMask(t, mask)
      value = len(intervals)
      valid = value == 0
      obs_dic['numOfLongLapse'] = value, valid

      obs_dics.append(obs_dic)
    return egoVehTime, dic, obs_dics, sCamAvailables
 
  def search(self, param, time, dic, obs_dics, sCamAvailables):
    batch = self.get_batch()
   
    check_votes = 'sensor check'
    obs_votes = 'S-Cam obstacle data'
    check_quas = 'S-Cam sensor check'
    intervals = cIntervalList(time)
    names = batch.get_quanamegroups(check_quas)
    votes = batch.get_labelgroups(check_votes, obs_votes)
    report = Report(intervals, 'SensorCheck', names=names, votes=votes)

    interval = 0, time.size
    set_sensorcheck(dic, report, check_quas, check_votes, interval)
  
    for i, dic in enumerate(obs_dics):
      ids = set_sensorcheck(dic, report, check_quas, check_votes, interval)
      for idx in ids:
        report.vote(idx, obs_votes, str(i + 1))
    batch.add_entry(report, tags=['S-Cam'])

    result = self.PASSED if sCamAvailables else self.FAILED
    report = Report(sCamAvailables, 'SensorCheck-SCamAvailable')
    batch.add_entry(report, result, tags=['S-Cam'])
    return

