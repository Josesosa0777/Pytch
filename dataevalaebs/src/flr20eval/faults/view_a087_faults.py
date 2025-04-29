# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"Plots the three most relevant internal faults in FLR21."

from collections import OrderedDict

import numpy as np

import interface
import datavis
from primitives.bases import TuplePrimitive

N_FAULTS = 3
FAULT_ID_MAX = 500
INVALID_ID = 0xFFFF

sg = OrderedDict(); sgs = [sg]
for i in xrange(1, N_FAULTS+1):
  # bit 8
  signal_name = "fault_%01d_ID_bit8" % i
  sg[signal_name] = ("General_radar_status", signal_name)
  # bits 0..7
  signal_name = "fault_%01d_ID" % i
  sg[signal_name] = ("General_radar_status", signal_name)


class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group
  
  def fill(self, group):
    time = group.get_time("fault_1_ID")  # ASSUMPTION: all signals in same msg
    fault_list = []
    for i in xrange(1, N_FAULTS+1):
      # extract value
      msb = group.get_value("fault_%01d_ID_bit8" % i).astype(np.uint16)
      lsb = group.get_value("fault_%01d_ID" % i).astype(np.uint16)
      raw_fault = (msb << 8) + lsb
      # process value
      raw_fault[raw_fault == 0] = INVALID_ID  # 0=invalid --> map to a pre-defined value
      mask = raw_fault == INVALID_ID
      fault = np.ma.masked_array(raw_fault, mask=mask, fill_value=INVALID_ID)
      fault_list.append(fault)
    faults = TuplePrimitive(time, fault_list)
    return faults,
  
  def view(self, faults):
    pn = datavis.cPlotNavigator(title="FLR21 faults - A087")
    fault_mapping = {i: str(i) for i in xrange(FAULT_ID_MAX+1)}
    fault_mapping[INVALID_ID] = "--"
    yticks = range(0, FAULT_ID_MAX+1, 100)
    yticklabels = [str(i) for i in yticks]
    for i, fault in enumerate(faults):
      ax = pn.addAxis(ylabel="ID", yticks=fault_mapping)  # yticks for legend
      ax.set_yticks(yticks)  # yticks for y axis
      ax.set_yticklabels(yticklabels)  # yticks for y axis
      ax.set_ylim((-1, FAULT_ID_MAX+1))  # limit *after* yticks provided
      pn.addSignal2Axis(ax, "fault_%01d" % (i+1), faults.time, fault.data)
    self.sync.addClient(pn)
    return
