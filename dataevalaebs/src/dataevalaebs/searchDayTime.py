import os

import interface
import measproc

DefParam = interface.NullParam

__type__ = 'search-2.0'

deviceNames = 'MRR1plus', 'RadarFC'

egoVelocitySG = []
for device in deviceNames:
  tmpSignalGroup = {}
  tmpSignalGroup['evi.General_TC.vxvRef'] = (device, 'evi.General_TC.vxvRef')
  egoVelocitySG.append(tmpSignalGroup)

# day light times (between these hours) at Stuttgart (from: http://www.gaisma.com/en/location/stuttgart.html)
# dict(month = (start time, end time))
DAY_LIGHT_TIMES = {1:  (8, 16),
                   2:  (8, 17),
                   3:  (7, 18),
                   4:  (7, 20),
                   5:  (6, 21),
                   6:  (6, 21),
                   7:  (6, 21),
                   8:  (6, 21),
                   9:  (7, 19),
                   10: (8, 18),
                   11: (8, 16),
                   12: (8, 16)}

class cSearch(interface.iSearch):
  def check(self):
    Source = self.get_source('main')
    egoGroups = Source.selectSignalGroup(egoVelocitySG)
    return egoGroups
  
  def fill(self, egoGroups):
    Source = self.get_source('main')
    Batch = self.get_batch()

    title = 'Day time (day or night) of measurements'
    votes = Batch.get_labelgroups('daytime')
    
    egoVehTime, egoVehVel = Source.getSignalFromSignalGroup(egoGroups, 'evi.General_TC.vxvRef')
    egoIntervalsTCTime = measproc.cIntervalList(egoVehTime)
    report = measproc.report2.Report(egoIntervalsTCTime, title, votes)
    
    # determine daytime according to month
    fileName  = Source.FileName
    measName = os.path.split(fileName)[-1]
    measDate, measTime = os.path.splitext(measName)[0].split('_')[-2:]
    measMonth = int(measDate.split('-')[1])
    measHour, measMinutes = measTime.split('-')[0:2]
    measHM = float(measHour) + (float(measMinutes) / 60)
    
    dayBoundLower, dayBoundUpper = DAY_LIGHT_TIMES[measMonth]
    interval = (0, egoVehTime.size)
    
    if dayBoundLower <= measHM and measHM <= dayBoundUpper:
      index = report.addInterval(interval)
      report.vote(index, 'daytime', 'day')
    else:
      index = report.addInterval(interval)
      report.vote(index, 'daytime', 'night')
    
    return report
  
  def search(self, param, report):
    Batch = self.get_batch()
    result = self.FAILED if report.isEmpty() else self.PASSED
    Batch.add_entry(report, result=result)
    return
  
