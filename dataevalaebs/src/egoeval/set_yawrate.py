# -*- dataeval: init -*-

"""
Store yaw rate for a report.

Set the yaw rate as quantity for each interval of the given report.
For usage example, see e.g. search_events@ldwseval.
"""

from aebs.abc import set_signal_quantity

init_params = set_signal_quantity.init_params

class Calc(set_signal_quantity.Calc):
  # attributes overridden
  dep = 'calc_egomotion@aebs.fill',
  quantity_group = 'ego vehicle'
  quantity_base = 'yaw rate'
  
  # method overridden
  def calc_signal(self, fill):
    return fill.yaw_rate
