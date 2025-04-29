# -*- dataeval: init -*-

"""
Stores the FLR21 software version.
"""

from aebs.abc import search_sw_version

class Search(search_sw_version.Search):
  entry_title = "FLR21 SW version"
  version_dep = "view_sw_version"
  time_dep = "calc_flr20_common_time@aebs.fill"
  quantity_setters = ("set_drivendistance@egoeval",)
