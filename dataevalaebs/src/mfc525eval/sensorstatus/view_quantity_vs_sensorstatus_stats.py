# -*- dataeval: init -*-

"""
Sum up the driven distance [km] and time [h] using result of the script 
"search_sensorstatus".
Road type based mileages and durations are also shown.
"""

from collections import OrderedDict

from aebs.abc import view_quantity_vs_status_stats
from aebs.par import camera_sensor_status

init_params = view_quantity_vs_status_stats.init_params

class View(view_quantity_vs_status_stats.View):
  label_group = 'camera status'
  search_class = 'mfc525eval.sensorstatus.search_sensorstatus.Search'
  
  base_title = "MFC525 sensor status"
  label2color = camera_sensor_status.label2color
  
  # redefine label order (but don't group or rename anything)
  labelmap = OrderedDict((l,l) for l in (
    'Fully Operational',
    'Warming up / Initializing',
    'Misaligned',
    'Slightly Blocked',
    'Partially Blocked',
    'Blocked',
    'Reserved',
    'Error',
    'NotAvailable',
  ))
  
  # group labels: hide 'Reserved' and show as 'Error'
  #labelmap = OrderedDict((
  #  ('Fully Operational', 'Fully Operational'),
  #  ('Warming up / Initializing', 'Warming up / Initializing'),
  #  ('Misaligned', 'Misaligned'),
  #  ('Slightly Blocked', 'Slightly Blocked'),
  #  ('Partially Blocked', 'Partially Blocked'),
  #  ('Blocked', 'Blocked'),
  #  ('Reserved', 'Error'),  # hide 'Reserved' and show as 'Error'
  #  ('Error', 'Error'),
  #  ('NotAvailable', 'NotAvailable'),
  #))
  #show_none = False
