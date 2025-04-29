# -*- dataeval: init -*-

from interface import iCalc

sgs = [
    {
        "RSPTestActive": ("Lausch_19","RSPTestActive"),
        "RSPStep1Active": ("Lausch_19","RSPStep1Active"),
        "RSPStep2Active": ("Lausch_19","RSPStep2Active"),
        "RSPTestedLifted": ("Lausch_19","RSPTestedLifted"),
        "RSPVDCActive": ("Lausch_19","RSPVDCActive")
    }
]


class cFill(iCalc):
    dep = ('calc_common_time-trailer_eval',)

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        time = self.modules.fill('calc_common_time-trailer_eval')

        RSPTestActive_time, RSPTestActive_value, RSPTestActive_unit = group.get_signal_with_unit('RSPTestActive', ScaleTime=time)
        RSPStep1Active_time, RSPStep1Active_value, RSPStep1Active_unit = group.get_signal_with_unit('RSPStep1Active', ScaleTime=time)
        RSPStep2Active_time, RSPStep2Active_value, RSPStep2Active_unit = group.get_signal_with_unit('RSPStep2Active', ScaleTime=time)
        RSPTestedLifted_time, RSPTestedLifted_value, RSPTestedLifted_unit = group.get_signal_with_unit('RSPTestedLifted', ScaleTime=time)
        RSPVDCActive_time, RSPVDCActive_value, RSPVDCActive_unit = group.get_signal_with_unit('RSPVDCActive', ScaleTime=time)

        RSPTestActive_masked_array = (RSPTestActive_value == 1)
        RSPStep1Active_masked_array = (RSPStep1Active_value == 1)
        RSPStep2Active_masked_array = (RSPStep2Active_value == 1)
        RSPTestedLifted_masked_array = (RSPTestedLifted_value == 1)
        RSPVDCActive_masked_array = (RSPVDCActive_value == 1)


        return time, RSPTestActive_masked_array, RSPStep1Active_masked_array, RSPStep2Active_masked_array,\
               RSPTestedLifted_masked_array,RSPVDCActive_masked_array


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\pytch2\TrailerTasks\RSP_Evaluation_Report_Signal_Plot\new\RSP_log_L4911.mat"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_trailer_rsp_active@aebs.fill', manager)
