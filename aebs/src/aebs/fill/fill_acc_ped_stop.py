# -*- dataeval: init -*-

from interface import iCalc
import numpy as np
import os
# from fillFLC25_TSR import parse_icon_data
from measparser.PostmarkerJSONParser import parse_icon_data

TRACK_MESSAGE_NUM = 40

signal_template = (
		("EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObject[%d]_General_uiID"),
		("EMCustomerObjData", "ARS4xx_Device_DataProcCycle_EMCustomerObjData_CustObjects[%d]_uiPedHighConfidence"),
		("EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObject[%d]_Qualifiers_uiEbaObjQuality"),

)
signal_templateh5 = (
		("ARS4xx Device.DataProcCycle.EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObject%d_General_uiID"),
		("ARS4xx Device.DataProcCycle.EMCustomerObjData", "ARS4xx_Device_DataProcCycle_EMCustomerObjData_CustObjects%d_uiPedHighConfidence"),
		("ARS4xx Device.DataProcCycle.EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObject%d_Qualifiers_uiEbaObjQuality"),

)

def createMessageGroups(MESSAGE_NUM, signalTemplates):
		messageGroups = []
		for m in xrange(MESSAGE_NUM):
				messageGroup = {}
				SignalDict = []
				for signalTemplate in signalTemplates:
						fullName = signalTemplate[1] % m
						shortName = signalTemplate[1].split('_')[-1]
						messageGroup[shortName] = (signalTemplate[0], fullName)
						SignalDict.append(messageGroup)
				messageGroup2={}
				for signalTemplate in signal_templateh5:
						fullName = signalTemplate[1] % m
						shortName = signalTemplate[1].split('_')[-1]
						messageGroup[shortName] = (signalTemplate[0], fullName)
						SignalDict.append(messageGroup2)
				messageGroups.append(SignalDict)
		return messageGroups


messageGroups = createMessageGroups(TRACK_MESSAGE_NUM, signal_template)


