# -*- dataeval: init -*-

from interface import iCalc

sgs = [
    {
        "ABS_Active": ("PGN65315_Tx", "ABS_Active"),
        "RSP_Active": ("PGN65315_Tx", "RSP_Active"),
        "VDC_Active": ("PGN65315_Tx", "VDC_Active"),
        "EMR_Active": ("PGN65315_Tx", "EMR_Active"),
        "RSP_TestPulse": ("PGN65314_Tx", "RSP_TestPulse"),
        "RSP_Step_1": ("PGN65314_Tx", "RSP_Step_1"),
        "RSP_Step_2": ("PGN65314_Tx", "RSP_Step_2"),
        "RSP_Step_3": ("PGN65314_Tx", "RSP_Step_3"),
        "ABSAct": ("PGN65316_Tx", "ABSAct"),
        "RSPAct": ("PGN65316_Tx", "RSPAct"),
    }
]


class cFill(iCalc):
    dep = ('calc_common_time-flr25',)

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        time = self.modules.fill('calc_common_time-flr25')

        _, ABS_data, unit = group.get_signal_with_unit('ABS_Active', ScaleTime=time)
        _, RSP_data, unit = group.get_signal_with_unit('RSP_Active', ScaleTime=time)
        _, VDC_data, unit = group.get_signal_with_unit('VDC_Active', ScaleTime=time)
        _, EMR_data, unit = group.get_signal_with_unit('EMR_Active', ScaleTime=time)
        _, RSP_TestPulse_data, unit = group.get_signal_with_unit('RSP_TestPulse', ScaleTime=time)
        _, RSP_Step_1_data, unit = group.get_signal_with_unit('RSP_Step_1', ScaleTime=time)
        _, RSP_Step_2_data, unit = group.get_signal_with_unit('RSP_Step_2', ScaleTime=time)
        _, RSP_Step_3_data, unit = group.get_signal_with_unit('RSP_Step_3', ScaleTime=time)
        _, ABSAct_data, unit = group.get_signal_with_unit('ABSAct', ScaleTime=time)
        _, RSPAct_data, unit = group.get_signal_with_unit('RSPAct', ScaleTime=time)

        abs_and_rsp_active_events = (ABS_data == 1) | (RSP_data == 1) | (VDC_data == 1) | (EMR_data == 1) | (RSP_TestPulse_data == 1) | (RSP_Step_1_data == 1) \
                           | (RSP_Step_2_data == 1) | (RSP_Step_3_data != 3) | (ABSAct_data == 1) | (RSPAct_data == 1)

        return time, abs_and_rsp_active_events


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\trailer_evaluation\Dauerlauf_itebsx_2022_03_23-09-02-27.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_trailer_abs_and_rsp_active@aebs.fill', manager)
    # print flr25_egomotion.vx
