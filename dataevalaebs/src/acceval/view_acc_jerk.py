# -*- dataeval: init -*-

"""
Plot basic driver activities and AEBS outputs

AEBS-relevant driver activities (pedal activation, steering etc.) and
AEBS outputs (in AEBS1 and XBR messages) are shown.
"""

import numpy as np

import datavis
from interface import iView
from dmw import SignalFilters


class View(iView):

    def check(self):
        sgs = [
            {
                "ACC1_ACCMode": ("CAN_MFC_Public_ACC1_2A", "ACC1_ACCMode_2A"),
                "VehDynSync_Longitudinal_Accel": (
                "MFC5xx Device.VDY.VehDyn", "MFC5xx Device.VDY.VehDyn.Longitudinal.Accel"),
                "XBR_ExtAccelDem": ("CAN_MFC_Public_XBR_0B_2A", "XBR_ExtAccelDem_0B_2A"),

            }
            #{
                #"ACC1_ACCMode_2A_s2A": ("ACC1_2A_CAN20", "ACC1_ACCMode_2A_s2A"),
                #"MFC5xx_Device_VDY_VehDyn_Longitudinal_Accel": (
                #"MFC5xx Device.VDY.VehDyn", "MFC5xx_Device_VDY_VehDyn_Longitudinal_Accel"),
            #},
            #{
                #"ACC1_ACCMode_2A_s2A": ("CAN_MFC_Public_ACC1_2A", "ACC1_ACCMode_2A"),
                #"MFC5xx_Device_VDY_VehDyn_Longitudinal_Accel": (
                #"MFC5xx Device.VDY.VehDyn", "MFC5xx Device.VDY.VehDyn.Longitudinal.Accel"),
            #}
        ]
        common_time_signal=[
            {
                "time": ("VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity"),
            },
            {
                "time": (
                    "ARS4xx Device.AlgoVehCycle.VehDyn",
                    "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity"),
            },
            {
                "time": ("VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity"),
            },
            {
                "time": ("MFC5xx Device.FCU.VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity"),
            },
            {
                "time": ("EBS12_Tx_TICAN", "VehWhlSpeed"),
            },
            {
                "time": ("VehDyn", "MFC5xx_Device_VDY_VehDyn_Longitudinal_Velocity"),
            },
            {
                "time": ("MFC5xx Device.VDY.VehDyn", "MFC5xx_Device_VDY_VehDyn_Longitudinal_Velocity"),
            },
            {
                "time": ("ACC1_2A", "SpeedOfForwardVehicle"),
            },
            {
                "time": ("EBC2", "FrontAxleSpeed_s0B"),
            },
            {
                "time": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
            },
            {
                "time": ("CAN_MFC_Public_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
            },
            ]

        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        group1 = self.source.selectLazySignalGroup(common_time_signal)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)

        for alias in sgs[0]:
            if alias not in group1:
                self.logger.warning("Signal for '%s' not available" % alias)
        return group, group1

    def acc_diff(self,acc_samples, diff_set1):
        diff = np.copy(diff_set1)

        for present_index in range(len(diff)):
            end = present_index + acc_samples
            if (end > (len(diff)-1)):
                diff[present_index:] = diff[present_index-1]
                break
            else:
                diff[present_index] = (diff[end] - diff[present_index])

        return diff

    def view(self, group, group1):

        pn = datavis.cPlotNavigator(title="ACC Controller")
        ax = pn.addAxis(ylabel=" Before filtering")
        if "time" in group1:
            time, value = group1.get_signal("time")

        # Subplot 1
        #if 'MFC5xx_Device_VDY_VehDyn_Longitudinal_Accel' in group:
            #_, VehDyn, unit_vy = group.get_signal_with_unit('MFC5xx_Device_VDY_VehDyn_Longitudinal_Accel', ScaleTime=time)
            # time_diff = np.append(np.diff(time00), np.diff(time00)[-1])
             # VehDyn_diff = np.append(np.diff(value00), np.diff(value00)[-1])
            # VehJerk = np.divide(VehDyn_diff, time_diff)
            #pn.addSignal2Axis(ax, "Veh Accel", time, VehDyn, unit=unit_vy)

        #ax = pn.addAxis(ylabel="")

        # Subplot 1
        if 'ACC1_ACCMode' in group:
            _, acc_mode, unit_vy = group.get_signal_with_unit('ACC1_ACCMode', ScaleTime=time)
        if 'VehDynSync_Longitudinal_Accel' in group:
            _, VehDyn, unit_vy = group.get_signal_with_unit('VehDynSync_Longitudinal_Accel', ScaleTime=time)
        if 'XBR_ExtAccelDem' in group:
            _, xbr, unit_vy = group.get_signal_with_unit('XBR_ExtAccelDem', ScaleTime=time)

        pn.addSignal2Axis(ax, "Before filtering", time, VehDyn, unit=unit_vy)

        ax1 = pn.addAxis(ylabel=" After filtering")
        filtered_VehDyn = SignalFilters.savgol_filter(VehDyn, window_length=53, polyorder=9)
        pn.addSignal2Axis(ax1, "After filtering", time, filtered_VehDyn, unit=unit_vy)

        ax2 = pn.addAxis(ylabel=" Jerk")
        Vehdyn_diff = self.acc_diff(3, filtered_VehDyn)
        time_diff = self.acc_diff(3, time)

        VehJerk = np.divide(Vehdyn_diff, time_diff)
        pn.addSignal2Axis(ax2, "Jerk", time, VehJerk, unit=unit_vy)

        self.sync.addClient(pn)
        return

    def extend_aebs_state_axis(self, pn, ax):
        return