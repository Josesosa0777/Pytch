# -*- dataeval: init -*-

"""
Stores the FLC20 software version.
"""

from aebs.abc import search_sw_version
import view_sw_version

init_params = view_sw_version.init_params

class Search(search_sw_version.Search):
  time_dep = "calc_flc20_common_time@aebs.fill"
  quantity_setters = ("set_drivendistance@egoeval",)
  
  def init(self, ver_type):
    self.entry_title = "FLC20 %s SW version" % ver_type
    self.version_dep = "view_sw_version-%s" % ver_type
    search_sw_version.Search.init(self)  # call parent
    return
