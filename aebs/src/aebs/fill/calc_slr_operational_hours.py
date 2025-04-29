# -*- dataeval: init -*-

from interface import iCalc

sgs = [
    {
        "FrontAxleSpeed": ("CAN_MFC_Public_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
    }

]


class cFill(iCalc):
    dep = ('calc_common_time-flr25')

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        bsis = 0
        mois = 0
        vdp = 0
        lcda = 0
        fna = 0

        block = 0

        # time = self.modules.fill('calc_common_time-flr25')

        FrontAxleSpeed_time, speed, FrontAxleSpeed_unit = group.get_signal_with_unit('FrontAxleSpeed')

        time = FrontAxleSpeed_time - FrontAxleSpeed_time[1]
        n = len(FrontAxleSpeed_time)
        m = len(speed)
        dim = min(n, m)

        for i in range(dim - 1):
            dt = time[i + 1] - time[i]

            if speed[i] <= 10:
                vdp = vdp + dt
                mois = mois + dt
                bsis = bsis + dt
                block = 1
            elif (speed[i] <= 15) and (speed[i] > 10) and (block == 0):
                mois = mois + dt
                bsis = bsis + dt
                block = 1
            elif (speed[i] <= 33) and (speed[i] > 15) and (block == 0):
                bsis = bsis + dt
                block = 1
            elif (speed[i] < 43) and (speed[i] > 33) and (block == 0):
                fna = fna + dt
                block = 1
            elif (speed[i] >= 43) and (block == 0):
                lcda = lcda + dt

            block = 0

        BSIS_hours = bsis / 60
        MOIS_hours = mois / 60
        VDP_hours = vdp / 60
        LCDA_hours = lcda / 60
        FNA_hours = fna / 60

        # print(['BSIS: ', bsis / 60, ' min'])
        # print(['MOIS: ', mois / 60, ' min'])
        # print(['VDP : ', vdp / 60, ' min'])
        # print(['LCDA: ', lcda / 60, ' min'])
        # print(['FNA : ', fna / 60, ' min'])

        return BSIS_hours, MOIS_hours, VDP_hours, LCDA_hours, FNA_hours


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\pytch2_development\SRR_eval\testing\2024-08-28\mi5id5506__2024-08-28_14-51-16.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_slr_operational_hours@aebs.fill', manager)
