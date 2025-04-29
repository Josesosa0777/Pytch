# -*- dataeval: init -*-

"""
Helper window to select Groups, i.e. activate/deactivate object visualization
filters.
Same functionality is available in several navigators via key press events.
"""

import datavis
import interface

class View(interface.iView):
  def view(self):
    GN = datavis.cGroupNavigator()
    self.sync.addClient(GN)    
    GN.addGroups(interface.Groups)
    return [GN]
