# -*- dataeval: init -*-

"""
Search for faults

Register faults into two separate reports:
* single fault report (1 interval <-> 1 fault):
  contains the individual fault intervals
* combined fault report (1 interval <-> 0/1/multiple faults):
  contains the combined intervals with all active faults attached to them
This redundancy enables easier database queries.
"""

import numpy as np

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report

class Search(iSearch):
  fault_fill = None
  quantity_setters = ()
  
  def init(self):
    self.optdep = self.quantity_setters
    self.dep = dict(faults=self.fault_fill)
    return
  
  def fill(self):
    faults, = self.modules.fill(self.fault_fill)
    reports = []
    
    # create single fault report
    report = self.init_single_fault_report(self.batch, faults)
    for fault in faults:
      jumps = np.ediff1d(fault.data, to_begin=1, to_end=1) != 0
      jump_idxs = np.where(jumps)[0]
      for i in xrange(len(jump_idxs)-1):
        st, end = jump_idxs[i : i+2]
        value = fault[st]
        if value is not np.ma.masked:
          int_idx = report.addInterval((st, end))
          self.set_single_fault_attributes(report, int_idx, value)
    reports.append(report)
    
    # create combined fault report
    report = self.init_combined_fault_report(self.batch, faults)
    jumps = np.zeros(faults.time.size+1, dtype=bool)
    for fault in faults:
      jumps |= np.ediff1d(fault.data, to_begin=1, to_end=1) != 0
    jump_idxs = np.where(jumps)[0]
    for i in xrange(len(jump_idxs)-1):
      st, end = jump_idxs[i : i+2]
      for fault in faults:
        value = fault[st]
        int_idx = report.addSingletonInterval((st, end))
        if value is not np.ma.masked:
          self.set_combined_fault_attributes(report, int_idx, value)
    reports.append(report)
    
    # set general quantities
    for report in reports:
      for qua_setter in self.quantity_setters:
        if qua_setter in self.passed_optdep:
          set_qua_for_report = self.modules.get_module(qua_setter)
          set_qua_for_report(report)
        else:
          self.logger.warning("Inactive quantity setter: %s" % qua_setter)
    return reports
  
  def search(self, reports):
    for report in reports:
      self.batch.add_entry(report)
    return
  
  
  @staticmethod
  def init_single_fault_report(batch, faults):
    title = "(no title)"
    votes = batch.get_labelgroups()
    names = batch.get_quanamegroups()
    return Report(cIntervalList(faults.time), title, votes=votes, names=names)
  
  @staticmethod
  def init_combined_fault_report(batch, faults):
    title = "(no title)"
    votes = batch.get_labelgroups()
    names = batch.get_quanamegroups()
    return Report(cIntervalList(faults.time), title, votes=votes, names=names)
  
  @staticmethod
  def set_single_fault_attributes(report, int_idx, value):
    return
  
  @staticmethod
  def set_combined_fault_attributes(report, int_idx, value):
    return
