# -*- dataeval: init -*-

"""
Interactive video visualizer (VideoNavigator) with object overlay
visualization capabilities.
The selected parameter determines the name of the video file:
* DefParam: assumes the same video basename as the measurement file
* VideoSuffix_m0: assumes an "_m0" suffix at the end of the video basename
* CustomVideo: requires explicit video file name specification
"""
import logging
import os
import re

import datavis
import interface
from evaltools.view_videonav import SignalGroups, getVideoName
from measparser.filenameparser import FileNameParser
from pyutils.string import rreplace

init_params = {
    "DefParam" : dict(video_name=None, video_suffix=""),
    "VideoSuffix_m0" : dict(video_name=None, video_suffix="_m0"),
    "VideoSuffix_m1" : dict(video_name=None, video_suffix="_m1"),
    "VideoSuffix_m2" : dict(video_name=None, video_suffix="_m2"),
    "VideoSuffix_m3" : dict(video_name=None, video_suffix="_m3"),
    "VideoSuffix_m4" : dict(video_name=None, video_suffix="_m4"),
    "CustomVideo" : dict(video_name="C:\\Temp\\foo.avi", video_suffix=""),
}

ENABLE_HACK_FOR_MULTIMEDIA_OFFSET = False

SignalGroups = [
  # multimedia signals
  {'VidTime': ('Multimedia_1', 'Multimedia_1')},
  {'VidTime': ('Multimedia', 'Multimedia_1')},
  {'VidTime': ('Multimedia', 'Multimedia')},
  {'VidTime': ('Multimedia', 'Pro9000')},
  {'VidTime': ('Multimedia', 'LifeCam')},
  {'VidTime': ('TA', 'Multimedia_1')},
  {"VidTime": ("WebCam_Genius_FaceCam_100x", "WebCam_Genius_FaceCam_100x")},
  {'VidTime': ('Webcam', 'Webcam')},
  {"VidTime": ("VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity")},
  {"VidTime": ("VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity")},
	{"VidTime": ("ARS4xx Device.AlgoVehCycle.VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity")},
  {"VidTime": ("MFC5xx Device.FCU.VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity")},
  {"VidTime": ("VehDyn","SRR520_RightFrontBackwards_AlgoVehCycle_VehDyn_Longitudinal_Velocity")},
  {"VidTime": ("EBC2_0B","EBC2_FrontAxleSpeed_0B_s0B")},
  # other signals as fallback solution to construct multimedia time
  {"Time": ("ARS4xx Device.AlgoVehCycle.VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity")},
  {"Time": ("MFC5xx Device.FCU.VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity")},
	{"Time": ("VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity")},
  {"Time": ("VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity")},
  {"Time": ("EBC2_0B", "EBC2_MeanSpdFA_0B")},
  {"Time": ("General_radar_status", "actual_vehicle_speed")},
  {"Time": ("ACC_S02", "ActiveFault01")},
  {"Time": ("Video_Object_0_A", "ID_0_A")},
  {"Time": ("trajectory_generator_flx20_autobox", "tg_driver_input_main_switch")},
  {"Time": ("VehDyn","SRR520_RightFrontBackwards_AlgoVehCycle_VehDyn_Longitudinal_Velocity")},
  {"Time": ("EBC2_0B","EBC2_FrontAxleSpeed_0B_s0B")},
]

AccelGroups = [{'Accel': ('ECU',        'evi.General_TC.axvRef')},
               {'Accel': ('MRR1plus',   'evi.General_TC.axvRef')},
               {'Accel': ('RadarFC',   'evi.General_TC.axvRef')}]

Optionals = [{'ego_speed': ('ECU',      'evi.General_T20.vxvRef'),
              'ego_acc':   ('ECU',      'evi.General_T20.axvRef'),},
             {'ego_speed': ('MRR1plus', 'evi.General_T20.vxvRef'),
              'ego acc':   ('MRR1plus', 'evi.General_T20.axvRef'),},
             {'ego_speed': ('RadarFC', 'evi.General_T20.vxvRef'),
              'ego_acc':   ('RadarFC', 'evi.General_T20.axvRef'),},]


