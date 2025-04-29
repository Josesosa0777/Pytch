# -*- dataeval: init -*-

from aebseval.view_driveract_aebsout import View as BaseClass
import view_driveract_aebsout_sim

init_params = view_driveract_aebsout_sim.init_params

def shorten_dpv(s):
  return s.replace('DEV_', '', 1).replace('.DPV', '')

class SimView(BaseClass):
  def init(self, dpv_old, dpv_new):
    dep_template = 'calc_aebs_c_sil_mbt-%s@aebs.fill'
    self.dep = {
      'old' : dep_template %dpv_old,
      'new' : dep_template %dpv_new,
    }
    # legend stuff
    self.dpv_short = {
      'old' : shorten_dpv(dpv_old),
      'new' : shorten_dpv(dpv_new),
    }
    return

  def fill(self, *args, **kwargs):
    self.t, inp, par, self.out_sim_old, self.internals = self.modules.fill( self.dep['old'] )
    _,      inp, par, self.out_sim_new, self.internals = self.modules.fill( self.dep['new'] )
    return BaseClass.fill(self, *args, **kwargs)

  def extend_aebs_state_axis(self, pn, ax):
    pn.addSignal2Axis(ax, self.dpv_short['old'], self.t, self.out_sim_old['AEBS1_SystemState'], ls='--', lw=2, color='k')
    pn.addSignal2Axis(ax, self.dpv_short['new'], self.t, self.out_sim_new['AEBS1_SystemState'], color='r')
    if 'aAvoidDynWarnApprox' in self.internals: # available only from 7.0
      ax_dbg = pn.addAxis(ylabel="debug")
      pn.addSignal2Axis(ax_dbg, 'aAvoidDynWarnApprox (sim)', self.t, self.internals['aAvoidDynWarnApprox'])
      pn.addSignal2Axis(ax_dbg, 'aAvoidAccSuppression (sim)', self.t, self.internals['aAvoidAccSuppression'])
      pn.addSignal2Axis(ax_dbg, 'accSuppressionActive (sim)', self.t, self.internals['accSuppressionActive'])
    return
