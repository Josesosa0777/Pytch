# -*- dataeval: init -*-

from interface import iView
import datavis

init_params = dict(
  AEBS_C_7_0_vs_7_1__DEV_GENERAL_8_17_BRAKING=dict(calc_version='AEBS_C_7_0_vs_7_1__DEV_GENERAL_8_17_BRAKING'),
  AEBS_C_6_1_vs_7_0__DEV_GENERAL_8_17_BRAKING=dict(calc_version='AEBS_C_6_1_vs_7_0__DEV_GENERAL_8_17_BRAKING'),
  AEBS_C_6_1_vs_7_0__DEV_FORD_7_11_BRAKING=dict(calc_version='AEBS_C_6_1_vs_7_0__DEV_FORD_7_11_BRAKING'),
)

sgs = [
{
  "AEBS1_AEBSState_2A": ("AEBS1_2A", "AEBS1_AEBSState_2A"),
  "AEBS1_CollisionWarningLevel_2A": ("AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
  "XBR_ExtAccelDem_2A": ("XBR_2A", "XBR_ExtAccelDem_2A"),
},
]

class View(iView):
  def init(self, calc_version):
    self.calc_version = calc_version
    self.dep = {'aebs_c_sil_versions': 'calc_aebs_c_sil_versions-%s@aebseval.sim' % calc_version}
    return

  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def fill(self,group):
    t, inp_new, par, out_sim_old, out_sim_new, internals_old, internals_new, source_type = self.modules.fill(self.dep['aebs_c_sil_versions'])
    return t, inp_new, par, out_sim_old, out_sim_new, internals_old, internals_new, group, source_type

  def view(self, t, inp_new, par, out_sim_old, out_sim_new, internals_old, internals_new, group, source_type):
    title = ""
    client00 = datavis.cPlotNavigator(title=title)
    self.sync.addClient(client00)
    yticks = {0: "not ready", 1: "temp. n/a", 2: "deact.", 3: "ready",
              4: "override", 5: "warning", 6: "part. brk.", 7: "emer. brk.",
              14: "error", 15: "n/a"}
    yticks = dict( (k, "(%s) %d"%(v,k)) for k, v in yticks.iteritems() )
    axis00 = client00.addAxis(yticks=yticks)
    time00, value00, unit00 = group.get_signal_with_unit("AEBS1_AEBSState_2A")
    client00.addSignal2Axis(axis00, "AEBS1_AEBSState_2A", time00, value00, unit=unit00)
    client00.addSignal2Axis(axis00, "AEBS1_SystemState_series", t, out_sim_old['AEBS1_SystemState'], color='r')
    client00.addSignal2Axis(axis00, "AEBS1_SystemState_resim", t, out_sim_new['AEBS1_SystemState'], ls='--', lw=2, color='k')
    axis00 = client00.addTwinAxis(axis00)
    time01, value01, unit01 = group.get_signal_with_unit("AEBS1_CollisionWarningLevel_2A")
    client00.addSignal2Axis(axis00, "AEBS1_AEBSState_2A", time01, value01, unit=unit01, color='g')
    yticks = {0: "0", 1: "1", 1.5: "0", 2.5: "1", 3: "0", 4: "1"}
    axis01 = client00.addAxis(yticks=yticks)
    #Acc bool flags
    client00.addSignal2Axis(axis01, "AccInControl_b", t, inp_new["AccInControl_b"], offset = 3)
    client00.addSignal2Axis(axis01, "Stopped_b", t, inp_new["Stopped_b"], offset=1.5)
    client00.addSignal2Axis(axis01, "Stand_b", t, inp_new["Stand_b"], offset=1.5)
    client00.addSignal2Axis(axis01, "ACC_Suppression_active", t, internals_new["accSuppressionActive"])
    #Accel data
    axis02 = client00.addAxis(ylim=(-6.5, 0.5))
    #value07 = out_sim_new['XBR_Demand']
    client00.addSignal2Axis(axis02, "AccAccelDemand", t, inp_new["AccAccelDemand"], unit="m/s2")
    client00.addSignal2Axis(axis02, "AccAccelDemandMin", t, inp_new["AccAccelDemandMin"], unit="m/s2")
    client00.addSignal2Axis(axis02, "aAvoidAccSuppression", t, internals_new["aAvoidAccSuppression"], unit="m/s2")
    client00.addSignal2Axis(axis02, "aAvoid_resim", t, internals_new["aAvoidDynWarnApprox"], unit="m/s2")
    time06, value06, unit06 = group.get_signal_with_unit("XBR_ExtAccelDem_2A")
    client00.addSignal2Axis(axis02, "XBR_ExtAccelDem_2A", time06, value06, unit=unit06)
    client00.addSignal2Axis(axis02, "XBR_Demand_resim", t, out_sim_new['XBR_Demand'], unit=unit06)
    axis03 = client00.addAxis()
    client00.addSignal2Axis(axis03, "GPPos", t, inp_new["GPPos"], unit="%")
    client00.addSignal2Axis(axis03, "BPPos", t, inp_new["BPPos"], unit="%")
    return
