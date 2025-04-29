# -*- dataeval: init -*-

"""
TBD
"""

import view_quantity_vs_sensorstatus_stats
from aebs.par import camera_sensor_status

init_params = view_quantity_vs_sensorstatus_stats.init_params

class View(view_quantity_vs_sensorstatus_stats.View):
  labelmap = camera_sensor_status.label2maingroup
  show_none = False
  label2color = camera_sensor_status.maingroup2color
