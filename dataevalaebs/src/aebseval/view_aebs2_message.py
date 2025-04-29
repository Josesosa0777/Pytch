# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"Show and check AEBS2 CAN message"

import numpy as np

import interface
import datavis
from measparser.signalgroup import SignalGroup

aebs2_sas = (0x17, 0x21, 0x27, 0x30, 0xE6)  # possible source addresses for AEBS2
sgs = { sa:
{
  "AEBS2_DriverActDemand": ("AEBS2_%X" % sa, "AEBS2_DriverActDemand_%X" % sa),
  "AEBS2_MessageChkSum": ("AEBS2_%X" % sa, "AEBS2_MessageChkSum_%X" % sa),
  "AEBS2_MessageCnt": ("AEBS2_%X" % sa, "AEBS2_MessageCnt_%X" % sa),
}
for sa in aebs2_sas
}

class View(interface.iView):
  def check(self):
    group = SignalGroup.from_named_signalgroups(sgs, self.source)
    return group
  
  def view(self, group):
    client00 = datavis.cPlotNavigator(title="AEBS2 message")
    aebs2_id = 0xC0B2A00 + group.winner
    
    axis00 = client00.addAxis()
    time00, value00, unit00 = group.get_signal_with_unit("AEBS2_DriverActDemand")
    client00.addSignal2Axis(axis00, "AEBS2_DriverActDemand", time00, value00, unit=unit00)
    
    axis01 = client00.addAxis()
    time01, value01, unit01 = group.get_signal_with_unit("AEBS2_MessageCnt")
    client00.addSignal2Axis(axis01, "AEBS2_MessageCnt", time01, value01, unit=unit01)
    axis01 = client00.addAxis()
    cnt_diff = np.diff(value01.astype(np.int16))
    cnt_problem = (cnt_diff != 1) & (cnt_diff != -15)
    client00.addSignal2Axis(axis01, "Cnt problem", time01[:-1], cnt_problem, unit=unit01)
    
    axis02 = client00.addAxis()
    time02, value02, unit02 = group.get_signal_with_unit("AEBS2_MessageChkSum")
    client00.addSignal2Axis(axis02, "AEBS2_MessageChkSum", time02, value02, unit=unit02)
    chksum_calc = calc_aebs2_checksum(aebs2_id, value01, value00)
    client00.addSignal2Axis(axis02, "ChkSum calculated [ID:0x%X]" % aebs2_id, time02, chksum_calc)
    axis02 = client00.addAxis()
    chksum_problem = chksum_calc != value02
    client00.addSignal2Axis(axis02, "ChkSum problem [ID:0x%X]" % aebs2_id, time02, chksum_problem)
    
    self.sync.addClient(client00)
    return

def calc_aebs2_checksum(msg_id, counter, driver_demand, empty_bit_value=True):
  """
  :Parameters:
    msg_id: int
    counter: np.ndarray or int
    driver_demand: np.ndarray or int
    empty_bit_value: bool, optional
  """
  msg_id = msg_id & 0x7FFFFFFF  # can_pl.c: /*This is done to ignore the Extended Id bit*/
  tmp_checksum = np.array(driver_demand, dtype=np.uint16)
  if empty_bit_value:
    tmp_checksum += 252 + 6*255
  tmp_checksum += np.bitwise_and(counter, 0x0F)
  tmp_checksum += (msg_id & 0xFF000000) >> 24
  tmp_checksum += (msg_id & 0x00FF0000) >> 16
  tmp_checksum += (msg_id & 0x0000FF00) >> 8
  tmp_checksum += (msg_id & 0x000000FF)
  checksum = np.bitwise_and(np.right_shift(tmp_checksum, 4) + tmp_checksum, 0x0F)
  return checksum