class cView(interface.iView):
		def init(self, video_name = None, video_suffix = ""):
				self.video_name = video_name
				self.video_suffix = video_suffix
				return

		def check(self):
				# video file
				if self.video_name is not None:  # video file explicitly specified
						assert os.path.exists(self.video_name), "Video file not found: `%s`" % \
																										self.video_name
						avi_filename = self.video_name
				else:  # video file needs to be found
						Name, Ext = os.path.splitext(interface.Source.FileName)
						avi_filename = getVideoName(Name + self.video_suffix + Ext)
				self.logger.debug("Selected video file: %s" % avi_filename)
				multimedia_sgs = SignalGroups
				vidtime_group = self.source.selectLazySignalGroup(multimedia_sgs,
																													StrictTime = interface.StrictlyGrowingTimeCheck,
																													TimeMonGapIdx = 5)
				if 'VidTime' not in vidtime_group:
						vidtime_group = self.source.selectSignalGroup(multimedia_sgs,
																													StrictTime = False, TimeMonGapIdx = 5)
						if 'VidTime' in vidtime_group:
								self.logger.warning("Corrupt multimedia signal; video synchronization might be incorrect!")
						else:
								self.logger.warning("No multimedia signal; video synchronization might be incorrect!")
				return avi_filename, vidtime_group


		def fill(self, avi_filename,vidtime_group):
				return avi_filename,vidtime_group

		def view(self, avi_filename,vidtime_group):
				if 'VidTime' in vidtime_group:
						TimeVidTime, VidTime = vidtime_group.get_signal('VidTime')
				# VidTime = TimeVidTime - TimeVidTime[0]
				else:
						TimeVidTime = vidtime_group.get_time('Time')
				VidTime = TimeVidTime - TimeVidTime[0]

				VN = datavis.cNxtVideoNavigator(avi_filename, TimeVidTime, VidTime,self.vidcalibs, slave=True)
				if ENABLE_HACK_FOR_MULTIMEDIA_OFFSET:
						VidTime = getManuallyCorrectedMultimedia(self.source.BaseName, VidTime, self.logger)
				interface.Sync.addClient(VN, (TimeVidTime, VidTime))

				# interface.Sync.addClient(VN)
				VN.setDisplayTime(TimeVidTime, VidTime)


				return


def getVideoName(MeasFile):
		# pre-defined list of alternative folders for video files
		alternative_dirs = [
				("DAS/EnduranceRun", "DAS/ConvertedMeas"),
				("DAS/EnduranceRun/EnduranceRun_DAF_WabcoBX", "DAS/ConvertedMeas/EnduranceRun_DAF_Wabco"),
				("DAS/EnduranceRun/EnduranceRun_DAF_WabcoBX", "DAS/ConvertedMeas/EnduranceRun_DAF_BX"),
				("DAS/EnduranceRun/EnduranceRun_DAF_WabcoBX", "DAS/ConvertedMeas/EnduranceRun_DAF_KBResim"),
				("DAS/EnduranceRun/EnduranceRun_DAF_WabcoKB", "DAS/ConvertedMeas/EnduranceRun_DAF"),
				("DAS/EnduranceRun/EnduranceRun_DAF_WabcoKB", "DAS/ConvertedMeas/EnduranceRun_DAF_Wabco"),
				("DAS/EnduranceRun/EnduranceRun_Iveco_Stralis_WabcoKB", "DAS/ConvertedMeas/Iveco_Stralis_KB"),
				("DAS/EnduranceRun/EnduranceRun_Iveco_Stralis_WabcoKB", "DAS/ConvertedMeas/Iveco_Stralis_Wabco"),
				("DAS/Customer", "DAS/ConvertedMeas"),
				("measurement", "measurement_conv"),
				("measurement/DAF_WabcoBX", "measurement_conv/DAF_Wabco"),
				("measurement/DAF_WabcoBX", "measurement_conv/DAF_BX"),
				("measurement/DAF_WabcoBX", "measurement_conv/DAF_KBResim"),
				("DAS/TurningAssist/06xB365", "DAS/ConvertedMeas/TurningAssist/06xB365"),
				("Eng_Data", "Eng_Data/measurement_conv"),
				("X:", "X:/measurement_conv"),  # \\elys7027\Eng_Data
		]
		# normalize paths
		meas_file = os.path.normpath(MeasFile)
		meas_file_lower = meas_file.lower()
		alternative_dirs = [(os.path.normpath(k), os.path.normpath(v))
												for (k, v) in alternative_dirs]
		# create "reversed" list (to check both 1->2 and 2->1 replacement)
		alternative_dirs_reversed = [(v, k) for (k, v) in alternative_dirs]
		# put complete list of alternative folders together; start with the original
		alternative_dirs = [("", "")] + alternative_dirs + alternative_dirs_reversed
		# try to find the video file...
		for orig_dir, alternative_dir in alternative_dirs:
				if orig_dir.lower() not in meas_file_lower:
						continue
				# "meas_file.replace(orig_dir, alternative_dir)" with ignore-case
				pattern = re.compile(re.escape(orig_dir), re.IGNORECASE)
				meas_file_mod = pattern.sub(re.escape(alternative_dir), meas_file)
				if os.path.isdir(os.path.dirname(meas_file_mod)):
						try:
								Name = getVideoNameInSameDir(meas_file_mod)
								return Name
						except AssertionError:
								continue
		raise AssertionError('Video file not found for `%s`' % MeasFile)


