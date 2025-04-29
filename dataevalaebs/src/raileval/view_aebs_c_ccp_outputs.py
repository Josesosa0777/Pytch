# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"Visualize AEBS_C library outputs recorded by CCP"

from collections import OrderedDict

import datavis
import measproc
from interface import iView
from tceval.rail_eval_n_ccp_meas_handler import cAcquireSignals
from view_aebs_c_ccp_inputs import make_view


init_params = {
  'show_rail_maneuver': dict(show_rail_maneuver=True),
  'hide_rail_maeuver': dict(show_rail_maneuver=False),
}


view_content = OrderedDict([('bendoff', ['AEBS1_BendOff']),
                            ('relobj', ['AEBS1_RelevantObjectDetected']),
                            ('sysstate', ['AEBS1_SystemState']),
                            ('warnlev', ['AEBS1_WarningLevel']),
                            ('aebs1req', ['AEBS1_request']),
                            ('ttc', ['AEBS1_ttc']),
                            ('torquelim', ['TSC1_TorqueLimitation']),
                            ('tsc1req', ['TSC1_request']),
                            ('xbrdem', ['XBR_Demand']),
                            ('xbrreq', ['XBR_request'])])


class cView(iView, cAcquireSignals):
  def init(self, show_rail_maneuver):
    self.show_rail_maneuver = show_rail_maneuver
    return
  
  def view(self):
    # prepare version
    version_major, version_minor = self.get_version()
    version = "v%d.%d" %(version_major, version_minor)
    # create plot with version and current meas in title
    title = "AEBS_C %s outputs (%s)" %(version, self.source.getBaseName())
    pn = datavis.cPlotNavigator(title=title)
    # layout hack, see #1504
    pn.createWindowId = lambda x,title=None: "AEBS_C outputs"
    pn.getWindowId = lambda : "AEBS_C outputs"
    pn._windowId = pn.createWindowId(None)
    self.sync.addClient(pn)
    # get CCP input signals
    needed_sgn_names = []
    for sgn_name in view_content.itervalues():
      needed_sgn_names.extend(sgn_name)
    avail_sgn_names = self.available_in_ccp_output(*needed_sgn_names)
    ccp_output_signals = self.get_ccp_output_sgn(*avail_sgn_names, inc_units=True)
    
    if self.show_rail_maneuver:
      avail_rail_sgn_names = self.available_in_rail_eval('set_new_conditions')
      if avail_rail_sgn_names:
        rail_signals = self.get_rail_eval_sgn(*avail_rail_sgn_names)
        man_time, man_val = rail_signals['set_new_conditions']
        maneuver_intervals =\
          measproc.EventFinder.cEventFinder.compare(man_time, man_val,
                                                    measproc.not_equal, 0)
      else:
        maneuver_intervals = None
      make_view(pn, ccp_output_signals, view_content,
                rail_man_ints=maneuver_intervals)
    else:
      make_view(pn, ccp_output_signals, view_content)
    return
