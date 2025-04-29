# -*- dataeval: init -*-
"""
:Name:
	view_paebs_kpi_for_gt_raw_with_flc25_paebs_aoaoutput.py
:Type:
	View Script
:Visualization Type:
	Plot and Table Visualization
:Full Path:
	dataevalaebs/src/dataevalaebs/view_paebs_kpi_for_gt_raw_with_flc25_paebs_aoaoutput.py
:Sensors:
	FLC25(AOA), ADMA(CAN)
:Short Description:
		`More Information about ADMA, AOA, Usage and Output <../html/dataevalaebs.html#module-dataevalaebs.view_paebs_kpi_for_gt_raw_with_flc25_cem_tpf_tracks>`__
:Dependencies:
		- fill_flc25_paebs_aoaoutput_tracks@aebs.fill
		- fill_ground_truth_raw_tracks@aebs.fill

.. note::
	For source code click on [source] tag beside functions
"""
import numpy as np

from interface import iParameter, iView
import datavis

# instantiation of module parameters
init_params = dict(('TRACK_%02d' % i, dict(id = i)) for i in xrange(0, 3))


class cMyView(iView):
		dep = 'fill_flc25_paebs_aoaoutput_tracks@aebs.fill', 'fill_ground_truth_raw_tracks@aebs.fill'

		def init(self, id):
				self.id = id
				return

		def check(self):
				modules = self.get_modules()
				flc25_tracks = modules.fill("fill_flc25_paebs_aoaoutput_tracks@aebs.fill")
				gt_track = modules.fill("fill_ground_truth_raw_tracks@aebs.fill")
				flc25_tracks = flc25_tracks.rescale(gt_track["time"])
				assert self.id in flc25_tracks, 'Track %d is not recorded' % self.id

				flc25_tracks = flc25_tracks[self.id]
				gt_track["dx"] = np.ma.masked_array(gt_track['dx'], mask = flc25_tracks.dx.mask)
				return flc25_tracks, gt_track

		def view(self, flc25_tracks, gt_track):
				t = flc25_tracks.time
				plot_nav = datavis.cPlotNavigator(title = 'Compare GT and FLC25 track #%d' % self.id)
				dx_axis = plot_nav.addAxis(ylabel = 'dx')
				dy_axis = plot_nav.addAxis(ylabel = 'dy')
				vx_abs_axis = plot_nav.addAxis(ylabel = 'vx_abs')
				vy_abs_axis = plot_nav.addAxis(ylabel = 'vy_abs')

				list_nav = datavis.cListNavigator(
								title = "Comparison between GT with FLC25 track #%d" % self.id)
				self.sync.addClient(list_nav)

				diff_flc25_gt_dx = np.absolute(flc25_tracks.dx - gt_track['dx'])
				diff_flc25_gt_dy = np.absolute(flc25_tracks.dy - gt_track['dy'])
				interval_of_interest = np.argwhere((diff_flc25_gt_dx < 3) & (diff_flc25_gt_dy < 3) & (gt_track['dx'] > 0.0))

				# There is not any gt object tracking flc25 obj in the track
				if interval_of_interest.size == 0:
						invalid_track = np.repeat("NA", len(t))
						list_nav.addsignal("Could not find FLC25 object following ground truth object".format(self.id),
															 (t, invalid_track),
															 groupname = "Default")
						return

				flc25_dx = flc25_tracks.dx[interval_of_interest].squeeze()
				gt_dx = gt_track['dx'][interval_of_interest].squeeze()
				flc25_dx_std_p = flc25_tracks.dx[interval_of_interest].squeeze() + flc25_tracks.dx_std[
						interval_of_interest].squeeze()
				flc25_dx_std_n = flc25_tracks.dx[interval_of_interest].squeeze() - flc25_tracks.dx_std[
						interval_of_interest].squeeze()

				flc25_dy = flc25_tracks.dy[interval_of_interest].squeeze()
				gt_dy = gt_track['dy'][interval_of_interest].squeeze()
				flc25_dy_std_p = flc25_tracks.dy[interval_of_interest].squeeze() + flc25_tracks.dy_std[
						interval_of_interest].squeeze()
				flc25_dy_std_n = flc25_tracks.dy[interval_of_interest].squeeze() - flc25_tracks.dy_std[
						interval_of_interest].squeeze()

				flc25_vx_abs = flc25_tracks.vx_abs[interval_of_interest].squeeze()
				gt_vx = gt_track['vx_abs'][interval_of_interest].squeeze()

				flc25_vx_abs_std_p = flc25_tracks.vx_abs[interval_of_interest].squeeze() + flc25_tracks.vx_abs_std[
						interval_of_interest].squeeze()
				flc25_vx_abs_std_n = flc25_tracks.vx_abs[interval_of_interest].squeeze() - flc25_tracks.vx_abs_std[
						interval_of_interest].squeeze()

				flc25_vy_abs = flc25_tracks.vy_abs[interval_of_interest].squeeze()
				gt_vy = gt_track['vy_abs'][interval_of_interest].squeeze()

				flc25_vy_abs_std_p = flc25_tracks.vy_abs[interval_of_interest].squeeze() + flc25_tracks.vy_abs_std[
						interval_of_interest].squeeze()
				flc25_vy_abs_std_n = flc25_tracks.vy_abs[interval_of_interest].squeeze() - flc25_tracks.vy_abs_std[
						interval_of_interest].squeeze()

				t_int = t[interval_of_interest].squeeze()
				t = t_int

				plot_nav.addSignal2Axis(dx_axis, 'dx', t_int, flc25_dx,
																unit = 'm')
				plot_nav.addSignal2Axis(dx_axis, 'gt_dx', t_int, gt_dx,
																unit = 'm')
				plot_nav.addSignal2Axis(dx_axis, 'dx+std', t, flc25_dx_std_p, unit = 'm', ls = "--", color = "green")
				plot_nav.addSignal2Axis(dx_axis, 'dx-std', t, flc25_dx_std_n, unit = 'm', ls = "--", color = "green")
				dx_axis.fill_between(t, flc25_dx_std_p, flc25_dx_std_n, color = "green", alpha = "0.3")

				plot_nav.addSignal2Axis(dy_axis, 'dy', t_int, flc25_dy,
																unit = 'm')
				plot_nav.addSignal2Axis(dy_axis, 'gt_dy', t_int, gt_dy,
																unit = 'm')
				plot_nav.addSignal2Axis(dy_axis, 'dy+std', t, flc25_dy_std_p, unit = 'm', ls = "--", color = "green")
				plot_nav.addSignal2Axis(dy_axis, 'dy-std', t, flc25_dy_std_n, unit = 'm', ls = "--", color = "green")
				dy_axis.fill_between(t, flc25_dy_std_p, flc25_dy_std_n, color = "green", alpha = "0.3")

				plot_nav.addSignal2Axis(vx_abs_axis, 'vx_abs', t_int, flc25_vx_abs,
																unit = 'm/s')
				plot_nav.addSignal2Axis(vx_abs_axis, 'gt_vx', t_int, gt_vx,
																unit = 'm/s')

				plot_nav.addSignal2Axis(vx_abs_axis, 'vx_abs+std', t, flc25_vx_abs_std_p, unit = 'm/s', ls = "--", color = "green")
				plot_nav.addSignal2Axis(vx_abs_axis, 'vx_abs-std', t, flc25_vx_abs_std_n, unit = 'm/s', ls = "--", color = "green")
				vx_abs_axis.fill_between(t, flc25_vx_abs_std_p, flc25_vx_abs_std_n, color = "green", alpha = "0.3")

				plot_nav.addSignal2Axis(vy_abs_axis, 'vy_abs', t_int, flc25_vy_abs,
																unit = 'm/s')
				plot_nav.addSignal2Axis(vy_abs_axis, 'gt_vy', t_int, gt_vy,
																unit = 'm/s')

				plot_nav.addSignal2Axis(vy_abs_axis, 'vy_abs+std', t, flc25_vy_abs_std_p, unit = 'm/s', ls = "--", color = "green")
				plot_nav.addSignal2Axis(vy_abs_axis, 'vy_abs-std', t, flc25_vy_abs_std_n, unit = 'm/s', ls = "--", color = "green")
				vy_abs_axis.fill_between(t, flc25_vy_abs_std_p, flc25_vy_abs_std_n, color = "green", alpha = "0.3")

				sync = self.get_sync()
				sync.addClient(plot_nav)

				# dx
				dx_max_lag_time = self.get_max_lag(flc25_dx, gt_dx, t_int)
				dx_max_lag_time = np.repeat(dx_max_lag_time, len(t))
				list_nav.addsignal("dx: Max lag (Seconds)".format(self.id), (t, dx_max_lag_time), groupname = "Default")

				dx_isd = self.get_int_of_squared_diff(flc25_dx, gt_dx, t_int)
				dx_isd = np.repeat(dx_isd, len(t))
				list_nav.addsignal("dx: Integral of squared differences".format(self.id), (t, dx_isd), groupname = "Default")

				# dy
				dy_max_lag_time = self.get_max_lag(flc25_dy, gt_dy, t_int)
				dy_max_lag_time = np.repeat(dy_max_lag_time, len(t))
				list_nav.addsignal("dy: Max lag (Seconds)".format(self.id), (t, dy_max_lag_time), groupname = "Default")

				dy_isd = self.get_int_of_squared_diff(flc25_dy, gt_dy, t_int)
				dy_isd = np.repeat(dy_isd, len(t))
				list_nav.addsignal("dy: Integral of squared differences".format(self.id), (t, dy_isd), groupname = "Default")

				# vx_abs
				vx_abs_max_lag_time = self.get_max_lag(flc25_vx_abs, gt_vx, t_int)
				vx_abs_max_lag_time = np.repeat(vx_abs_max_lag_time, len(t))
				list_nav.addsignal("vx_abs: Max lag (Seconds)".format(self.id), (t, vx_abs_max_lag_time), groupname =
				"Default")

				vx_abs_isd = self.get_int_of_squared_diff(flc25_vx_abs, gt_vx, t_int)
				vx_abs_isd = np.repeat(vx_abs_isd, len(t))
				list_nav.addsignal("vx_abs: Integral of squared differences".format(self.id), (t, vx_abs_isd),
													 groupname = "Default")

				# vy_abs
				vy_abs_max_lag_time = self.get_max_lag(flc25_vy_abs, gt_vy, t_int)
				vy_abs_max_lag_time = np.repeat(vy_abs_max_lag_time, len(t))
				list_nav.addsignal("vy_abs: Max lag (Seconds)".format(self.id), (t, vy_abs_max_lag_time), groupname =
				"Default")

				vy_abs_isd = self.get_int_of_squared_diff(flc25_vy_abs, gt_vy, t_int)
				vy_abs_isd = np.repeat(vy_abs_isd, len(t))
				list_nav.addsignal("vy_abs: Integral of squared differences".format(self.id), (t, vy_abs_isd),
													 groupname = "Default")

				return

		def get_max_lag(self, x1_array, x2_array, time):
				npts = len(x1_array)
				lags = np.arange(-npts + 1, npts)
				ccor = np.correlate(x1_array, x2_array, mode = 'full')
				max_lag = lags[np.argmax(ccor)]
				if max_lag < 0:
						max_lag_time = - time[abs(max_lag)] - time[0]
				else:
						max_lag_time = time[max_lag] - time[0]
				return max_lag_time

		def get_int_of_squared_diff(self, x1_array, x2_array, t):
				"""https://www.sciencedirect.com/topics/engineering/squared-difference
		"""
				ssd = 0
				sd = 0
				a = np.trapz(np.square(x1_array - x2_array), x = t)
				for i in range(x1_array.size):
						for j in range(x2_array.size):
								diff = x1_array[i] - x2_array[j]
								ssd += diff * diff
				# 		sd += np.sqrt(ssd/x2_array.size)
				#
				# # Mean of all standard devialtions wrt x1
				# final_sd = sd/x1_array.size
				# print(final_sd)
				return a
