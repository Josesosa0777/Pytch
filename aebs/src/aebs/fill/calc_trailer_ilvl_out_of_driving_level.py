# -*- dataeval: init -*-

from interface import iCalc

sgs = [
    {
        "vVeh": ("PGN65313_Tx", "vVeh"),
        "RideHeiLevel": ("RGE21_Tx_TICAN","RideHeiLevel"),
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

        _, vVeh_data, unit = group.get_signal_with_unit('vVeh', ScaleTime=time)
        _, RideHeiLevel_data, unit = group.get_signal_with_unit('RideHeiLevel', ScaleTime=time)

        ilvl_out_of_driving_level_event = (vVeh_data > 20) & (RideHeiLevel_data == 0)

        return time, ilvl_out_of_driving_level_event


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\trailer_evaluation\Dauerlauf_itebsx_2022_03_23-09-02-27.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_trailer_ilvl_out_of_driving_level@aebs.fill', manager)
    # print flr25_egomotion.vx
