# -*- dataeval: init -*-
"""
:Name:
	view_sprague_geer_metric_calculation_for_gt_raw_with_flc25_cem_tpf_tracks.py
:Type:
	View Script
:Full Path:
	dataevalaebs/src/dataevalaebs/view_sprague_geer_metric_calculation_for_gt_raw_with_flc25_cem_tpf_tracks.py
:Short Description:
		`More Information <../html/dataevalaebs.html#module-dataevalaebs.view_paebs_kpi_for_gt_raw_with_flc25_cem_tpf_tracks>`__
:Large Description:
		.. image:: ../images/view_sprague_geer_metric_calculation_for_gt_raw_with_flc25_cem_tpf_tracks_1.png
"""
import numpy as np

from interface import iParameter, iView
import datavis

# instantiation of module parameters


init_params = dict(('TRACK_%03d' % i, dict(id = i)) for i in xrange(0, 100))


class cMyView(iView):
		dep = 'fill_flc25_cem_tpf_tracks@aebs.fill', 'fill_ground_truth_raw_tracks@aebs.fill'

		def init(self, id):
				self.id = id
				return

		def check(self):
				modules = self.get_modules()
				flc25_tracks,_ = modules.fill("fill_flc25_cem_tpf_tracks@aebs.fill")
				gt_track = modules.fill("fill_ground_truth_raw_tracks@aebs.fill")
				flc25_tracks = flc25_tracks.rescale(gt_track["time"])
				assert self.id in flc25_tracks, 'Track %d is not recorded' % self.id

				flc25_tracks = flc25_tracks[self.id]

				return flc25_tracks, gt_track

		def view(self, flc25_tracks, gt_track):
				t = flc25_tracks.time
				plot_nav = datavis.cPlotNavigator(title = 'Sprague and Geer metric compare GT and FLC25 track #%d' % self.id)
				dx_axis = plot_nav.addAxis(ylabel = 'dx')
				dy_axis = plot_nav.addAxis(ylabel = 'dy')
				vx_abs_axis = plot_nav.addAxis(ylabel = 'vx_abs')
				vy_abs_axis = plot_nav.addAxis(ylabel = 'vy_abs')

				list_nav = datavis.cListNavigator(
								title = "Sprague and Geer metric comparison between GT with FLC25 track #%d" % self.id)
				self.sync.addClient(list_nav)

				t_start, t_end = self.get_time_mask(gt_track, 110, 50, 2)

				# There is not any gt object tracking flc25 obj in the track
				if t_start is None and t_end is None:
						invalid_track = np.repeat("NA", len(t))
						list_nav.addsignal("Could not find FLC25 object following ground truth object".format(self.id),
															 (t, invalid_track),
															 groupname = "Default")
						return

				flc25_dx = flc25_tracks.dx[t_start:  t_end].squeeze().data
				gt_dx = gt_track['dx'][t_start:  t_end].squeeze()
				flc25_dx_std = flc25_tracks.dx_std[t_start:  t_end].squeeze().data
				flc25_dx_std_p = flc25_dx + flc25_dx_std
				flc25_dx_std_n = flc25_dx - flc25_dx_std

				flc25_dy = flc25_tracks.dy[t_start:  t_end].squeeze().data
				gt_dy = gt_track['dy'][t_start:  t_end].squeeze()
				flc25_dy_std = flc25_tracks.dy_std[t_start:  t_end].squeeze().data
				flc25_dy_std_p = flc25_dy + flc25_dy_std
				flc25_dy_std_n = flc25_dy - flc25_dy_std

				flc25_vx_abs = flc25_tracks.vx_abs[t_start:  t_end].squeeze().data
				gt_vx_abs = gt_track['vx_abs'][t_start:  t_end].squeeze()
				flc25_vx_abs_std = flc25_tracks.vx_abs_std[t_start:  t_end].squeeze().data
				flc25_vx_abs_std_p = flc25_vx_abs + flc25_vx_abs_std
				flc25_vx_abs_std_n = flc25_vx_abs - flc25_vx_abs_std

				flc25_vy_abs = flc25_tracks.vy_abs[t_start:  t_end].squeeze().data
				gt_vy_abs = gt_track['vy_abs'][t_start:  t_end].squeeze()
				flc25_vy_abs_std = flc25_tracks.vy_abs_std[t_start:  t_end].squeeze().data
				flc25_vy_abs_std_p = flc25_vy_abs + flc25_vy_abs_std
				flc25_vy_abs_std_n = flc25_vy_abs - flc25_vy_abs_std

				t_int = t[t_start:  t_end].squeeze()
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
				plot_nav.addSignal2Axis(vx_abs_axis, 'gt_vx_abs', t_int, gt_vx_abs,
																unit = 'm/s')

				plot_nav.addSignal2Axis(vx_abs_axis, 'vx_abs+std', t, flc25_vx_abs_std_p, unit = 'm/s', ls = "--",
																color = "green")
				plot_nav.addSignal2Axis(vx_abs_axis, 'vx_abs-std', t, flc25_vx_abs_std_n, unit = 'm/s', ls = "--",
																color = "green")
				vx_abs_axis.fill_between(t, flc25_vx_abs_std_p, flc25_vx_abs_std_n, color = "green", alpha = "0.3")

				plot_nav.addSignal2Axis(vy_abs_axis, 'vy_abs', t_int, flc25_vy_abs,
																unit = 'm/s')
				plot_nav.addSignal2Axis(vy_abs_axis, 'gt_vy_abs', t_int, gt_vy_abs,
																unit = 'm/s')

				plot_nav.addSignal2Axis(vy_abs_axis, 'vy_abs+std', t, flc25_vy_abs_std_p, unit = 'm/s', ls = "--",
																color = "green")
				plot_nav.addSignal2Axis(vy_abs_axis, 'vy_abs-std', t, flc25_vy_abs_std_n, unit = 'm/s', ls = "--",
																color = "green")
				vy_abs_axis.fill_between(t, flc25_vy_abs_std_p, flc25_vy_abs_std_n, color = "green", alpha = "0.3")

				sync = self.get_sync()
				sync.addClient(plot_nav)

				# dx
				dx_magnitude_error = self.sprague_geer_magnitude(flc25_dx, gt_dx)
				dx_magnitude_error = np.repeat(dx_magnitude_error, len(t))
				list_nav.addsignal("dx: Magnitude Error".format(self.id), (t, dx_magnitude_error), groupname = "Default")

				dx_phase_error = self.sprague_geer_phase(flc25_dx, gt_dx)
				dx_phase_error = np.repeat(dx_phase_error, len(t))
				list_nav.addsignal("dx: Phase Error".format(self.id), (t, dx_phase_error), groupname = "Default")

				dx_russel_err = self.sprague_geer(flc25_dx, gt_dx)
				dx_russel_err = np.repeat(dx_russel_err, len(t))
				list_nav.addsignal("dx: Sprague Geer Combined Error".format(self.id), (t, dx_russel_err), groupname =
				"Default")

				# dy
				dy_magnitude_error = self.sprague_geer_magnitude(flc25_dy, gt_dy)
				dy_magnitude_error = np.repeat(dy_magnitude_error, len(t))
				list_nav.addsignal("dy:  Magnitude Error".format(self.id), (t, dy_magnitude_error), groupname = "Default")

				dy_phase_error = self.sprague_geer_phase(flc25_dy, gt_dy)
				dy_phase_error = np.repeat(dy_phase_error, len(t))
				list_nav.addsignal("dy: Phase Error".format(self.id), (t, dy_phase_error), groupname = "Default")

				dy_russel_err = self.sprague_geer(flc25_dy, gt_dy)
				dy_russel_err = np.repeat(dy_russel_err, len(t))
				list_nav.addsignal("dy:  Sprague Geer Combined Error".format(self.id), (t, dy_russel_err),
													 groupname = "Default")

				# vx
				vx_abs_magnitude_error = self.sprague_geer_magnitude(flc25_vx_abs, gt_vx_abs)
				vx_abs_magnitude_error = np.repeat(vx_abs_magnitude_error, len(t))
				list_nav.addsignal("vx_abs: Magnitude Error".format(self.id), (t, vx_abs_magnitude_error), groupname =
				"Default")

				vx_abs_phase_error = self.sprague_geer_phase(flc25_vx_abs, gt_vx_abs)
				vx_abs_phase_error = np.repeat(vx_abs_phase_error, len(t))
				list_nav.addsignal("vx_abs: Phase Error".format(self.id), (t, vx_abs_phase_error),
													 groupname = "Default")

				vx_abs_sprague_geer_err = self.sprague_geer(flc25_vx_abs, gt_vx_abs)
				vx_abs_sprague_geer_err = np.repeat(vx_abs_sprague_geer_err, len(t))
				list_nav.addsignal("vx_abs:  Sprague Geer Combined Error".format(self.id), (t, vx_abs_sprague_geer_err),
													 groupname = "Default")

				# vy
				vy_abs_magnitude_error = self.sprague_geer_magnitude(flc25_vy_abs, gt_vy_abs)
				vy_abs_magnitude_error = np.repeat(vy_abs_magnitude_error, len(t))
				list_nav.addsignal("vy_abs:  Magnitude Error".format(self.id), (t, vy_abs_magnitude_error), groupname =
				"Default")

				vy_abs_phase_error = self.sprague_geer_phase(flc25_vy_abs, gt_vy_abs)
				vy_abs_phase_error = np.repeat(vy_abs_phase_error, len(t))
				list_nav.addsignal("vy_abs: Phase Error".format(self.id), (t, vy_abs_phase_error),
													 groupname = "Default")

				vy_abs_sprague_geer_err = self.sprague_geer(flc25_vy_abs, gt_vy_abs)
				vy_abs_sprague_geer_err = np.repeat(vy_abs_sprague_geer_err, len(t))
				list_nav.addsignal("vy_abs:  Sprague Geer Combined  Error".format(self.id), (t, vy_abs_sprague_geer_err),
													 groupname = "Default")
				return

		def sprague_geer_magnitude(self, flc25_signal, gt_signal):
				SPErrM = (np.sum(flc25_signal ** 2) / np.sum(gt_signal ** 2)) ** 0.5 - 1
				return SPErrM

		def sprague_geer_phase(self, flc25_signal, gt_signal):

				SPErrP = (1 / np.pi) * np.arccos(
								(np.sum(gt_signal * flc25_signal)) / (
												(np.sum(flc25_signal ** 2) * np.sum(gt_signal ** 2)) ** 0.5))

				return SPErrP

		def sprague_geer(self, flc25_signal, gt_signal):

				sp_err_combined = (self.sprague_geer_magnitude(flc25_signal, gt_signal) ** 2 + self.sprague_geer_phase(
						flc25_signal, gt_signal) ** 2) ** 0.5
				return sp_err_combined

		def get_time_mask(self, ground_truth, fov_angle_degree, fov_dist, fov_min_dist):
				# GET_TIME_MASK returns relative start and end time where ground truth
				#   object meets in FoV and relative speed condition
				#   FoV is defined as opening angle and distance triangle.
				#   Min speed is defined as abs of relative velocity
				#   Ground truth data is provided by in structure according to dcnvt matlab
				fov_x_start = fov_dist
				fov_x_end = 0
				fov_alpha = np.deg2rad(fov_angle_degree)
				fov_y = fov_x_start * np.tan(fov_alpha / 2)
				x_ground_truth = ground_truth['dx']
				x_ground_truth_t = ground_truth['time']
				x_ground_truth_t = x_ground_truth_t - x_ground_truth_t[0]

				y_ground_truth = ground_truth['dy']
				y_ground_truth_t = ground_truth['time']
				y_ground_truth_t = y_ground_truth_t - y_ground_truth_t[0]
				y_ground_truth_resampled = y_ground_truth

				m = x_ground_truth * False

				v_abs = ground_truth['vx_abs']
				v_abs_t = ground_truth['time']
				v_abs_t = v_abs_t - v_abs_t[0]
				v_abs_resampled = v_abs

				for i in range(1, len(x_ground_truth)):
						P1 = [fov_x_end, 0]
						P2 = [fov_x_start, fov_y]
						P3 = [fov_x_start, -fov_y]
						P = [x_ground_truth[i], y_ground_truth_resampled[i]]
						P12 = np.subtract(P1, P2)
						P23 = np.subtract(P2, P3)
						P31 = np.subtract(P3, P1)
						m[i] = np.sign(np.linalg.det([P31, P23])) * np.sign(np.linalg.det([np.subtract(P3, P), P23])) >= 0 and \
									 np.sign(np.linalg.det([P12, P31])) * np.sign(np.linalg.det([np.subtract(P1, P), P31])) >= 0 and \
									 np.sign(np.linalg.det([P23, P12])) * np.sign(np.linalg.det([np.subtract(P2, P), P12])) >= 0
						pass
				m = ((m == 1) & (x_ground_truth >= fov_min_dist))

				idx_m_first_rising_edge = np.argmax(m == True)
				# idx_m_last_rising_edge = len(m) - np.argmax(m[::-1])

				# t_start = x_ground_truth_t[idx_m_first_rising_edge]
				# t_end = x_ground_truth_t[idx_m_last_rising_edge]

				idx_m_first_falling_edge_after_rising = np.argmax(~m[idx_m_first_rising_edge:] == True)
				m[idx_m_first_rising_edge + idx_m_first_falling_edge_after_rising:] = 0

				t_start = idx_m_first_rising_edge
				t_end = idx_m_first_falling_edge_after_rising + idx_m_first_rising_edge
				return (t_start, t_end)
