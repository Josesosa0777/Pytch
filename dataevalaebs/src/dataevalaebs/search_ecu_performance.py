# -*- dataeval: init -*-
import numpy

from interface.Interfaces import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList


class Search(iSearch):
  group = {
    "proc_load": ("General_radar_status", "processor_time_used"),
  }

  def check(self):
    group = self.get_source().selectSignalGroup([self.group])
    return group

  def fill(self, group):
    time, proc_load = group.get_signal('proc_load')
    proc_load =  proc_load / 100.0

    # list quatity groups
    ecu_qua = 'ecu performance'
    # create report
    batch = self.get_batch()
    quas = batch.get_quanamegroups(ecu_qua)
    report = Report(cIntervalList(time), 'ECU-performance', names=quas)

    # fill quantities
    ## set processor load quantities
    idx = report.addInterval((0, time.size))
    report.set(idx, ecu_qua, 'processor load min', proc_load.min())
    report.set(idx, ecu_qua, 'processor load max', proc_load.max())
    report.set(idx, ecu_qua, 'processor load avg', proc_load.mean())
    ## set cycle time quantities
    dt = numpy.diff(time)
    report.set(idx, ecu_qua, 'cycle time min', dt.min())
    report.set(idx, ecu_qua, 'cycle time max', dt.max())
    report.set(idx, ecu_qua, 'cycle time avg', dt.mean())
    return report

  def search(self, report):
    self.get_batch().add_entry(report)
    return
    
