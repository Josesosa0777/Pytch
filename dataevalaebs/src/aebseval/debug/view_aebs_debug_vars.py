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


init_params = { 'CCP data' : dict(dpv='CCP') }
init_params.update(calc_aebs_c_sil.init_params)

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
      'aebs_c_sil' : 'calc_aebs_c_sil_ccp@aebs.fill' if dpv == 'CCP' else 'calc_aebs_c_sil-%s@aebs.fill' %dpv
    }
    return

  @debug(cmd_fpath, tidy=True)
  def fill(self):
    t, inp, par, out_sim, internals = self.modules.fill( self.dep['aebs_c_sil'] )
    return t, inp, par, out_sim

  def view(self, fill_res, dbg_arr):
    t, inp, par, out_sim = fill_res
    version = calc_aebs_c_sil.AEBS_C_wrapper.version
    basename = self.source.getBaseName()
    dpv = shorten_dpv(self.dpv)
    title = "AEBS_C %s-%s sim (%s)" %(version, dpv, basename)
    pn = cPlotNavigator(title=title)
    self.sync.addClient(pn)
    # state machine and aRel signals
    for name,              unit,    yticks in (
       ('mstState',        None,    as_yticks(mstState_t)),
       ('mstCascadeState', None,    as_yticks(mstCascaseState_t)),
       ('aAvoid',          'm/s/s', None),
       ('tWarnDt',         's',     None)
    ):
      ax = pn.addAxis(yticks=yticks)
      pn.addSignal2Axis(ax, name, t, dbg_arr[name], unit=unit)
    # ttc suppression signals
    ax = pn.addAxis()
    for name in ('ttcSimpleMax', 'ttcSimple'):
      pn.addSignal2Axis(ax, name, t, dbg_arr[name], unit='s')
    # override signals
    ovr_signames = [name for name in dbg_arr.dtype.names if 'ovr' in name.lower()]
    sig_cnt = len(ovr_signames)
    yticks = dict( (k,v) for k,v in zip(xrange(2*sig_cnt), [0,1]*sig_cnt) )
    ax = pn.addAxis(yticks=yticks)
    for k, name in enumerate(ovr_signames):
      offset = 2*(sig_cnt-k-1)
      kwargs = {} if offset == 0 else dict(offset=offset, displayscaled=False)
      pn.addSignal2Axis(ax, name, t, dbg_arr[name], **kwargs)
    # agent signals
    agt_plaus_signames  = [name for name in dbg_arr.dtype.names if name.lower().endswith('plaus')]
    agt_skill_signames  = [name for name in dbg_arr.dtype.names if name.lower().endswith('skill')]
    agt_skillw_signames = [name for name in dbg_arr.dtype.names if name.lower().endswith('skillw')]
    for names in (agt_plaus_signames, agt_skill_signames, agt_skillw_signames):
      ax = pn.addAxis()
      for name in names:
        pn.addSignal2Axis(ax, name, t, dbg_arr[name])
    return
