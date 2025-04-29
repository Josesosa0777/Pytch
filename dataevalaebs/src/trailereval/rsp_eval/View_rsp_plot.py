# -*- dataeval: init -*-
from matplotlib import pyplot as plt

import datavis
from interface import iView

#def_param = interface.NullParam


RSP_sig =[
{
    # Group1
    "P21_p": ("Lausch_1", "P21_p"),
    "P21_Pdes": ("Lausch_26","P21_Pdes"),
    "P21_Pref": ("Lausch_26","P21_Pref"),
    "P22_p": ("Lausch_1", "P22_p"),
    "P22_Pdes": ("Lausch_26","P22_Pdes"),
    "P22_Pref": ("Lausch_26","P22_Pref"),
    "CanDemand": ("Lausch_11", "CanDemand"),
    "PneuDemand": ("Lausch_11", "PneuDemand"),
    "PdesDriver": ("Lausch_11", "PdesDriver"),
    "EM_P2_p": ("Lausch_31","EM_P2_p"),
    "PdemABSP2": ("Lausch_29","PdemABSP2"),
    "PdemEbsBxg0": ("Lausch_28","PdemEbsBxg0"),
    "PdemEbsBxg1": ("Lausch_28","PdemEbsBxg1"),


    # Group2
    "VrefFilter": ("Lausch_2","VrefFilter"),
    "SC_v": ("Lausch_1", "SC_v"),
    "SD_v": ("Lausch_1", "SD_v"),
    "SA_v": ("Lausch_29","SA_v"),
    "SB_v": ("Lausch_29","SB_v"),
    "SE_v": ("Lausch_30","SE_v"),
    "SF_v": ("Lausch_30","SF_v"),


    # Group3
    "AyFilt": ("Lausch_17","AyFilt"),
    "AyHFilt": ("Lausch_17","AyHFilt"),
    "AyLimLeft": ("Lausch_17","AyLimLeft"),
    "AyLimRight": ("Lausch_17","AyLimRight"),
    "dAyWeight": ("Lausch_18","dAyWeight"),

    # Group4
    "RSPtUnstabA": ("Lausch_18","RSPtUnstabA"),
    "RSPtUnstabB": ("Lausch_18","RSPtUnstabB"),
    "RSPtUnstabC": ("Lausch_18","RSPtUnstabC"),
    "RSPtUnstabD": ("Lausch_18","RSPtUnstabD"),
    "RSPtUnstabE": ("Lausch_18","RSPtUnstabE"),
    "RSPtUnstabF": ("Lausch_18","RSPtUnstabF"),

    # Group5
    "RSPStep1Enabled": ("Lausch_19","RSPStep1Enabled"),

    # Group6
    "RSPStep2Enabled": ("Lausch_19","RSPStep2Enabled"),

    # Group7
    "RSPTestedLifted": ("Lausch_19","RSPTestedLifted"),

    # Group8
    "RSPStep1Active": ("Lausch_19","RSPStep1Active"),
    "RSPStep2Active": ("Lausch_19","RSPStep2Active"),
    "RSPTestActive": ("Lausch_19","RSPTestActive"),

    # Group9
    # Group10
  },
]

signalColors={
    # Group 1
    'P21_p' : 'limegreen',
    'P21_Pdes' : 'green',
    'P21_Pref' : 'lightseagreen',
    'P22_p' : 'red',
    'P22_Pdes' : 'darkred',
    'P22_Pref' : 'mediumorchid',
    # 'CanDemand' : '?',
    # 'PneuDemand' : '?',
    'PdesDriver' : 'white',
    'EM_P2_p' : 'lightskyblue',
    'PdemABSP2' : 'paleturquoise',
    'PdemEbsBxg0' : 'darkgrey',
    # 'PdemEbsBxg1' : '',

    #  Group2
    'VrefFilter' : 'white',
    'SC_v' : 'red',
    'SD_v' : 'limegreen',
    'SA_v' : 'magenta',
    'SB_v' : 'cyan',
    # 'SE_v' : 'white',
    # 'SF_v' : 'white',

    # Group3
    "AyFilt": 'magenta',
    "AyHFilt": 'yellow',
    "AyLimLeft": 'goldenrod',
    "AyLimRight": 'goldenrod',
    "dAyWeight": 'cyan',

    # Group4
    "RSPtUnstabA": 'magenta' ,
    "RSPtUnstabB": 'cyan',
    "RSPtUnstabC": 'red',
    "RSPtUnstabD":'limegreen',
    # "RSPtUnstabE": ,
    # "RSPtUnstabF": ,

    # Group5
    "RSPStep1Enabled": 'yellow',

    # Group6
    "RSPStep2Enabled": 'green',

    # Group7
    "RSPTestedLifted": 'lightsteelblue',

    # Group8
    "RSPStep1Active": 'yellow',
    "RSPStep2Active": 'red',
    "RSPTestActive": 'darkgrey',

    # Group9
    # Group10
}

