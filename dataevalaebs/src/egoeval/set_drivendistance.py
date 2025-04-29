# -*- dataeval: init -*-

"""
Store driven distance for a report.

Set the driven distance as quantity for each interval of the given report.
For usage example, see e.g. search_aebs_warning@dataevalaebs.
"""

import numpy as np

from aebs.abc import set_interval_quantity

class Calc(set_interval_quantity.Calc):
  # attributes overridden
  dep = 'calc_egomotion@aebs.fill',
  quantity_group = 'ego vehicle'
  quantity = 'driven distance'
  
  # method overridden
  def calc_quantity(self, fill, start, end):
    dist = np.trapz(fill.vx[start:end], fill.time[start:end])/1000.0 # [m]->[km]
    return dist
