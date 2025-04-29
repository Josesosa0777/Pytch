# -*- dataeval: init -*-

import numpy as np

import interface
import measparser

Aliases = 'dxv', 'dyv', 'vxv', 'Index'

SignalGroups = []
SignalGroup = {}
for Alias in Aliases:
  SignalGroup[Alias] = 'ECU', 'Mrf._.PssObjectDebugInfo.%s' %(Alias)
SignalGroups.append(SignalGroup)
PSSSignalGroups = [{"repprew.__b_Rep.__b_RepBase.status": ("ECU", "repprew.__b_Rep.__b_RepBase.status"),
                    "repretg.__b_Rep.__b_RepBase.status": ("ECU", "repretg.__b_Rep.__b_RepBase.status"),
                    "csi.4AsfSysCondBc_TC.sysCondBcFlags.sysCondBcFlags.ObjConfirmedByVideo_b": ("ECU", "csi.4AsfSysCondBc_TC.sysCondBcFlags.sysCondBcFlags.ObjConfirmedByVideo_b"),
                    "vlc.Phy_T20.AsfFlags.w.ReqFlagsDecReqASF_b": ("ECU", "vlc.Phy_T20.AsfFlags.w.ReqFlagsDecReqASF_b"),
                    "vlc.Phy_T20.axvCvASF": ("ECU", "vlc.Phy_T20.axvCvASF"),},]
  
class cFill(interface.iObjectFill):
  def check(self):
    Groups, Errors = interface.Source._filterSignalGroups(SignalGroups)
    measparser.signalgroup.check_allvalid(Groups, Errors, len(Aliases))
    PSSGroups, Errors = interface.Source._filterSignalGroups(PSSSignalGroups)
    measparser.signalgroup.check_allvalid(PSSGroups, Errors, 5)
    return Groups, PSSGroups

  def fill(self, Groups, PSSGroups):
    Group = Groups[0]
    PSSGroup = PSSGroups[0]

    Signals = measparser.signalgroup.extract_signals(Groups, PSSGroups)
    scaletime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    len_scaletime = len(scaletime)
    Objects = []

    owarning = {}
    owarning["dx"] = interface.Source.getSignalFromSignalGroup(Group, 'dxv',         ScaleTime=scaletime)[1]
    owarning["dy"] = interface.Source.getSignalFromSignalGroup(Group, 'dyv',         ScaleTime=scaletime)[1]
    owarning["dv"] = interface.Source.getSignalFromSignalGroup(Group, 'vxv',         ScaleTime=scaletime)[1]
    owarning["id"] = interface.Source.getSignalFromSignalGroup(Group, 'Index',       ScaleTime=scaletime)[1]
    WarningReq = interface.Source.getSignalFromSignalGroup(PSSGroup, "repprew.__b_Rep.__b_RepBase.status", ScaleTime=scaletime)[1]
    owarning["label"] = ""
    owarning["type"]  = np.where(WarningReq == 6,
                          self.get_grouptype('LRR3_ASF_WARNING'), 
                          self.get_grouptype('NONE_TYPE'))
    Objects.append(owarning)

    obrake = {}
    obrake["dx"] = interface.Source.getSignalFromSignalGroup(Group, 'dxv',         ScaleTime=scaletime)[1]
    obrake["dy"] = interface.Source.getSignalFromSignalGroup(Group, 'dyv',         ScaleTime=scaletime)[1]
    obrake["dv"] = interface.Source.getSignalFromSignalGroup(Group, 'vxv',         ScaleTime=scaletime)[1]
    obrake["id"] = interface.Source.getSignalFromSignalGroup(Group, 'Index',       ScaleTime=scaletime)[1]
    Decell = interface.Source.getSignalFromSignalGroup(PSSGroup, "vlc.Phy_T20.axvCvASF", ScaleTime=scaletime)[1]
    BrakeReq = interface.Source.getSignalFromSignalGroup(PSSGroup, "vlc.Phy_T20.AsfFlags.w.ReqFlagsDecReqASF_b", ScaleTime=scaletime)[1]
    obrake["type"]  = np.where(BrakeReq > 0,
                          self.get_grouptype('LRR3_ASF_BRAKE'), 
                          self.get_grouptype('NONE_TYPE'))
    obrake["label"] = ""
    obrake["color"] = np.zeros((3, Decell.size), dtype=int)
    obrake["color"][0] = Decell * -25
    obrake["color"] = obrake["color"].T
    Objects.append(obrake)

    ovideoconf = {}
    ovideoconf["dx"] = interface.Source.getSignalFromSignalGroup(Group, 'dxv',         ScaleTime=scaletime)[1]
    ovideoconf["dy"] = interface.Source.getSignalFromSignalGroup(Group, 'dyv',         ScaleTime=scaletime)[1]
    ovideoconf["dv"] = interface.Source.getSignalFromSignalGroup(Group, 'vxv',         ScaleTime=scaletime)[1]
    ovideoconf["id"] = interface.Source.getSignalFromSignalGroup(Group, 'Index',       ScaleTime=scaletime)[1]
    VideoConf = interface.Source.getSignalFromSignalGroup(PSSGroup, "csi.4AsfSysCondBc_TC.sysCondBcFlags.sysCondBcFlags.ObjConfirmedByVideo_b", ScaleTime=scaletime)[1]
    ovideoconf["label"] = ""
    ovideoconf["type"]  = np.where(VideoConf > 0,
                          self.get_grouptype('LRR3_ASF_VIDEOCONF'), 
                          self.get_grouptype('NONE_TYPE'))
    Objects.append(ovideoconf)
    return scaletime, Objects
