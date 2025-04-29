# -*- dataeval: init -*-

from interface import iCalc

sgs = [
    {
        "ACC1_ACCMode_2A_s2A": ("ACC1_2A_CAN20","ACC1_ACCMode_2A_s2A"),
        "XBR_ExtAccelDem_0B_2A_d0B_s2A": ("XBR_0B_2A_CAN20","XBR_ExtAccelDem_0B_2A_d0B_s2A"),
    },
    {
        "ACC1_ACCMode_2A_s2A": ("CAN_MFC_Public_ACC1_2A","ACC1_ACCMode_2A"),
        "XBR_ExtAccelDem_0B_2A_d0B_s2A": ("CAN_MFC_Public_XBR_0B_2A","XBR_ExtAccelDem_0B_2A"),
    },
    {
        "ACC1_ACCMode_2A_s2A": ("CAN_VEHICLE_ACC1_2A","ACC1_ACCMode_2A"),
        "XBR_ExtAccelDem_0B_2A_d0B_s2A": ("CAN_VEHICLE_XBR_0B_2A","XBR_ExtAccelDem_0B_2A"),
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
        # rescale_kwargs = {'ScaleTime': time, 'Order': 'valid'}
        # vx
        _, xbr_ext_data, unit_vy = group.get_signal_with_unit('XBR_ExtAccelDem_0B_2A_d0B_s2A', ScaleTime=time)

        valid_xbr_data = (xbr_ext_data < -3.5)

        return time, valid_xbr_data, xbr_ext_data

if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"\\corp.knorr-bremse.com\str\Measure\DAS\ConvertedMeas_Xcellis\FER\AEBS\F30\FMAX_5506\FC232295_FU232260\2023-08-21\mi5id5506__2023-08-21_18-18-08.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_acc_braking@aebs.fill', manager)
