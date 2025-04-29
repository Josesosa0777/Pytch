# -*- dataeval: init -*-

import datavis
from interface import iView

# def_param = interface.NullParam

sgs = [
    {
        "CemState": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState"),
        "eSigStatus": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                       "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sSigHeader_eSigStatus"),
        "sensorRadar_state": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                              "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state"),
        "sensorCamera_state": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                               "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state"),

    },
    {
        "CemState": (
            "CEM_FDP_KB_M_p_StateOutputIfMeas", "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState"),
        "eSigStatus": ("CEM_FDP_KB_M_p_StateOutputIfMeas",
                       "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sSigHeader_eSigStatus"),
        "sensorRadar_state": ("CEM_FDP_KB_M_p_StateOutputIfMeas",
                              "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state"),
        "sensorCamera_state": ("CEM_FDP_KB_M_p_StateOutputIfMeas",
                               "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state"),

    }
]
vehSpdSgs = [
    {
        "FrontAxleSpeed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
    },
    {
        "FrontAxleSpeed": ("EBC2", "FrontAxleSpeed_s0B"),
    },
    {
        "FrontAxleSpeed": ("EBC2_s0B", "FrontAxleSpeed"),
    },
    {
        "FrontAxleSpeed": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                           "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
    },
    {
        "FrontAxleSpeed": ("EBC2_0B_s0B_EBC2_0B_CAN20_16_idx877", "EBC2_FrontAxleSpeed_0B"),
    }
]


class View(iView):
    def check(self):
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        veh_grp = self.source.selectLazySignalGroup(vehSpdSgs)

        if veh_grp.has_key('FrontAxleSpeed'):
            group["FrontAxleSpeed"] = veh_grp["FrontAxleSpeed"]
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
        for alias in vehSpdSgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
        return group

    def view(self, group):

        pn = datavis.cPlotNavigator(title="CEM STATES")
        mapping_cem = {0: 'OFF', 1: 'INIT', 2: 'NORMAL', 3: 'FAILURE'}
        mapping = {0: 'FAILED', 1: 'DEGRADED', 2: 'AVAILABLE'}
        mapping_eSig = {0: 'AL_SIG_STATE_INIT', 1: 'AL_SIG_STATE_OK', 2: 'AL_SIG_STATE_INVALID'}

        axis00 = pn.addAxis(ylabel='CemState', yticks=mapping_cem,
                            ylim=(min(mapping_cem) - 0.5, max(mapping_cem) + 0.5))
        if "CemState" in group:
            time_CemState, value_CemState, unit_CemState = group.get_signal_with_unit("CemState")
            pn.addSignal2Axis(axis00, "CemState", time_CemState, value_CemState, unit=unit_CemState)

        axis01 = pn.addAxis(ylabel='sSigHeader_eSigStatus', yticks=mapping_eSig,
                            ylim=(min(mapping_eSig) - 0.5, max(mapping_eSig) + 0.5))
        if "eSigStatus" in group:
            time_sSigHeader_eSigStatus, value_sSigHeader_eSigStatus, unit_SigHeader_eSigStatus = group.get_signal_with_unit(
                "eSigStatus")
            pn.addSignal2Axis(axis01, "sSigHeader_eSigStatus", time_sSigHeader_eSigStatus, value_sSigHeader_eSigStatus,
                              unit=unit_SigHeader_eSigStatus)

        axis02 = pn.addAxis(ylabel='SensorState', yticks=mapping, ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
        if "sensorRadar_state" in group and "sensorCamera_state" in group:
            time_sensorRadar_state, value_sensorRadar_state, unit_sensorRadar_state = group.get_signal_with_unit(
                "sensorRadar_state")
            pn.addSignal2Axis(axis02, "sensorRadar_state", time_sensorRadar_state, value_sensorRadar_state,
                              unit=unit_sensorRadar_state)

            time_sensorCamera_state, value_sensorCamera_state, unit_sensorCamera_state = group.get_signal_with_unit(
                "sensorCamera_state")
            pn.addSignal2Axis(axis02, "sensorCamera_state", time_sensorCamera_state, value_sensorCamera_state,
                              unit=unit_sensorCamera_state)

        axis03 = pn.addAxis(ylabel='FrontAxleSpeed')
        if "FrontAxleSpeed" in group:
            time_FrontAxleSpeed, value_FrontAxleSpeed, unit_FrontAxleSpeed = group.get_signal_with_unit(
                "FrontAxleSpeed")
            pn.addSignal2Axis(axis03, "FrontAxleSpeed", time_FrontAxleSpeed, value_FrontAxleSpeed,
                              unit=unit_FrontAxleSpeed)

        self.sync.addClient(pn)
        return
