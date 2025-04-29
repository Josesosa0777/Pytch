# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
import logging

logger = logging.getLogger("view_acal_sig")
def_param = interface.NullParam

sgs = [
		{
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fPitch": ("pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fPitch"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fRoll": ("pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fRoll"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fYaw": ("pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fYaw"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliOdometer": ("pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliOdometer"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliOdometerToFirstValidCalib": ("pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliOdometerToFirstValidCalib"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliTimer": ("pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliTimer"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fVdyOdometer": ("pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fVdyOdometer"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isHeightCalibrated": ("pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isHeightCalibrated"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isPitchCalibrated": ("pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isPitchCalibrated"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isRollCalibrated": ("pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isRollCalibrated"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isYawCalibrated": ("pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isYawCalibrated"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiPitchQuality": ("pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiPitchQuality"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiRollQuality": ("pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiRollQuality"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiTotalAngleQuality": ("pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiTotalAngleQuality"),
		},
		{
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fPitch"             : (
				"MFC5xx Device.ACAL.pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fPitch"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fRoll"              : (
				"MFC5xx Device.ACAL.pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fRoll"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fYaw"               : (
				"MFC5xx Device.ACAL.pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fYaw"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliOdometer"                       : (
				"MFC5xx Device.ACAL.pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliOdometer"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliOdometerToFirstValidCalib"      : (
				"MFC5xx Device.ACAL.pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliOdometerToFirstValidCalib"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliTimer"                          : (
				"MFC5xx Device.ACAL.pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliTimer"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fVdyOdometer"                        : (
				"MFC5xx Device.ACAL.pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fVdyOdometer"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isHeightCalibrated"                  : (
				"MFC5xx Device.ACAL.pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isHeightCalibrated"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isPitchCalibrated"                   : (
				"MFC5xx Device.ACAL.pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isPitchCalibrated"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isRollCalibrated"                    : (
				"MFC5xx Device.ACAL.pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isRollCalibrated"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isYawCalibrated"                     : (
				"MFC5xx Device.ACAL.pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isYawCalibrated"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiPitchQuality"     : (
				"MFC5xx Device.ACAL.pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiPitchQuality"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiRollQuality"      : (
				"MFC5xx Device.ACAL.pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiRollQuality"),
				"MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiTotalAngleQuality": (
				"MFC5xx Device.ACAL.pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiTotalAngleQuality"),
		},

]


class View(interface.iView):
		def check(self):
				group = self.source.selectSignalGroupOrEmpty(sgs)
				return group

		def fill(self, group):
				return group

		def view(self, param, group):
				client00 = datavis.cListNavigator(title="ACAL Signals")
				self.sync.addClient(client00)
				if 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fPitch' in group:
						time00, value00 = group.get_signal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fPitch")
						client00.addsignal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fPitch", (time00, value00), groupname="Default")
				else:
						logger.warning("Missing signal 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fPitch'")

				if 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fRoll' in group:
						time01, value01 = group.get_signal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fRoll")
						client00.addsignal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fRoll", (time01, value01), groupname="Default")
				else:
						logger.warning("Missing signal 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fRoll'")

				if 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fPitch' in group:
						time02, value02 = group.get_signal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fYaw")
						client00.addsignal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fYaw", (time02, value02), groupname="Default")
				else:
						logger.warning("Missing signal 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fPitch'")

				if 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliOdometer' in group:
						time03, value03 = group.get_signal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliOdometer")
						client00.addsignal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliOdometer", (time03, value03), groupname="Default")
				else:
						logger.warning("Missing signal 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliOdometer'")

				if 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliOdometerToFirstValidCalib' in group:
						time04, value04 = group.get_signal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliOdometerToFirstValidCalib")
						client00.addsignal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliOdometerToFirstValidCalib", (time04, value04), groupname="Default")
				else:
						logger.warning("Missing signal 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliOdometerToFirstValidCalib'")

				if 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliTimer' in group:
						time05, value05 = group.get_signal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliTimer")
						client00.addsignal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliTimer", (time05, value05), groupname="Default")
				else:
						logger.warning("Missing signal 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fCaliTimer'")

				if 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fVdyOdometer' in group:
						time06, value06 = group.get_signal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fVdyOdometer")
						client00.addsignal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fVdyOdometer", (time06, value06), groupname="Default")
				else:
						logger.warning("Missing signal 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_fVdyOdometer'")

				if 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isHeightCalibrated' in group:
						time07, value07 = group.get_signal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isHeightCalibrated")
						client00.addsignal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isHeightCalibrated", (time07, value07), groupname="Default")
				else:
						logger.warning("Missing signal 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isHeightCalibrated'")

				if 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isPitchCalibrated' in group:
						time08, value08 = group.get_signal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isPitchCalibrated")
						client00.addsignal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isPitchCalibrated", (time08, value08), groupname="Default")
				else:
						logger.warning("Missing signal 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isPitchCalibrated'")

				if 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fPitch' in group:
						time09, value09 = group.get_signal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isRollCalibrated")
						client00.addsignal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isRollCalibrated", (time09, value09), groupname="Default")
				else:
						logger.warning("Missing signal 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fPitch'")

				if 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isYawCalibrated' in group:
						time10, value10 = group.get_signal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isYawCalibrated")
						client00.addsignal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isYawCalibrated", (time10, value10), groupname="Default")
				else:
						logger.warning("Missing signal 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_isYawCalibrated'")

				if 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiPitchQuality' in group:
						time11, value11 = group.get_signal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiPitchQuality")
						client00.addsignal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiPitchQuality", (time11, value11), groupname="Default")
				else:
						logger.warning("Missing signal 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiPitchQuality'")

				if 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiRollQuality' in group:
						time12, value12 = group.get_signal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiRollQuality")
						client00.addsignal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiRollQuality", (time12, value12), groupname="Default")
				else:
						logger.warning("Missing signal 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiRollQuality'")

				if 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiTotalAngleQuality' in group:
						time13, value13 = group.get_signal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiTotalAngleQuality")
						client00.addsignal("MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiTotalAngleQuality", (time13, value13), groupname="Default")
				else:
						logger.warning("Missing signal 'MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_uiTotalAngleQuality'")
				return
