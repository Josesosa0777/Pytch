# -*- dataeval: init -*-

"""
Sum up the driven distance [km] and time [h] using result of the script 
"search_flc25_LDWS_state".
Road type based mileages and durations are also shown.
"""

from aebs.abc import view_quantity_vs_status_stats

init_params = view_quantity_vs_status_stats.init_params

class View(view_quantity_vs_status_stats.View):
  label_group = 'FLC25 LDWS state'
  search_class = 'mfc525eval.laneeval.search_flc25_LDWS_state.Search'
  show_none = False
  base_title = "FLC25 ldws\nstate ready"
  label2color = {
  'not ready':        (0.5, 0.5, 0.5),
  'temp. not avail':  (0.8, 0.8, 0.0),
  'deact. by driver': (1.0, 0.5, 0.0),
  'ready':            (0.0, 0.5, 0.0),
  'driver override':  (0.5, 0.0, 0.5),
  'warning':          (1.0, 0.0, 0.0),
  'error':            (0.5, 0.0, 0.0),
  }