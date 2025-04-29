# -*- dataeval: init -*-

"""
Stores software version.
"""

import interface
from measproc import cIntervalList
from measproc.report2 import Report

class Search(interface.iSearch):
  entry_title = "(no title)"
  version_dep = None
  time_dep = None
  quantity_setters = () # optional (e.g. 'set_drivendistance@egoeval')
  
  def init(self):
    self.dep = {
      'time': self.time_dep,
      'version': self.version_dep,
    }
    self.optdep = self.quantity_setters
    return
  
  def fill(self):
    # get version and time
    time = self.modules.fill(self.dep['time'])
    ver = self.modules.fill(self.dep['version'])
    # create report
    report = Report(cIntervalList(time), self.entry_title)
    # add interval
    index = report.addInterval( (0, time.size) )
    # store version
    report.setComment(index, ver)
    # set general quantities
    for qua_setter in self.quantity_setters:
      if qua_setter in self.passed_optdep:
        set_qua_for_report = self.modules.get_module(qua_setter)
        set_qua_for_report(report)
      else:
        self.logger.warning("Inactive quantity setter: %s" % qua_setter)
    return report
  
  def search(self, report):
    self.batch.add_entry(report, result=self.PASSED)
    return
