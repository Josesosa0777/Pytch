import re

import numpy

from aebs.par.labels import default as label_groups
from measproc.IntervalList import maskToIntervals

class ActiveFault:
  FREE = 0xFFFF
  LABEL_GROUP = 'TRW active fault'
  dtc_id_label_pattern = re.compile('\\w+ \((0x[\\dA-F]+)\)')
  fault_id_label_pattern = re.compile('fault.+\(*(0x[\\dA-F]+)\)*')

  def __init__(self):
    _, label_group = label_groups[self.LABEL_GROUP]
    self.dtc_id_labels = {}
    self.fault_id_labels = {}
    for label in label_group:
      dtc_id_label = self.dtc_id_label_pattern.search(label)
      if dtc_id_label is not None:
        fault = int(dtc_id_label.group(1), base=16)
        self.dtc_id_labels[fault] = label
      fault_id_label = self.fault_id_label_pattern.search(label)
      if fault_id_label is not None:
        fault = int(fault_id_label.group(1), base=16)
        self.fault_id_labels[fault] = label
    return

  def __call__(self, report, value, is_dtc_id=True):
    for value, interval in self.slice(value, is_dtc_id):
      index = report.addInterval(interval)
      self.label(report, index, value, is_dtc_id)
    return

  def slice(self, value, is_dtc_id):
    values = numpy.unique(value).tolist()
    no_error = self.FREE if is_dtc_id else 0x0
    if no_error in values:
      values.remove(no_error)
    for fault in values:
      for interval in maskToIntervals(value == fault):
        yield fault, interval
    return

  def label(self, report, index, value, is_dtc_id):
    if is_dtc_id:
      labels = self.dtc_id_labels
    else:
      labels = self.fault_id_labels
    
    try:
      label = labels[value]
    except KeyError:
      label = 'UNKNOWN (0x%X)' % value
    report.vote(index, self.LABEL_GROUP, label)
    return

