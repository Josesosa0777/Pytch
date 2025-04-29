# -*- dataeval: init -*-

import numpy as np

from aebseval.view_driveract_aebsout import View as BaseClass

class SimView(BaseClass):
  dep = {'ccp' : 'calc_aebs_c_sil_ccp@aebs.fill'}

  def fill(self, *args, **kwargs):
    self.t, inp, par, self.out_sim, self.internals = self.modules.fill( self.dep['ccp'] )
    return BaseClass.fill(self, *args, **kwargs)

  def extend_aebs_state_axis(self, pn, ax):
    pn.addSignal2Axis(ax, 'AEBSState (sim)', self.t, self.out_sim['AEBS1_SystemState'], color='r')
    if 'aAvoidDynWarnApprox' in self.internals: # available only from 7.0
      ax_dbg = pn.addAxis(ylabel="debug")
      pn.addSignal2Axis(ax_dbg, 'aAvoidDynWarnApprox (sim)', self.t, self.internals['aAvoidDynWarnApprox'])
      pn.addSignal2Axis(ax_dbg, 'aAvoidAccSuppression (sim)', self.t, self.internals['aAvoidAccSuppression'])
      pn.addSignal2Axis(ax_dbg, 'accSuppressionActive (sim)', self.t, self.internals['accSuppressionActive'])
    return
