# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis

def_param = interface.NullParam

sgs  = [
{
  "AEBS1_AEBSState"     : ("AEBS1_2A", "AEBS1_AEBSState_2A"),
  "CCVS_CCSetSpeed"     : ("CCVS_00", "CCVS_CCSetSpeed_00"),
  "CCVS_CCSetSwitch"    : ("CCVS_00", "CCVS_CCSetSwitch_00"),
  "CCVS_CCAccelSwitch"  : ("CCVS_00", "CCVS_CCAccelSwitch_00"),
  "CCVS_CCActive"       : ("CCVS_00", "CCVS_CCActive_00"),
  "CCVS_CCCoastSwitch"  : ("CCVS_00", "CCVS_CCCoastSwitch_00"),
  "CCVS_CCEnableSwitch" : ("CCVS_00", "CCVS_CCEnableSwitch_00"),
  "CCVS_CCPauseSwitch"  : ("CCVS_00", "CCVS_CCPauseSwitch_00"),
  "CCVS_CCResumeSwitch" : ("CCVS_00", "CCVS_CCResumeSwitch_00"),
  "XBR_Prio"            : ("XBR_2A", "XBR_Prio_2A"),
  "XBR_ExtAccelDem"     : ("XBR_2A", "XBR_ExtAccelDem_2A"),
},
{
  "AEBS1_AEBSState"     : ("AEBS1_2A", "AEBS1_AEBSState_2A"),
  "CCVS_CCSetSpeed"     : ("CCVS_27", "CCVS_CCSetSpeed_27"),
  "CCVS_CCSetSwitch"    : ("CCVS_27", "CCVS_CCSetSwitch_27"),
  "CCVS_CCAccelSwitch"  : ("CCVS_27", "CCVS_CCAccelSwitch_27"),
  "CCVS_CCActive"       : ("CCVS_27", "CCVS_CCActive_27"),
  "CCVS_CCCoastSwitch"  : ("CCVS_27", "CCVS_CCCoastSwitch_27"),
  "CCVS_CCEnableSwitch" : ("CCVS_27", "CCVS_CCEnableSwitch_27"),
  "CCVS_CCPauseSwitch"  : ("CCVS_27", "CCVS_CCPauseSwitch_27"),
  "CCVS_CCResumeSwitch" : ("CCVS_27", "CCVS_CCResumeSwitch_27"),
  "XBR_Prio"            : ("XBR_2A", "XBR_Prio_2A"),
  "XBR_ExtAccelDem"     : ("XBR_2A", "XBR_ExtAccelDem_2A"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    # create plot with version and current meas in title
    title = "ACC outputs (%s)" % (self.source.getBaseName())
    pn = datavis.cPlotNavigator(title=title)
    # layout hack, see #1504
    pn.createWindowId = lambda x, title=None: 'ACC outputs'
    pn.getWindowId = lambda: 'ACC outputs'
    pn._windowId = pn.createWindowId(None)
    self.sync.addClient(pn)
    axis00 = pn.addAxis()
    time00, value00, unit00 = group.get_signal_with_unit("AEBS1_AEBSState")
    pn.addSignal2Axis(axis00, "AEBS1_AEBSState", time00, value00, unit=unit00)
    axis01 = pn.addAxis()
    time01, value01, unit01 = group.get_signal_with_unit("CCVS_CCSetSpeed")
    pn.addSignal2Axis(axis01, "CCVS_CCSetSpeed", time01, value01, unit=unit01)
    axis02 = pn.addAxis()
    time02, value02, unit02 = group.get_signal_with_unit("CCVS_CCSetSwitch")
    pn.addSignal2Axis(axis02, "CCVS_CCSetSwitch", time02, value02, unit=unit02)
    time03, value03, unit03 = group.get_signal_with_unit("CCVS_CCAccelSwitch")
    pn.addSignal2Axis(axis02, "CCVS_CCAccelSwitch", time03, value03, unit=unit03)
    time04, value04, unit04 = group.get_signal_with_unit("CCVS_CCActive")
    pn.addSignal2Axis(axis02, "CCVS_CCActive", time04, value04, unit=unit04)
    time05, value05, unit05 = group.get_signal_with_unit("CCVS_CCCoastSwitch")
    pn.addSignal2Axis(axis02, "CCVS_CCCoastSwitch", time05, value05, unit=unit05)
    time06, value06, unit06 = group.get_signal_with_unit("CCVS_CCEnableSwitch")
    pn.addSignal2Axis(axis02, "CCVS_CCEnableSwitch", time06, value06, unit=unit06)
    time07, value07, unit07 = group.get_signal_with_unit("CCVS_CCPauseSwitch")
    pn.addSignal2Axis(axis02, "CCVS_CCPauseSwitch", time07, value07, unit=unit07)
    time08, value08, unit08 = group.get_signal_with_unit("CCVS_CCResumeSwitch")
    pn.addSignal2Axis(axis02, "CCVS_CCResumeSwitch", time08, value08, unit=unit08)
    axis03 = pn.addAxis()
    time09, value09, unit09 = group.get_signal_with_unit("XBR_Prio")
    pn.addSignal2Axis(axis03, "XBR_Prio", time09, value09, unit=unit09)
    axis04 = pn.addAxis()
    time10, value10, unit10 = group.get_signal_with_unit("XBR_ExtAccelDem")
    pn.addSignal2Axis(axis04, "XBR_ExtAccelDem", time10, value10, unit=unit10)
    return
