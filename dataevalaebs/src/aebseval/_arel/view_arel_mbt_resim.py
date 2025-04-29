# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import glob
import imp

import numpy as np

import interface
import datavis
from measparser import cSignalSource
AEBS_C_wrapper = imp.load_dynamic('AEBS_C_wrapper', r'C:\KBData\sandbox\AEBS_C_AREL\cython\release\AEBS_C_wrapper.pyd')
from sim_mbt_mat import sim_mat

sgs   = [
{
  "kbaebsInput_dxv": ("sil", "kbaebsInput_dxv"),
  "kbaebsInput_vxv": ("sil", "kbaebsInput_vxv"),
  "kbaebsInput_axv": ("sil", "kbaebsInput_axv"),
  "kbaebsInput_vRef": ("sil", "kbaebsInput_vRef"),
  "kbaebsOutput_AEBS1_SystemState": ("sil", "kbaebsOutput_AEBS1_SystemState"),
  "kbaebsOutput_XBR_Demand": ("sil", "kbaebsOutput_XBR_Demand"),
  "kbaebsOutput_AEBS1_WarningLevel": ("sil", "kbaebsOutput_AEBS1_WarningLevel"),
  # "tWarnDtForPred": ("sil", "AEBSAnalyse.ttc_at_start_of_state"),

},
]

# unreliable aAvoid with aRel OFF: 
# tc_aebs_dtChar_ev55rv0ra0d15aOnnra_2_0_513_4_1.mat
# tc_aebs_dtChar_ev30rv0ra0d40aOnnra_2_0_1071_4_1.mat

class View(interface.iView):
  def check(self):
    basename = self.source.getBaseName()
    assert 'aOn' in basename, 'Please select an "aOn" measurement'
    # search for the aOff measurement
    basename_replaced = basename.replace('aOn', 'aOff')
    split_until = 5 if 'NP' not in basename else 6 # handle test case naming convention change
    basename_split = basename_replaced.split('_', split_until)
    basename_part = '_'.join( basename_split[:-1] )
    dirname = glob.os.path.dirname(self.source.FileName)
    filepath, = glob.glob( glob.os.path.join(dirname, basename_part) + '_*' )
    source2 = cSignalSource(filepath)
    group_on = self.source.selectSignalGroup(sgs)
    group_off = source2.selectSignalGroup(sgs)
    t_on, inp, out, par, out_sim_on, internals_on     = sim_mat(source2.FileName,     UseAccelerationInfo=True)
    t_off, inp, out, par, out_sim_off, internals_off  = sim_mat(self.source.FileName, UseAccelerationInfo=False)
    return group_on, group_off, t_on, out_sim_on, internals_on, t_off, out_sim_off, internals_off

  def view(self, group_on, group_off, t_on, out_sim_on, internals_on, t_off, out_sim_off, internals_off):
    pn = datavis.cPlotNavigator(title="aRel ON/OFF comparison", figureNr=None)
    self.sync.addClient(pn)

    axis00 = pn.addAxis()
    time00, value00 = group_on.get_signal("kbaebsInput_vRef")
    pn.addSignal2Axis(axis00, "kbaebsInput_vRef (ON)", time00, value00)
    time00, value00 = group_off.get_signal("kbaebsInput_vRef")
    pn.addSignal2Axis(axis00, "kbaebsInput_vRef (OFF)", time00, value00)

    axis01 = pn.addAxis()
    time01, value01 = group_on.get_signal("kbaebsInput_vxv")
    pn.addSignal2Axis(axis01, "kbaebsInput_vxv (ON)", time01, value01)
    time00, value00 = group_off.get_signal("kbaebsInput_vxv")
    pn.addSignal2Axis(axis01, "kbaebsInput_vxv (OFF)", time00, value00)
    
    axis00 = pn.addAxis()
    time00, value00 = group_on.get_signal("kbaebsInput_dxv")
    pn.addSignal2Axis(axis00, "kbaebsInput_dxv (ON)", time00, value00)
    time00, value00 = group_off.get_signal("kbaebsInput_dxv")
    pn.addSignal2Axis(axis00, "kbaebsInput_dxv (OFF)", time00, value00)

    axis01 = pn.addAxis()
    time01, value01 = group_on.get_signal("kbaebsInput_axv")
    pn.addSignal2Axis(axis01, "kbaebsInput_axv (ON)", time01, value01)
    time00, value00 = group_off.get_signal("kbaebsInput_axv")
    pn.addSignal2Axis(axis01, "kbaebsInput_axv (OFF)", time00, value00)

    axis01 = pn.addAxis()
    if "tWarnDtForPred" in internals_off:
      pn.addSignal2Axis(axis01, "tWarnDtForPredFormula (OFF)", t_off, internals_off["tWarnDtForPred"])
    pn.addSignal2Axis(axis01, "tWarnDtForPredApprox (OFF)", t_off, internals_off["tWarnDtForPredApprox"])

    axis01 = pn.addAxis()
    pn.addSignal2Axis(axis01, "aAvoid (ON)", t_on, internals_on["aAvoidDynWarnApprox"])
    if "aAvoidDynWarn" in internals_off:
      pn.addSignal2Axis(axis01, "aAvoidFormula (OFF)", t_off, internals_off["aAvoidDynWarn"])
    pn.addSignal2Axis(axis01, "aAvoidApprox (OFF)", t_off, internals_off["aAvoidDynWarnApprox"])

    axis02 = pn.addAxis()
    time02, value02 = group_on.get_signal("kbaebsOutput_AEBS1_SystemState")
    pn.addSignal2Axis(axis02, "kbaebsOutput_AEBS1_SystemState (ON)", time02, value02)
    time00, value00 = group_off.get_signal("kbaebsOutput_AEBS1_SystemState")
    pn.addSignal2Axis(axis02, "kbaebsOutput_AEBS1_SystemState (OFF)", time00, value00)
    pn.addSignal2Axis(axis02, "AEBS1_SystemState sim (ON)", t_on, out_sim_on["AEBS1_SystemState"])
    pn.addSignal2Axis(axis02, "AEBS1_SystemState sim (OFF)", t_off, out_sim_off["AEBS1_SystemState"])

    axis03 = pn.addAxis()
    time03, value03 = group_on.get_signal("kbaebsOutput_XBR_Demand")
    pn.addSignal2Axis(axis03, "kbaebsOutput_XBR_Demand (ON)", time03, AEBS_C_wrapper.FixedPointArray(value03, 'XBR_Demand').float_value)
    time00, value00 = group_off.get_signal("kbaebsOutput_XBR_Demand")
    pn.addSignal2Axis(axis03, "kbaebsOutput_XBR_Demand (OFF)", time00, AEBS_C_wrapper.FixedPointArray(value00, 'XBR_Demand').float_value)

    axis03 = pn.addAxis()
    time03, value03 = group_on.get_signal("kbaebsOutput_AEBS1_WarningLevel")
    pn.addSignal2Axis(axis03, "kbaebsOutput_AEBS1_WarningLevel (ON)", time03, value03)
    time00, value00 = group_off.get_signal("kbaebsOutput_AEBS1_WarningLevel")
    pn.addSignal2Axis(axis03, "kbaebsOutput_AEBS1_WarningLevel (OFF)", time00, value00)
    return
