# -*- dataeval: init -*-

"""
Store ego speed for a report.

Set the ego speed as quantity for each interval of the given report.
For usage example, see e.g. search_events@aebseval.
"""

from aebs.abc import set_signal_quantity

init_params = set_signal_quantity.init_params

class Calc(set_signal_quantity.Calc):
  # attributes overridden
  dep = 'calc_egomotion@aebs.fill',
  quantity_group = 'ego vehicle'
  quantity_base = 'speed'
  
  # method overridden
  def calc_signal(self, fill):
    return fill.vx
