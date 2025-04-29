# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import os
import sys
import imp

from interface import iView
import datavis
from measparser.signalgroup import SignalGroup


AEBS_C_SANDBOX = r'C:\KBData\sandbox\AEBS_C'

class View(iView):
  def init(self):
    assert os.path.exists(AEBS_C_SANDBOX)
    # load dll-s
    dll_dir = os.path.join(AEBS_C_SANDBOX, r'cython\release\ttc_suppression')
    self.AEBS_C_before_fix = imp.load_dynamic('AEBS_C_wrapper', os.path.join(dll_dir, 'AEBS_C_wrapper__1_21.pyd'))
    sys.modules.pop('AEBS_C_wrapper') # trick for multiple simulation instances
    self.AEBS_C_after_fix  = imp.load_dynamic('AEBS_C_wrapper', os.path.join(dll_dir, 'AEBS_C_wrapper__1_21_ttc_suppression.pyd'))
    # create signal groups
    sg_base = { "AEBS1_AEBSState_2A": ("AEBS1_2A", "AEBS1_AEBSState_2A") }
    # float data
    sg = {name : ('kbaebsInput', name) for name in self.AEBS_C_before_fix.kbaebsInputSt_t_dtype.names}
    sg.update(sg_base)
    sg.pop('PlatformReady_b') # not recorded in old measurements
    # fixed-point data
    sg_ccp = {name : ('CCP', 'kbaebsInaebs.' + name) for name in self.AEBS_C_before_fix.kbaebsInputSt_t_dtype.names}
    sg_ccp.update(sg_base)
    sg_ccp.pop('PlatformReady_b') # not recorded in old measurements
    self.sgs = {'float' : sg, 'fixed-point' : sg_ccp}
    return

  def check(self):
    group = SignalGroup.from_named_signalgroups(self.sgs, self.source)
    return group

  def view(self, group):
    # get params
    dpvs = imp.load_source('dpvs', os.path.join(AEBS_C_SANDBOX, r'cython\release\dpvs.py'))
    # get time and inputs
    t = group.get_time("dxv")
    if group.winner == 'float':
      inp = {name : group.get_value(name) for name in group}
      par = dpvs.get_dpv('DEV_FORD_6.12_NON-BRAKING.DPV')
    elif group.winner == 'fixed-point':
      # convert fixed-point signal to float if it has norming constant
      inp = {}
      for name in group:
        value = group.get_value(name)
        if name in self.AEBS_C_before_fix.signame2norm:
          value = self.AEBS_C_before_fix.FixedPointArray(value, name, typecheck=False).float_value
        inp[name] = value
      par = dpvs.get_dpv('DEV_FORD_6.11_BRAKING.DPV')
    else:
      raise ValueError
    # patch missing signals
    inp['PlatformReady_b'] = True
    # simulate
    out_sim_before_RB,   internals_before_RB   = self.AEBS_C_before_fix.AEBSproc_float(t, inp, par, typecheck=False, warn_trig=1)
    self.AEBS_C_before_fix.reset = True # reset lib before using aRel triggering
    out_sim_before_aRel, internals_before_aRel = self.AEBS_C_before_fix.AEBSproc_float(t, inp, par, typecheck=False, warn_trig=0)
    out_sim_after,       internals_after       = self.AEBS_C_after_fix.AEBSproc_float( t, inp, par, typecheck=False)
    # plot
    pn = datavis.cPlotNavigator(title='aRel ttc suppression validation (%s)' %self.source.BaseName)
    # layout hack, see #1504
    layout_id = 'foo'
    pn.createWindowId = lambda x,title=None: layout_id
    pn.getWindowId = lambda : layout_id
    pn._windowId = pn.createWindowId(None)
    self.sync.addClient(pn)
    ax = pn.addAxis()
    pn.addSignal2Axis(ax, "AEBS state (1.21 RB)", t, out_sim_before_RB['AEBS1_SystemState'])
    pn.addSignal2Axis(ax, "AEBS state (1.21 aRel)", t, out_sim_before_aRel['AEBS1_SystemState'])
    pn.addSignal2Axis(ax, "AEBS state (1.21 aRel + ttc suppr.)", t, out_sim_after['AEBS1_SystemState'])
    pn.addSignal2Axis(ax, "AEBS state (recorded)", *group.get_signal('AEBS1_AEBSState_2A'))
    ax = pn.addAxis()
    pn.addSignal2Axis(ax, "aAvoid (1.21 RB)",   t, internals_before_RB['aAvoidDynWarnApprox'],   unit='m/s/s')
    pn.addSignal2Axis(ax, "aAvoid (1.21 aRel)", t, internals_before_aRel['aAvoidDynWarnApprox'], unit='m/s/s')
    return
