# -*- dataeval: method -*-
# -*- coding: utf-8 -*-
"""
:Name:
	view_flc25_sw_version.py

:Type:
	View script

:Visualization Type:
	Plot

:Full Path:
	dataevalaebs/src/mfc525eval/version/view_flc25_sw_version.py

:Sensors:
	FLC25

:Short Description:
	Knorr version label is specific number given to software version for quick identification
	Camera alignment is important when functions are working. It should be in the operational state. It has following enumeration
	0:NA, 1:Init, 2:Operational, 0xE:Temporarily not aligned, 0xF:Permanently not aligned
	Status of the camera is important while analysis, It has following enumeration
	0:NA, 1:Init, 2:Operational, 0x3:Degraded, 0xE:Blocked, 0xF:Error

:Large Description:
	Usage:
		- Shows Camera software version information
		- Shows Camera state and alignment

:Dependencies:
	- calc_common_time-flc25@aebs.fill

:Output Data Image/s:
	.. image:: ../images/view_flc25_sw_version_1.png

.. note::
	For source code click on [source] tag beside functions
"""
import interface
import datavis
import numpy as np

def_param = interface.NullParam

sgs = [
		{
				"Knorr_version_label": ("GeneralInfo", "Knorr_version_label"),
				"Camera_Alignment"   : ("GeneralInfo", "Camera_Alignment"),
				"Camera_State"       : ("GeneralInfo", "Camera_State"),
		},
		{
				"Knorr_version_label": ("GeneralInfo_A0_sA0", "GeneralInfo_KBVersLabel_A0"),
				"Camera_Alignment"   : ("GeneralInfo_A0_sA0", "GeneralInfo_CamAlignment_A0"),
				"Camera_State"       : ("GeneralInfo_A0_sA0", "GeneralInfo_CameraState_A0"),
		},
]


class View(interface.iView):
		dep = 'calc_common_time-flc25@aebs.fill',

		def check(self):
				modules = self.get_modules()
				commonTime = modules.fill(self.dep[0])
				group = self.source.selectSignalGroupOrEmpty(sgs)
				return group, commonTime

		def fill(self, group, commonTime):
				return group, commonTime

		def view(self, param, group, commonTime):
				client00 = datavis.cListNavigator(title = "FLC25 Camera Version")
				self.sync.addClient(client00)
				time00, value00 = group.get_signal("Knorr_version_label")
				if value00.size == 0:
						invalid_track = np.repeat("NA", len(commonTime))
						client00.addsignal("Missing Signal: Knorr version label", (commonTime, invalid_track), groupname = "Default", bg = '#FFFFE0')
				else:
						value00 = value00.astype(int)
						client00.addsignal("Knorr version label", (time00, value00), groupname = "Default", bg = '#FFFFE0')

				time01, value01 = group.get_signal("Camera_Alignment")
				if value01.size == 0:
						invalid_track = np.repeat("NA", len(commonTime))
						client00.addsignal("Missing Signal: Camera_Alignment", (commonTime, invalid_track), groupname = "Default", bg = '#FFFFE0')
				else:
						camera_alignment_mapped = np.empty(value01.shape, dtype = 'object')
						camera_alignment_mapped[:] = 'U'

						camera_alignment_mapped[value01 == 0] = 'NA'
						camera_alignment_mapped[value01 == 1] = 'Init'
						camera_alignment_mapped[value01 == 2] = 'Operational'
						camera_alignment_mapped[value01 == 0xE] = 'Temporarily not aligned'
						camera_alignment_mapped[value01 == 0xF] = 'Permanently not aligned'

						client00.addsignal("Camera Alignment", (time01, camera_alignment_mapped), groupname = "Default",
															 bg = '#FFFFE0')
				# client00.addsignal("Camera_Alignment (enum)", (time01, value01), groupname = "Default")

				time02, value02 = group.get_signal("Camera_State")
				if value01.size == 0:
						invalid_track = np.repeat("NA", len(commonTime))
						client00.addsignal("Missing signal: Camera_State", (commonTime, invalid_track), groupname = "Default", bg = '#FFFFE0')
				else:
						camera_state_mapped = np.empty(value02.shape, dtype = 'object')
						camera_state_mapped[:] = 'U'

						camera_state_mapped[value02 == 0] = 'NA'
						camera_state_mapped[value02 == 1] = 'Init'
						camera_state_mapped[value02 == 2] = 'Operational'
						camera_state_mapped[value02 == 0x3] = 'Degraded'
						camera_state_mapped[value02 == 0xE] = 'Blocked'
						camera_state_mapped[value02 == 0xF] = 'Error'
						client00.addsignal("Camera State", (time02, camera_state_mapped), groupname = "Default", bg = '#FFFFE0')
				# client00.addsignal("Camera_State (enum)", (time02, value02), groupname = "Default")

				return
