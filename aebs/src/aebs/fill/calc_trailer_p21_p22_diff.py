# -*- dataeval: init -*-

from interface import iCalc

sgs = [
    {
        "ABS_Active": ("PGN65315_Tx", "ABS_Active"),
        "RSP_Active": ("PGN65315_Tx", "RSP_Active"),
        "VDC_Active": ("PGN65315_Tx", "VDC_Active"),
        "EMR_Active": ("PGN65315_Tx", "EMR_Active"),
        "PPneuCh0": ("PGN65312_Tx","PPneuCh0"),
        "PPneuCh1": ("PGN65312_Tx","PPneuCh1"),
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
        _, PPneuCh0_data, unit = group.get_signal_with_unit('PPneuCh0', ScaleTime=time)
        _, PPneuCh1_data, unit = group.get_signal_with_unit('PPneuCh1', ScaleTime=time)

        p21_or_p22_diff_events = (ABS_data == 0) & (RSP_data == 0) & (VDC_data == 0) & (EMR_data == 0) & (abs(PPneuCh0_data - PPneuCh1_data)>150)

        return time, p21_or_p22_diff_events


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\trailer_evaluation\Dauerlauf_itebsx_2022_03_23-09-02-27.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_trailer_p21_p22_diff@aebs.fill', manager)
    # print flr25_egomotion.vx
