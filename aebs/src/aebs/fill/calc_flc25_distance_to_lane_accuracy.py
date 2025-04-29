# -*- dataeval: init -*-

from interface import iCalc
import numpy as np
from measproc.IntervalList import maskToIntervals
from scipy import signal

sgs = [
    {
        "ego_left_clothoidNear_offset": ("LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_offset"),
        "ego_right_clothoidNear_offset": ("LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_offset"),
        "StWheelAngle": ("VehSig", "MFC5xx_Device_FCU_VehSig_VehSigMain_StWheelAngle"),
    },
    {
        "ego_left_clothoidNear_offset": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_offset"),
        "ego_right_clothoidNear_offset": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_offset"),
        "StWheelAngle": ("MFC5xx Device.FCU.VehSig", "MFC5xx_Device_FCU_VehSig_VehSigMain_StWheelAngle"),
    }
]

MAX = 0
MIN = 0
valid_interval = []


class cFill(iCalc):
    dep = ('calc_common_time-flc25',)

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        time = self.modules.fill('calc_common_time-flc25')
        rescale_kwargs = {'ScaleTime': time}
        _, ego_left_index, unit = group.get_signal_with_unit('ego_left_clothoidNear_offset', **rescale_kwargs)
        _, ego_right_index, unit = group.get_signal_with_unit('ego_right_clothoidNear_offset', **rescale_kwargs)
        _, steerwheelangle_index, unit = group.get_signal_with_unit('StWheelAngle', **rescale_kwargs)

        # Check steer wheel angle condition
        steer_wheel_angle = (steerwheelangle_index <= 0.04)
        # Extract valid intervals
        intervals = maskToIntervals(steer_wheel_angle)

        # Create window of 1 second and check for other two conditions
        for time_interval in intervals:
            start_index = time_interval[0]
            end_index = time_interval[1]
            start_time = time[time_interval[0]]
            end_time = time[time_interval[1] - 1]
            interval = start_time + 4
            index = np.amax(np.where(time < interval))

            if end_time - start_time <= 4:
                ego_left_valid_signal = np.split(ego_left_index, [start_index, end_index])[1]
                ego_right_valid_signal = np.split(ego_right_index, [start_index, end_index])[1]

                peak_amplitude = self.peak_to_peak_amplitude(ego_left_valid_signal, ego_right_valid_signal)
                if peak_amplitude >= 0.1:
                    peak_count = self.find_peaks(ego_left_valid_signal, ego_right_valid_signal)
                    if peak_count >= 1:
                        intervals = (start_index, end_index)
                        valid_interval.append(intervals)
            else:
                for i in time[start_index:index]:
                    if interval < end_time:
                        end_index = index

                        ego_left_valid_signal = np.split(ego_left_index, [start_index, end_index])[1]
                        ego_right_valid_signal = np.split(ego_right_index, [start_index, end_index])[1]
                        # peaktopeak function call
                        peak_amplitude = self.peak_to_peak_amplitude(ego_left_valid_signal, ego_right_valid_signal)
                        if peak_amplitude >= 0.1:
                            # count number of peak function call
                            peak_count = self.find_peaks(ego_left_valid_signal, ego_right_valid_signal)
                            if peak_count >= 1:
                                intervals = (start_index, end_index)
                                valid_interval.append(intervals)

                        interval = interval + 4
                        new_index = np.amax(np.where(time < interval))
                        start_index = index + 1
                        index = new_index

        return time, valid_interval

    # Calculate Peak to Peak Amplitude
    def peak_to_peak_amplitude(self, ego_left_valid_signal, ego_right_valid_signal):
        MAX = np.amax(ego_left_valid_signal)
        MIN = np.amin(ego_right_valid_signal)
        peak_amplitude = np.absolute(MAX + MIN)
        return peak_amplitude

    def find_peaks(self, ego_left_valid_signal, ego_right_valid_signal):
        # Find local maxima
        local_maxima = signal.argrelextrema(ego_left_valid_signal, comparator=np.greater)
        # Find local minima
        local_minima = signal.argrelextrema(np.array(ego_right_valid_signal), comparator=np.less)

        return len(local_maxima[0])+len(local_minima[0])


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"\\pu2w6474\shared-drive\measurements\new_meas_09_11_21\mi5id787__2021-10-28_00-03-59.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    data = manager_modules.calc('calc_flc25_distance_to_lane_accuracy@aebs.fill', manager)
    print data
