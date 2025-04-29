# -*- dataeval: init -*-
import logging
import os

import numpy as np
import scipy
from dmw.resimulation_export import sensorports
from interface import iObjectFill

# from measparser.PostmarkerJSONParser import parse_icon_data

logger = logging.getLogger("fillFLC25_RESIM_EXPORT")
INVALID_ID = 255
INVALID_TRACK_ID = -1
CONFIG_DIRECTORY = os.path.join(os.path.dirname(__file__), "config")


class cFill(iObjectFill):
		optdep = (
				"fill_flc25_cem_tpf_tracks@aebs.fill",
				"fill_flc25_em_tracks@aebs.fill",
				"fill_flc25_can_tracks@aebs.fill",
				"fill_flc25_ars_fcu_tracks@aebs.fill",
				"calc_egomotion_resim@aebs.fill",
				"calc_lanes_flc25_ld@aebs.fill",
				"calc_lanes_flc25_abd@aebs.fill",
				"calc_lanes-flc25@aebs.fill",
				"fillFLC25_TSR@aebs.fill",
				"fill_postmarker_traffic_signs@aebs.fill",
				"calc_common_time-flc25@aebs.fill",
				"calc_common_time-tsrresim@aebs.fill",
				"fill_ground_truth_raw_tracks@aebs.fill",
		)

		def check(self):
				(
						cem_tpf_tracks,
						em_tracks,
						can_tracks,
						ars_fcu_tracks,
						ego_orig,
						ld_lanes,
						can_lanes,
						abd_lanes,
						postmarker_tsr,
						conti_tsr,
						conti_tsr_suppl,
						value_is_conti_sign_detected,
						common_time,
						gps_adma_object,
						common_time_tsr,
				) = (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
				self.sensor = sensorports
				modules = self.get_modules()
				common_time = modules.fill("calc_common_time-flc25")
				if np.any(np.array(self.sensor["CONTI_TSR"].values()) == True) or (
								np.any(np.array(self.sensor["TSR_DETECTION_COMPARISION"].values()) == True)
				) or (
								np.any(np.array(self.sensor["CONTI_TSR"].values()) == True)
				):
						common_time_tsr = modules.fill("calc_common_time-tsrresim@aebs.fill")

				value_is_conti_sign_detected = None
				if np.any(np.array(self.sensor["FLC25_CEM_TPF"].values()) == True):
						cem_tpf_tracks, _ = modules.fill("fill_flc25_cem_tpf_tracks@aebs.fill")

				if np.any(np.array(self.sensor["FLC25_EM"].values()) == True):
						em_tracks, _ = modules.fill("fill_flc25_em_tracks@aebs.fill")
						em_tracks = em_tracks.rescale(common_time)

				if np.any(np.array(self.sensor["FLC25_CAN"].values()) == True):
						can_tracks, _ = modules.fill("fill_flc25_can_tracks@aebs.fill")
						can_tracks = can_tracks.rescale(common_time)

				if np.any(np.array(self.sensor["FLC25_ARS_FCU"].values()) == True):
						ars_fcu_tracks, _ = modules.fill("fill_flc25_ars_fcu_tracks@aebs.fill")
						ars_fcu_tracks = ars_fcu_tracks.rescale(common_time)

				if np.any(np.array(self.sensor["FLC25_LD_LANES"].values()) == True):
						ld_lanes = modules.fill("calc_lanes_flc25_ld@aebs.fill")
						ld_lanes = ld_lanes.rescale(common_time)

				if np.any(np.array(self.sensor["FLC25_CAN_LANES"].values()) == True):
						can_lanes = modules.fill("calc_lanes-flc25@aebs.fill")
						can_lanes = can_lanes.rescale(common_time)

				if np.any(np.array(self.sensor["FLC25_ABD_LANES"].values()) == True):
						abd_lanes = modules.fill("calc_lanes_flc25_abd@aebs.fill")
						abd_lanes = abd_lanes.rescale(common_time)

				if np.any(np.array(self.sensor["TSR_DETECTION_COMPARISION"].values()) == True):
						_, postmarker_tsr,resim_deviation,traffic_sign_report = modules.fill("fill_postmarker_traffic_signs@aebs.fill")
						conti_tsr = modules.fill("fillFLC25_TSR@aebs.fill")
						lmk_tracks, conti_tsr_suppl = modules.fill("fill_flc25_tsr_raw_tracks@aebs.fill")
						sgs = [
								{
										"iNumOfUsedLandmarks": (
												"LmkGenLandmarkList",
												"MFC5xx_Device_LMK_LmkGenLandmarkList_HeaderLmkList_iNumOfUsedLandmarks",
										),
								},
						]
						group = self.source.selectSignalGroupOrEmpty(sgs)
						_, value, _ = group.get_signal_with_unit(
										"iNumOfUsedLandmarks", ScaleTime = common_time_tsr
						)
						value_is_conti_sign_detected = value > 0

				if np.any(np.array(self.sensor["POSTMARKER_TOOL"].values()) == True) and not (
								np.any(np.array(self.sensor["TSR_DETECTION_COMPARISION"].values()) == True)
				):
						_, postmarker_tsr,resim_deviation,traffic_sign_report = modules.fill("fill_postmarker_traffic_signs@aebs.fill")

				if np.any(np.array(self.sensor["CONTI_TSR"].values()) == True) and not (
								np.any(np.array(self.sensor["TSR_DETECTION_COMPARISION"].values()) == True)
				):
						conti_tsr = modules.fill("fillFLC25_TSR@aebs.fill")
						lmk_tracks, conti_tsr_suppl = modules.fill("fill_flc25_tsr_raw_tracks@aebs.fill")

				if np.any(np.array(self.sensor["EGO_VEHICLE"].values()) == True):
						ego_orig = modules.fill("calc_egomotion_resim@aebs.fill")
						ego_orig = ego_orig.rescale(common_time)

				if np.any(np.array(self.sensor["GPS"].values()) == True):
						gps_adma_object = modules.fill("fill_ground_truth_raw_tracks@aebs.fill")

				return (
						cem_tpf_tracks,
						em_tracks,
						can_tracks,
						ars_fcu_tracks,
						ego_orig,
						ld_lanes,
						can_lanes,
						abd_lanes,
						postmarker_tsr,
						conti_tsr,
						conti_tsr_suppl,
						value_is_conti_sign_detected,
						common_time,
            common_time_tsr,
						gps_adma_object,
				)

		def fill(
						self,
						cem_tpf_tracks,
						em_tracks,
						can_tracks,
						ars_fcu_tracks,
						ego_orig,
						ld_lanes,
						can_lanes,
						abd_lanes,
						postmarker_tsr,
						conti_tsr,
						conti_tsr_suppl,
						value_is_conti_sign_detected,
						common_time,
            common_time_tsr,
						gps_adma_object,
		):

				import time

				start = time.time()
				logger.info("FLC25  object retrieval is started, Please wait...")

				final_buffer = {}
				lane_object = {}
				# <editor-fold desc="LD Lanes">
				if np.any(np.array(self.sensor["FLC25_LD_LANES"].values()) == True):
						ld_lanesinfo = {}

						if ld_lanes.left_line is not None:
								left_line = {}
								if self.sensor["FLC25_LD_LANES"]["Lane_View_Range"]:
										left_line["range"] = ld_lanes.left_line.view_range
								if self.sensor["FLC25_LD_LANES"]["C0"]:
										left_line["C0"] = ld_lanes.left_line.c0
								if self.sensor["FLC25_LD_LANES"]["C1"]:
										left_line["C1"] = ld_lanes.left_line.c1
								if self.sensor["FLC25_LD_LANES"]["C2"]:
										left_line["C2"] = ld_lanes.left_line.c2
								if self.sensor["FLC25_LD_LANES"]["C3"]:
										left_line["C3"] = ld_lanes.left_line.c3
								if self.sensor["FLC25_LD_LANES"]["time"]:
										left_line["time"] = ld_lanes.left_line.time
								ld_lanesinfo["left_line"] = left_line

						if ld_lanes.right_line is not None:
								right_line = {}
								if self.sensor["FLC25_LD_LANES"]["Lane_View_Range"]:
										right_line["range"] = ld_lanes.right_line.view_range
								if self.sensor["FLC25_LD_LANES"]["C0"]:
										right_line["C0"] = ld_lanes.right_line.c0
								if self.sensor["FLC25_LD_LANES"]["C1"]:
										right_line["C1"] = ld_lanes.right_line.c1
								if self.sensor["FLC25_LD_LANES"]["C2"]:
										right_line["C2"] = ld_lanes.right_line.c2
								if self.sensor["FLC25_LD_LANES"]["C3"]:
										right_line["C3"] = ld_lanes.right_line.c3
								if self.sensor["FLC25_LD_LANES"]["time"]:
										right_line["time"] = ld_lanes.right_line.time
								ld_lanesinfo["right_line"] = right_line

						if ld_lanes.left_left_line is not None:
								left_left_line = {}
								if self.sensor["FLC25_LD_LANES"]["Lane_View_Range"]:
										left_left_line["range"] = ld_lanes.left_left_line.view_range
								if self.sensor["FLC25_LD_LANES"]["C0"]:
										left_left_line["C0"] = ld_lanes.left_left_line.c0
								if self.sensor["FLC25_LD_LANES"]["C1"]:
										left_left_line["C1"] = ld_lanes.left_left_line.c1
								if self.sensor["FLC25_LD_LANES"]["C2"]:
										left_left_line["C2"] = ld_lanes.left_left_line.c2
								if self.sensor["FLC25_LD_LANES"]["C3"]:
										left_left_line["C3"] = ld_lanes.left_left_line.c3
								if self.sensor["FLC25_LD_LANES"]["time"]:
										left_left_line["time"] = ld_lanes.left_left_line.time
								ld_lanesinfo["left_left_line"] = left_left_line

						if ld_lanes.right_right_line is not None:
								right_right_line = {}
								if self.sensor["FLC25_LD_LANES"]["Lane_View_Range"]:
										right_right_line["range"] = ld_lanes.right_right_line.view_range
								if self.sensor["FLC25_LD_LANES"]["C0"]:
										right_right_line["C0"] = ld_lanes.right_right_line.c0
								if self.sensor["FLC25_LD_LANES"]["C1"]:
										right_right_line["C1"] = ld_lanes.right_right_line.c1
								if self.sensor["FLC25_LD_LANES"]["C2"]:
										right_right_line["C2"] = ld_lanes.right_right_line.c2
								if self.sensor["FLC25_LD_LANES"]["C3"]:
										right_right_line["C3"] = ld_lanes.right_right_line.c3
								if self.sensor["FLC25_LD_LANES"]["time"]:
										right_right_line["time"] = ld_lanes.right_right_line.time
								ld_lanesinfo["right_right_line"] = right_right_line

						lane_object_key1 = "flc25_ld_lanes"
						lane_object[lane_object_key1] = ld_lanesinfo

				# </editor-fold>

				# <editor-fold desc="CAN Lanes">
				if np.any(np.array(self.sensor["FLC25_CAN_LANES"].values()) == True):
						can_lanesinfo = {}
						if can_lanes.left_line is not None:
								left_line = {}
								if self.sensor["FLC25_CAN_LANES"]["Lane_View_Range"]:
										left_line["range"] = can_lanes.left_line.view_range
								if self.sensor["FLC25_CAN_LANES"]["C0"]:
										left_line["C0"] = can_lanes.left_line.c0
								if self.sensor["FLC25_CAN_LANES"]["C1"]:
										left_line["C1"] = can_lanes.left_line.c1
								if self.sensor["FLC25_CAN_LANES"]["C2"]:
										left_line["C2"] = can_lanes.left_line.c2
								if self.sensor["FLC25_CAN_LANES"]["C3"]:
										left_line["C3"] = can_lanes.left_line.c3
								if self.sensor["FLC25_CAN_LANES"]["time"]:
										left_line["time"] = can_lanes.left_line.time
								can_lanesinfo["left_line"] = left_line

						if can_lanes.right_line is not None:
								right_line = {}
								if self.sensor["FLC25_CAN_LANES"]["Lane_View_Range"]:
										right_line["range"] = can_lanes.right_line.view_range
								if self.sensor["FLC25_CAN_LANES"]["C0"]:
										right_line["C0"] = can_lanes.right_line.c0
								if self.sensor["FLC25_CAN_LANES"]["C1"]:
										right_line["C1"] = can_lanes.right_line.c1
								if self.sensor["FLC25_CAN_LANES"]["C2"]:
										right_line["C2"] = can_lanes.right_line.c2
								if self.sensor["FLC25_CAN_LANES"]["C3"]:
										right_line["C3"] = can_lanes.right_line.c3
								if self.sensor["FLC25_CAN_LANES"]["time"]:
										right_line["time"] = can_lanes.right_line.time
								can_lanesinfo["right_line"] = right_line

						if can_lanes.left_left_line is not None:
								left_left_line = {}
								if self.sensor["FLC25_CAN_LANES"]["Lane_View_Range"]:
										left_left_line["range"] = can_lanes.left_left_line.view_range
								if self.sensor["FLC25_CAN_LANES"]["C0"]:
										left_left_line["C0"] = can_lanes.left_left_line.c0
								if self.sensor["FLC25_CAN_LANES"]["C1"]:
										left_left_line["C1"] = can_lanes.left_left_line.c1
								if self.sensor["FLC25_CAN_LANES"]["C2"]:
										left_left_line["C2"] = can_lanes.left_left_line.c2
								if self.sensor["FLC25_CAN_LANES"]["C3"]:
										left_left_line["C3"] = can_lanes.left_left_line.c3
								if self.sensor["FLC25_CAN_LANES"]["time"]:
										left_left_line["time"] = can_lanes.left_left_line.time
								can_lanesinfo["left_left_line"] = left_left_line

						if can_lanes.right_right_line is not None:
								right_right_line = {}
								if self.sensor["FLC25_CAN_LANES"]["Lane_View_Range"]:
										right_right_line["range"] = can_lanes.right_right_line.view_range
								if self.sensor["FLC25_CAN_LANES"]["C0"]:
										right_right_line["C0"] = can_lanes.right_right_line.c0
								if self.sensor["FLC25_CAN_LANES"]["C1"]:
										right_right_line["C1"] = can_lanes.right_right_line.c1
								if self.sensor["FLC25_CAN_LANES"]["C2"]:
										right_right_line["C2"] = can_lanes.right_right_line.c2
								if self.sensor["FLC25_CAN_LANES"]["C3"]:
										right_right_line["C3"] = can_lanes.right_right_line.c3
								if self.sensor["FLC25_CAN_LANES"]["time"]:
										right_right_line["time"] = can_lanes.right_right_line.time
								can_lanesinfo["right_right_line"] = right_right_line

						lane_object_key2 = "flc25_can_lanes"
						lane_object[lane_object_key2] = can_lanesinfo
				# </editor-fold>

				# <editor-fold desc="ABD Lanes">
				if np.any(np.array(self.sensor["FLC25_ABD_LANES"].values()) == True):
						abd_lanesinfo = {}
						if abd_lanes.left_line is not None:
								left_line = {}
								if self.sensor["FLC25_ABD_LANES"]["Lane_View_Range"]:
										left_line["range"] = abd_lanes.left_line.view_range
								if self.sensor["FLC25_ABD_LANES"]["C0"]:
										left_line["C0"] = abd_lanes.left_line.c0
								if self.sensor["FLC25_ABD_LANES"]["C1"]:
										left_line["C1"] = abd_lanes.left_line.c1
								if self.sensor["FLC25_ABD_LANES"]["C2"]:
										left_line["C2"] = abd_lanes.left_line.c2
								if self.sensor["FLC25_ABD_LANES"]["C3"]:
										left_line["C3"] = abd_lanes.left_line.c3
								if self.sensor["FLC25_ABD_LANES"]["time"]:
										left_line["time"] = abd_lanes.left_line.time
								abd_lanesinfo["left_line"] = left_line

						if abd_lanes.right_line is not None:
								right_line = {}
								if self.sensor["FLC25_ABD_LANES"]["Lane_View_Range"]:
										right_line["range"] = abd_lanes.right_line.view_range
								if self.sensor["FLC25_ABD_LANES"]["C0"]:
										right_line["C0"] = abd_lanes.right_line.c0
								if self.sensor["FLC25_ABD_LANES"]["C1"]:
										right_line["C1"] = abd_lanes.right_line.c1
								if self.sensor["FLC25_ABD_LANES"]["C2"]:
										right_line["C2"] = abd_lanes.right_line.c2
								if self.sensor["FLC25_ABD_LANES"]["C3"]:
										right_line["C3"] = abd_lanes.right_line.c3
								if self.sensor["FLC25_ABD_LANES"]["time"]:
										right_line["time"] = abd_lanes.right_line.time
								abd_lanesinfo["right_line"] = right_line

						if abd_lanes.left_left_line is not None:
								left_left_line = {}
								if self.sensor["FLC25_ABD_LANES"]["Lane_View_Range"]:
										left_left_line["range"] = abd_lanes.left_left_line.view_range
								if self.sensor["FLC25_ABD_LANES"]["C0"]:
										left_left_line["C0"] = abd_lanes.left_left_line.c0
								if self.sensor["FLC25_ABD_LANES"]["C1"]:
										left_left_line["C1"] = abd_lanes.left_left_line.c1
								if self.sensor["FLC25_ABD_LANES"]["C2"]:
										left_left_line["C2"] = abd_lanes.left_left_line.c2
								if self.sensor["FLC25_ABD_LANES"]["C3"]:
										left_left_line["C3"] = abd_lanes.left_left_line.c3
								if self.sensor["FLC25_ABD_LANES"]["time"]:
										left_left_line["time"] = abd_lanes.left_left_line.time
								abd_lanesinfo["left_left_line"] = left_left_line

						if abd_lanes.right_right_line is not None:
								right_right_line = {}
								if self.sensor["FLC25_ABD_LANES"]["Lane_View_Range"]:
										right_right_line["range"] = abd_lanes.right_right_line.view_range[
										                            :500
										                            ]
								if self.sensor["FLC25_ABD_LANES"]["C0"]:
										right_right_line["C0"] = abd_lanes.right_right_line.c0
								if self.sensor["FLC25_ABD_LANES"]["C1"]:
										right_right_line["C1"] = abd_lanes.right_right_line.c1
								if self.sensor["FLC25_ABD_LANES"]["C2"]:
										right_right_line["C2"] = abd_lanes.right_right_line.c2
								if self.sensor["FLC25_ABD_LANES"]["C3"]:
										right_right_line["C3"] = abd_lanes.right_right_line.c3
								if self.sensor["FLC25_ABD_LANES"]["time"]:
										right_right_line["time"] = abd_lanes.right_right_line.time
								abd_lanesinfo["right_right_line"] = right_right_line

						lane_object_key3 = "flc25_abd_lanes"
						lane_object[lane_object_key3] = abd_lanesinfo

				# </editor-fold>

				# <editor-fold desc="CEM_TPF Objects">
				if np.any(np.array(self.sensor["FLC25_CEM_TPF"].values()) == True):
						cem_tpf_objectbufferlist = {}
						for id, cem_tpf_track in cem_tpf_tracks.iteritems():
								o = {}
								if self.sensor["FLC25_CEM_TPF"]["time"]:
										o["time"] = cem_tpf_track.time
								if self.sensor["FLC25_CEM_TPF"]["id"]:
										o["id"] = np.where(cem_tpf_track.dx.mask, INVALID_ID, id)
								if self.sensor["FLC25_CEM_TPF"]["tr_state"]:
										o["valid"] = (
														cem_tpf_track.tr_state.valid.data
														& ~cem_tpf_track.tr_state.valid.mask
										)
								if self.sensor["FLC25_CEM_TPF"]["obj_type"]:
										object_type = np.empty(cem_tpf_track.dx.shape, dtype = "int")
										object_type[:] = 6
										car = np.where(cem_tpf_track.obj_type.car, 1, 0)
										truck = np.where(cem_tpf_track.obj_type.truck, 2, 0)
										motorcycle = np.where(cem_tpf_track.obj_type.motorcycle, 3, 0)
										pedestrian = np.where(cem_tpf_track.obj_type.pedestrian, 4, 0)
										bicycle = np.where(cem_tpf_track.obj_type.bicycle, 5, 0)
										unknown = np.where(cem_tpf_track.obj_type.unknown, 6, 0)
										point = np.where(cem_tpf_track.obj_type.point, 7, 0)
										wide = np.where(cem_tpf_track.obj_type.wide, 8, 0)

										object_type[car == 1] = 1
										object_type[truck == 2] = 2
										object_type[motorcycle == 3] = 3
										object_type[pedestrian == 4] = 4
										object_type[bicycle == 5] = 5
										object_type[unknown == 6] = 6
										object_type[point == 7] = 7
										object_type[wide == 8] = 8

										o["object_type"] = object_type
								if self.sensor["FLC25_CEM_TPF"]["dx"]:
										cem_tpf_track.dx.data[cem_tpf_track.dx.mask] = 0
										o["dx"] = cem_tpf_track.dx.data
								if self.sensor["FLC25_CEM_TPF"]["dy"]:
										cem_tpf_track.dy.data[cem_tpf_track.dy.mask] = 0
										o["dy"] = cem_tpf_track.dy.data
								if self.sensor["FLC25_CEM_TPF"]["ax"]:
										o["ax"] = cem_tpf_track.ax.data
								if self.sensor["FLC25_CEM_TPF"]["ay"]:
										o["ay"] = cem_tpf_track.ay.data
								if self.sensor["FLC25_CEM_TPF"]["vx"]:
										o["vx"] = cem_tpf_track.vx.data
								if self.sensor["FLC25_CEM_TPF"]["vy"]:
										o["vy"] = cem_tpf_track.vy.data
								if self.sensor["FLC25_CEM_TPF"]["height"]:
										o["height"] = cem_tpf_track.height.data
								if self.sensor["FLC25_CEM_TPF"]["width"]:
										o["width"] = cem_tpf_track.width.data
								if self.sensor["FLC25_CEM_TPF"]["length"]:
										o["length"] = cem_tpf_track.length.data
								if self.sensor["FLC25_CEM_TPF"]["dx_std"]:
										o["dx_std"] = cem_tpf_track.dx_std.data
								if self.sensor["FLC25_CEM_TPF"]["dy_std"]:
										o["dy_std"] = cem_tpf_track.dy_std.data
								if self.sensor["FLC25_CEM_TPF"]["range"]:
										o["range"] = cem_tpf_track.range.data
								if self.sensor["FLC25_CEM_TPF"]["angle"]:
										o["angle"] = cem_tpf_track.angle.data
								if self.sensor["FLC25_CEM_TPF"]["ay_abs"]:
										o["ay_abs"] = cem_tpf_track.ay_abs.data
								if self.sensor["FLC25_CEM_TPF"]["ax_abs"]:
										o["ax_abs"] = cem_tpf_track.ax_abs.data

								# o["ax_abs"] = cem_tpf_track.ax_abs.data
								if self.sensor["FLC25_CEM_TPF"]["vx_std"]:
										o["vx_std"] = cem_tpf_track.vx_std.data
								if self.sensor["FLC25_CEM_TPF"]["vy_std"]:
										o["vy_std"] = cem_tpf_track.vy_std.data
								if self.sensor["FLC25_CEM_TPF"]["vx_abs"]:
										o["vx_abs"] = cem_tpf_track.vx_abs.data
								if self.sensor["FLC25_CEM_TPF"]["vy_abs"]:
										o["vy_abs"] = cem_tpf_track.vy_abs.data
								if self.sensor["FLC25_CEM_TPF"]["vx_abs_std"]:
										o["vx_abs_std"] = cem_tpf_track.vx_abs_std.data
								if self.sensor["FLC25_CEM_TPF"]["vy_abs_std"]:
										o["vy_abs_std"] = cem_tpf_track.vy_abs_std.data
								if self.sensor["FLC25_CEM_TPF"]["dz"]:
										o["dz"] = cem_tpf_track.dz.data
								if self.sensor["FLC25_CEM_TPF"]["dz_std"]:
										o["dz_std"] = cem_tpf_track.dz_std.data
								if self.sensor["FLC25_CEM_TPF"]["yaw"]:
										o["yaw"] = cem_tpf_track.yaw.data
								if self.sensor["FLC25_CEM_TPF"]["yaw_std"]:
										o["yaw_std"] = cem_tpf_track.yaw_std.data
								if self.sensor["FLC25_CEM_TPF"]["mov_state"]:
										o["mov_state"] = cem_tpf_track.mov_state.join()
								if self.sensor["FLC25_CEM_TPF"]["video_conf"]:
										o["video_conf"] = cem_tpf_track.video_conf.data
								if self.sensor["FLC25_CEM_TPF"]["measured_by"]:
										o["measured_by"] = cem_tpf_track.measured_by.join()
								if self.sensor["FLC25_CEM_TPF"]["lane"]:
										o["lane"] = cem_tpf_track.lane.join()

								objectbuffer_key = "cem_tpf_objectbuffer" + str(id)
								cem_tpf_objectbufferlist[objectbuffer_key] = o
						final_buffer_key1 = "flc25_cem_tpf_objects"
						final_buffer[final_buffer_key1] = cem_tpf_objectbufferlist
				# </editor-fold>

				# <editor-fold desc="EM Objects">
				if np.any(np.array(self.sensor["FLC25_EM"].values()) == True):
						em_objectbufferlist = {}
						for id, em_track in em_tracks.iteritems():
								o = {}
								if self.sensor["FLC25_EM"]["time"]:
										o["time"] = em_track.time
								if self.sensor["FLC25_EM"]["id"]:
										o["id"] = np.where(em_track.dx.mask, INVALID_ID, id)
								if self.sensor["FLC25_EM"]["tr_state"]:
										o["valid"] = (
														em_track.tr_state.valid.data & ~em_track.tr_state.valid.mask
										)
								if self.sensor["FLC25_EM"]["obj_type"]:
										object_type = np.empty(em_track.dx.shape, dtype = "int")
										object_type[:] = 6
										car = np.where(em_track.obj_type.car, 1, 0)
										truck = np.where(em_track.obj_type.truck, 2, 0)
										motorcycle = np.where(em_track.obj_type.motorcycle, 3, 0)
										pedestrian = np.where(em_track.obj_type.pedestrian, 4, 0)
										bicycle = np.where(em_track.obj_type.bicycle, 5, 0)
										unknown = np.where(em_track.obj_type.unknown, 6, 0)
										point = np.where(em_track.obj_type.point, 7, 0)
										wide = np.where(em_track.obj_type.wide, 8, 0)

										object_type[car == 1] = 1
										object_type[truck == 2] = 2
										object_type[motorcycle == 3] = 3
										object_type[pedestrian == 4] = 4
										object_type[bicycle == 5] = 5
										object_type[unknown == 6] = 6
										object_type[point == 7] = 7
										object_type[wide == 8] = 8
										o["object_type"] = object_type
								if self.sensor["FLC25_EM"]["dx"]:
										em_track.dx.data[em_track.dx.mask] = 0
										o["dx"] = em_track.dx.data
								if self.sensor["FLC25_EM"]["dy"]:
										em_track.dy.data[em_track.dy.mask] = 0
										o["dy"] = em_track.dy.data
								if self.sensor["FLC25_EM"]["dx_std"]:
										o["dx_std"] = em_track.dx_std.data
								if self.sensor["FLC25_EM"]["dy_std"]:
										o["dy_std"] = em_track.dy_std.data
								if self.sensor["FLC25_EM"]["ax"]:
										o["ax"] = em_track.ax.data
								if self.sensor["FLC25_EM"]["ay"]:
										o["ay"] = em_track.ay.data
								if self.sensor["FLC25_EM"]["ay_abs"]:
										o["ay_abs"] = em_track.ay_abs.data
								if self.sensor["FLC25_EM"]["ax_abs"]:
										o["ax_abs"] = em_track.ax_abs.data
								if self.sensor["FLC25_EM"]["vx"]:
										o["vx"] = em_track.vx.data
								if self.sensor["FLC25_EM"]["vy"]:
										o["vy"] = em_track.vy.data
								if self.sensor["FLC25_EM"]["vx_abs"]:
										o["vx_abs"] = em_track.vx_abs.data
								if self.sensor["FLC25_EM"]["vy_abs"]:
										o["vy_abs"] = em_track.vy_abs.data
								if self.sensor["FLC25_EM"]["vx_abs_std"]:
										o["vx_abs_std"] = em_track.vx_abs_std.data
								if self.sensor["FLC25_EM"]["vy_abs_std"]:
										o["vy_abs_std"] = em_track.vy_abs_std.data
								if self.sensor["FLC25_EM"]["dz"]:
										o["dz"] = em_track.dz.data
								if self.sensor["FLC25_EM"]["dz_std"]:
										o["dz_std"] = em_track.dz_std.data
								if self.sensor["FLC25_EM"]["yaw"]:
										o["yaw"] = em_track.yaw.data
								if self.sensor["FLC25_EM"]["yaw_std"]:
										o["yaw_std"] = em_track.yaw_std.data
								if self.sensor["FLC25_EM"]["mov_state"]:
										o["mov_state"] = em_track.mov_state.join()
								if self.sensor["FLC25_EM"]["video_conf"]:
										o["video_conf"] = em_track.video_conf.data
								if self.sensor["FLC25_EM"]["height"]:
										o["height"] = em_track.height.data
								if self.sensor["FLC25_EM"]["width"]:
										o["width"] = em_track.width.data
								if self.sensor["FLC25_EM"]["length"]:
										o["length"] = em_track.width.data
								if self.sensor["FLC25_CEM_TPF"]["range"]:
										o["range"] = em_track.range.data
								if self.sensor["FLC25_EM"]["angle"]:
										o["angle"] = em_track.angle.data
								if self.sensor["FLC25_EM"]["lane"]:
										o["lane"] = em_track.lane.join()

								objectbuffer_key = "em_objectbuffer" + str(id)
								em_objectbufferlist[objectbuffer_key] = o
						final_buffer_key2 = "flc25_em_objects"
						final_buffer[final_buffer_key2] = em_objectbufferlist
				# </editor-fold>

				# <editor-fold desc="CAN Objects">
				if np.any(np.array(self.sensor["FLC25_CAN"].values()) == True):
						can_objectbufferlist = {}
						for id, can_track in can_tracks.iteritems():
								o = {}
								if self.sensor["FLC25_CAN"]["time"]:
										o["time"] = can_tracks.time
								if self.sensor["FLC25_CAN"]["id"]:
										o["id"] = np.where(can_track.dx.mask, INVALID_ID, id)
								if self.sensor["FLC25_CAN"]["tr_state"]:
										o["valid"] = (
														can_track.tr_state.valid.data & ~can_track.tr_state.valid.mask
										)
								if self.sensor["FLC25_CAN"]["obj_type"]:
										object_type = np.empty(can_track.dx.shape, dtype = "int")
										object_type[:] = 6
										car = np.where(can_track.obj_type.car, 1, 0)
										truck = np.where(can_track.obj_type.truck, 2, 0)
										motorcycle = np.where(can_track.obj_type.motorcycle, 3, 0)
										pedestrian = np.where(can_track.obj_type.pedestrian, 4, 0)
										bicycle = np.where(can_track.obj_type.bicycle, 5, 0)
										unknown = np.where(can_track.obj_type.unknown, 6, 0)
										point = np.where(can_track.obj_type.point, 7, 0)
										wide = np.where(can_track.obj_type.wide, 8, 0)

										object_type[car == 1] = 1
										object_type[truck == 2] = 2
										object_type[motorcycle == 3] = 3
										object_type[pedestrian == 4] = 4
										object_type[bicycle == 5] = 5
										object_type[unknown == 6] = 6
										object_type[point == 7] = 7
										object_type[wide == 8] = 8
										o["object_type"] = object_type
								if self.sensor["FLC25_CAN"]["dx"]:
										can_track.dx.data[can_track.dx.mask] = 0
										o["dx"] = can_track.dx.data
								if self.sensor["FLC25_CAN"]["dy"]:
										can_track.dy.data[can_track.dy.mask] = 0
										o["dy"] = can_track.dy.data
								if self.sensor["FLC25_CAN"]["ax"]:
										o["ax"] = can_track.ax.data
								if self.sensor["FLC25_CAN"]["ay"]:
										o["ay"] = can_track.ay.data
								if self.sensor["FLC25_CAN"]["vx"]:
										o["vx"] = can_track.vx.data
								if self.sensor["FLC25_CAN"]["vy"]:
										o["vy"] = can_track.vy.data
								if self.sensor["FLC25_CAN"]["width"]:
										o["width"] = can_track.width.data
								if self.sensor["FLC25_CAN"]["range"]:
										o["range"] = can_track.range.data
								if self.sensor["FLC25_CAN"]["angle"]:
										o["angle"] = can_track.angle.data
								if self.sensor["FLC25_CAN"]["mov_state"]:
										o["mov_state"] = can_track.mov_state.join()
								if self.sensor["FLC25_CAN"]["video_conf"]:
										o["video_conf"] = can_track.video_conf.data
								if self.sensor["FLC25_CAN"]["measured_by"]:
										o["measured_by"] = can_track.measured_by.join()
								if self.sensor["FLC25_CAN"]["can_tracking_state"]:
										o["can_tracking_state"] = can_track.tracking_state.data
								if self.sensor["FLC25_CAN"]["cut_in_cut_out"]:
										o["cut_in_cut_out"] = can_track.cut_in_cut_out.data

								objectbuffer_key = "can_objectbuffer" + str(id)
								can_objectbufferlist[objectbuffer_key] = o
						final_buffer_key3 = "flc25_can_objects"
						final_buffer[final_buffer_key3] = can_objectbufferlist
				# </editor-fold>

				# <editor-fold desc="ARS_FCU Objects">
				if np.any(np.array(self.sensor["FLC25_ARS_FCU"].values()) == True):
						ars_fcu_objectbufferlist = {}
						for id, ars_fcu_track in ars_fcu_tracks.iteritems():
								o = {}
								if self.sensor["FLC25_ARS_FCU"]["time"]:
										o["time"] = ars_fcu_tracks.time
								if self.sensor["FLC25_ARS_FCU"]["id"]:
										o["id"] = np.where(ars_fcu_track.dx.mask, INVALID_ID, id)
								if self.sensor["FLC25_ARS_FCU"]["tr_state"]:
										o["valid"] = (
														ars_fcu_track.tr_state.valid.data
														& ~ars_fcu_track.tr_state.valid.mask
										)
								if self.sensor["FLC25_ARS_FCU"]["obj_type"]:
										object_type = np.empty(ars_fcu_track.dx.shape, dtype = "int")
										object_type[:] = 6
										car = np.where(ars_fcu_track.obj_type.car, 1, 0)
										truck = np.where(ars_fcu_track.obj_type.truck, 2, 0)
										motorcycle = np.where(ars_fcu_track.obj_type.motorcycle, 3, 0)
										pedestrian = np.where(ars_fcu_track.obj_type.pedestrian, 4, 0)
										bicycle = np.where(ars_fcu_track.obj_type.bicycle, 5, 0)
										unknown = np.where(ars_fcu_track.obj_type.unknown, 6, 0)
										point = np.where(ars_fcu_track.obj_type.point, 7, 0)
										wide = np.where(ars_fcu_track.obj_type.wide, 8, 0)

										object_type[car == 1] = 1
										object_type[truck == 2] = 2
										object_type[motorcycle == 3] = 3
										object_type[pedestrian == 4] = 6
										object_type[bicycle == 5] = 5
										object_type[unknown == 6] = 6
										object_type[point == 7] = 7
										object_type[wide == 8] = 8
										o["object_type"] = object_type
								if self.sensor["FLC25_ARS_FCU"]["dx"]:
										ars_fcu_track.dx.data[ars_fcu_track.dx.mask] = 0
										o["dx"] = ars_fcu_track.dx.data
								if self.sensor["FLC25_ARS_FCU"]["dy"]:
										ars_fcu_track.dy.data[ars_fcu_track.dy.mask] = 0
										o["dy"] = ars_fcu_track.dy.data
								if self.sensor["FLC25_ARS_FCU"]["dx_std"]:
										o["dx_std"] = ars_fcu_track.dx_std.data
								if self.sensor["FLC25_ARS_FCU"]["dy_std"]:
										o["dy_std"] = ars_fcu_track.dy_std.data
								if self.sensor["FLC25_ARS_FCU"]["ax_abs"]:
										o["ax_abs"] = ars_fcu_track.ax_abs.data
								if self.sensor["FLC25_ARS_FCU"]["ay_abs"]:
										o["ay_abs"] = ars_fcu_track.ay_abs.data
								if self.sensor["FLC25_ARS_FCU"]["ax"]:
										o["ax"] = ars_fcu_track.ax.data
								if self.sensor["FLC25_ARS_FCU"]["ay"]:
										o["ay"] = ars_fcu_track.ay.data
								if self.sensor["FLC25_ARS_FCU"]["angle"]:
										o["angle"] = ars_fcu_track.angle.data
								if self.sensor["FLC25_ARS_FCU"]["range"]:
										o["range"] = ars_fcu_track.range.data
								if self.sensor["FLC25_ARS_FCU"]["width"]:
										o["width"] = ars_fcu_track.width.data
								if self.sensor["FLC25_ARS_FCU"]["length"]:
										o["length"] = ars_fcu_track.length.data
								if self.sensor["FLC25_ARS_FCU"]["vx_abs"]:
										o["vx_abs"] = ars_fcu_track.vx_abs.data
								if self.sensor["FLC25_ARS_FCU"]["vy_abs"]:
										o["vy_abs"] = ars_fcu_track.vy_abs.data
								if self.sensor["FLC25_ARS_FCU"]["vx"]:
										o["vx"] = ars_fcu_track.vx.data
								if self.sensor["FLC25_ARS_FCU"]["vy"]:
										o["vy"] = ars_fcu_track.vy.data
								if self.sensor["FLC25_ARS_FCU"]["lane"]:
										o["lane"] = ars_fcu_track.lane.join()
								if self.sensor["FLC25_ARS_FCU"]["mov_state"]:
										o["mov_state"] = ars_fcu_track.mov_state.join()
								if self.sensor["FLC25_ARS_FCU"]["video_conf"]:
										o["video_conf"] = ars_fcu_track.video_conf.data
								if self.sensor["FLC25_ARS_FCU"]["acc_obj_quality"]:
										o["acc_obj_quality"] = ars_fcu_track.acc_obj_quality.data
								if self.sensor["FLC25_ARS_FCU"]["aeb_obj_quality"]:
										o["aeb_obj_quality"] = ars_fcu_track.aeb_obj_quality.data

								objectbuffer_key = "objectbuffer" + str(id)
								ars_fcu_objectbufferlist[objectbuffer_key] = o
						final_buffer_key4 = "flc25_ars_fcu_objects"
						final_buffer[final_buffer_key4] = ars_fcu_objectbufferlist
				# </editor-fold>

				# <editor-fold desc="EGO Object">
				if np.any(np.array(self.sensor["EGO_VEHICLE"].values()) == True):
						ego_objectbufferlist = {}
						o = {}
						if self.sensor["EGO_VEHICLE"]["time"]:
								o["time"] = ego_orig.time
						if self.sensor["EGO_VEHICLE"]["ax"]:
								o["ax"] = ego_orig.ax
						if self.sensor["EGO_VEHICLE"]["vx"]:
								o["vx"] = ego_orig.vx
						if self.sensor["EGO_VEHICLE"]["yaw_rate"]:
								o["yaw_rate"] = ego_orig.yaw_rate
						if self.sensor["EGO_VEHICLE"]["dir_ind"]:
								o["dir_ind"] = ego_orig.dir_ind
						if self.sensor["EGO_VEHICLE"]["steer_angle"]:
								o["steer_angle"] = ego_orig.steer_angle
						if self.sensor["EGO_VEHICLE"]["brkped_pos"]:
								o["brkped_pos"] = ego_orig.brkped_pos
						if self.sensor["EGO_VEHICLE"]["accped_pos"]:
								o["accped_pos"] = ego_orig.accped_pos

						objectbuffer_key = "ego_objectbuffer"
						ego_objectbufferlist[objectbuffer_key] = o
						final_buffer_key5 = "ego_objects"
						final_buffer[final_buffer_key5] = ego_objectbufferlist

				# </editor-fold>

				# <editor-fold desc="CONTI TSR">
				if np.any(np.array(self.sensor["CONTI_TSR"].values()) == True):
						conti_tsr_objectbufferlist = {}
						o = {}
						objects = []
						hasImageData = True

						# Prepare data for TSR sign images, sign class, value, active_status etc.
						config_file = os.path.join(CONFIG_DIRECTORY, "SR_signs.txt")
						# Identifier_to_icon_mapping is  mapping dictionary for images with respect to defined image identifier
						# Traffic sign data is used in table navigator
						# traffic_sign_data_for_table, identifier_to_icon_mapping = parse_icon_data(config_file = config_file,
						#                                                                           seperator = "=")
						tsr_time, tracks = conti_tsr
						for id, track in enumerate(tracks):
								if np.all(track["valid"] == False):
										continue
								o = dict()
								# o["id"] = np.where(track.universal_id.mask, -1, id)
								if self.sensor["CONTI_TSR"]["valid"]:
										o["valid"] = track["valid"]
								if self.sensor["CONTI_TSR"]["traffic_sign_id"]:
										sign_id = track["traffic_sign_id"]
										o["traffic_sign_id"] = sign_id.data

								if self.sensor["CONTI_TSR"]["suppl_sign_ids"]:
										# supplementary_sign_details[id][0]["esupplclassid"].data.astype(int)
										# suppl_sign_ids = {}
										# if id in available_suppl_ids:
										#     for _id, suppl_sign_id in conti_tsr_suppl[id].iteritems():
										#         suppl_sign_ids[_id] = suppl_sign_id["esupplclassid"].data.astype(int)
										suppl_sign_ids = []
										# suppl_uids = []
										for _id, suppl_sign_id in conti_tsr_suppl[id].iteritems():
												suppl_sign_ids.append(suppl_sign_id["esupplclassid"].data.astype(int))
										# suppl_uid = track["universal_id"].data.copy()
										# # suppl_uid = np.array(map(lambda uid: str(uid).replace(str(uid), str(uid) + "-SUPPL"),
										# suppl_uid))
										# suppl_uid[suppl_sign_id["esupplclassid"].mask] = 0
										# suppl_uids.append(suppl_uid)

										# o["suppl_sign_ids"] = np.vstack(tuple(suppl_sign_ids))
										o["suppl_sign_ids"] = np.dstack(tuple(suppl_sign_ids))[0]
										suppl_uid = track["universal_id"].data.copy()
										suppl_uid[conti_tsr_suppl[id][0]["esupplclassid"].mask] = 0
										o["uid_suppl"] = suppl_uid
								# o["uid_suppl"] = np.dstack(tuple(suppl_uids))[0]

								if self.sensor["CONTI_TSR"]["uid"]:
										uid = track["universal_id"]
										o["uid"] = uid.data

								# np.ma.array(map(lambda uid: str(uid).replace(str(uid), str(uid) + "-SUPPL"), o["universal_id"]),
								# mask=mask)
								if self.sensor["CONTI_TSR"]["status"]:
										status = track["sign_visibility_status"]
										o["status"] = status

								if self.sensor["CONTI_TSR"]["time"]:
										o["time"] = tsr_time

								objectbuffer_key = "conti_tsr_objectbuffer" + str(id)
								conti_tsr_objectbufferlist[objectbuffer_key] = o

						final_buffer_key5 = "conti_tsr_objects"
						final_buffer[final_buffer_key5] = conti_tsr_objectbufferlist

				# </editor-fold>

				# <editor-fold desc="POSTMARKER_TOOL">
				if np.any(np.array(self.sensor["POSTMARKER_TOOL"].values()) == True):
						postmarker_objectbufferlist = {}
						for id, postmarker_track in enumerate(postmarker_tsr):
								o = {}
								if self.sensor["POSTMARKER_TOOL"]["time"]:
										o["time"] = common_time_tsr
								if self.sensor["POSTMARKER_TOOL"]["sign_class_id"]:
										o["sign_class_id"] = postmarker_track["sign_class_id"].data
								# if self.sensor['POSTMARKER_TOOL']['sign_class']:
								# 		o["sign_class"] = postmarker_tsr['sign_class']
								if self.sensor["POSTMARKER_TOOL"]["valid"]:
										o["valid"] = postmarker_track["valid"].data

								if self.sensor["POSTMARKER_TOOL"]["quantity"]:
										o["quantity"] = postmarker_track["sign_quantity"].data

								objectbuffer_key = "postmarker_objectbuffer" + str(id)
								postmarker_objectbufferlist[objectbuffer_key] = o
						final_buffer_key5 = "postmarker_objects"
						final_buffer[final_buffer_key5] = postmarker_objectbufferlist
				# </editor-fold>

				# <editor-fold desc="POSTMARKER_TOOL">
				if np.any(np.array(self.sensor["TSR_DETECTION_COMPARISION"].values()) == True):
						postmarker_objectbufferlist = {}
						o = {}
						if self.sensor["TSR_DETECTION_COMPARISION"]["time"]:
								o["time"] = common_time_tsr
						if self.sensor["TSR_DETECTION_COMPARISION"]["conti_detection"]:
								o["conti_detection"] = value_is_conti_sign_detected
						# if self.sensor['POSTMARKER_TOOL']['sign_class']:
						# 		o["sign_class"] = postmarker_tsr['sign_class']
						if self.sensor["TSR_DETECTION_COMPARISION"]["postmarker_detection"]:
								o["postmarker_detection"] = postmarker_tsr[0]["is_sign_detected"].data

						objectbuffer_key = "detection_compare_objectbuffer"
						postmarker_objectbufferlist[objectbuffer_key] = o
						final_buffer_key5 = "detection_compare_objects"
						final_buffer[final_buffer_key5] = postmarker_objectbufferlist
				# </editor-fold>

				# <editor-fold desc="GPS ADMA OBJECT">
				if np.any(np.array(self.sensor["GPS"].values()) == True):
						postmarker_objectbufferlist = {}
						o = {}
						if self.sensor["GPS"]["time"]:
								o["time"] = gps_adma_object["time"]
						if self.sensor["GPS"]["dx"]:
								o["dx"] = gps_adma_object["dx"]
						if self.sensor["GPS"]["dy"]:
								o["dy"] = gps_adma_object["dy"]

						objectbuffer_key = "gps_objectbuffer"
						postmarker_objectbufferlist[objectbuffer_key] = o
						final_buffer_key5 = "gps_objects"
						final_buffer[final_buffer_key5] = postmarker_objectbufferlist
				# </editor-fold>

				done = time.time()
				elapsed = done - start
				logger.info(
								"FLC25 object retrieval is completed in " + str(elapsed) + " seconds"
				)

				return final_buffer, lane_object


def convert_file(matpath, final_objects, lanes):
		file_path, _ = os.path.splitext(matpath)
		matpath = file_path + "_export.mat"
		df_dict = dict(final_objects.items() + lanes.items())
		scipy.io.savemat(matpath, mdict = df_dict, oned_as = "column", long_field_names = True)
		return


def export(matfile):
		from config.Config import init_dataeval

		meas_path = matfile
		config, manager, manager_modules = init_dataeval(["-m", meas_path])
		objectbufferlist, lanes = manager_modules.calc(
						"fillFLC25_RESIM_EXPORT@aebs.fill", manager
		)
		# outputpath = os.path.join(os.path.dirname(matfile), "dspace_asm_export.csv")
		# outputpath = r"C:\\KBApps\\Resimulation\\resim_mat_files\\resim3_mat.csv"
		convert_file(meas_path, objectbufferlist, lanes)
		return


if __name__ == "__main__":
		from config.Config import init_dataeval

		meas_path = (
				r"C:\KBData\__PythonToolchain\Meas\TSR\HMC-QZ-STR__2021-02-15_16-51-57.h5"
		)
		config, manager, manager_modules = init_dataeval(["-m", meas_path])
		conti, objects = manager_modules.calc("fillFLC25_RESIM_EXPORT@aebs.fill", manager)
		print(objects)
