# -*- dataeval: init -*-

import logging

from aebs.abc import search_faults
from aebs.par.trw_active_faults import dtc2label
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report

__doc__ = search_faults.__doc__.replace(
  "Search for faults", "Search for FLR21 faults in ACC_S02 message")


def init_fault_report(batch, faults, title):
  votes = batch.get_labelgroups('FLR21 fault')
  names = batch.get_quanamegroups('fault identifier')
  return Report(cIntervalList(faults.time), title, votes=votes, names=names)

def set_fault_attributes(report, int_idx, value):
  if value in dtc2label:
    report.vote(int_idx, 'FLR21 fault', dtc2label[value])
  else:
    logging.getLogger().warning("Unknown DTC detected: %d" % value)
    report.vote(int_idx, 'FLR21 fault', "UNKNOWN")
  report.set(int_idx, 'fault identifier', 'DTC', value)
  return

class Search(search_faults.Search):
  fault_fill = 'view_smess_faults'
  
  quantity_setters = (
    'set_egospeed-start@egoeval',
    'set_egospeed-max@egoeval', 
    'set_drivendistance@egoeval',
  )
  
  @staticmethod
  def init_single_fault_report(batch, faults):
    title = "FLR21 faults - ACC_S02 - single"
    return init_fault_report(batch, faults, title)
  
  @staticmethod
  def init_combined_fault_report(batch, faults):
    title = "FLR21 faults - ACC_S02 - combined"
    return init_fault_report(batch, faults, title)
  
  @staticmethod
  def set_single_fault_attributes(report, int_idx, value):
    return set_fault_attributes(report, int_idx, value)
  
  @staticmethod
  def set_combined_fault_attributes(report, int_idx, value):
    return set_fault_attributes(report, int_idx, value)
