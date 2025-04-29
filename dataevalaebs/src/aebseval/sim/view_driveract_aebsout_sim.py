# -*- dataeval: init -*-

from aebseval.view_driveract_aebsout import View as BaseClass

init_params = dict(
  GEN_8_17_vs_DAF_80kph = dict(dpv_old='DEV_DAF_80KPH_7.15_BRAKING.DPV', dpv_new='DEV_GENERAL_8.17_BRAKING.DPV'),
  FORD_vs_DAF_80kph = dict(dpv_old='DEV_FORD_8.11_BRAKING.DPV', dpv_new='DEV_DAF_80KPH_7.15_BRAKING.DPV'),
  FORD_vs_DAF_89kph = dict(dpv_old='DEV_FORD_7.11_BRAKING.DPV', dpv_new='DEV_DAF_89KPH_7.15_BRAKING_MBT_tuned_after_Boxberg.DPV'),
  MAN_GV_vs_DAF_80kph = dict(dpv_old='DEV_FORD_7.12_NON-BRAKING.DPV', dpv_new='DEV_DAF_80KPH_7.15_BRAKING.DPV'),
  YUTONG_vs_DAF_80kph = dict(dpv_old='DEV_GENERAL_7.14_NON-BRAKING.DPV', dpv_new='DEV_DAF_80KPH_7.15_BRAKING.DPV'),
  OTOKAR_vs_DAF_80kph = dict(dpv_old='DEV_OTOKAR_7.10_NON-BRAKING.DPV', dpv_new='DEV_DAF_80KPH_7.15_BRAKING.DPV'),
  DE_PV2_vs_DAF_80kph = dict(dpv_old='DEV_DE_7.6_NON-BRAKING.DPV', dpv_new='DEV_DAF_80KPH_7.15_BRAKING.DPV'),
)

def shorten_dpv(s):
  return s.replace('DEV_', '', 1).replace('.DPV', '')

class SimView(BaseClass):
  def init(self, dpv_old, dpv_new):
    dep_template = 'calc_aebs_c_sil-%s@aebs.fill'
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
      pn.addSignal2Axis(ax_dbg, 'aAvoidDynWarnApprox (sim)',  self.t, self.internals['aAvoidDynWarnApprox'])
      pn.addSignal2Axis(ax_dbg, 'aAvoidAccSuppression (sim)', self.t, self.internals['aAvoidAccSuppression'])
      pn.addSignal2Axis(ax_dbg, 'accSuppressionActive (sim)', self.t, self.internals['accSuppressionActive'])
    return
