# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"Plots the four most relevant active faults in FLR21."

from collections import OrderedDict

import numpy as np

import interface
import datavis
from primitives.bases import TuplePrimitive
from aebs.par.trw_active_faults import trw_active_faults

N_FAULTS = 4
FAULT_ID_MAX = 500  # limit to avoid memory overuse
INVALID_ID = 0xFFFF

ENABLE_HACK_FOR_MAN = True

sg = OrderedDict(); sgs = [sg]
for i in xrange(1, N_FAULTS+1):
  signal_name = "ActiveFault%02d" % i
  sg[signal_name] = ("ACC_S02", signal_name)

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group
  
  def fill(self, group):
    time = group.get_time("ActiveFault01")  # ASSUMPTION: all signals in same msg
    fault_list = []
    for alias in sg:
      raw_fault = group.get_value(alias).astype('<u2')  # upcast to avoid e.g. uint8 dtype if all values are small
      if ENABLE_HACK_FOR_MAN:
        if self.source.BaseName.startswith(("MAN_GV", "GV_TGX", "B365")):
          raw_fault[raw_fault == 127] = INVALID_ID  # ignore FAULT_SIGNAL_ERROR_EBC5_XBR_STATE (0x7F)
      mask = raw_fault == INVALID_ID
      fault = np.ma.masked_array(raw_fault, mask=mask, fill_value=INVALID_ID)
      fault_list.append(fault)
    faults = TuplePrimitive(time, fault_list)
    return faults,
  
  def view(self, faults):
    pn = datavis.cPlotNavigator(title="FLR21 faults - ACC_S02")
    fault_mapping = dict(enumerate(trw_active_faults[:FAULT_ID_MAX+1]))
    fault_mapping[INVALID_ID] = "--"
    yticks = range(0, FAULT_ID_MAX+1, 100)
    yticklabels = [str(i) for i in yticks]
    for i, fault in enumerate(faults):
      ax = pn.addAxis(ylabel="DTC", yticks=fault_mapping)  # yticks for legend
      ax.set_yticks(yticks)  # yticks for y axis
      ax.set_yticklabels(yticklabels)  # yticks for y axis
      ax.set_ylim((-1, FAULT_ID_MAX+1))  # limit *after* yticks provided
      pn.addSignal2Axis(ax, "ActiveFault%02d" % (i+1), faults.time, fault.data)
    self.sync.addClient(pn)
    return
