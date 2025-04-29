import numpy

import interface
import measproc
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList

DefParam = interface.NullParam

timeSignalGroups = [
  {
    "year":   ("TD", "Year"),
    "month":  ("TD", "Month"),
    "day":    ("TD", "Day"),
    "hour":   ("TD", "Hour"),
    "minute": ("TD", "Minute"),
    "second": ("TD", "Second"),
  },
  {
    "year":   ("TD", "Year"),
    "month":  ("TD", "Month"),
    "day":    ("TD", "Day"),
    "hour":   ("TD", "Hours"),
    "minute": ("TD", "Minutes"),
    "second": ("TD", "Seconds"),
  },
  {
    "year":   ("Time_Date", "year"),
    "month":  ("Time_Date", "month"),
    "day":    ("Time_Date", "day"),
    "hour":   ("Time_Date", "hours"),
    "minute": ("Time_Date", "minutes"),
    "second": ("Time_Date", "seconds"),
  },
]

def ceilDay(day, hour):
  ceilOffset = numpy.empty_like(hour)
  ceilOffset.fill(0.5)

  hour = (hour+0.5).astype(int)
  
  ceilOffset[hour<18] = 0.75
  ceilOffset[hour<12] = 1.0
  ceilOffset[hour< 6] = 1.25

  day = (day+ceilOffset).astype(int)
  return day

class cSearch(interface.iSearch):
  def check(self):
    Source = self.get_source('main')
    group = Source.selectSignalGroup(timeSignalGroups)
    return group
  
  def fill(self, group):
    time = group.get_time('year')
    measDate = group.get_all_values(ScaleTime=time)
    measDate['day'] = ceilDay(measDate['day'], measDate['hour'])
    return time, measDate
  
  def search(self, param, time, measDate):
    batch = self.get_batch()
    date_quas = 'date'
    names = batch.get_quanamegroups(date_quas)
    report = Report(cIntervalList(time), 'AEBS-DateTime', names=names)
    for interval in [(0, 1), (time.size-1, time.size)]:
      idx = report.addInterval(interval)
      start, end = interval
      for qua_name, value in measDate.iteritems():
        report.set(idx, date_quas, qua_name, value[start])
    batch.add_entry(report)
    return

