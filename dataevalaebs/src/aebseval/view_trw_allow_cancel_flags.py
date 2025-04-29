# -*- dataeval: init -*-

"Plot TRW allow-entry and cancel flags for AEBS"

import interface
import datavis

class View(interface.iView):
  def check(self):
    sgs = [{
      "cw_cancel": ("ACC_S30", "cw_cancel"),
      "cm_allow_entry_global_conditions": ("ACC_S30", "cm_allow_entry_global_conditions"),
      "cmb_allow_entry": ("ACC_S30", "cmb_allow_entry"),
      "cmb_cancel": ("ACC_S30", "cmb_cancel"),
      "cm_cancel_global_conditions": ("ACC_S30", "cm_cancel_global_conditions"),
      "cw_allow_entry": ("ACC_S30", "cw_allow_entry"),
    }]
    group = self.source.selectSignalGroup(sgs)
    return group

  def view(self, group):
    client00 = datavis.cPlotNavigator(title="TRW allow-entry and cancel flags")
    self.sync.addClient(client00)
    axis00 = client00.addAxis()
    time02, value02, unit02 = group.get_signal_with_unit("cm_allow_entry_global_conditions")
    client00.addSignal2Axis(axis00, "cm_allow_entry_global_conditions", time02, value02, unit=unit02)
    time01, value01, unit01 = group.get_signal_with_unit("cw_allow_entry")
    client00.addSignal2Axis(axis00, "cw_allow_entry", time01, value01, unit=unit01)
    time00, value00, unit00 = group.get_signal_with_unit("cmb_allow_entry")
    client00.addSignal2Axis(axis00, "cmb_allow_entry", time00, value00, unit=unit00)
    axis01 = client00.addAxis()
    time03, value03, unit03 = group.get_signal_with_unit("cm_cancel_global_conditions")
    client00.addSignal2Axis(axis01, "cm_cancel_global_conditions", time03, value03, unit=unit03)
    time05, value05, unit05 = group.get_signal_with_unit("cw_cancel")
    client00.addSignal2Axis(axis01, "cw_cancel", time05, value05, unit=unit05)
    time04, value04, unit04 = group.get_signal_with_unit("cmb_cancel")
    client00.addSignal2Axis(axis01, "cmb_cancel", time04, value04, unit=unit04)
    return
