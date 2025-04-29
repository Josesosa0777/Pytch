# -*- dataeval: init -*-

import datavis
from interface import iView

# def_param = interface.NullParam
sgs = [
    {
        "engine_speed": ("CAN_MFC_Public_EEC1_00", "EEC1_EngSpd_00"),
        "aebs_state": ("CAN_MFC_Public_AEBS1_2A", "AEBS1_AEBSState_2A"),
        "ldws_state": ("CAN_MFC_Public_FLI2_E8", "FLI2_LDWSState_E8"),
        "front_axle_speed": ("CAN_MFC_Public_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
        # Sensor_State
        "sensorRadar_state": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                              "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state"),
        "sensorCamera_state": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                               "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state"),
        # CEM_State
        "CemState": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState")
    },
]


class View(iView):
    def check(self):
        # select signals
        group = self.source.selectLazySignalGroup(sgs)

        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
        return group

    def view(self, group):

        pn = datavis.cPlotNavigator(title=" ")

        axis00 = pn.addAxis(ylabel='')
        if "aebs_state" in group:
            time_aebs_state, value_aebs_state, unit_aebs_state = group.get_signal_with_unit(
                "aebs_state")
            pn.addSignal2Axis(axis00, "aebs_state", time_aebs_state, value_aebs_state,
                              unit=unit_aebs_state)

        if "ldws_state" in group:
            time_ldws_state, value_ldws_state, unit_ldws_state = group.get_signal_with_unit(
                "ldws_state")
            pn.addSignal2Axis(axis00, "ldws_state", time_ldws_state, value_ldws_state,
                              unit=unit_ldws_state)

        axis01 = pn.addAxis(ylabel='engine_speed')
        if "engine_speed" in group:
            time_engine_speed, value_engine_speed, unit_engine_speed = group.get_signal_with_unit(
                "engine_speed")
            pn.addSignal2Axis(axis01, "engine_speed", time_engine_speed, value_engine_speed,
                              unit=unit_engine_speed)

        axis02 = pn.addAxis(ylabel='FrontAxleSpeed')
        if "front_axle_speed" in group:
            time_front_axle_speed, value_front_axle_speed, unit_front_axle_speed = group.get_signal_with_unit(
                "front_axle_speed")
            pn.addSignal2Axis(axis02, "FrontAxleSpeed", time_front_axle_speed, value_front_axle_speed,
                              unit=unit_front_axle_speed)

        mapping = {0: 'FAILED', 1: 'DEGRADED', 2: 'AVAILABLE'}

        if "sensorRadar_state" in group and "sensorCamera_state" in group:
            axis00 = pn.addAxis(ylabel='SensorState', yticks=mapping, ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
            time_sensorRadar_state, value_sensorRadar_state, unit_sensorRadar_state = group.get_signal_with_unit(
                "sensorRadar_state")
            pn.addSignal2Axis(axis00, "sensorRadar_state", time_sensorRadar_state, value_sensorRadar_state,
                              unit=unit_sensorRadar_state)

            time_sensorCamera_state, value_sensorCamera_state, unit_sensorCamera_state = group.get_signal_with_unit(
                "sensorCamera_state")
            pn.addSignal2Axis(axis00, "sensorCamera_state", time_sensorCamera_state, value_sensorCamera_state,
                              unit=unit_sensorCamera_state)

        mapping_cem = {0: 'OFF', 1: 'INIT', 2: 'NORMAL', 3: 'FAILURE'}

        if "CemState" in group:
            axis01 = pn.addAxis(ylabel='CemState', yticks=mapping_cem,
                                ylim=(min(mapping_cem) - 0.5, max(mapping_cem) + 0.5))
            time_CemState, value_CemState, unit_CemState = group.get_signal_with_unit("CemState")
            pn.addSignal2Axis(axis01, "CemState", time_CemState, value_CemState, unit=unit_CemState)

        self.sync.addClient(pn)
        return