class cFill(iCalc):
		dep = {
				'common_time': 'calc_common_time-flr25'
		}

		def check(self):
				commonTime = self.modules.fill(self.dep["common_time"])

				sgs = [
						{
								"vehicle_speed": ("VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity"),
								"obj_speed": ("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
															"ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_ped_stop_object_vx_rel"),
								"ego_long_state": ("Rte_SWC_APS_RPort_im_aps_vehicle_DEP_im_aps_vehicle_Buf",
																	 "ARS4xx_Device_SW_Every10ms_Rte_SWC_APS_RPort_im_aps_vehicle_DEP_im_aps_vehicle_Buf_ego_longitudinal_state"),
								"aps_system_state": ("Rte_SWC_OutputManager_RPort_aps_om_hmi_DEP_aps_om_hmi_Buf",
																		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_aps_om_hmi_DEP_aps_om_hmi_Buf_aps_system_state"),
								"acc_active": ("Rte_SWC_APS_RPort_im_aps_function_info_DEP_im_aps_function_info_Buf",
															 "ARS4xx_Device_SW_Every10ms_Rte_SWC_APS_RPort_im_aps_function_info_DEP_im_aps_function_info_Buf_acc_active"),
								"aps_object_id": ("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
																	"ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_ped_stop_object_id"),

						},
						{
								"vehicle_speed"   : ("ARS4xx Device.AlgoVehCycle.VehDyn","ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity"),

								"obj_speed"       : ("ARS4xx Device.SW_Every10ms.Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_ped_stop_object_vx_rel"),

								"ego_long_state"  : ("ARS4xx Device.SW_Every10ms.Rte_SWC_APS_RPort_im_aps_vehicle_DEP_im_aps_vehicle_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_APS_RPort_im_aps_vehicle_DEP_im_aps_vehicle_Buf_ego_longitudinal_state"),

								"aps_system_state": ("ARS4xx Device.SW_Every10ms.Rte_SWC_OutputManager_RPort_aps_om_hmi_DEP_aps_om_hmi_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_aps_om_hmi_DEP_aps_om_hmi_Buf_aps_system_state"),

								"acc_active"      : ("ARS4xx Device.SW_Every10ms.Rte_SWC_APS_RPort_im_aps_function_info_DEP_im_aps_function_info_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_APS_RPort_im_aps_function_info_DEP_im_aps_function_info_Buf_acc_active"),

								"aps_object_id"   : ("ARS4xx Device.SW_Every10ms.Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_ped_stop_object_id"),


						},
				]
				sgs_1 = [{"acc_pedal_pos": ("EEC2_00_s00", "EEC2_AccPedalPos1_00"), },
								 {"acc_pedal_pos": ("EEC2_00_s00", "EEC2_AccelPedalPos1_00"), },
								 {"acc_pedal_pos": ("EEC2_00", "EEC2_AccPedalPos1_00"), },
								 {"acc_pedal_pos": ("EEC2_00", "EEC2_AccelPedalPos1_00"), },
								 {"acc_pedal_pos":("EEC2_00", "EEC2_AccPedalPos1_00_s00"),}

				]

				# select signals
				group = self.source.selectLazySignalGroup(sgs)
				group_1 = self.source.selectLazySignalGroup(sgs_1)

				aobjects_groups = []
				for sg in messageGroups:
						aobjects_groups.append(self.source.selectSignalGroup(sg))

				# give warning for not available signals
				signals = {}
				for alias in sgs[0].keys():
						if alias not in group:
								self.logger.warning("Signal for '%s' not available" % alias)
								continue

						# for signal_alias in sgs[0].keys():
						signal_data = {}
						_, value, unit = group.get_signal_with_unit(alias, ScaleTime=commonTime)
						signal_data["value"] = value
						signal_data["unit"] = unit
						signals[alias] = signal_data

				for alias in sgs_1[0].keys():
						if alias not in group_1:
								self.logger.warning("Signal for '%s' not available" % alias)
								continue

								# for signal_alias in sgs[0].keys():
						signal_data = {}
						_, value, unit = group_1.get_signal_with_unit(alias, ScaleTime=commonTime)
						signal_data["value"] = value
						signal_data["unit"] = unit
						signals[alias] = signal_data
				return commonTime, signals, aobjects_groups

		def fill(self, commonTime, signals, aobjects_groups):
				system_state = signals["aps_system_state"]["value"]
				aps_active_position = np.argmax(system_state==6)
				invalid_mask = (signals["aps_object_id"]["value"] == 255) | (np.isnan(signals["aps_object_id"]["value"]))

				signals = self.add_acc_ped_stop_objs(signals, aobjects_groups, commonTime, aps_active_position)

				return commonTime, signals


		def add_acc_ped_stop_objs(self, signals, aobjects_groups, common_time, aps_active_position):
				aps_object_ids = signals["aps_object_id"]["value"]
				id_found = False
				for _id, group in enumerate(aobjects_groups):
						_, object_id = group.get_signal("uiID", ScaleTime=common_time)
						if object_id[aps_active_position+1] == aps_object_ids[aps_active_position+1]:
								id_found = True
								_, uiPedHighConfidence, unit00 = group.get_signal_with_unit("uiPedHighConfidence",
																																						ScaleTime=common_time)
								signals["ped_confidence"] = {}
								signals["ped_confidence"]["value"] = uiPedHighConfidence
								signals["ped_confidence"]["unit"] = unit00
								_, uiEbaObjQuality, unit01 = group.get_signal_with_unit("uiEbaObjQuality", ScaleTime=common_time)
								signals["eba_quality"] = {}
								signals["eba_quality"]["value"] = uiEbaObjQuality
								signals["eba_quality"]["unit"] = unit01
				if not id_found:
						print("Critical warning: ACC ped stop Object not found in aobject list")

				return signals


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6474\shared-drive\transfer\shubham\measurements\ARS4xx_new_dcnvt_h5_format\New folder\mi5id787__2021-06-09_06-40-32.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		tracks = manager_modules.calc('fill_acc_ped_stop@aebs.fill', manager)
		print(tracks)
