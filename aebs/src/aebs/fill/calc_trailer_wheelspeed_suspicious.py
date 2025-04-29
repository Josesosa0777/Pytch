# -*- dataeval: init -*-

from interface import iCalc

sgs = [
    {
        "RedWLReq_PGN65315_Tx": ("PGN65315_Tx", "RedWLReq_PGN65315_Tx"),
        "AmbWLReq_PGN65315_Tx": ("PGN65315_Tx", "AmbWLReq_PGN65315_Tx"),
        "AmbInfReq": ("PGN65315_Tx", "AmbInfReq"),
        "ABS_Active": ("PGN65315_Tx", "ABS_Active"),
        "RSP_Active": ("PGN65315_Tx", "RSP_Active"),
        "VDC_Active": ("PGN65315_Tx", "VDC_Active"),
        "EMR_Active": ("PGN65315_Tx", "EMR_Active"),
        "vVeh": ("PGN65313_Tx", "vVeh"),
        "vWhl0": ("PGN65313_Tx", "vWhl0"),
        "vWhl1": ("PGN65313_Tx", "vWhl1"),
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

        _, RedWLReq_data, unit = group.get_signal_with_unit('RedWLReq_PGN65315_Tx', ScaleTime=time)
        _, AmbWLReq_data, unit = group.get_signal_with_unit('AmbWLReq_PGN65315_Tx', ScaleTime=time)
        _, AmbInfReq_data, unit = group.get_signal_with_unit('AmbInfReq', ScaleTime=time)
        _, ABS_data, unit = group.get_signal_with_unit('ABS_Active', ScaleTime=time)
        _, RSP_data, unit = group.get_signal_with_unit('RSP_Active', ScaleTime=time)
        _, VDC_data, unit = group.get_signal_with_unit('VDC_Active', ScaleTime=time)
        _, EMR_data, unit = group.get_signal_with_unit('EMR_Active', ScaleTime=time)
        _, vVeh_data, unit = group.get_signal_with_unit('vVeh', ScaleTime=time)
        _, vWhl0_data, unit = group.get_signal_with_unit('vWhl0', ScaleTime=time)
        _, vWhl1_data, unit = group.get_signal_with_unit('vWhl1', ScaleTime=time)


        wheelspeed_suspicious_events = (RedWLReq_data == 0) & (AmbWLReq_data == 0) & (AmbInfReq_data == 0) & (ABS_data == 0) & \
                                 (RSP_data == 0) & (VDC_data == 0) & (EMR_data == 0) & (vVeh_data > 7) & \
                                 ((vWhl0_data == 0) | (vWhl1_data == 0))

        return time, wheelspeed_suspicious_events


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\trailer_evaluation\Dauerlauf_itebsx_2022_03_23-09-02-27.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_trailer_wheelspeed_suspicious@aebs.fill', manager)
    # print flr25_egomotion.vx
