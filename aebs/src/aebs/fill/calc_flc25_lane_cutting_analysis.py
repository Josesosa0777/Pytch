# -*- dataeval: init -*-
import interface
import logging
from measproc.IntervalList import maskToIntervals
from interface import iCalc

logger = logging.getLogger('calc_flc25_sample_point')


class Calc(iCalc):
    dep = ('calc_common_time-flr25',)

    def check(self):
        sgs = [
            {
                "FLI2_StateOfLDWS": ("CAN_MFC_Public_FLI2_E8", "FLI2_LDWSState_E8"),
                "LaneDepartureLeft": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_left"),
                "LaneDepartureRight": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_right"),

            },
            {
                "FLI2_StateOfLDWS": ("FLI2_E8", "FLI2_StateOfLDWS"),
                "LaneDepartureLeft": (
                "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_left"),
                "LaneDepartureRight": (
                "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_right"),
            },
            {
                "FLI2_StateOfLDWS": ("FLI2_E8", "FLI2_LDWSState_E8_sE8"),
                "LaneDepartureLeft": (
                "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_left"),
                "LaneDepartureRight": (
                "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_right"),
            },
        ]
        source = self.get_source()
        try:
            group = source.selectSignalGroup(sgs)
            return group
        except Exception as e:
            logger.error(str(e))

    def fill(self, group):

        time = self.modules.fill('calc_common_time-flr25')

        # load signals
        ldws_state_time, ldws_state_values, unit = group.get_signal_with_unit("FLI2_StateOfLDWS" ,ScaleTime=time)
        LaneDepartureLeft_time, LaneDepartureLeft_values, LaneDepartureLeft_unit = group.get_signal_with_unit("LaneDepartureLeft",ScaleTime=time)
        LaneDepartureRight_time, LaneDepartureRight_values, LaneDepartureRight_unit = group.get_signal_with_unit(
            "LaneDepartureRight", ScaleTime=time)

        left_departure_warning = (ldws_state_values == 5) & (LaneDepartureLeft_values==1)

        state_change_intervals = maskToIntervals(left_departure_warning)

        for interval in state_change_intervals:
            if ldws_state_values[interval[0] - 1] == 3:
                left_departure_warning[interval[0]:interval[1]] = True

        right_departure_warning = (ldws_state_values == 5) & (LaneDepartureRight_values == 1)

        state_change_intervals = maskToIntervals(right_departure_warning)

        for interval in state_change_intervals:
            if ldws_state_values[interval[0] - 1] == 3:
                right_departure_warning[interval[0]:interval[1]] = True

        return time, left_departure_warning, right_departure_warning


if __name__ == "__main__":
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Python_Toolchain_2\Evaluation_data\LDWS\axiscamera_ldkpi\2023-06-22\mi5id5506__2023-06-22_09-03-28.h5"
    config, manager, manager_modules = init_dataeval(["-m", meas_path])
    sample_point = manager_modules.calc("calc_flc25_lane_cutting_analysis@aebs.fill", manager)
    print(sample_point)
