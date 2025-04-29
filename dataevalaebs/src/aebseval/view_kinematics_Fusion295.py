# -*- dataeval: init -*-

"""
Plot AEBS-relevant kinematic information

Plot basic attributes of ego vehicle and primary track, including speed,
distance etc. 
"""

from numpy import rad2deg

import datavis
from interface import iView
from measparser.signalproc import rescale

DETAIL_LEVEL = 1

mps2kph = lambda v: v*3.6

class View(iView):
	dep = 'fill_flr25_aeb_track@aebs.fill', 'calc_radar_egomotion-flr25@aebs.fill'
	
	def check(self):
		sgs = [
			{
				"Camera_obj_dx": ("Rte_SWC_Postprocessor_Rport_postp_norm_camera_DEP_norm_postp_camera_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_Postprocessor_Rport_postp_norm_camera_DEP_norm_postp_camera_Buf_camera_messages[0]_video_object_A_Longitudinal_Distance_A"),
				"Camera_obj_dx_b": ("Rte_SWC_Postprocessor_Rport_postp_norm_camera_DEP_norm_postp_camera_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_Postprocessor_Rport_postp_norm_camera_DEP_norm_postp_camera_Buf_camera_messages[0]_video_object_B_Longitudinal_Distance_STD_B"),
			}
		]
		# select signals
		group = self.source.selectSignalGroup(sgs)
		# give warning for not available signals
		for alias in sgs[0]:
				if alias not in group:
						self.logger.warning("Signal for '%s' not available" % alias)
		return group

	def view(self, group):
		# process signals
		track = self.modules.fill(self.dep[0])
		t = track.time
		ego = self.modules.fill(self.dep[1])
		time , cam_obj_dx, _ = group.get_signal_with_unit("Camera_obj_dx")
		_ , cam_obj_dx_b, _ = group.get_signal_with_unit("Camera_obj_dx_b")
		
		# create plot
		pn = datavis.cPlotNavigator(title='Ego vehicle and obstacle kinematics')
		
		# speed
		ax = pn.addAxis(ylabel='speed', ylim=(-5.0, 100.0))
		pn.addSignal2Axis(ax, 'ego speed', t, mps2kph(ego.vx), unit='km/h')
		track_vx_abs = rescale(ego.time, ego.vx, t)[1] + track.vx   # v_ego + v_track #rescale(ego.time, ego.vx, t)[1]
		pn.addSignal2Axis(ax, 'obst. speed', t,  mps2kph(track_vx_abs), unit='km/h')
		self.extend_speed_axis(pn, ax)

		# acceleration
		ax = pn.addAxis(ylabel = 'accel.conti', ylim = (-10.0, 10.0))
		pn.addSignal2Axis(ax, 'ego acceleration', t, ego.ax, unit = 'm/s^2')
		pn.addSignal2Axis(ax, 'obst. acceleration', t, track.ax, unit='m/s^2') # ax_abs
		self.extend_accel_axis(pn, ax)

		# yaw rate
		if DETAIL_LEVEL > 0:
			ax = pn.addAxis(ylabel = "yaw rate", ylim = (-12.0, 12.0))
			pn.addSignal2Axis(ax, "yaw rate", t, rad2deg(ego.yaw_rate), unit = "deg/s")
		# if DETAIL_LEVEL > 0:
		#   ax = pn.addAxis(ylabel = "yaw rate", ylim = (-12.0, 12.0))
		#   pn.addSignal2Axis(ax, "yaw rate", t, rad2deg(ego.yaw_rate), unit = "deg/s")
		# dx
		
		ax = pn.addAxis(ylabel = 'long. dist.', ylim = (0.0, 150.0))
		RED = '#CC2529'
		pn.addSignal2Axis(ax, 'cam_dx', time, cam_obj_dx, unit = 'm', color=RED)
		pn.addSignal2Axis(ax, 'cam_dx_B', time, cam_obj_dx_b, unit = 'm', color = 'orange')
		pn.addSignal2Axis(ax, 'dx', t, track.dx, unit = 'm', color='b')
		ax = pn.addTwinAxis(ax, ylabel = 'lat. dist.', ylim = (-15, 15), color = 'g')
		pn.addSignal2Axis(ax, 'dy', t, track.dy, unit = 'm', color = 'g')

		# mov_state
		mapping = track.mov_state.mapping
		ax = pn.addAxis(ylabel='moving state', yticks=mapping, ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
		pn.addSignal2Axis(ax, 'obst. mov_st', t, track.mov_state.join(), color='g')
		# mov_dir
		if DETAIL_LEVEL > 0:
			mapping = track.mov_dir.mapping
			ax = pn.addAxis(ylabel='moving direction', yticks=mapping,
											ylim=(min(mapping)-0.5, max(mapping)+0.5))
			pn.addSignal2Axis(ax, 'obst. mov_dir', t, track.mov_dir.join(), color='g')
		# # confidence
		# if DETAIL_LEVEL > 0:
		#   ax = pn.addAxis(ylabel='confidence', yticks={0:0, 1:1, 2:'no', 3:'yes'},
		#                   ylim=(-0.1, 3.1))
		#   pn.addSignal2Axis(ax, 'radar conf', t, track.radar_conf)
		#   pn.addSignal2Axis(ax, 'video conf', t, track.video_conf)
		#   pn.addSignal2Axis(ax, 'video associated', t, track.fused, offset=2,
		#                     displayscaled=True)
		
		# register client
		self.sync.addClient(pn)
		return

	def extend_speed_axis(self, pn, ax):
		return

	def extend_accel_axis(self, pn, ax):
		return
