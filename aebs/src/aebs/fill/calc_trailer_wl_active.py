# -*- dataeval: init -*-

from interface import iCalc

sgs = [
    {
        "RedWLReq_PGN65315_Tx": ("PGN65315_Tx", "RedWLReq_PGN65315_Tx"),
        "AmbWLReq_PGN65315_Tx": ("PGN65315_Tx", "AmbWLReq_PGN65315_Tx"),
        "AmbInfReq": ("PGN65315_Tx", "AmbInfReq"),
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

        wl_active_events = (RedWLReq_data == 1) | (AmbWLReq_data == 1) | (AmbInfReq_data == 1)

        return time, wl_active_events


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\trailer_evaluation\Dauerlauf_itebsx_2022_03_23-09-02-27.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_trailer_wl_active@aebs.fill', manager)
    # print flr25_egomotion.vx
