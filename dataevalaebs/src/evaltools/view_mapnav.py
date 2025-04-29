"""
Interactive map visualizer (MapNavigator)

MapNavigator shows the traveled route based on
the measured GPS data. Additional functionalities, such as event visualization,
are also available.
The selected parameter determines the zoom level (detail level) of the map.
Map database has to be set.
"""

import datavis
import interface


class cParameter(interface.iParameter):
  def __init__(self, zoom):
    self.zoom = zoom
    self.genKeys()
    return

# instantiation of module parameters
AUTO_ZOOM = cParameter(None)
ZOOM_LEVEL_07 = cParameter(7)
ZOOM_LEVEL_08 = cParameter(8)
ZOOM_LEVEL_09 = cParameter(9)
ZOOM_LEVEL_10 = cParameter(10)
ZOOM_LEVEL_11 = cParameter(11)
ZOOM_LEVEL_12 = cParameter(12)
ZOOM_LEVEL_13 = cParameter(13)
ZOOM_LEVEL_14 = cParameter(14)
ZOOM_LEVEL_15 = cParameter(15)
ZOOM_LEVEL_16 = cParameter(16)

class cView(interface.iView):
  def view(self, param):
    # prepare navigator
    mapman = self.get_mapman()
    Client = datavis.MapNavigator(mapman)
    Client.addGroups(interface.Groups)
    Client.addStyles(interface.Legends)
    for StatusName in interface.Objects.get_selected_by_parent(interface.iGPSTrajectoryFill):
      Time, Traj = interface.Objects.fill(StatusName)
      Client.add_trajectory(Time, Traj)
    try:
      Client.set_route(zoom=param.zoom)
    except IOError:
      self.logger.warning("Inactive module: view_mapnav")
      self.logger.info("Reason:\nNo available GPS signal for trajectory visualization")
      return
 
    # Client.set_markers([(1200, 1500), (2000, 3200)], 'Test Event', event_marker_style='*', event_color='y')
    # Client.set_markers([(5100, 6500)], 'Test Event2', event_color='c', event_marker_style='v')
 
    self.sync.addClient(Client)
    return
