# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "eval_inj_fault_type": ("Environment", "eval_inj_fault_type"),
  "eval_inj_fault_dtc_id_ok": ("Environment", "eval_inj_fault_dtc_id_ok"),
  "CAN_ID_msg_to_timeout": ("Environment", "CAN_ID_msg_to_timeout"),
  "eval_inj_fault_flag_ok": ("Environment", "eval_inj_fault_flag_ok"),
  "CAN_ID_msg_to_sgn_chg": ("Environment", "CAN_ID_msg_to_sgn_chg"),
  "ActiveFault04": ("ACC_S02", "ActiveFault04"),
  "ActiveFault03": ("ACC_S02", "ActiveFault03"),
  "ActiveFault02": ("ACC_S02", "ActiveFault02"),
  "ActiveFault01": ("ACC_S02", "ActiveFault01"),
  "AEBS1_AEBSState_2A": ("AEBS1_2A", "AEBS1_AEBSState_2A"),
  "Immediate_irrev_off_raised": ("CCP", "Immediate_irrev_off_raised"),
  "Controlled_irrev_off_raised": ("CCP", "Controlled_irrev_off_raised"),
  "Controlled_rev_off_raised": ("CCP", "Controlled_rev_off_raised"),
  "ReducedPerf_rev_raised": ("CCP", "ReducedPerf_rev_raised"),
  "Immediate_rev_off_raised": ("CCP", "Immediate_rev_off_raised"),
},
]


class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    client00 = datavis.cPlotNavigator(title="Error handler interface view")
    self.sync.addClient(client00)
    axis00 = client00.addAxis()
    time00, value00, unit00 = group.get_signal_with_unit("eval_inj_fault_dtc_id_ok")
    client00.addSignal2Axis(axis00, "eval_inj_fault_dtc_id_ok", time00, value00, unit=unit00)
    axis01 = client00.addAxis()
    time01, value01, unit01 = group.get_signal_with_unit("eval_inj_fault_flag_ok")
    client00.addSignal2Axis(axis01, "eval_inj_fault_flag_ok", time01, value01, unit=unit01)
    axis02 = client00.addAxis()
    time02, value02, unit02 = group.get_signal_with_unit("eval_inj_fault_type")
    client00.addSignal2Axis(axis02, "eval_inj_fault_type", time02, value02, unit=unit02)
    axis03 = client00.addAxis()
    time03, value03, unit03 = group.get_signal_with_unit("CAN_ID_msg_to_sgn_chg")
    time04, value04, unit04 = group.get_signal_with_unit("CAN_ID_msg_to_timeout")
    client00.addSignal2Axis(axis03, "CAN_ID_msg_to_sgn_chg", time03, value03, unit=unit03)
    client00.addSignal2Axis(axis03, "CAN_ID_msg_to_timeout", time04, value04, unit=unit04)
    axis04 = client00.addAxis()
    time05, value05, unit05 = group.get_signal_with_unit("AEBS1_AEBSState_2A")
    client00.addSignal2Axis(axis04, "AEBS1_AEBSState_2A", time05, value05, unit=unit05)
    axis05 = client00.addAxis()
    time06, value06, unit06 = group.get_signal_with_unit("ActiveFault01")
    time07, value07, unit07 = group.get_signal_with_unit("ActiveFault02")
    time08, value08, unit08 = group.get_signal_with_unit("ActiveFault03")
    time09, value09, unit09 = group.get_signal_with_unit("ActiveFault04")
    client00.addSignal2Axis(axis05, "ActiveFault01", time06, value06, unit=unit06)
    client00.addSignal2Axis(axis05, "ActiveFault02", time07, value07, unit=unit07)
    client00.addSignal2Axis(axis05, "ActiveFault03", time08, value08, unit=unit08)
    client00.addSignal2Axis(axis05, "ActiveFault04", time09, value09, unit=unit09)
    axis06 = client00.addAxis()
    time06, value06, unit06 = group.get_signal_with_unit("Immediate_rev_off_raised")
    time07, value07, unit07 = group.get_signal_with_unit("Immediate_irrev_off_raised")
    time08, value08, unit08 = group.get_signal_with_unit("Controlled_irrev_off_raised")
    time09, value09, unit09 = group.get_signal_with_unit("Controlled_rev_off_raised")
    time10, value10, unit10 = group.get_signal_with_unit("ReducedPerf_rev_raised")
    client00.addSignal2Axis(axis06, "Immediate_rev_off_raised", time06, value06, unit=unit06)
    client00.addSignal2Axis(axis06, "Immediate_irrev_off_raised", time07, value07, unit=unit07)
    client00.addSignal2Axis(axis06, "Controlled_irrev_off_raised", time08, value08, unit=unit08)
    client00.addSignal2Axis(axis06, "Controlled_rev_off_raised", time09, value09, unit=unit09)
    client00.addSignal2Axis(axis06, "ReducedPerf_rev_raised", time10, value10, unit=unit10)
    return
