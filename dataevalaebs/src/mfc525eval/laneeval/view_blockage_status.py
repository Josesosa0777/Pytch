# -*- dataeval: init -*-

from aebs.abc import view_quantity_vs_status_stats

init_params = view_quantity_vs_status_stats.init_params

class View(view_quantity_vs_status_stats.View):
  label_group = 'FLC25 Blockage state'
  search_class = 'mfc525eval.laneeval.search_flc25_lane_blockage_detection.Search'
  show_none = False
  base_title = "FLC25 Blockage State"
  label2color = {
    'CB_UNKNOWN_STATUS':       (0.0, 1.0, 0.0),
    'CB_NO_BLOCKAGE':          (0.0, 0.8, 0.0),
    'CB_CONDENSATION':         (0.0, 0.6, 0.0),
    'CB_TOP_PART_BLOCKAGE':    (0.0, 0.4, 0.0),
    'CB_BOTTOM_PART_BLOCKAGE': (0.5, 0.5, 0.5),
    'CB_BLOCKAGE':             (0.0, 0.0, 0.0),
    'CB_LEFT_PART_BLOCKAGE':   (1.0, 0.0, 0.0),
    'CB_RIGHT_PART_BLOCKAGE':  (1.0, 0.0, 0.0),
  }

