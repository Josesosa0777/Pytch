# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"Visualize AEBS_C library inputs recorded by CCP"

from collections import OrderedDict

import datavis
import measproc
from interface import iView
from tceval.rail_eval_n_ccp_meas_handler import cAcquireSignals


init_params = {
  'show_rail_maneuver': dict(show_rail_maneuver=True),
  'hide_rail_maeuver': dict(show_rail_maneuver=False),
}

view_content =\
  OrderedDict([('tracks_dist', ['dxv', 'dyv']),
               ('tracks_vel', ['vxv', 'vyv']),
               ('tracks_stance', ['Valid_b', 'Stopped_b', 'Stand_b', 'Drive_b',
                                  'AdditionalSensorAssociated_b']),
               ('ego_vref', ['vRef']),
               ('ego_aref', ['aRef', 'axv']),
               ('engine_speed', ['EngineSpeed']),
               ('pedal_pos', ['GPPos', 'BPPos']),
               ('steering_wheel', ['alpSteeringWheel']),
               ('driver_override_flags', ['DriverActivationDemand_b',
                                          'DirIndL_b', 'DirIndR_b', 'BPAct_b',
                                          'GPKickdown_B', 'ReverseGearDetected_b']),
               ('allow_cancel_flags', ['CWAllowEntry_b', 'CMAllowEntry_b',
                                       'CMBAllowEntry_b', 'CWCancel_b',
                                       'CMCancel_b', 'CMBCancel_b']),
               ('fault_flags', ['ControlledIrrevOffRaised_b',
                                'ControlledRevOffRaised_b',
                                'ImmediateIrrevOffRaised_b',
                                'ImmediateRevOffRaised_b',
                                'ReducedPerformance_b',
                                'FusionOperational_b'])])

pn_incs_in_twinax = {'tracks_dist': ['dyv'],
                     'tracks_vel': ['vyv']}

modif_ticks = ['driver_override_flags', 'allow_cancel_flags', 'fault_flags',
               'tracks_stance']

sign_flip = {}


def _calc_offset(modif_ticks, ax_content, sgn_name):
  sgn_idx = ax_content.index(sgn_name)
  if modif_ticks:
    displayscaled = False
    tick_zip = zip(modif_ticks.keys(), modif_ticks.values())
    offset_vals = [k for (k, v) in tick_zip if v == 0]
    offset_vals.sort(reverse=True)
    offset = offset_vals[sgn_idx]
  else:
    displayscaled = True
    offset = None
  return offset, displayscaled

def make_view(nav, sgn_signals, content, **kwargs):
  if 'pn_incs_in_twinax' in kwargs:
    pn_incs_in_twinax = kwargs['pn_incs_in_twinax']
  else:
    pn_incs_in_twinax = {}
  if 'modif_ticks' in kwargs:
    modif_ticks = kwargs['modif_ticks']
  else:
    modif_ticks = {}
  if 'sign_flip' in kwargs:
    sign_flip = kwargs['sign_flip']
  else:
    sign_flip = {}
  if 'rail_man_ints' in kwargs:
    rail_man_ints = kwargs['rail_man_ints']
  else:
    rail_man_ints = None
  
  for ax_name, ax_content in content.iteritems():
    present_sgn_names = set(sgn_signals.keys()).intersection(set(ax_content))
    twinax_req = ax_name in pn_incs_in_twinax
    sign_flip_req = ax_name in sign_flip
    ax_modif_ticks = None
    twin_modif_ticks = None
    if ax_name in modif_ticks:
      if twinax_req:
        sgn_cnt = len(pn_incs_in_twinax[ax_name])
        twin_modif_ticks =\
          dict( (k,v) for k,v in zip(xrange(2*sgn_cnt), [0,1]*sgn_cnt) )
      else:
        sgn_cnt = len(present_sgn_names)
        ax_modif_ticks =\
          dict( (k,v) for k,v in zip(xrange(2*sgn_cnt), [0,1]*sgn_cnt) )
    if present_sgn_names:
      axis = nav.addAxis(yticks=ax_modif_ticks)
      if twinax_req:
        twin_axis = nav.addTwinAxis(axis, color='g', yticks=twin_modif_ticks)
      for sgn_name in ax_content:
        if sgn_name in sgn_signals:
          time, value, unit = sgn_signals[sgn_name]
          if twinax_req and sgn_name in pn_incs_in_twinax[ax_name]:
            plt_axis = twin_axis
            offset, displayscaled = _calc_offset(twin_modif_ticks,
                                                 ax_content, sgn_name)
          else:
            plt_axis = axis
            offset, displayscaled = _calc_offset(ax_modif_ticks,
                                                 ax_content, sgn_name)
          if sign_flip_req and sgn_name in sign_flip[ax_name]:
            value = value * (-1.0)
          nav.addSignal2Axis(plt_axis, sgn_name, time, value, unit=unit,
                             offset=offset, displayscaled=displayscaled)
      # include RaIL maneuver intervals if requested
      if rail_man_ints:
        rail_man_ints = rail_man_ints.rescale(time)
        for start, end in rail_man_ints.iterTime():
          axis.axvspan(start, end, facecolor='b', alpha=0.07)
  return

class View(iView, cAcquireSignals):
  def init(self, show_rail_maneuver):
    self.show_rail_maneuver = show_rail_maneuver
    return
  
  def view(self):
    # prepare version
    version_major, version_minor = self.get_version()
    version = "v%d.%d" %(version_major, version_minor)
    # create plot with version and current meas in title
    title = "AEBS_C %s inputs (%s)" %(version, self.source.getBaseName())
    pn = datavis.cPlotNavigator(title=title)
    # layout hack, see #1504
    pn.createWindowId = lambda x,title=None: "AEBS_C inputs"
    pn.getWindowId = lambda : "AEBS_C inputs"
    pn._windowId = pn.createWindowId(None)
    self.sync.addClient(pn)
    # get CCP input signals
    needed_sgn_names = []
    for sgn_name in view_content.itervalues():
      needed_sgn_names.extend(sgn_name)
    avail_sgn_names = self.available_in_ccp_input(*needed_sgn_names)
    ccp_input_signals = self.get_ccp_input_sgn(*avail_sgn_names, inc_units=True)
    
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
      make_view(pn, ccp_input_signals, view_content,
                pn_incs_in_twinax=pn_incs_in_twinax, sign_flip=sign_flip,
                modif_ticks=modif_ticks, rail_man_ints=maneuver_intervals)
    else:
      make_view(pn, ccp_input_signals, view_content,
                pn_incs_in_twinax=pn_incs_in_twinax, sign_flip=sign_flip,
                modif_ticks=modif_ticks)
    return
