# -*- dataeval: init -*-
from collections import OrderedDict

import interface
import datavis
from measparser.signalgroup import SignalGroupError
from aebs.fill.calc_bendix_acc_activity import Calc as AccCalc
from aebs.fill.calc_bendix_cmt_warning import Calc as CmtCalc
from aebs.fill.calc_bendix_umo import Calc as UmoCalc
from aebs.fill.calc_bendix_stat_obj_alert import Calc as StatCalc
from aebs.fill.calc_bendix_ldw import Calc as LdwCalc

from aebs.fill.calc_aebs_phases import Calc as KbCalc
from aebs.fill.calc_trw_aebs_phases import Calc as TrwCalc

MPS_2_KPH = 3.6

init_params = {
  'cmt': dict(group=CmtCalc.group),
  'acc': dict(group=AccCalc.group),
  'umo': dict(group=UmoCalc.group),
  'stat': dict(group=StatCalc.group),
  'ldw': dict(group=LdwCalc.group),
  'kb': dict(group=KbCalc.group),
  'trw': dict(group=TrwCalc.group),
}

class cView(interface.iView):
  group = {
    "actual_vehicle_speed": ("General_radar_status", "actual_vehicle_speed"),
    # "EEC1_EngSpd_00": ("EEC1_00", "EEC1_EngSpd_00"),
    # "VD_TotVehDist_00": ("VD_00", "VD_TotVehDist_00"),
    # gas and brake activation signals
    "EEC2_APPos1": ("EEC2_00", "EEC2_APPos1_00"),
    # "EBC1_BrkPedPos_0B": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
    "EBC1_EBSBrkSw": ("EBC1_0B", "EBC1_EBSBrkSw_0B"),
    # XBR signals
    "XBR_AccelDemand": ("XBRUS_2A", "XBRUS_AccelDemand_2A"),
    "XBR_ControlMode": ("XBRUS_2A", "XBRUS_ControlMode_2A"),
  }
  def init(self, group):
    self.group = self.group.copy()
    self.cond_group = OrderedDict(group)

    for alias in self.group.keys():
      if alias in self.cond_group:
        self.group[alias] = self.cond_group.pop(alias)
    
    self.group.update(self.cond_group)
    return

  def check(self):
    group = self.get_source().selectSignalGroup([self.group])
    return group

  def view(self, group):
    source = self.get_source()
    nav = datavis.cPlotNavigator(title="Ego vehicle", fontSize='medium')
    
    # pedals
    ax = nav.addAxis(ylabel='pedals')
    for alias, unit in [('EEC2_APPos1', '%'), ('EBC1_EBSBrkSw', '')]:
      time, value = group.get_signal(alias)
      nav.addSignal2Axis(ax, alias, time, value, unit=unit)

    # condition
    ax = nav.addAxis(ylabel='condition')
    for alias in self.cond_group:
      time, value = group.get_signal(alias)
      nav.addSignal2Axis(ax, alias, time, value)

    # XBR signals
    ax = nav.addAxis(ylabel='XBR')
    for alias, unit in [('XBR_AccelDemand', 'm/s$^2$'), ('XBR_ControlMode', '')]:
      time, value = group.get_signal(alias)
      nav.addSignal2Axis(ax, alias, time, value, unit=unit)

    interface.Sync.addClient(nav)
    return

