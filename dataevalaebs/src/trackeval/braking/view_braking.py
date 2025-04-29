# -*- dataeval: init -*-

"""
Plot basic signals to check dynamic situations.

Plot speed and acceleration values of the ego vehicle and the primary target.
"""

import interface
import datavis


class View(interface.iView):
  dep = "fill_flr20_aeb_track@aebs.fill", "calc_flr20_egomotion@aebs.fill"
  
  def view(self):
    track = self.modules.fill(self.dep[0])
    ego_motion = self.modules.fill(self.dep[1])
    
    # create navigator
    pn = datavis.cPlotNavigator(title="Braking forward vehicle")
    # speeds
    ax = pn.addAxis(ylabel="speed", ylim=(-5.0, 90.0))
    pn.addSignal2Axis(ax, "ego speed", ego_motion.time, 3.6 * ego_motion.vx, unit="km/h")
    pn.addSignal2Axis(ax, "object speed", track.time, 3.6 * track.vx, unit="km/h")
    # accelerations
    ax = pn.addAxis(ylabel="acceleration", ylim=(-6.0, 3.0))
    pn.addSignal2Axis(ax, "ego acc.", ego_motion.time, ego_motion.ax, unit="m/s2")
    pn.addSignal2Axis(ax, "object acc.", track.time, track.ax_abs, unit="m/s2")
    #from search_braking import AX_THRESHOLD; ax.axhline(AX_THRESHOLD)
    # register navigator
    self.sync.addClient(pn)
    return
