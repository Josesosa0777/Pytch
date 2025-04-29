# -*- dataeval: init -*-
import interface
import logging
from measproc.IntervalList import cIntervalList, maskToIntervals
from interface import iCalc



logger = logging.getLogger('calc_flc25_sample_point')


class Calc(iCalc):
    def check(self):
        sgs = [
            {
                "FLI2_StateOfLDWS": ("FLI2_E8", "FLI2_StateOfLDWS"),
            },
            {
                "FLI2_StateOfLDWS": ("FLI2_E8", "FLI2_LDWSState_E8_sE8"),
            },
        ]
        source = self.get_source()
        try:
            group = source.selectSignalGroup(sgs)
            return group
        except Exception as e:
            logger.error(str(e))

    def fill(self, group):
        # load signals
        time, ldws_state_values = group.get_signal("FLI2_StateOfLDWS")

        lane_available_masked_array = (ldws_state_values != 0) & (ldws_state_values != 15) & (ldws_state_values != 14)
        lane_available_intervals = maskToIntervals(lane_available_masked_array)[0]
        if lane_available_intervals:
            eventTime = time[lane_available_intervals[0]]
            sample_point = "lane_available@" + str(eventTime)
            return sample_point
        else:
            return None



if __name__ == "__main__":
    from config.Config import init_dataeval

    meas_path = r"C:\Users\ext-gorea\Downloads\HMC-QZ-STR__2021-03-02_13-47-55.h5"
    config, manager, manager_modules = init_dataeval(["-m", meas_path])
    sample_point = manager_modules.calc("calc_flc25_sample_point@aebs.fill", manager)
    print(sample_point)
