# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView


class View(iView):
    def check(self):
        sgs = [
            {
                "ACCMode": ("ACC1_2A_CAN20", "ACC1_ACCMode_2A_s2A"),
                "XBR_ExtAccelDem": ("XBR_0B_2A_CAN20", "XBR_ExtAccelDem_0B_2A_d0B_s2A"),
                "Longitudinal_Accel": ("MFC5xx Device.VDY.VehDyn", "MFC5xx_Device_VDY_VehDyn_Longitudinal_Accel"),
                "sensor_acc_object_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_acc_object_id"),
                "sensor_acc_object_dx": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_acc_object_dx"),

            },
            {
                "ACCMode": ("CAN_MFC_Public_ACC1_2A", "ACC1_ACCMode_2A"),
                "XBR_ExtAccelDem": ("CAN_MFC_Public_XBR_0B_2A", "XBR_ExtAccelDem_0B_2A"),
                "Longitudinal_Accel": ("MFC5xx Device.VDY.VehDyn", "MFC5xx Device.VDY.VehDyn.Longitudinal.Accel"),
                "sensor_acc_object_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_AoaOutput.im_input_sensor.acc_object.id"),
                "sensor_acc_object_dx": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_AoaOutput.im_input_sensor.acc_object.dx"),

            },
            {
                "ACCMode": ("CAN_VEHICLE_ACC1_2A", "ACC1_ACCMode_2A"),
                "XBR_ExtAccelDem": ("CAN_VEHICLE_XBR_0B_2A", "XBR_ExtAccelDem_0B_2A"),
                "Longitudinal_Accel": ("MFC5xx Device.VDY.VehDyn", "MFC5xx Device.VDY.VehDyn.Longitudinal.Accel"),
                "sensor_acc_object_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_AoaOutput.im_input_sensor.acc_object.id"),
                "sensor_acc_object_dx": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_AoaOutput.im_input_sensor.acc_object.dx"),

            },
            {
                "ACCMode": ("ACC1_2A_CAN22", "ACC1_ACCMode_2A_s2A"),
                "XBR_ExtAccelDem": ("XBR_0B_2A_CAN22", "XBR_ExtAccelDem_0B_2A_d0B_s2A"),
                "Longitudinal_Accel": ("MFC5xx Device.VDY.VehDyn", "MFC5xx_Device_VDY_VehDyn_Longitudinal_Accel"),
                "sensor_acc_object_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_acc_object_id"),
                "sensor_acc_object_dx": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_acc_object_dx"),
            },
            {
                "ACCMode": ("CAN_MFC_Public_ACC1_2A", "ACC1_ACCMode_2A"),
                "XBR_ExtAccelDem": ("CAN_MFC_Public_XBR_0B_2A", "XBR_ExtAccelDem_0B_2A"),
                "Longitudinal_Accel": (
                    "MFC5xx Device.VDY.VehDyn", "MFC5xx_Device_VDY_VehDyn_Longitudinal_Accel"),
                "sensor_acc_object_id": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AccInput_sensor_input_acc_object_obj_id"),
                "sensor_acc_object_dx": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AccInput_sensor_input_acc_object_obj_lon_dist"),

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

        ax = pn.addAxis(ylabel="ACC mode")
        if 'ACCMode' in group:
            time00, value00, unit00 = group.get_signal_with_unit("ACCMode")
            pn.addSignal2Axis(ax, "ACCMode", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="XBR")
        if 'XBR_ExtAccelDem' in group:
            time00, value00, unit00 = group.get_signal_with_unit("XBR_ExtAccelDem")
            pn.addSignal2Axis(ax, "XBR_ExtAccelDem", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="Longitudinal Accel")
        if 'Longitudinal_Accel' in group:
            time00, value00, unit00 = group.get_signal_with_unit("Longitudinal_Accel")
            pn.addSignal2Axis(ax, "Longitudinal_Accel", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="Obj ID")
        if 'sensor_acc_object_id' in group:
            time00, value00, unit00 = group.get_signal_with_unit("sensor_acc_object_id")
            pn.addSignal2Axis(ax, "sensor_acc_object_id", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="Obj dx")
        if 'sensor_acc_object_dx' in group:
            time00, value00, unit00 = group.get_signal_with_unit("sensor_acc_object_dx")
            pn.addSignal2Axis(ax, "sensor_acc_object_dx", time00, value00, unit=unit00)

        self.sync.addClient(pn)
        return
