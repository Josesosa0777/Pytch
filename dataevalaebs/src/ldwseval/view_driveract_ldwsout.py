# -*- dataeval: init -*-

"""
Plot basic driver activities and LDWS outputs

LDWS-relevant driver activities (pedal activation, steering etc.) and
LDWS outputs (in FLI1/FLI2 messages) are shown.
"""

import numpy as np

import datavis
from interface import iView

class View(iView):
  def check(self):
    sgs = [{
      # driver
      "accped_pos":      ("EEC2_00", "EEC2_APPos1_00"),
      "brkped_pos":      ("EBC1_0B", "EBC1_BrkPedPos_0B"),
      "steer_angle":     ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
      "dir_ind":         ("OEL_21", "OEL_TurnSigSw_21"),  # SA 0x21
      # ldws
      "ldws_state":      ("FLI2_E8", "FLI2_StateOfLDWS"),
      "warn_left":       ("FLI1_E8", "FLI1_LaneDepartImminentLeft_E8"),
      "warn_right":      ("FLI1_E8", "FLI1_LaneDepartImminentRight_E8"),
    }, {
      # driver
      "accped_pos":      ("EEC2_00", "EEC2_APPos1_00"),
      "brkped_pos":      ("EBC1_0B", "EBC1_BrkPedPos_0B"),
      "steer_angle":     ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
      "dir_ind":         ("OEL_E6", "OEL_TurnSigSw_E6"),  # SA 0xE6
      # ldws
      "ldws_state":      ("FLI2_E8", "FLI2_StateOfLDWS"),
      "warn_left":       ("FLI1_E8", "FLI1_LaneDepartImminentLeft_E8"),
      "warn_right":      ("FLI1_E8", "FLI1_LaneDepartImminentRight_E8"),
    }, {
      # driver
      "accped_pos":      ("EEC2_00", "EEC2_APPos1_00"),
      "brkped_pos":      ("EBC1_0B", "EBC1_BrkPedPos_0B"),
      "steer_angle":     ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
      "dir_ind":         ("OEL_27", "OEL_TurnSigSw_27"),  # SA 0x27
      # ldws
      "ldws_state":      ("FLI2_E8", "FLI2_StateOfLDWS"),
      "warn_left":       ("FLI1_E8", "FLI1_LaneDepartImminentLeft_E8"),
      "warn_right":      ("FLI1_E8", "FLI1_LaneDepartImminentRight_E8"),
    }]
    # select signals
    group = self.source.selectLazySignalGroup(sgs)
    # give warning for not available signals
    for alias in sgs[0]:
      if alias not in group:
        self.logger.warning("Signal for '%s' not available" % alias)
    return group
  
  def view(self, group):
    pn = datavis.cPlotNavigator(title="Driver activities and LDWS outputs")
    
    ax = pn.addAxis(ylabel="pos.", ylim=(-5.0, 105.0))
    # accel. pedal
    if 'accped_pos' in group:
      time00, value00, unit00 = group.get_signal_with_unit("accped_pos")
      pn.addSignal2Axis(ax, "accel. p. pos.", time00, value00, unit=unit00)
    # brake pedal
    if 'brkped_pos' in group:
      time02, value02, unit02 = group.get_signal_with_unit("brkped_pos")
      pn.addSignal2Axis(ax, "brake p. pos.", time02, value02, unit=unit02)
    
    # steering wheel
    ax = pn.addAxis(ylabel="angle", ylim=(-100.0, 100.0))
    if 'steer_angle' in group:
      time04, value04, unit04 = group.get_signal_with_unit("steer_angle")
      if unit04 == "rad" or not unit04:  # assuming rad if unit is empty
        value04 = np.rad2deg(value04)
        unit04 = "deg"
      pn.addSignal2Axis(ax, "steering wheel angle", time04, value04, unit=unit04)
    # direction indicator
    yticks = {0: "none", 1: "left", 2: "right", 3: "n/a"}
    yticks = dict( (k, "%d (%s)"%(k,v)) for k, v in yticks.iteritems() )
    ax = pn.addTwinAxis(ax, ylabel="state", ylim=(-1.0, 4.0), yticks=yticks, color='g')
    if 'dir_ind' in group:
      time05, value05, unit05 = group.get_signal_with_unit("dir_ind")
      pn.addSignal2Axis(ax, "dir. indicator", time05, value05, unit=unit05)
    
    # LDWS state
    yticks = {0: "not ready", 1: "temp. n/a", 2: "deact.", 3: "ready",
              4: "override", 5: "warning",
              14: "error", 15: "n/a"}
    yticks = dict( (k, "(%s) %d"%(v,k)) for k, v in yticks.iteritems() )
    ax = pn.addAxis(ylabel="state", yticks=yticks)
    ax.set_ylim((-1.0, 8.0))
    if 'ldws_state' in group:
      time00, value00, unit00 = group.get_signal_with_unit("ldws_state")
      pn.addSignal2Axis(ax, "LDWS State", time00, value00, unit=unit00)
    
    # LDWS warning side
    yticks = {0: "none", 1: "left", 2: "right", 3: "n/a"}
    yticks = dict( (k, "(%s) %d"%(v,k)) for k, v in yticks.iteritems() )
    ax = pn.addAxis(ylabel="side", ylim=(-1.0, 4.0), yticks=yticks)
    if 'warn_left' in group and 'warn_right' in group:
      time05, value05, unit05 = group.get_signal_with_unit("warn_left")
      time06, value06, unit06 = group.get_signal_with_unit("warn_right")
      warn_side = np.minimum(value05 + 2.0*value06, 3.0)
      pn.addSignal2Axis(ax, "LDWS warning side", time05, warn_side)
    
    self.sync.addClient(pn)
    return
