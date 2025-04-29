# -*- dataeval: init -*-
import numpy
import logging
from interface import iCalc

logger = logging.getLogger('calc_flc25_sw_version')

class Calc(iCalc):

		def check(self):
				sgn_group = [
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
						{
							"Knorr_version_label": ("GeneralInfo_A0", "GeneralInfo_KBVersLabel_A0_sA0"),
							"Camera_Alignment": ("GeneralInfo_A0", "GeneralInfo_CamAlignment_A0_sA0"),
							"Camera_State": ("GeneralInfo_A0", "GeneralInfo_CameraState_A0_sA0"),
						},
						{
							"Knorr_version_label": ("GeneralInfo_A0", "GeneralInfo_KBVersLabel_A0"),
							"Camera_Alignment": ("GeneralInfo_A0", "GeneralInfo_CamAlignment_A0"),
							"Camera_State": ("GeneralInfo_A0", "GeneralInfo_CameraState_A0"),
						},
				]
				source = self.get_source()
				try:
						group = source.selectSignalGroup(sgn_group)
						return group
				except:
						logger.error("Missing Knorr_version_label signal")

		def fill(self, group):
				time00, swVersion = group.get_signal("Knorr_version_label")

				time01, cameraAlign = group.get_signal("Camera_Alignment")
				camera_alignment_mapped = numpy.empty(cameraAlign.shape, dtype = 'object')
				camera_alignment_mapped[:] = 'U'
				camera_alignment_mapped[cameraAlign == 0] = 'NA'
				camera_alignment_mapped[cameraAlign == 1] = 'Init'
				camera_alignment_mapped[cameraAlign == 2] = 'Operational'
				camera_alignment_mapped[cameraAlign == 0xE] = 'Temporarily not aligned'
				camera_alignment_mapped[cameraAlign == 0xF] = 'Permanently not aligned'

				time02, cameraStatus = group.get_signal("Camera_State")
				camera_state_mapped = numpy.empty(cameraStatus.shape, dtype = 'object')
				camera_state_mapped[:] = 'U'
				camera_state_mapped[cameraStatus == 0] = 'NA'
				camera_state_mapped[cameraStatus == 1] = 'Init'
				camera_state_mapped[cameraStatus == 2] = 'Operational'
				camera_state_mapped[cameraStatus == 0x3] = 'Degraded'
				camera_state_mapped[cameraStatus == 0xE] = 'Blocked'
				camera_state_mapped[cameraStatus == 0xF] = 'Error'

				return swVersion, camera_alignment_mapped, camera_state_mapped


if __name__ == "__main__":
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\__PythonToolchain\Meas\TSR\2021-07-22\mi5id787__2021-07-22_05-46-55.h5"
		config, manager, manager_modules = init_dataeval(["-m", meas_path])
		tracks = manager_modules.calc("calc_flc25_sw_version@aebs.fill", manager)
		print(tracks)

