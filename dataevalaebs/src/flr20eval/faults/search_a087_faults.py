# -*- dataeval: init -*-

from aebs.abc import search_faults
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report

__doc__ = search_faults.__doc__.replace(
  "Search for faults", "Search for FLR21 faults on A087")


def init_fault_report(batch, faults, title):
  names = batch.get_quanamegroups('fault identifier')
  return Report(cIntervalList(faults.time), title, names=names)

def set_fault_attributes(report, int_idx, value):
  report.set(int_idx, 'fault identifier', 'ID', value)
  return

class Search(search_faults.Search):
  fault_fill = 'view_a087_faults'
  
  quantity_setters = (
    'set_egospeed-start@egoeval',
    'set_egospeed-max@egoeval', 
    'set_drivendistance@egoeval',
  )
  
  @staticmethod
  def init_single_fault_report(batch, faults):
    title = "FLR21 faults - A087 - single"
    return init_fault_report(batch, faults, title)
  
  @staticmethod
  def init_combined_fault_report(batch, faults):
    title = "FLR21 faults - A087 - combined"
    return init_fault_report(batch, faults, title)
  
  @staticmethod
  def set_single_fault_attributes(report, int_idx, value):
    return set_fault_attributes(report, int_idx, value)
  
  @staticmethod
  def set_combined_fault_attributes(report, int_idx, value):
    return set_fault_attributes(report, int_idx, value)
