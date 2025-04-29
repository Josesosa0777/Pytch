# -*- dataeval: init -*-
import numpy as np
from interface import iCalc
from numpy.core.fromnumeric import size

INVALID_ID = 255
STABLE_TRACK_DURATION = 150
TRACK_CHANGE_DURATION = 1

def find_runs(x):
    """Find runs of consecutive items in an array."""

    x = np.asanyarray(x)
    if x.ndim != 1:
        raise ValueError('only 1D array supported')
    n = x.shape[0]

    if n == 0:
        return np.array([]), np.array([]), np.array([])

    else:
        loc_run_start = np.empty(n, dtype=bool)
        loc_run_start[0] = True
        np.not_equal(x[:-1], x[1:], out=loc_run_start[1:])
        run_starts = np.nonzero(loc_run_start)[0]

        run_values = x[loc_run_start]

        run_lengths = np.diff(np.append(run_starts, n))
        
        duration_mask = (run_lengths[0:-1] > STABLE_TRACK_DURATION) & (run_lengths[1:] > TRACK_CHANGE_DURATION)
        duration_mask = np.append(duration_mask, False)
        value_mask_curr = ~np.ma.getmask(run_values[0:-2])
        id_invalid_mask = run_values[0:-2] != INVALID_ID
        next_id_invalid_mask = run_values[1:-1] != INVALID_ID
        changes_back = (run_values[0:-2] == run_values[2:])
        pattern_mask = changes_back & value_mask_curr & id_invalid_mask & next_id_invalid_mask
        pattern_mask = np.append(pattern_mask, False)
        pattern_mask = np.append(pattern_mask, False)
        indices_mask = duration_mask & pattern_mask
        indices = np.where(indices_mask == True)
        length = run_lengths[indices]

        return run_starts[indices] + run_lengths[indices]

class cFill(iCalc):
        dep = ('fill_flc25_aoa_acc_tracks',)

        def check(self):
                modules = self.get_modules()
                acc_obj_data = modules.fill("fill_flc25_aoa_acc_tracks")
                assert acc_obj_data, 'ACC AOA struct should not be empty'
                return acc_obj_data[0]

        def fill(self, acc_obj_data):
                timestamps = acc_obj_data.time
                id = acc_obj_data.object_id
                event_indices = find_runs(id)

                valid_interval_mask = np.zeros(size(id), dtype = bool)
                valid_interval_mask[event_indices] = True
                return timestamps, valid_interval_mask, id

        

if __name__ == '__main__':
        from config.Config import init_dataeval

        meas_path = r"\\corp.knorr-bremse.com\str\Measure\DAS\ConvertedMeas_Xcellis\FER\ACC_AEBS\F30\B365_5288\FC220365_FU213440\2022-02-08\mi5id5288__2022-02-08_08-54-15.h5"
        config, manager, manager_modules = init_dataeval(['-m', meas_path])
        tracks = manager_modules.calc('calc_flc25_acc_obj_unstable_tracking@aebs.fill', manager)
        print(tracks)