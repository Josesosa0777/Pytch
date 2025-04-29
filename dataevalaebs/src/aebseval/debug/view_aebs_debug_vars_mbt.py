# -*- dataeval: init -*-

"""
Plot AEBS debug information from simulation
"""

import os.path

from debugutils.gdb import debug

from interface import iView
from datavis import cPlotNavigator
from aebs.fill import calc_aebs_c_sil
from pyutils.enum import enum
from aebseval.sim.view_driveract_aebsout_sim import shorten_dpv


init_params = calc_aebs_c_sil.init_params

thisdir = os.path.dirname(__file__)
cmd_fpath = os.path.abspath( os.path.join(thisdir, "aebs.gdb") )

mstState_t = enum(
  "IDLE",
  "REACTIONSUPPORTSTAT",
  "REACTIONSUPPORTMOV",
  "LANECHANGE",
)

mstCascaseState_t = enum(
	"IDLE",
	"WAITFORWARNING",
	"WARNING",
	"PARTIAL",
	"EMERGENCY",
	"ICB",
	"SSB",
)

def as_yticks(myenum):
  return { v:k for k,v in myenum._asdict().iteritems() }


class View(iView):
  def init(self, dpv):
    self.dpv = dpv
    self.dep = {
      'aebs_c_sil' : 'calc_aebs_c_sil_mbt-%s@aebs.fill' %dpv
    }
    return

  @debug(cmd_fpath, tidy=False)
  def fill(self):
    t, inp, par, out_sim, internals = self.modules.fill( self.dep['aebs_c_sil'] )
    print out_sim
    return t, inp, par, out_sim, internals

  def view(self, fill_res, dbg_arr):
    t, inp, par, out_sim, internals = fill_res
    version = calc_aebs_c_sil.AEBS_C_wrapper.version
    basename = self.source.getBaseName()
    dpv = shorten_dpv(self.dpv)
    title = "AEBS_C %s-%s sim (%s)" %(version, dpv, basename)
    pn = cPlotNavigator(title=title)
    self.sync.addClient(pn)
    # aebs state
    yticks = {0: "not ready", 1: "temp. n/a", 2: "deact.", 3: "ready",
              4: "override", 5: "warning", 6: "part. brk.", 7: "emer. brk.",
              14: "error", 15: "n/a"}
    yticks = dict( (k, "(%s) %d"%(v,k)) for k, v in yticks.iteritems() )
    ax = pn.addAxis(yticks=yticks)
    pn.addSignal2Axis(ax, 'AEBS1_SystemState', t, out_sim['AEBS1_SystemState'])
    
    ax = pn.addTwinAxis(ax)
    pn.addSignal2Axis(ax, 'AEBS1_WarningLevel', t, out_sim['AEBS1_WarningLevel'], color = 'r')
    # state machine and aRel signals
    for name,              unit,    yticks in (
       ('mstState',        None,    as_yticks(mstState_t)),
       ('mstCascadeState', None,    as_yticks(mstCascaseState_t)),
       ('aAvoid',          'm/s/s', None),
       ('tWarnDt',         's',     None)
    ):
      ax = pn.addAxis(yticks=yticks)
      pn.addSignal2Axis(ax, name, t, dbg_arr[name], unit=unit)
      if name == 'aAvoid':
        pn.addSignal2Axis(ax, 'aAvoidDynWarnApprox', t, internals['aAvoidDynWarnApprox'], color = 'g')
        pn.addSignal2Axis(ax, 'aAvoidAccSuppression', t, internals['aAvoidAccSuppression'], color = 'r')
      if name == 'mstCascadeState':
        ax = pn.addTwinAxis(ax)
        pn.addSignal2Axis(ax, 'accSuppressionActive', t, internals['accSuppressionActive'], color = 'r')
    
    # ttc suppression signals
    ax = pn.addAxis()
    for name in ('ttcSimpleMax', 'ttcSimple'):
      pn.addSignal2Axis(ax, name, t, dbg_arr[name], unit='s')
    # agent signals
    agt_plaus_signames  = [name for name in dbg_arr.dtype.names if name.lower().endswith('plaus')]
    agt_skill_signames  = [name for name in dbg_arr.dtype.names if name.lower().endswith('skill')]
    for names in (agt_plaus_signames, agt_skill_signames):
      ax = pn.addAxis()
      for name in names:
        pn.addSignal2Axis(ax, name, t, dbg_arr[name])
    return