def getVideoNameInSameDir(MeasFile):
		supp_exts = '.flv', '.avi'
		deltaSec = 60

		deltaSecs = [0]
		fn = FileNameParser(MeasFile)
		if fn is not None:
				deltaSecs += [val for i in xrange(1, deltaSec + 1) for val in (-i, +i)]  # results [-1, +1, -2, +2, ...]
		dirname = os.path.dirname(MeasFile)
		files = os.listdir(dirname)
		for d in deltaSecs:
				new_path = fn.timedelta(d) if fn is not None else MeasFile

				sim_file_suffix = '_kbaebs'
				Base, Ext_ = os.path.splitext(new_path)
				if Base.endswith(sim_file_suffix):
						Base = rreplace(Base, sim_file_suffix, '', 1)
				elif '_resim' in Base:
						Base = Base.split('_resim')[0]
				BaseBase = os.path.basename(Base)
				for Ext in supp_exts:
						if BaseBase + Ext in files:
								Name = Base + Ext
								return Name
				# else:
				for Ext in supp_exts:
						for f in files:
								if f.startswith(BaseBase) and f.endswith(Ext):  # ca. "glob.glob('%s*%s' % (Base, Ext))" but much faster
										Name = os.path.join(dirname, f)
										logger = logging.getLogger()
										logger.warning('Alternative video file selected: %s' % Name)
										return Name
				# else:
				fn_basebase = FileNameParser(BaseBase)
				if fn_basebase is not None:
						BaseBaseBase = fn_basebase.base2  # cut extra parts from the end
						for Ext in supp_exts:
								for f in files:
										if f.startswith(BaseBaseBase) and f.endswith(
														Ext):  # ca. "glob.glob('%s*%s' % (Base, Ext))" but much faster
												Name = os.path.join(dirname, f)
												logger = logging.getLogger()
												logger.warning('Alternative video file selected: %s' % Name)
												return Name
		raise AssertionError('Video file not found for `%s`' % MeasFile)


def getManuallyCorrectedMultimedia(MeasBaseName, VidTime, Logger = None):
		"""
		Manipulate multimedia signal in case of high inaccuracy, mainly in order
		to have well-fit overlay images in customer reports
		"""
		offsets = {
				'DE_SN-20070__2015-11-23_09-52-39.mat'          : 1.4,
				'DE_SN-20070__2015-12-22_11-46-58.mat'          : 1.4,
				'DE_SN-20070__2016-01-06_09-45-18.mat'          : -1.5,
				'DE_SN-20070__2016-01-06_15-49-51.mat'          : -3.9,
				'OTOKAR_Vectio_Project__2015-11-23_17-55-18.mat': -0.7,
				'OTOKAR_Vectio_Project__2015-12-30_11-19-06.mat': -0.25,
				'M1SH10__2016-03-05_14-41-50.mat'               : -0.5,
				'M1SH10__2016-03-05_17-42-49.mat'               : -1.0,
				'M1SH10__2016-03-30_19-31-47.mat'               : -1.0,
				'M1SH10__2016-04-04_19-10-57.mat'               : -1.0,
				'M1SH10__2016-04-04_22-12-58.mat'               : -0.5,
				'M1SH10__2016-04-28_19-24-20.mat'               : 1.0,
				'Stralis_C11-SM248__2017-02-10_15-05-29.mat'    : -0.5,
		}
		if MeasBaseName in offsets:
				if Logger is not None:
						Logger.warning("Multimedia signal manually adjusted")
				VidTime = VidTime + offsets[MeasBaseName]
		return VidTime
