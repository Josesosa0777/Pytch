# -*- dataeval: init -*-

from interface import iCalc

sgs = [
    {
        "RSPTestActive": ("Lausch_19", "RSPTestActive"),
        "RSPStep1Active": ("Lausch_19", "RSPStep1Active"),
        "RSPStep2Active": ("Lausch_19", "RSPStep2Active"),
        "NearlyRSP": ("Lausch_19", "NearlyRSP"),
        "VrefFilter": ("Lausch_2", "VrefFilter"),
        "RSPStep1Enabled": ("Lausch_19", "RSPStep1Enabled"),
        "RSPStep2Enabled": ("Lausch_19", "RSPStep2Enabled"),

        "AyFilt": ("Lausch_17", "AyFilt"),
        "AyCalc": ("Lausch_43", "AyCalc"),
        "AyLimLeft": ("Lausch_17", "AyLimLeft"),
        "AyLimRight": ("Lausch_17", "AyLimRight"),

        "AyOffset": ("Lausch_43", "AyOffset"),

        "RSPTestedLifted": ("Lausch_19","RSPTestedLifted"),
        "RSPLowMuSide": ("Lausch_19","RSPLowMuSide"),
        "RSPVDCActive": ("Lausch_19","RSPVDCActive"),
        "RSPPlauError": ("Lausch_19","RSPPlauError"),

        "RSPtUnstabA": ("Lausch_18","RSPtUnstabA"),
        "RSPtUnstabB": ("Lausch_18","RSPtUnstabB"),
        "RSPtUnstabC": ("Lausch_18","RSPtUnstabC"),
        "RSPtUnstabD": ("Lausch_18","RSPtUnstabD"),
        "RSPtUnstabE": ("Lausch_18","RSPtUnstabE"),
        "RSPtUnstabF": ("Lausch_18","RSPtUnstabF"),
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
        NearlyRSP_time, NearlyRSP_value, NearlyRSP_unit = group.get_signal_with_unit('NearlyRSP', ScaleTime=time)

        _, AyOffset_values, AyOffset_unit = group.get_signal_with_unit('AyOffset', ScaleTime=time)

        # VrefFilter > 2100 AND(RSPStep1Enable=0 OR RSPStep2 = 0)

        VrefFilter_time, VrefFilter_value, VrefFilter_unit = group.get_signal_with_unit('VrefFilter', ScaleTime=time)
        RSPStep1Enabled_time, RSPStep1Enabled_value, RSPStep1Enabled_unit = group.get_signal_with_unit(
            'RSPStep1Enabled', ScaleTime=time)
        RSPStep2Enabled_time, RSPStep2Enabled_value, RSPStep2Enabled_unit = group.get_signal_with_unit(
            'RSPStep2Enabled', ScaleTime=time)

        VrefFilter_masked_array = (VrefFilter_value > 2100) & (
                    (RSPStep1Enabled_value == 0) | (RSPStep2Enabled_value == 0))

        AyFilt_time, AyFilt_value, AyFilt_unit = group.get_signal_with_unit('AyFilt', ScaleTime=time)
        AyCalc_time, AyCalc_value, AyCalc_unit = group.get_signal_with_unit('AyCalc', ScaleTime=time)
        AyLimLeft_time, AyLimLeft_value, AyLimLeft_unit = group.get_signal_with_unit('AyLimLeft', ScaleTime=time)
        AyLimRight_time, AyLimRight_value, AyLimRight_unit = group.get_signal_with_unit('AyLimRight', ScaleTime=time)

        AyFilt_masked_event_array = (abs(AyFilt_value) > 2500)

        AyCalc_masked_event_array = (abs(AyCalc_value) > 2000)

        max_values = []

        AyFilt_max_value = max(AyFilt_value)
        max_values.append(AyFilt_max_value)

        AyCalc_max_value = max(AyCalc_value)
        max_values.append(AyCalc_max_value)

        AyLimLeft_max_value = max(AyLimLeft_value)
        max_values.append(AyLimLeft_max_value)

        AyLimRight_max_value = max(AyLimRight_value)
        max_values.append(AyLimRight_max_value)

        AyLimLeft_masked_array = (AyLimLeft_value[:-1] != AyLimLeft_value[1:])

        AyLimRight_masked_array = (AyLimRight_value[:-1] != AyLimRight_value[1:])

        RSPTestedLifted_time, RSPTestedLifted_values, RSPTestedLifted_unit = group.get_signal_with_unit('RSPTestedLifted', ScaleTime=time)
        RSPLowMuSide_time, RSPLowMuSide_values, RSPLowMuSide_unit = group.get_signal_with_unit('RSPLowMuSide', ScaleTime=time)
        RSPVDCActive_Time, RSPVDCActive_values, RSPVDCActive_unit = group.get_signal_with_unit('RSPVDCActive', ScaleTime=time)
        RSPPlauError_Time, RSPPlauError_values, RSPPlauError_unit = group.get_signal_with_unit('RSPPlauError', ScaleTime=time)

        RSPtUnstabA_time, RSPtUnstabA_values, RSPtUnstabA_unit = group.get_signal_with_unit('RSPtUnstabA', ScaleTime=time)
        RSPtUnstabB_time, RSPtUnstabB_values, RSPtUnstabB_unit = group.get_signal_with_unit('RSPtUnstabB', ScaleTime=time)
        RSPtUnstabC_time, RSPtUnstabC_values, RSPtUnstabC_unit = group.get_signal_with_unit('RSPtUnstabC', ScaleTime=time)
        RSPtUnstabD_time, RSPtUnstabD_values, RSPtUnstabD_unit = group.get_signal_with_unit('RSPtUnstabD', ScaleTime=time)
        RSPtUnstabE_time, RSPtUnstabE_values, RSPtUnstabE_unit = group.get_signal_with_unit('RSPtUnstabE', ScaleTime=time)
        RSPtUnstabF_time, RSPtUnstabF_values, RSPtUnstabF_unit = group.get_signal_with_unit('RSPtUnstabF', ScaleTime=time)

        RSPTestActive_masked_array = (RSPTestActive_value == 1)
        RSPStep1Active_masked_array = (RSPStep1Active_value == 1)
        RSPStep2Active_masked_array = (RSPStep2Active_value == 1)
        NearlyRSP_masked_array = (NearlyRSP_value == 1)

        # delta(AyOffset) <>0 constant value is -3
        # delta = when value is changed
        AyOffset_masked_array = (AyOffset_values[:-1] != AyOffset_values[1:])

        RSPTestedLifted_masked_array = RSPTestedLifted_values == 1
        RSPLowMuSide_masked_array = RSPLowMuSide_values > 0
        RSPVDCActive_masked_array = RSPVDCActive_values == 1
        RSPPlauError_masked_array = RSPPlauError_values > 0

        # RSPtUnstabA_masked_array = RSPtUnstabA_values >= 0
        # RSPtUnstabB_masked_array = RSPtUnstabB_values >= 0
        # RSPtUnstabC_masked_array = RSPtUnstabC_values >= 0
        # RSPtUnstabD_masked_array = RSPtUnstabD_values >= 0
        # RSPtUnstabE_masked_array = RSPtUnstabE_values >= 0
        # RSPtUnstabF_masked_array = RSPtUnstabF_values >= 0

        RSPtUnstabA_masked_array = (RSPtUnstabA_values >= 0)
        RSPtUnstabB_masked_array = (RSPtUnstabB_values >= 0)
        RSPtUnstabC_masked_array = (RSPtUnstabC_values >= 0 )
        RSPtUnstabD_masked_array = (RSPtUnstabD_values >= 0 )
        RSPtUnstabE_masked_array = (RSPtUnstabE_values >= 0 )
        RSPtUnstabF_masked_array = (RSPtUnstabF_values >= 0)

        return time, RSPTestActive_masked_array,RSPStep1Active_masked_array,RSPStep2Active_masked_array,NearlyRSP_masked_array ,VrefFilter_masked_array,AyFilt_masked_event_array,AyCalc_masked_event_array,AyLimLeft_masked_array,AyLimRight_masked_array,\
               AyOffset_masked_array,RSPTestedLifted_masked_array,RSPLowMuSide_masked_array,RSPVDCActive_masked_array,\
               RSPPlauError_masked_array,RSPtUnstabA_masked_array,RSPtUnstabB_masked_array,RSPtUnstabC_masked_array,RSPtUnstabD_masked_array,RSPtUnstabE_masked_array,RSPtUnstabF_masked_array,max_values


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\pytch2\TrailerTasks\RSP_Evaluation_Report_Signal_Plot\new\RSP_log_L4911.mat"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_trailer_rsp_active@aebs.fill', manager)
