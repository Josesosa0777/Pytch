# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import sys

import interface
import numpy as np
import scipy.signal
from measparser.signalgroup import SignalGroupError
from primitives.egomotion import EgoMotion

sgs = [{
		"dx": ("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf", "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_ped_stop_object_dy"),
		"dy": ("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf", "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_ped_stop_object_dx"),
		"state": ("Rte_SWC_OutputManager_RPort_aps_om_hmi_DEP_aps_om_hmi_Buf", "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_aps_om_hmi_DEP_aps_om_hmi_Buf_aps_system_state"),
		"vx_rel": ("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_vx_rel"),
		"id": ("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_ped_stop_object_id"),


},
		{
				"dx"    : ("ARS4xx Device.SW_Every10ms.Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_ped_stop_object_dy"),

				"dy"    : ("ARS4xx Device.SW_Every10ms.Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_ped_stop_object_dx"),

				"state" : ("ARS4xx Device.SW_Every10ms.Rte_SWC_OutputManager_RPort_aps_om_hmi_DEP_aps_om_hmi_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_aps_om_hmi_DEP_aps_om_hmi_Buf_aps_system_state"),

				"vx_rel": ("ARS4xx Device.SW_Every10ms.Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_vx_rel"),

				"id"    : ("ARS4xx Device.SW_Every10ms.Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_ped_stop_object_id"),

		}
]


class Calc(interface.iCalc):
		dep = {
				'common_time': 'calc_common_time-flr25'
		}

		def check(self):
				commonTime = self.modules.fill(self.dep["common_time"])
				group = self.source.selectSignalGroup(sgs)
				return commonTime, group

		def fill(self, commonTime, group):
				track = {}

				_, object_id = group.get_signal('id', ScaleTime=commonTime)
				_, dx = group.get_signal('dx', ScaleTime=commonTime)
				_, dy = group.get_signal('dy', ScaleTime=commonTime)
				_, state = group.get_signal('state', ScaleTime=commonTime)
				_, vx_rel = group.get_signal('vx_rel', ScaleTime=commonTime)
				invalid_mask = (object_id == 255) | (np.isnan(object_id))
				track["time"] = commonTime
				track["dx"] = np.ma.array(dx, mask=invalid_mask)
				track["dy"] = np.ma.array(dy, mask=invalid_mask)
				track["vx_rel"] = np.ma.array(vx_rel, mask=invalid_mask)

				return track



if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6474\shared-drive\transfer\shubham\measurements\ARS4xx_new_dcnvt_h5_format\New folder\mi5id787__2021-06-09_06-40-32.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		flr25_common_time = manager_modules.calc('calc_radar_egomotion-flr25@aebs.fill', manager)
		print flr25_common_time
