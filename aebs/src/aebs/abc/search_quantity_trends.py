# -*- coding: utf-8 -*-

"""
Abstract class to search for quantity trends (blindness, misalignment, ..)
"""

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals


class SearchQuantity(iSearch):
  """ register quantities into database by partitioning a signal's range
  and setting them as events

  assumptions:
  (1) bins cover the whole signal range
  """

  # class variables to control behavior (to be overridden in descendant class)
  sgs = None            # only 1 signal expected
  quanamegroup = None   # e.g. 'AC100 sensor check'
  quaname_base = None   # e.g. 'covi'
  title = None          # optional (by default alias is used as report title)
  bins = ()             # use np.linspace to create bins (np.arange unreliable for endpoints)
  quantity_setters = () # optional (e.g. 'set_drivendistance@egoeval')
  quantity_types = {    # extend or override if necessary
    'min' : np.min,
    'max' : np.max,
  }

  def init(self):
    self.optdep = self.quantity_setters
    return

  def check(self):
    group = self.source.selectSignalGroup(self.sgs)
    assert len(group) == 1, 'Only 1 signal expected, but more given: %s' %group
    return group

  def fill(self, group):
    alias = group.iterkeys().next()
    time, report = self._create_report(group, alias)
    value = group.get_value(alias)
    # check if signal is not outside bin range
    bin_min = self.bins[0]
    bin_max = self.bins[-1]
    value_min = value.min()
    value_max = value.max()
    if value_min < bin_min or value_max > bin_max:
      self.logger.warn('%s min-max %.1f-%.1f outside bin range %.1f-%.1f' %(alias, value_min, value_max, bin_min, bin_max))
    # change signal's quantization (partition signal range)
    for lower,upper in zip(self.bins, self.bins[1::]): # (1)
      mask_lower = value >= lower
      # special care for endpoint
      op = np.less_equal if upper == self.bins[-1] else np.less
      mask_upper = op(value, upper)
      partition = mask_lower & mask_upper
      for interval in maskToIntervals(partition):
        self._set_quantity(report, interval, alias, value)
    # sort events over time (instead of value range partitions)
    report.sort()
    # set general quantities
    self._set_general_quantities(report)
    return report

  def search(self, report):
    result = self.FAILED if report.isEmpty() else self.PASSED
    self.batch.add_entry(report, result=result)
    return

  def _create_report(self, group, alias):
    time = group.get_time(alias)
    title = self.title or alias
    names = self.batch.get_quanamegroups(self.quanamegroup)
    report = Report(cIntervalList(time), title, names=names)
    return time, report

  def _set_quantity(self, report, interval, alias, value, index=None):
    if index is None:
      index = report.addInterval(interval)
    st,end = interval
    quaname_base = self.quaname_base or alias
    for qua_type, op in self.quantity_types.iteritems():
      qua_value = op( value[st:end] )
      report.set(index, self.quanamegroup, '%s %s' % (quaname_base,qua_type), qua_value)
    return

  def _set_general_quantities(self, report):
    for qua_setter in self.quantity_setters:
      if qua_setter in self.passed_optdep:
        set_qua_for_report = self.modules.get_module(qua_setter)
        set_qua_for_report(report)
      else:
        self.logger.warning("Inactive quantity setter: %s" % qua_setter)
    return


class SearchBasedOnEvent(SearchQuantity):
  """ find events and register corresponding quantities into database

  assumptions:
  (1) events can be found based on 1 signal
  (2) by default, event signal is assumed to be an error indicator (behavior can be overridden)
  """
  event_signame = None

  def _find_event_mask(self, group):
    error = group.get_value(self.event_signame) # (1),(2)
    mask = error != 0
    return mask

  def _find_intervals(self, group):
    mask = self._find_event_mask(group)
    return maskToIntervals(mask)

  def check(self):
    group = self.source.selectSignalGroup(self.sgs)
    return group

  def fill(self, group):
    time, report = self._create_report(group, self.event_signame) # (1)
    intervals = self._find_intervals(group)
    # if no event found, return with empty report
    if not intervals:
      return report
    # set quantities for events
    for alias in group:
      if alias == self.event_signame:
        continue
      t = group.get_time(alias)
      # rescale signal if not on event signal's time
      kwargs = {} if t is time else dict(ScaleTime=time)
      value = group.get_value(alias, **kwargs)
      for interval in intervals:
        index = report.addSingletonInterval(interval)
        self._set_quantity(report, interval, alias, value, index=index)
    # set general quantities
    self._set_general_quantities(report)
    return report
