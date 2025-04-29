# -*- dataeval: init -*-
import numpy as np
from interface import iCalc
from numpy.core.fromnumeric import size



def find_consecutive(x, duration):
	"""Find consecutive items in an array."""

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
		duration_mask = (run_lengths > duration)
		#duration_mask = np.append(duration_mask, False)
		indices = np.where(duration_mask == True)
		start_indices = run_starts[indices]
		end_indices = run_starts[indices] + run_lengths[indices]
		stable_track_mask = np.zeros(size(x), dtype = bool)
		for val in indices[0]:
			curr_id = run_values[val]
			if curr_id != 255:
				stable_track_mask[run_starts[val]+1:run_starts[val] + run_lengths[val]] = True
		return stable_track_mask


class cFill(iCalc):
		dep = ('fillFLC25_AOA_ACC')

		
		def check(self):
				modules = self.get_modules()
				time, acc_obj = modules.fill("fillFLC25_AOA_ACC")
				return time, acc_obj[0]

		def fill(self, time, acc_obj):
				id = acc_obj["id"]  
				measuredBy = acc_obj["measured_by"]

				#Find a scene where the selected ID is longer than 5sec.
			
				#MeasuredBy
				#0 None
				#1 Prediction (it was detected before by one sensor of both, but now it is just a prediction)
				#2 Radar only
				#3 Camera only
				#4 fused 
				# 150 * 60ms -> 9 sec.
				findStableMask = find_consecutive(id, 50)

				#To find a change
				#Fused -> Radar only
				#i[x+1] + i[x] = 6	
				foundFusionStaetChangeEvents = (measuredBy[1:]+measuredBy[0:-1]) == 6

				#True= noneFused
				foundNoFusionState = measuredBy < 4
				findStableNoneFused = find_consecutive(foundNoFusionState, 5)

				#Extend array because before we lost one array index
				foundFusionStaetChangeEvents = np.insert(foundFusionStaetChangeEvents,0,0)

				finalMask = findStableMask & foundFusionStaetChangeEvents & findStableNoneFused

				return time, acc_obj, finalMask

if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\corp.knorr-bremse.com\str\Measure\DAS\ConvertedMeas_Xcellis\FER\ACC_F30\FC212993_FU212450\2021-10-26\mi5id787__2021-10-26_17-24-39.h5"
		#First finding: 1635269150.91
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		tracks = manager_modules.calc('calc_flc25_acc_obj_fusion_degradation@aebs.fill', manager)
		print(tracks)