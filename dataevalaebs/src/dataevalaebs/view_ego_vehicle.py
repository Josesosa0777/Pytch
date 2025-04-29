# -*- dataeval: init -*-
from collections import OrderedDict, namedtuple

import interface
import datavis

MPS_2_KPH = 3.6

init_params = {
  'kb': dict(calc='calc_aebs_phases@aebs.fill'),
  'trw': dict(calc='calc_trw_aebs_phases@aebs.fill'),
  'flr20': dict(calc='calc_flr20_aebs_phases-radar@aebs.fill'),
  'autobox': dict(calc='calc_flr20_aebs_phases-autobox@aebs.fill'),
}

class cView(interface.iView):
  group = {
    "actual_vehicle_speed": ("General_radar_status", "actual_vehicle_speed"),
    # "EEC1_EngSpd_00": ("EEC1_00", "EEC1_EngSpd_00"),
    # "VD_TotVehDist_00": ("VD_00", "VD_TotVehDist_00"),
    # gas and brake activation signals
    "EEC2_APPos1": ("EEC2_00", "EEC2_APPos1_00"),
    "EBC1_BrkPedPos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
    # "EBC1_EBSBrkSw": ("EBC1_0B", "EBC1_EBSBrkSw_0B"),
    # XBR signals
    "XBR_AccelDemand": ("XBR_2A", "XBR_ExtAccelDem_2A"),
    "XBR_ControlMode": ("XBR_2A", "XBR_CtrlMode_2A"),
  }
  def init(self, calc):
    self.dep = namedtuple('Dep', ['calc'])(calc)
    self.group = self.group.copy()
    return

  def check(self):
    calc = self.get_modules().get_module(self.dep.calc)
    self.cond_group = OrderedDict(calc.group)

    for alias in self.group.keys():
      if alias in self.cond_group:
        self.group[alias] = self.cond_group.pop(alias)

    self.group.update(self.cond_group)

    group = self.get_source().selectSignalGroup([self.group])
    return group

  def view(self, group):
    phases = self.get_modules().fill(self.dep.calc)
    nav = datavis.cPlotNavigator(title="Ego vehicle", fontSize='medium')

    # pedals
    ax = nav.addAxis(ylabel='pedals', ylim=(-5.0, 105.0))
    for alias, unit in [('EEC2_APPos1', '%'), ('EBC1_BrkPedPos', '%')]:
      time, value = group.get_signal(alias)
      nav.addSignal2Axis(ax, alias, time, value, unit=unit)

    # condition
    ax = nav.addAxis(ylabel='condition', ylim=(-0.5, 8.0))
    for alias in sorted(self.cond_group):  # sorted: hack
      value = group.get_value(alias, ScaleTime=phases.time)
      nav.addSignal2Axis(ax, alias, phases.time, value)

    # XBR signals
    ax = nav.addAxis(ylabel='XBR', ylim=(-11.0, 11.0))
    for alias, unit in [('XBR_AccelDemand', 'm/s$^2$'), ('XBR_ControlMode', '')]:
      value = group.get_value(alias, ScaleTime=phases.time)
      nav.addSignal2Axis(ax, alias, phases.time, value, unit=unit)

    interface.Sync.addClient(nav)
    return