class View(iView):
  def check(self):
    # select signals
    group = self.get_source().selectSignalGroup(RSP_sig)
    # # give warning for not available signals
    for alias in RSP_sig[0]:
      if alias not in group:
        self.logger.warning("Signal for '%s' not available" % alias)
    return group

  def view(self, group,):

    pn = datavis.cPlotNavigator(title="RSP Evaluation")
    # axis00 = pn.addAxis(ylabel='RSP Plot')
    ax = pn.addAxis(ylabel="Group 1", ylim=(-500.0, 9000.0))
    ax.set_axis_bgcolor('black')
    ax.grid(True,color='white',linewidth=0.5)

    # Group 1
    if 'P21_p' in group:
        time00, value00, unit00 = group.get_signal_with_unit("P21_p")
        pn.addSignal2Axis(ax, "P21_p", time00, value00, unit=unit00,  linewidth=2, color=signalColors['P21_p'])
        pn.setLegend(ax, 'RSP')
    if 'P21_Pdes' in group:
        time00, value00, unit00 = group.get_signal_with_unit("P21_Pdes")
        pn.addSignal2Axis(ax, "P21_Pdes", time00, value00, unit=unit00,  linewidth=2, color=signalColors['P21_Pdes'])
        pn.setLegend(ax, 'RSP')
    if 'P21_Pref' in group:
        time00, value00, unit00 = group.get_signal_with_unit("P21_Pref")
        pn.addSignal2Axis(ax, "P21_Pref", time00, value00, unit=unit00,  linewidth=2, color=signalColors['P21_Pref'])
        pn.setLegend(ax, 'RSP')
    if 'P22_p' in group:
        time00, value00, unit00 = group.get_signal_with_unit("P22_p")
        pn.addSignal2Axis(ax, "P22_p", time00, value00, unit=unit00,  linewidth=2, color=signalColors['P22_p'])
        pn.setLegend(ax, 'RSP')
    if 'P22_Pdes' in group:
        time00, value00, unit00 = group.get_signal_with_unit("P22_Pdes")
        pn.addSignal2Axis(ax, "P22_Pdes", time00, value00, unit=unit00,  linewidth=2, color=signalColors['P22_Pdes'])
        pn.setLegend(ax, 'RSP')
    if 'P22_Pref' in group:
        time00, value00, unit00 = group.get_signal_with_unit("P22_Pref")
        pn.addSignal2Axis(ax, "P22_Pref", time00, value00, unit=unit00,  linewidth=2, color=signalColors['P22_Pref'])
        pn.setLegend(ax, 'RSP')
    if 'CanDemand' in group:
        time00, value00, unit00 = group.get_signal_with_unit("CanDemand")
        pn.addSignal2Axis(ax, "CanDemand", time00, value00, unit=unit00,  linewidth=2)
        pn.setLegend(ax, 'RSP')
    if 'PneuDemand' in group:
        time00, value00, unit00 = group.get_signal_with_unit("PneuDemand")
        pn.addSignal2Axis(ax, "PneuDemand", time00, value00, unit=unit00,  linewidth=2)
        pn.setLegend(ax, 'RSP')
    if 'PdesDriver' in group:
        time00, value00, unit00 = group.get_signal_with_unit("PdesDriver")
        pn.addSignal2Axis(ax, "PdesDriver", time00, value00, unit=unit00,  linewidth=2, color=signalColors['PdesDriver'])
        pn.setLegend(ax, 'RSP')
    if 'EM_P2_p' in group:
        time00, value00, unit00 = group.get_signal_with_unit("EM_P2_p")
        pn.addSignal2Axis(ax, "EM_P2_p", time00, value00, unit=unit00,  linewidth=2, color=signalColors['EM_P2_p'])
        pn.setLegend(ax, 'RSP')
    if 'PdemABSP2' in group:
        time00, value00, unit00 = group.get_signal_with_unit("PdemABSP2")
        pn.addSignal2Axis(ax, "PdemABSP2", time00, value00, unit=unit00,  linewidth=2, color=signalColors['PdemABSP2'])
        pn.setLegend(ax, 'RSP')
    if 'PdemEbsBxg0' in group:
        time00, value00, unit00 = group.get_signal_with_unit("PdemEbsBxg0")
        pn.addSignal2Axis(ax, "PdemEbsBxg0", time00, value00, unit=unit00,  linewidth=2, color=signalColors['PdemEbsBxg0'])
        pn.setLegend(ax, 'RSP')
    if 'PdemEbsBxg1' in group:
        time00, value00, unit00 = group.get_signal_with_unit("PdemEbsBxg1")
        pn.addSignal2Axis(ax, "PdemEbsBxg1", time00, value00, unit=unit00,  linewidth=2)
        pn.setLegend(ax, 'RSP')

    ax = pn.addAxis(ylabel="Group 2",ylim=(2000.0, 8000.0))
    ax.set_axis_bgcolor('black')
    ax.grid(True,color='white',linewidth=0.5)

    # Group 2
    if 'VrefFilter' in group:
        time00, value00, unit00 = group.get_signal_with_unit("VrefFilter")
        pn.addSignal2Axis(ax, "VrefFilter", time00, value00, unit=unit00,  linewidth=2, color=signalColors['VrefFilter'])
        pn.setLegend(ax, 'RSP')
    if 'SC_v' in group:
        time00, value00, unit00 = group.get_signal_with_unit("SC_v")
        pn.addSignal2Axis(ax, "SC_v", time00, value00, unit=unit00,  linewidth=2, color=signalColors['SC_v'])
        pn.setLegend(ax, 'RSP')
    if 'SD_v' in group:
        time00, value00, unit00 = group.get_signal_with_unit("SD_v")
        pn.addSignal2Axis(ax, "SD_v", time00, value00, unit=unit00,  linewidth=2, color=signalColors['SD_v'])
        pn.setLegend(ax, 'RSP')
    if 'SA_v' in group:
        time00, value00, unit00 = group.get_signal_with_unit("SA_v")
        pn.addSignal2Axis(ax, "SA_v", time00, value00, unit=unit00,  linewidth=2, color=signalColors['SA_v'])
        pn.setLegend(ax, 'RSP')
    if 'SB_v' in group:
        time00, value00, unit00 = group.get_signal_with_unit("SB_v")
        pn.addSignal2Axis(ax, "SB_v", time00, value00, unit=unit00,  linewidth=2, color=signalColors['SB_v'])
        pn.setLegend(ax, 'RSP')
    if 'SE_v' in group:
        time00, value00, unit00 = group.get_signal_with_unit("SE_v")
        pn.addSignal2Axis(ax, "SE_v", time00, value00, unit=unit00,  linewidth=2)
        pn.setLegend(ax, 'RSP')
    if 'SF_v' in group:
        time00, value00, unit00 = group.get_signal_with_unit("SF_v")
        pn.addSignal2Axis(ax, "SF_v", time00, value00, unit=unit00,  linewidth=2)
        pn.setLegend(ax, 'RSP')


    # ax = pn.addAxis(ylabel="Group 3")
    #
    # # Group 3
    # if 'AyFilt' in group:
    #     time00, value00, unit00 = group.get_signal_with_unit("AyFilt")
    #     pn.addSignal2Axis(ax, "AyFilt", time00, value00, unit=unit00,  linewidth=2)
    # if 'AyHFilt' in group:
    #     time00, value00, unit00 = group.get_signal_with_unit("AyHFilt")
    #     pn.addSignal2Axis(ax, "AyHFilt", time00, value00, unit=unit00,  linewidth=2)
    # if 'AyLimLeft' in group:
    #     time00, value00, unit00 = group.get_signal_with_unit("AyLimLeft")
    #     pn.addSignal2Axis(ax, "AyLimLeft", time00, value00, unit=unit00,  linewidth=2)
    # if 'AyLimRight' in group:
    #     time00, value00, unit00 = group.get_signal_with_unit("AyLimRight")
    #     pn.addSignal2Axis(ax, "AyLimRight", time00, value00, unit=unit00,  linewidth=2)
    # if 'dAyWeight' in group:
    #     time00, value00, unit00 = group.get_signal_with_unit("dAyWeight")
    #     pn.addSignal2Axis(ax, "dAyWeight", time00, value00, unit=unit00,  linewidth=2)

    ax = pn.addAxis(ylabel="Group 4")
    ax.legend(bbox_to_anchor=(1.00, 1.10))
    ax.set_axis_bgcolor('black')
    ax.grid(True,color='white',linewidth=0.5)

    # Group 4
    if 'RSPtUnstabA' in group:
        time00, value00, unit00 = group.get_signal_with_unit("RSPtUnstabA")
        pn.addSignal2Axis(ax, "RSPtUnstabA", time00, value00, unit=unit00,  linewidth=2, color=signalColors['RSPtUnstabA'])
        pn.setLegend(ax, 'RSP')
    if 'RSPtUnstabB' in group:
        time00, value00, unit00 = group.get_signal_with_unit("RSPtUnstabB")
        pn.addSignal2Axis(ax, "RSPtUnstabB", time00, value00, unit=unit00,  linewidth=2, color=signalColors['RSPtUnstabB'])
        pn.setLegend(ax, 'RSP')
    if 'RSPtUnstabC' in group:
        time00, value00, unit00 = group.get_signal_with_unit("RSPtUnstabC")
        pn.addSignal2Axis(ax, "RSPtUnstabC", time00, value00, unit=unit00,  linewidth=2, color=signalColors['RSPtUnstabC'])
        pn.setLegend(ax, 'RSP')
    if 'RSPtUnstabD' in group:
        time00, value00, unit00 = group.get_signal_with_unit("RSPtUnstabD")
        pn.addSignal2Axis(ax, "RSPtUnstabD", time00, value00, unit=unit00,  linewidth=2, color=signalColors['RSPtUnstabD'])
        pn.setLegend(ax, 'RSP')
    if 'RSPtUnstabE' in group:
        time00, value00, unit00 = group.get_signal_with_unit("RSPtUnstabE")
        pn.addSignal2Axis(ax, "RSPtUnstabE", time00, value00, unit=unit00,  linewidth=2)
        pn.setLegend(ax, 'RSP')
    if 'RSPtUnstabF' in group:
        time00, value00, unit00 = group.get_signal_with_unit("RSPtUnstabF")
        pn.addSignal2Axis(ax, "RSPtUnstabF", time00, value00, unit=unit00,  linewidth=2)
        pn.setLegend(ax, 'RSP')

    # ax = pn.addAxis(ylabel="Group 5")
    #
    # # Group 5
    # if 'RSPStep1Enabled' in group:
    #     time00, value00, unit00 = group.get_signal_with_unit("RSPStep1Enabled")
    #     pn.addSignal2Axis(ax, "RSPStep1Enabled", time00, value00, unit=unit00,  linewidth=2)
    #
    # ax = pn.addAxis(ylabel="Group 6")
    #
    # # Group 6
    # if 'RSPStep2Enabled' in group:
    #     time00, value00, unit00 = group.get_signal_with_unit("RSPStep2Enabled")
    #     pn.addSignal2Axis(ax, "RSPStep2Enabled", time00, value00, unit=unit00,  linewidth=2)
    #
    # ax = pn.addAxis(ylabel="Group 7")
    #
    # # Group 7
    # if 'RSPTestedLifted' in group:
    #     time00, value00, unit00 = group.get_signal_with_unit("RSPTestedLifted")
    #     pn.addSignal2Axis(ax, "RSPTestedLifted", time00, value00, unit=unit00,  linewidth=2)
    #
    # ax = pn.addAxis(ylabel="Group 8")
    #
    # # Group 8
    # if 'RSPStep1Active' in group:
    #     time00, value00, unit00 = group.get_signal_with_unit("RSPStep1Active")
    #     pn.addSignal2Axis(ax, "RSPStep1Active.", time00, value00, unit=unit00,  linewidth=2)
    # if 'RSPStep2Active' in group:
    #     time00, value00, unit00 = group.get_signal_with_unit("RSPStep2Active")
    #     pn.addSignal2Axis(ax, "RSPStep2Active", time00, value00, unit=unit00,  linewidth=2)
    # if 'RSPTestActive' in group:
    #     time00, value00, unit00 = group.get_signal_with_unit("RSPTestActive")
    #     pn.addSignal2Axis(ax, "RSPTestActive", time00, value00, unit=unit00,  linewidth=2)

    # legendOrder = [
    #             "WLRed" ,
    #             "WLYellow",
    #             "WLInfo" ,
    #             "VrefFilter",
    #           "RSPStep1Enabled",
    #           "RSPStep2Enabled",
    #           "RSPStep3Enabled",
    #           "RSPTestedLifted",
    #           "RSPTestActive",
    #           "RSPStep1Active",
    #           "RSPStep2Active",
    #           "RSPStep3Active",
    #           "dAyWeight",
    #           "RSPtUnstabC",
    #           "RSPtUnstabD",
    #           "AyFilt",
    #           "AyHFilt",
    #           "AyLimLeft",
    #           "AyLimRight",
    #           "P4_p",
    #           "PdesDriver",
    #           "P21_p",
    #           "P22_p",
    #           "SC_v",
    #           "SD_v"]
    # axis00.set_axis_bgcolor('black')
    # axis00.grid(True,color='white',linewidth=1)
    # for grp in legendOrder:
    #     if grp in group:
    #       time,value, unit = group.get_signal_with_unit(grp)
    #       pn.addSignal2Axis(axis00, grp, time,value, unit=unit,color=signalColors[grp])
    self.sync.addClient(pn)
    return
