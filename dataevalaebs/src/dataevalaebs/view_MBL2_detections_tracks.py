# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "Azimuth_10_r": ("MBM_TARGET_DETECTION_10_r", "Azimuth_10_r"),
  "Range_21_r": ("MBM_TARGET_DETECTION_21_r", "Range_21_r"),
  "Velocity_03_r": ("MBM_TARGET_DETECTION_03_r", "Velocity_03_r"),
  "BeamNumber_09_r": ("MBM_TARGET_DETECTION_09_r", "BeamNumber_09_r"),
  "Velocity_05_r": ("MBM_TARGET_DETECTION_05_r", "Velocity_05_r"),
  "Velocity_13_r": ("MBM_TARGET_DETECTION_13_r", "Velocity_13_r"),
  "Azimuth_19_r": ("MBM_TARGET_DETECTION_19_r", "Azimuth_19_r"),
  "BeamNumber_17_r": ("MBM_TARGET_DETECTION_17_r", "BeamNumber_17_r"),
  "Azimuth_12_r": ("MBM_TARGET_DETECTION_12_r", "Azimuth_12_r"),
  "BeamNumber_19_r": ("MBM_TARGET_DETECTION_19_r", "BeamNumber_19_r"),
  "Azimuth_07_r": ("MBM_TARGET_DETECTION_07_r", "Azimuth_07_r"),
  "Range_23_r": ("MBM_TARGET_DETECTION_23_r", "Range_23_r"),
  "Velocity_24_r": ("MBM_TARGET_DETECTION_24_r", "Velocity_24_r"),
  "Velocity_22_r": ("MBM_TARGET_DETECTION_22_r", "Velocity_22_r"),
  "Azimuth_05_r": ("MBM_TARGET_DETECTION_05_r", "Azimuth_05_r"),
  "BeamNumber_02_r": ("MBM_TARGET_DETECTION_02_r", "BeamNumber_02_r"),
  "Range_17_r": ("MBM_TARGET_DETECTION_17_r", "Range_17_r"),
  "Velocity_18_r": ("MBM_TARGET_DETECTION_18_r", "Velocity_18_r"),
  "Power_12_r": ("MBM_TARGET_DETECTION_12_r", "Power_12_r"),
  "Velocity_20_r": ("MBM_TARGET_DETECTION_20_r", "Velocity_20_r"),
  "BeamNumber_04_r": ("MBM_TARGET_DETECTION_04_r", "BeamNumber_04_r"),
  "Azimuth_03_r": ("MBM_TARGET_DETECTION_03_r", "Azimuth_03_r"),
  "BeamNumber_10_r": ("MBM_TARGET_DETECTION_10_r", "BeamNumber_10_r"),
  "Power_14_r": ("MBM_TARGET_DETECTION_14_r", "Power_14_r"),
  "Velocity_16_r": ("MBM_TARGET_DETECTION_16_r", "Velocity_16_r"),
  "Azimuth_01_r": ("MBM_TARGET_DETECTION_01_r", "Azimuth_01_r"),
  "BeamNumber_06_r": ("MBM_TARGET_DETECTION_06_r", "BeamNumber_06_r"),
  "Range_24_r": ("MBM_TARGET_DETECTION_24_r", "Range_24_r"),
  "Velocity_08_r": ("MBM_TARGET_DETECTION_08_r", "Velocity_08_r"),
  "BeamNumber_05_r": ("MBM_TARGET_DETECTION_05_r", "BeamNumber_05_r"),
  "Azimuth_15_r": ("MBM_TARGET_DETECTION_15_r", "Azimuth_15_r"),
  "Power_16_r": ("MBM_TARGET_DETECTION_16_r", "Power_16_r"),
  "BeamNumber_15_r": ("MBM_TARGET_DETECTION_15_r", "BeamNumber_15_r"),
  "Azimuth_17_r": ("MBM_TARGET_DETECTION_17_r", "Azimuth_17_r"),
  "BeamNumber_13_r": ("MBM_TARGET_DETECTION_13_r", "BeamNumber_13_r"),
  "Track3_sixPos": ("MBM_TRACKS_XY_03_r", "Track3_sixPos"),
  "Range_20_r": ("MBM_TARGET_DETECTION_20_r", "Range_20_r"),
  "Power_03_r": ("MBM_TARGET_DETECTION_03_r", "Power_03_r"),
  "Track1_sixPos": ("MBM_TRACKS_XY_01_r", "Track1_sixPos"),
  "Azimuth_18_r": ("MBM_TARGET_DETECTION_18_r", "Azimuth_18_r"),
  "Range_12_r": ("MBM_TARGET_DETECTION_12_r", "Range_12_r"),
  "BeamNumber_01_r": ("MBM_TARGET_DETECTION_01_r", "BeamNumber_01_r"),
  "Range_22_r": ("MBM_TARGET_DETECTION_22_r", "Range_22_r"),
  "Power_01_r": ("MBM_TARGET_DETECTION_01_r", "Power_01_r"),
  "Azimuth_06_r": ("MBM_TARGET_DETECTION_06_r", "Azimuth_06_r"),
  "BeamNumber_03_r": ("MBM_TARGET_DETECTION_03_r", "BeamNumber_03_r"),
  "Range_03_r": ("MBM_TARGET_DETECTION_03_r", "Range_03_r"),
  "Range_11_r": ("MBM_TARGET_DETECTION_11_r", "Range_11_r"),
  "Velocity_19_r": ("MBM_TARGET_DETECTION_19_r", "Velocity_19_r"),
  "Azimuth_04_r": ("MBM_TARGET_DETECTION_04_r", "Azimuth_04_r"),
  "Velocity_11_r": ("MBM_TARGET_DETECTION_11_r", "Velocity_11_r"),
  "Track3_siyPos": ("MBM_TRACKS_XY_03_r", "Track3_siyPos"),
  "Velocity_17_r": ("MBM_TARGET_DETECTION_17_r", "Velocity_17_r"),
  "Azimuth_02_r": ("MBM_TARGET_DETECTION_02_r", "Azimuth_02_r"),
  "BeamNumber_07_r": ("MBM_TARGET_DETECTION_07_r", "BeamNumber_07_r"),
  "BeamNumber_11_r": ("MBM_TARGET_DETECTION_11_r", "BeamNumber_11_r"),
  "Velocity_15_r": ("MBM_TARGET_DETECTION_15_r", "Velocity_15_r"),
  "Range_09_r": ("MBM_TARGET_DETECTION_09_r", "Range_09_r"),
  "Velocity_14_r": ("MBM_TARGET_DETECTION_14_r", "Velocity_14_r"),
  "Azimuth_09_r": ("MBM_TARGET_DETECTION_09_r", "Azimuth_09_r"),
  "Azimuth_14_r": ("MBM_TARGET_DETECTION_14_r", "Azimuth_14_r"),
  "Velocity_07_r": ("MBM_TARGET_DETECTION_07_r", "Velocity_07_r"),
  "Power_21_r": ("MBM_TARGET_DETECTION_21_r", "Power_21_r"),
  "Velocity_09_r": ("MBM_TARGET_DETECTION_09_r", "Velocity_09_r"),
  "Track2_siyPos": ("MBM_TRACKS_XY_02_r", "Track2_siyPos"),
  "Azimuth_16_r": ("MBM_TARGET_DETECTION_16_r", "Azimuth_16_r"),
  "Velocity_01_r": ("MBM_TARGET_DETECTION_01_r", "Velocity_01_r"),
  "Power_23_r": ("MBM_TARGET_DETECTION_23_r", "Power_23_r"),
  "BeamNumber_12_r": ("MBM_TARGET_DETECTION_12_r", "BeamNumber_12_r"),
  "Power_02_r": ("MBM_TARGET_DETECTION_02_r", "Power_02_r"),
  "Range_01_r": ("MBM_TARGET_DETECTION_01_r", "Range_01_r"),
  "Power_24_r": ("MBM_TARGET_DETECTION_24_r", "Power_24_r"),
  "Range_07_r": ("MBM_TARGET_DETECTION_07_r", "Range_07_r"),
  "Range_05_r": ("MBM_TARGET_DETECTION_05_r", "Range_05_r"),
  "BeamNumber_22_r": ("MBM_TARGET_DETECTION_22_r", "BeamNumber_22_r"),
  "Power_19_r": ("MBM_TARGET_DETECTION_19_r", "Power_19_r"),
  "Range_02_r": ("MBM_TARGET_DETECTION_02_r", "Range_02_r"),
  "Power_09_r": ("MBM_TARGET_DETECTION_09_r", "Power_09_r"),
  "BeamNumber_20_r": ("MBM_TARGET_DETECTION_20_r", "BeamNumber_20_r"),
  "Velocity_12_r": ("MBM_TARGET_DETECTION_12_r", "Velocity_12_r"),
  "Track2_sixPos": ("MBM_TRACKS_XY_02_r", "Track2_sixPos"),
  "Track1_siyPos": ("MBM_TRACKS_XY_01_r", "Track1_siyPos"),
  "Range_19_r": ("MBM_TARGET_DETECTION_19_r", "Range_19_r"),
  "Velocity_10_r": ("MBM_TARGET_DETECTION_10_r", "Velocity_10_r"),
  "Azimuth_21_r": ("MBM_TARGET_DETECTION_21_r", "Azimuth_21_r"),
  "AMBM_Fatal_Error3_r": ("MBM_DIAG3_r", "AMBM_Fatal_Error3_r"),
  "Velocity_02_r": ("MBM_TARGET_DETECTION_02_r", "Velocity_02_r"),
  "Azimuth_23_r": ("MBM_TARGET_DETECTION_23_r", "Azimuth_23_r"),
  "Power_20_r": ("MBM_TARGET_DETECTION_20_r", "Power_20_r"),
  "Azimuth_08_r": ("MBM_TARGET_DETECTION_08_r", "Azimuth_08_r"),
  "Power_17_r": ("MBM_TARGET_DETECTION_17_r", "Power_17_r"),
  "Power_07_r": ("MBM_TARGET_DETECTION_07_r", "Power_07_r"),
  "Power_11_r": ("MBM_TARGET_DETECTION_11_r", "Power_11_r"),
  "Azimuth_24_r": ("MBM_TARGET_DETECTION_24_r", "Azimuth_24_r"),
  "Power_22_r": ("MBM_TARGET_DETECTION_22_r", "Power_22_r"),
  "Power_05_r": ("MBM_TARGET_DETECTION_05_r", "Power_05_r"),
  "Power_13_r": ("MBM_TARGET_DETECTION_13_r", "Power_13_r"),
  "Range_06_r": ("MBM_TARGET_DETECTION_06_r", "Range_06_r"),
  "Velocity_04_r": ("MBM_TARGET_DETECTION_04_r", "Velocity_04_r"),
  "Range_16_r": ("MBM_TARGET_DETECTION_16_r", "Range_16_r"),
  "Azimuth_11_r": ("MBM_TARGET_DETECTION_11_r", "Azimuth_11_r"),
  "BeamNumber_23_r": ("MBM_TARGET_DETECTION_23_r", "BeamNumber_23_r"),
  "BeamNumber_18_r": ("MBM_TARGET_DETECTION_18_r", "BeamNumber_18_r"),
  "BeamNumber_24_r": ("MBM_TARGET_DETECTION_24_r", "BeamNumber_24_r"),
  "Range_15_r": ("MBM_TARGET_DETECTION_15_r", "Range_15_r"),
  "BeamNumber_08_r": ("MBM_TARGET_DETECTION_08_r", "BeamNumber_08_r"),
  "Velocity_06_r": ("MBM_TARGET_DETECTION_06_r", "Velocity_06_r"),
  "Azimuth_13_r": ("MBM_TARGET_DETECTION_13_r", "Azimuth_13_r"),
  "BeamNumber_21_r": ("MBM_TARGET_DETECTION_21_r", "BeamNumber_21_r"),
  "Range_04_r": ("MBM_TARGET_DETECTION_04_r", "Range_04_r"),
  "Power_18_r": ("MBM_TARGET_DETECTION_18_r", "Power_18_r"),
  "Range_08_r": ("MBM_TARGET_DETECTION_08_r", "Range_08_r"),
  "Range_14_r": ("MBM_TARGET_DETECTION_14_r", "Range_14_r"),
  "Velocity_23_r": ("MBM_TARGET_DETECTION_23_r", "Velocity_23_r"),
  "Range_18_r": ("MBM_TARGET_DETECTION_18_r", "Range_18_r"),
  "Power_15_r": ("MBM_TARGET_DETECTION_15_r", "Power_15_r"),
  "Velocity_21_r": ("MBM_TARGET_DETECTION_21_r", "Velocity_21_r"),
  "BeamNumber_16_r": ("MBM_TARGET_DETECTION_16_r", "BeamNumber_16_r"),
  "Azimuth_20_r": ("MBM_TARGET_DETECTION_20_r", "Azimuth_20_r"),
  "Range_10_r": ("MBM_TARGET_DETECTION_10_r", "Range_10_r"),
  "Power_06_r": ("MBM_TARGET_DETECTION_06_r", "Power_06_r"),
  "BeamNumber_14_r": ("MBM_TARGET_DETECTION_14_r", "BeamNumber_14_r"),
  "Range_13_r": ("MBM_TARGET_DETECTION_13_r", "Range_13_r"),
  "Azimuth_22_r": ("MBM_TARGET_DETECTION_22_r", "Azimuth_22_r"),
  "Power_08_r": ("MBM_TARGET_DETECTION_08_r", "Power_08_r"),
  "Power_04_r": ("MBM_TARGET_DETECTION_04_r", "Power_04_r"),
  "Power_10_r": ("MBM_TARGET_DETECTION_10_r", "Power_10_r"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    client00 = datavis.cPlotNavigator(title="", figureNr=None)
    self.sync.addClient(client00)
    kwargs = {'lw' : 0}
    axis00 = client00.addAxis()
    time00, value00, unit00 = group.get_signal_with_unit("Range_01_r")
    client00.addSignal2Axis(axis00, "Range_01_r", time00, value00, unit=unit00, marker='.', **kwargs)
    time01, value01, unit01 = group.get_signal_with_unit("Range_02_r")
    client00.addSignal2Axis(axis00, "Range_02_r", time01, value01, unit=unit01, marker='.', **kwargs)
    time02, value02, unit02 = group.get_signal_with_unit("Range_03_r")
    client00.addSignal2Axis(axis00, "Range_03_r", time02, value02, unit=unit02, marker='.', **kwargs)
    time03, value03, unit03 = group.get_signal_with_unit("Range_04_r")
    client00.addSignal2Axis(axis00, "Range_04_r", time03, value03, unit=unit03, **kwargs)
    time04, value04, unit04 = group.get_signal_with_unit("Range_05_r")
    client00.addSignal2Axis(axis00, "Range_05_r", time04, value04, unit=unit04, **kwargs)
    time05, value05, unit05 = group.get_signal_with_unit("Range_06_r")
    client00.addSignal2Axis(axis00, "Range_06_r", time05, value05, unit=unit05, **kwargs)
    time06, value06, unit06 = group.get_signal_with_unit("Range_07_r")
    client00.addSignal2Axis(axis00, "Range_07_r", time06, value06, unit=unit06, **kwargs)
    time07, value07, unit07 = group.get_signal_with_unit("Range_08_r")
    client00.addSignal2Axis(axis00, "Range_08_r", time07, value07, unit=unit07, **kwargs)
    time08, value08, unit08 = group.get_signal_with_unit("Range_09_r")
    client00.addSignal2Axis(axis00, "Range_09_r", time08, value08, unit=unit08, **kwargs)
    time09, value09, unit09 = group.get_signal_with_unit("Range_10_r")
    client00.addSignal2Axis(axis00, "Range_10_r", time09, value09, unit=unit09, **kwargs)
    time10, value10, unit10 = group.get_signal_with_unit("Range_11_r")
    client00.addSignal2Axis(axis00, "Range_11_r", time10, value10, unit=unit10, **kwargs)
    time11, value11, unit11 = group.get_signal_with_unit("Range_12_r")
    client00.addSignal2Axis(axis00, "Range_12_r", time11, value11, unit=unit11, **kwargs)
    time12, value12, unit12 = group.get_signal_with_unit("Range_13_r")
    client00.addSignal2Axis(axis00, "Range_13_r", time12, value12, unit=unit12, **kwargs)
    time13, value13, unit13 = group.get_signal_with_unit("Range_14_r")
    client00.addSignal2Axis(axis00, "Range_14_r", time13, value13, unit=unit13, **kwargs)
    time14, value14, unit14 = group.get_signal_with_unit("Range_15_r")
    client00.addSignal2Axis(axis00, "Range_15_r", time14, value14, unit=unit14, **kwargs)
    time15, value15, unit15 = group.get_signal_with_unit("Range_16_r")
    client00.addSignal2Axis(axis00, "Range_16_r", time15, value15, unit=unit15, **kwargs)
    time16, value16, unit16 = group.get_signal_with_unit("Range_17_r")
    client00.addSignal2Axis(axis00, "Range_17_r", time16, value16, unit=unit16, **kwargs)
    time17, value17, unit17 = group.get_signal_with_unit("Range_18_r")
    client00.addSignal2Axis(axis00, "Range_18_r", time17, value17, unit=unit17, **kwargs)
    time18, value18, unit18 = group.get_signal_with_unit("Range_19_r")
    client00.addSignal2Axis(axis00, "Range_19_r", time18, value18, unit=unit18, **kwargs)
    time19, value19, unit19 = group.get_signal_with_unit("Range_20_r")
    client00.addSignal2Axis(axis00, "Range_20_r", time19, value19, unit=unit19, **kwargs)
    time20, value20, unit20 = group.get_signal_with_unit("Range_21_r")
    client00.addSignal2Axis(axis00, "Range_21_r", time20, value20, unit=unit20, **kwargs)
    time21, value21, unit21 = group.get_signal_with_unit("Range_22_r")
    client00.addSignal2Axis(axis00, "Range_22_r", time21, value21, unit=unit21, **kwargs)
    time22, value22, unit22 = group.get_signal_with_unit("Range_23_r")
    client00.addSignal2Axis(axis00, "Range_23_r", time22, value22, unit=unit22, **kwargs)
    time23, value23, unit23 = group.get_signal_with_unit("Range_24_r")
    client00.addSignal2Axis(axis00, "Range_24_r", time23, value23, unit=unit23, **kwargs)
    axis01 = client00.addAxis()
    time24, value24, unit24 = group.get_signal_with_unit("Azimuth_01_r")
    client00.addSignal2Axis(axis01, "Azimuth_01_r", time24, value24, unit=unit24, marker='.', **kwargs)
    time25, value25, unit25 = group.get_signal_with_unit("Azimuth_02_r")
    client00.addSignal2Axis(axis01, "Azimuth_02_r", time25, value25, unit=unit25, marker='.', **kwargs)
    time26, value26, unit26 = group.get_signal_with_unit("Azimuth_03_r")
    client00.addSignal2Axis(axis01, "Azimuth_03_r", time26, value26, unit=unit26, marker='.', **kwargs)
    time27, value27, unit27 = group.get_signal_with_unit("Azimuth_04_r")
    client00.addSignal2Axis(axis01, "Azimuth_04_r", time27, value27, unit=unit27, **kwargs)
    time28, value28, unit28 = group.get_signal_with_unit("Azimuth_05_r")
    client00.addSignal2Axis(axis01, "Azimuth_05_r", time28, value28, unit=unit28, **kwargs)
    time29, value29, unit29 = group.get_signal_with_unit("Azimuth_06_r")
    client00.addSignal2Axis(axis01, "Azimuth_06_r", time29, value29, unit=unit29, **kwargs)
    time30, value30, unit30 = group.get_signal_with_unit("Azimuth_07_r")
    client00.addSignal2Axis(axis01, "Azimuth_07_r", time30, value30, unit=unit30, **kwargs)
    time31, value31, unit31 = group.get_signal_with_unit("Azimuth_08_r")
    client00.addSignal2Axis(axis01, "Azimuth_08_r", time31, value31, unit=unit31, **kwargs)
    time32, value32, unit32 = group.get_signal_with_unit("Azimuth_09_r")
    client00.addSignal2Axis(axis01, "Azimuth_09_r", time32, value32, unit=unit32, **kwargs)
    time33, value33, unit33 = group.get_signal_with_unit("Azimuth_10_r")
    client00.addSignal2Axis(axis01, "Azimuth_10_r", time33, value33, unit=unit33, **kwargs)
    time34, value34, unit34 = group.get_signal_with_unit("Azimuth_11_r")
    client00.addSignal2Axis(axis01, "Azimuth_11_r", time34, value34, unit=unit34, **kwargs)
    time35, value35, unit35 = group.get_signal_with_unit("Azimuth_12_r")
    client00.addSignal2Axis(axis01, "Azimuth_12_r", time35, value35, unit=unit35, **kwargs)
    time36, value36, unit36 = group.get_signal_with_unit("Azimuth_13_r")
    client00.addSignal2Axis(axis01, "Azimuth_13_r", time36, value36, unit=unit36, **kwargs)
    time37, value37, unit37 = group.get_signal_with_unit("Azimuth_14_r")
    client00.addSignal2Axis(axis01, "Azimuth_14_r", time37, value37, unit=unit37, **kwargs)
    time38, value38, unit38 = group.get_signal_with_unit("Azimuth_15_r")
    client00.addSignal2Axis(axis01, "Azimuth_15_r", time38, value38, unit=unit38, **kwargs)
    time39, value39, unit39 = group.get_signal_with_unit("Azimuth_16_r")
    client00.addSignal2Axis(axis01, "Azimuth_16_r", time39, value39, unit=unit39, **kwargs)
    time40, value40, unit40 = group.get_signal_with_unit("Azimuth_17_r")
    client00.addSignal2Axis(axis01, "Azimuth_17_r", time40, value40, unit=unit40, **kwargs)
    time41, value41, unit41 = group.get_signal_with_unit("Azimuth_18_r")
    client00.addSignal2Axis(axis01, "Azimuth_18_r", time41, value41, unit=unit41, **kwargs)
    time42, value42, unit42 = group.get_signal_with_unit("Azimuth_19_r")
    client00.addSignal2Axis(axis01, "Azimuth_19_r", time42, value42, unit=unit42, **kwargs)
    time43, value43, unit43 = group.get_signal_with_unit("Azimuth_20_r")
    client00.addSignal2Axis(axis01, "Azimuth_20_r", time43, value43, unit=unit43, **kwargs)
    time44, value44, unit44 = group.get_signal_with_unit("Azimuth_21_r")
    client00.addSignal2Axis(axis01, "Azimuth_21_r", time44, value44, unit=unit44, **kwargs)
    time45, value45, unit45 = group.get_signal_with_unit("Azimuth_22_r")
    client00.addSignal2Axis(axis01, "Azimuth_22_r", time45, value45, unit=unit45, **kwargs)
    time46, value46, unit46 = group.get_signal_with_unit("Azimuth_23_r")
    client00.addSignal2Axis(axis01, "Azimuth_23_r", time46, value46, unit=unit46, **kwargs)
    time47, value47, unit47 = group.get_signal_with_unit("Azimuth_24_r")
    client00.addSignal2Axis(axis01, "Azimuth_24_r", time47, value47, unit=unit47, **kwargs)
    client01 = datavis.cPlotNavigator(title="", figureNr=None)
    self.sync.addClient(client01)
    axis02 = client01.addAxis()
    time48, value48, unit48 = group.get_signal_with_unit("Track1_sixPos")
    client01.addSignal2Axis(axis02, "Track1_sixPos", time48, value48, unit=unit48)
    time49, value49, unit49 = group.get_signal_with_unit("Track2_sixPos")
    client01.addSignal2Axis(axis02, "Track2_sixPos", time49, value49, unit=unit49)
    time50, value50, unit50 = group.get_signal_with_unit("Track3_sixPos")
    client01.addSignal2Axis(axis02, "Track3_sixPos", time50, value50, unit=unit50)
    axis03 = client01.addAxis()
    time51, value51, unit51 = group.get_signal_with_unit("Track1_siyPos")
    client01.addSignal2Axis(axis03, "Track1_siyPos", time51, value51, unit=unit51)
    time52, value52, unit52 = group.get_signal_with_unit("Track2_siyPos")
    client01.addSignal2Axis(axis03, "Track2_siyPos", time52, value52, unit=unit52)
    time53, value53, unit53 = group.get_signal_with_unit("Track3_siyPos")
    client01.addSignal2Axis(axis03, "Track3_siyPos", time53, value53, unit=unit53)
    client02 = datavis.cListNavigator(title="LN")
    self.sync.addClient(client02 )
    time54, value54 = self.source.getSignalFromSignalGroup(group, "AMBM_Fatal_Error3_r")
    client02.addsignal("AMBM_Fatal_Error3_r", (time54, value54), groupname="Default")
    client03 = datavis.cPlotNavigator(title="", figureNr=None)
    self.sync.addClient(client03)
    axis04 = client03.addAxis()
    time55, value55, unit55 = group.get_signal_with_unit("Power_01_r")
    client03.addSignal2Axis(axis04, "Power_01_r", time55, value55, unit=unit55, marker='.', **kwargs)
    time56, value56, unit56 = group.get_signal_with_unit("Power_02_r")
    client03.addSignal2Axis(axis04, "Power_02_r", time56, value56, unit=unit56, marker='.', **kwargs)
    time57, value57, unit57 = group.get_signal_with_unit("Power_03_r")
    client03.addSignal2Axis(axis04, "Power_03_r", time57, value57, unit=unit57, marker='.', **kwargs)
    time58, value58, unit58 = group.get_signal_with_unit("Power_04_r")
    client03.addSignal2Axis(axis04, "Power_04_r", time58, value58, unit=unit58, **kwargs)
    time59, value59, unit59 = group.get_signal_with_unit("Power_05_r")
    client03.addSignal2Axis(axis04, "Power_05_r", time59, value59, unit=unit59, **kwargs)
    time60, value60, unit60 = group.get_signal_with_unit("Power_06_r")
    client03.addSignal2Axis(axis04, "Power_06_r", time60, value60, unit=unit60, **kwargs)
    time61, value61, unit61 = group.get_signal_with_unit("Power_07_r")
    client03.addSignal2Axis(axis04, "Power_07_r", time61, value61, unit=unit61, **kwargs)
    time62, value62, unit62 = group.get_signal_with_unit("Power_08_r")
    client03.addSignal2Axis(axis04, "Power_08_r", time62, value62, unit=unit62, **kwargs)
    time63, value63, unit63 = group.get_signal_with_unit("Power_09_r")
    client03.addSignal2Axis(axis04, "Power_09_r", time63, value63, unit=unit63, **kwargs)
    time64, value64, unit64 = group.get_signal_with_unit("Power_10_r")
    client03.addSignal2Axis(axis04, "Power_10_r", time64, value64, unit=unit64, **kwargs)
    time65, value65, unit65 = group.get_signal_with_unit("Power_11_r")
    client03.addSignal2Axis(axis04, "Power_11_r", time65, value65, unit=unit65, **kwargs)
    time66, value66, unit66 = group.get_signal_with_unit("Power_12_r")
    client03.addSignal2Axis(axis04, "Power_12_r", time66, value66, unit=unit66, **kwargs)
    time67, value67, unit67 = group.get_signal_with_unit("Power_13_r")
    client03.addSignal2Axis(axis04, "Power_13_r", time67, value67, unit=unit67, **kwargs)
    time68, value68, unit68 = group.get_signal_with_unit("Power_14_r")
    client03.addSignal2Axis(axis04, "Power_14_r", time68, value68, unit=unit68, **kwargs)
    time69, value69, unit69 = group.get_signal_with_unit("Power_15_r")
    client03.addSignal2Axis(axis04, "Power_15_r", time69, value69, unit=unit69, **kwargs)
    time70, value70, unit70 = group.get_signal_with_unit("Power_16_r")
    client03.addSignal2Axis(axis04, "Power_16_r", time70, value70, unit=unit70, **kwargs)
    time71, value71, unit71 = group.get_signal_with_unit("Power_17_r")
    client03.addSignal2Axis(axis04, "Power_17_r", time71, value71, unit=unit71, **kwargs)
    time72, value72, unit72 = group.get_signal_with_unit("Power_18_r")
    client03.addSignal2Axis(axis04, "Power_18_r", time72, value72, unit=unit72, **kwargs)
    time73, value73, unit73 = group.get_signal_with_unit("Power_19_r")
    client03.addSignal2Axis(axis04, "Power_19_r", time73, value73, unit=unit73, **kwargs)
    time74, value74, unit74 = group.get_signal_with_unit("Power_20_r")
    client03.addSignal2Axis(axis04, "Power_20_r", time74, value74, unit=unit74, **kwargs)
    time75, value75, unit75 = group.get_signal_with_unit("Power_21_r")
    client03.addSignal2Axis(axis04, "Power_21_r", time75, value75, unit=unit75, **kwargs)
    time76, value76, unit76 = group.get_signal_with_unit("Power_22_r")
    client03.addSignal2Axis(axis04, "Power_22_r", time76, value76, unit=unit76, **kwargs)
    time77, value77, unit77 = group.get_signal_with_unit("Power_23_r")
    client03.addSignal2Axis(axis04, "Power_23_r", time77, value77, unit=unit77, **kwargs)
    time78, value78, unit78 = group.get_signal_with_unit("Power_24_r")
    client03.addSignal2Axis(axis04, "Power_24_r", time78, value78, unit=unit78, **kwargs)
    axis05 = client03.addAxis()
    time79, value79, unit79 = group.get_signal_with_unit("BeamNumber_01_r")
    client03.addSignal2Axis(axis05, "BeamNumber_01_r", time79, value79, unit=unit79, marker='.', **kwargs)
    time80, value80, unit80 = group.get_signal_with_unit("BeamNumber_02_r")
    client03.addSignal2Axis(axis05, "BeamNumber_02_r", time80, value80, unit=unit80, marker='.', **kwargs)
    time81, value81, unit81 = group.get_signal_with_unit("BeamNumber_03_r")
    client03.addSignal2Axis(axis05, "BeamNumber_03_r", time81, value81, unit=unit81, marker='.', **kwargs)
    time82, value82, unit82 = group.get_signal_with_unit("BeamNumber_04_r")
    client03.addSignal2Axis(axis05, "BeamNumber_04_r", time82, value82, unit=unit82, **kwargs)
    time83, value83, unit83 = group.get_signal_with_unit("BeamNumber_05_r")
    client03.addSignal2Axis(axis05, "BeamNumber_05_r", time83, value83, unit=unit83, **kwargs)
    time84, value84, unit84 = group.get_signal_with_unit("BeamNumber_06_r")
    client03.addSignal2Axis(axis05, "BeamNumber_06_r", time84, value84, unit=unit84, **kwargs)
    time85, value85, unit85 = group.get_signal_with_unit("BeamNumber_07_r")
    client03.addSignal2Axis(axis05, "BeamNumber_07_r", time85, value85, unit=unit85, **kwargs)
    time86, value86, unit86 = group.get_signal_with_unit("BeamNumber_08_r")
    client03.addSignal2Axis(axis05, "BeamNumber_08_r", time86, value86, unit=unit86, **kwargs)
    time87, value87, unit87 = group.get_signal_with_unit("BeamNumber_09_r")
    client03.addSignal2Axis(axis05, "BeamNumber_09_r", time87, value87, unit=unit87, **kwargs)
    time88, value88, unit88 = group.get_signal_with_unit("BeamNumber_10_r")
    client03.addSignal2Axis(axis05, "BeamNumber_10_r", time88, value88, unit=unit88, **kwargs)
    time89, value89, unit89 = group.get_signal_with_unit("BeamNumber_11_r")
    client03.addSignal2Axis(axis05, "BeamNumber_11_r", time89, value89, unit=unit89, **kwargs)
    time90, value90, unit90 = group.get_signal_with_unit("BeamNumber_12_r")
    client03.addSignal2Axis(axis05, "BeamNumber_12_r", time90, value90, unit=unit90, **kwargs)
    time91, value91, unit91 = group.get_signal_with_unit("BeamNumber_13_r")
    client03.addSignal2Axis(axis05, "BeamNumber_13_r", time91, value91, unit=unit91, **kwargs)
    time92, value92, unit92 = group.get_signal_with_unit("BeamNumber_14_r")
    client03.addSignal2Axis(axis05, "BeamNumber_14_r", time92, value92, unit=unit92, **kwargs)
    time93, value93, unit93 = group.get_signal_with_unit("BeamNumber_15_r")
    client03.addSignal2Axis(axis05, "BeamNumber_15_r", time93, value93, unit=unit93, **kwargs)
    time94, value94, unit94 = group.get_signal_with_unit("BeamNumber_16_r")
    client03.addSignal2Axis(axis05, "BeamNumber_16_r", time94, value94, unit=unit94, **kwargs)
    time95, value95, unit95 = group.get_signal_with_unit("BeamNumber_17_r")
    client03.addSignal2Axis(axis05, "BeamNumber_17_r", time95, value95, unit=unit95, **kwargs)
    time96, value96, unit96 = group.get_signal_with_unit("BeamNumber_18_r")
    client03.addSignal2Axis(axis05, "BeamNumber_18_r", time96, value96, unit=unit96, **kwargs)
    time97, value97, unit97 = group.get_signal_with_unit("BeamNumber_19_r")
    client03.addSignal2Axis(axis05, "BeamNumber_19_r", time97, value97, unit=unit97, **kwargs)
    time98, value98, unit98 = group.get_signal_with_unit("BeamNumber_20_r")
    client03.addSignal2Axis(axis05, "BeamNumber_20_r", time98, value98, unit=unit98, **kwargs)
    time99, value99, unit99 = group.get_signal_with_unit("BeamNumber_21_r")
    client03.addSignal2Axis(axis05, "BeamNumber_21_r", time99, value99, unit=unit99, **kwargs)
    time100, value100, unit100 = group.get_signal_with_unit("BeamNumber_22_r")
    client03.addSignal2Axis(axis05, "BeamNumber_22_r", time100, value100, unit=unit100, **kwargs)
    time101, value101, unit101 = group.get_signal_with_unit("BeamNumber_23_r")
    client03.addSignal2Axis(axis05, "BeamNumber_23_r", time101, value101, unit=unit101, **kwargs)
    time102, value102, unit102 = group.get_signal_with_unit("BeamNumber_24_r")
    client03.addSignal2Axis(axis05, "BeamNumber_24_r", time102, value102, unit=unit102, **kwargs)
    axis06 = client03.addAxis()
    time103, value103, unit103 = group.get_signal_with_unit("Velocity_01_r")
    client03.addSignal2Axis(axis06, "Velocity_01_r", time103, value103, unit=unit103, marker='.', **kwargs)
    time104, value104, unit104 = group.get_signal_with_unit("Velocity_02_r")
    client03.addSignal2Axis(axis06, "Velocity_02_r", time104, value104, unit=unit104, marker='.', **kwargs)
    time105, value105, unit105 = group.get_signal_with_unit("Velocity_03_r")
    client03.addSignal2Axis(axis06, "Velocity_03_r", time105, value105, unit=unit105, marker='.', **kwargs)
    time106, value106, unit106 = group.get_signal_with_unit("Velocity_04_r")
    client03.addSignal2Axis(axis06, "Velocity_04_r", time106, value106, unit=unit106, **kwargs)
    time107, value107, unit107 = group.get_signal_with_unit("Velocity_05_r")
    client03.addSignal2Axis(axis06, "Velocity_05_r", time107, value107, unit=unit107, **kwargs)
    time108, value108, unit108 = group.get_signal_with_unit("Velocity_06_r")
    client03.addSignal2Axis(axis06, "Velocity_06_r", time108, value108, unit=unit108, **kwargs)
    time109, value109, unit109 = group.get_signal_with_unit("Velocity_07_r")
    client03.addSignal2Axis(axis06, "Velocity_07_r", time109, value109, unit=unit109, **kwargs)
    time110, value110, unit110 = group.get_signal_with_unit("Velocity_08_r")
    client03.addSignal2Axis(axis06, "Velocity_08_r", time110, value110, unit=unit110, **kwargs)
    time111, value111, unit111 = group.get_signal_with_unit("Velocity_09_r")
    client03.addSignal2Axis(axis06, "Velocity_09_r", time111, value111, unit=unit111, **kwargs)
    time112, value112, unit112 = group.get_signal_with_unit("Velocity_10_r")
    client03.addSignal2Axis(axis06, "Velocity_10_r", time112, value112, unit=unit112, **kwargs)
    time113, value113, unit113 = group.get_signal_with_unit("Velocity_11_r")
    client03.addSignal2Axis(axis06, "Velocity_11_r", time113, value113, unit=unit113, **kwargs)
    time114, value114, unit114 = group.get_signal_with_unit("Velocity_12_r")
    client03.addSignal2Axis(axis06, "Velocity_12_r", time114, value114, unit=unit114, **kwargs)
    time115, value115, unit115 = group.get_signal_with_unit("Velocity_13_r")
    client03.addSignal2Axis(axis06, "Velocity_13_r", time115, value115, unit=unit115, **kwargs)
    time116, value116, unit116 = group.get_signal_with_unit("Velocity_14_r")
    client03.addSignal2Axis(axis06, "Velocity_14_r", time116, value116, unit=unit116, **kwargs)
    time117, value117, unit117 = group.get_signal_with_unit("Velocity_15_r")
    client03.addSignal2Axis(axis06, "Velocity_15_r", time117, value117, unit=unit117, **kwargs)
    time118, value118, unit118 = group.get_signal_with_unit("Velocity_16_r")
    client03.addSignal2Axis(axis06, "Velocity_16_r", time118, value118, unit=unit118, **kwargs)
    time119, value119, unit119 = group.get_signal_with_unit("Velocity_17_r")
    client03.addSignal2Axis(axis06, "Velocity_17_r", time119, value119, unit=unit119, **kwargs)
    time120, value120, unit120 = group.get_signal_with_unit("Velocity_18_r")
    client03.addSignal2Axis(axis06, "Velocity_18_r", time120, value120, unit=unit120, **kwargs)
    time121, value121, unit121 = group.get_signal_with_unit("Velocity_19_r")
    client03.addSignal2Axis(axis06, "Velocity_19_r", time121, value121, unit=unit121, **kwargs)
    time122, value122, unit122 = group.get_signal_with_unit("Velocity_20_r")
    client03.addSignal2Axis(axis06, "Velocity_20_r", time122, value122, unit=unit122, **kwargs)
    time123, value123, unit123 = group.get_signal_with_unit("Velocity_21_r")
    client03.addSignal2Axis(axis06, "Velocity_21_r", time123, value123, unit=unit123, **kwargs)
    time124, value124, unit124 = group.get_signal_with_unit("Velocity_22_r")
    client03.addSignal2Axis(axis06, "Velocity_22_r", time124, value124, unit=unit124, **kwargs)
    time125, value125, unit125 = group.get_signal_with_unit("Velocity_23_r")
    client03.addSignal2Axis(axis06, "Velocity_23_r", time125, value125, unit=unit125, **kwargs)
    time126, value126, unit126 = group.get_signal_with_unit("Velocity_24_r")
    client03.addSignal2Axis(axis06, "Velocity_24_r", time126, value126, unit=unit126, **kwargs)
    return
