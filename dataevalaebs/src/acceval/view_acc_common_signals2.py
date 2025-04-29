# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView


class View(iView):
    def check(self):
        sgs = [
            {
                "EBC1_ABSActive_0B": ("EBC1_0B_CAN20","EBC1_ABSActive_0B_s0B"),
                "EBC1_ASRBrkCntrlActive_0B": ("EBC1_0B_CAN20","EBC1_ASRBrkCntrlActive_0B_s0B"),
                "EBC1_ASREngCntrlActive_0B": ("EBC1_0B_CAN20","EBC1_ASREngCntrlActive_0B_s0B"),
                "EBC5_BrakeTempWarning_0B": ("EBC5_0B_CAN20", "EBC5_BrakeTempWarning_0B_s0B"),
                "ACC1_ACCSystemShutoffWarning_2A_s2A": ("ACC1_2A_CAN20", "ACC1_ACCSystemShutoffWarning_2A_s2A"),
                "TSC1_EngReqTorqueLimit_00_2A": ("TSC1_00_2A_CAN20", "TSC1_EngReqTorqueLimit_00_2A_d00_s2A"),
            },
            {
                "EBC1_ABSActive_0B": ("CAN_MFC_Public_EBC1_0B", "EBC1_ABSActive_0B"),
                "EBC1_ASRBrkCntrlActive_0B": ("CAN_MFC_Public_EBC1_0B", "EBC1_ASRBrkCntrlActive_0B"),
                "EBC1_ASREngCntrlActive_0B": ("CAN_MFC_Public_EBC1_0B", "EBC1_ASREngCntrlActive_0B"),
                "EBC5_BrakeTempWarning_0B": ("CAN_MFC_Public_EBC5_0B", "EBC5_BrakeTempWarning_0B"),
                "ACC1_ACCSystemShutoffWarning_2A_s2A": ("CAN_MFC_Public_ACC1_2A", "ACC1_ACCSystemShutoffWarning_2A"),
                "TSC1_EngReqTorqueLimit_00_2A": ("CAN_MFC_Public_TSC1_00_2A", "TSC1_EngReqTorqueLimit_00_2A"),

            },
            {
                "EBC1_ABSActive_0B": ("CAN_VEHICLE_EBC1_0B", "EBC1_ABSActive_0B"),
                "EBC1_ASRBrkCntrlActive_0B": ("CAN_VEHICLE_EBC1_0B", "EBC1_ASRBrkCntrlActive_0B"),
                "EBC1_ASREngCntrlActive_0B": ("CAN_VEHICLE_EBC1_0B", "EBC1_ASREngCntrlActive_0B"),
                "EBC5_BrakeTempWarning_0B": ("CAN_VEHICLE_EBC5_0B", "EBC5_BrakeTempWarning_0B"),
                "ACC1_ACCSystemShutoffWarning_2A_s2A": ("CAN_VEHICLE_ACC1_2A", "ACC1_ACCSystemShutoffWarning_2A"),
                "TSC1_EngReqTorqueLimit_00_2A": ("CAN_VEHICLE_TSC1_00_2A", "TSC1_EngReqTorqueLimit_00_2A"),
            },
            {
                "EBC1_ABSActive_0B": ("CAN_MFC_ARS_EBC1_0B", "EBC1_ABSActive_0B"),
                "EBC1_ASRBrkCntrlActive_0B": ("CAN_MFC_ARS_EBC1_0B", "EBC1_ASRBrkCntrlActive_0B"),
                "EBC1_ASREngCntrlActive_0B": ("CAN_MFC_ARS_EBC1_0B", "EBC1_ASREngCntrlActive_0B"),
                "EBC5_BrakeTempWarning_0B": ("CAN_MFC_Public_EBC5_0B", "EBC5_BrakeTempWarning_0B"),
                "ACC1_ACCSystemShutoffWarning_2A_s2A": ("CAN_MFC_Public_ACC1_2A", "ACC1_ACCSystemShutoffWarning_2A"),
                "TSC1_EngReqTorqueLimit_00_2A": ("CAN_MFC_Public_TSC1_00_2A", "TSC1_EngReqTorqueLimit_00_2A"),
            },
            {
                "EBC1_ABSActive_0B": ("EBC1_0B_CAN22", "EBC1_ABSActive_0B_s0B"),
                "EBC1_ASRBrkCntrlActive_0B": ("EBC1_0B_CAN22", "EBC1_ASRBrkCntrlActive_0B_s0B"),
                "EBC1_ASREngCntrlActive_0B": ("EBC1_0B_CAN22", "EBC1_ASREngCntrlActive_0B_s0B"),
                "EBC5_BrakeTempWarning_0B": ("EBC5_0B_CAN22", "EBC5_BrakeTempWarning_0B_s0B"),
                "ACC1_ACCSystemShutoffWarning_2A_s2A": ("ACC1_2A_CAN22", "ACC1_ACCSystemShutoffWarning_2A_s2A"),
                "TSC1_EngReqTorqueLimit_00_2A": ("TSC1_00_2A_CAN22", "TSC1_EngReqTorqueLimit_00_2A_d00_s2A"),
            }

        ]
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
        return group

    def view(self, group):
        pn = datavis.cPlotNavigator(title="ACC Signal Analysis")

        ax = pn.addAxis(ylabel="ABS Active")
        if 'EBC1_ABSActive_0B' in group:
            time00, value00, unit00 = group.get_signal_with_unit("EBC1_ABSActive_0B")
            pn.addSignal2Axis(ax, "EBC1_ABSActive_0B", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="ASRBrkCntrlActive")
        if 'EBC1_ASRBrkCntrlActive_0B' in group:
            time00, value00, unit00 = group.get_signal_with_unit("EBC1_ASRBrkCntrlActive_0B")
            pn.addSignal2Axis(ax, "EBC1_ASRBrkCntrlActive_0B", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="ASREngCntrlActive")
        if 'EBC1_ASREngCntrlActive_0B' in group:
            time00, value00, unit00 = group.get_signal_with_unit("EBC1_ASREngCntrlActive_0B")
            pn.addSignal2Axis(ax, "EBC1_ASREngCntrlActive_0B", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="BrakeTempWarning")
        if 'EBC5_BrakeTempWarning_0B' in group:
            time00, value00, unit00 = group.get_signal_with_unit("EBC5_BrakeTempWarning_0B")
            pn.addSignal2Axis(ax, "EBC5_BrakeTempWarning_0B", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="ACC shutdown")
        if 'ACC1_ACCSystemShutoffWarning_2A_s2A' in group:
            time00, value00, unit00 = group.get_signal_with_unit("ACC1_ACCSystemShutoffWarning_2A_s2A")
            pn.addSignal2Axis(ax, "ACC1_ACCSystemShutoffWarning_2A_s2A", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="Torque Limit")
        if 'TSC1_EngReqTorqueLimit_00_2A' in group:
            time00, value00, unit00 = group.get_signal_with_unit("TSC1_EngReqTorqueLimit_00_2A")
            pn.addSignal2Axis(ax, "TSC1_EngReqTorqueLimit_00_2A", time00, value00, unit=unit00)


        self.sync.addClient(pn)
        return
