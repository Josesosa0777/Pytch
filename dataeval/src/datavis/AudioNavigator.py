import logging
import os
import re
import subprocess
from datetime import datetime

from Synchronizer import cNavigator
from datavis.AudioPlayer import cAudioPlayer
from measparser.ffmpeg import executable

from measparser.filenameparser import FileNameParser

AUDIO_FORMATS = ["MP3", "MP2", "MP1", "AAC", "AVI", "DVI4", "WMA1", "WMA2", "WMA", "XMA1", "XMA2", "ATRAC1", "ATRAC9", "ATRAC3", "ATRAC3PLUS"]



class cAudioNavigator(cNavigator):  # iGroup
		def __init__(self, time):
				super(cAudioNavigator, self).__init__()

				# TODO Add QLabel to show which file is playing, clean after file complete

				self.logger = logging.getLogger()
				self.device_time = time
				self.meas_time_start = None
				self.audio_data = {}  # {timestamp: {"fileName":filename to play, "timeGap":<float>}

				self.tolerance = 0.1  # seconds


				self.audio_player = cAudioPlayer()
				return

		def parse_audio_data(self, source):
				AUDIO_EXISTS = False
				fn_source = FileNameParser(source.BaseName)
				self.meas_time_start = fn_source._date
				meas_dir = os.path.dirname(source.FileName)
				meas_vehicle_name = fn_source.base3.split("\\")[-1].split("__")[0]
				duration = self.device_time[len(self.device_time) - 1] - self.device_time[0]

				for file_name in os.listdir(meas_dir):
						file = os.path.join(meas_dir, file_name)
						extension = file_name.split(".")[-1]
						if os.path.isfile(file) and "_audio" in file_name and extension.upper() in AUDIO_FORMATS:
								fn = FileNameParser(file)
								if fn is None:
										self.logger.warning('Filename does not match python toolchain file pattern: {}'.format(file))
										self.logger.info("Audio file name must have 'VehicleName__YYYY-mm-dd-MM-SS_audio' format")
										continue
								audio_vehicle_name = fn.base3.split("\\")[-1].split("__")[0]
								# Skip audio file if vehicle name not matching
								if audio_vehicle_name != meas_vehicle_name:
										continue
								AUDIO_EXISTS = True
								date_time = fn._date
								if date_time is None:
										continue
								mp3_file = os.path.join(meas_dir, "".join(file_name.split(".")[:-1]) + ".mp3")
								return_code = 0
								if not os.path.isfile(mp3_file):
										command = "\"" + executable + "\" -i \"" + file + "\" -vn \"" + mp3_file + "\""
										process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
										stdout, stderr = process.communicate()
										self.logger.info(str(stderr) + "\n" + str(stdout))
										return_code = process.returncode
								if return_code == 0:
										record = {}
										audio_time_gap_from_base = self.get_datetime_diff(self.meas_time_start, date_time)
										record["audio_file"] = mp3_file
										record["time_gap"] = audio_time_gap_from_base

										if audio_time_gap_from_base <= duration:
												self.audio_data[date_time] = record
				if not AUDIO_EXISTS:
						self.logger.info("There are no audio files for the selected vehicle measurement.")
				else:
						self.logger.info("Following audio files has been detected in the same folder, it will run based on video navigator timestamp")

						audio_data_list = sorted([value for key, value in self.audio_data.items()], key=lambda x: x["time_gap"])
						for audio_meta in audio_data_list:
								timestamp = self.device_time[0] + audio_meta["time_gap"]
								self.logger.info("Audio file: {}, timestamp: {}".format(audio_meta["audio_file"], timestamp))
						self.logger.warning("Don't forget to press 'Ctrl + R'(Synchronization ON) to get synchronized with audio navigator.")


		def get_datetime_diff(self, lower_timestamp, upper_timestamp):  # ("%m/%d/%Y, %H:%M:%S")
				_lower_timestamp = datetime.strptime(lower_timestamp, "%Y-%m-%d_%H-%M-%S")
				_upper_timestamp = datetime.strptime(upper_timestamp, "%Y-%m-%d_%H-%M-%S")
				diff = _upper_timestamp - _lower_timestamp
				return diff.seconds

		def extract_timestamp(self, file_name):
				date_time = re.search(r"([0-9]{4}\-[0-9]{2}\-[0-9]{2}\_[0-9]{2}\-[0-9]{2}\-[0-9]{2})", file_name)
				if date_time is not None:
						date_time = date_time.group()
				else:
						self.logger.info("Meas datetime format mismatch")
						date_time = None
				return date_time

		def seekWindow(self):
				seek_time = self.time
				global_time_gap_from_base = seek_time - self.device_time[0]
				for timestamp, record in self.audio_data.items():
						try:
								# Stop player condition
								if self.audio_player.player.playing and self.audio_player.playing_file == record["audio_file"] \
												and (global_time_gap_from_base < record["time_gap"] - self.tolerance \

														 or global_time_gap_from_base > record[
																 "time_gap"] + self.tolerance + self.audio_player.current_audio_duration):

										self.audio_player.player.delete()
						except:
								pass
						# Check if timestamp comes in current tolerance window
						if abs(record["time_gap"] - global_time_gap_from_base) <= self.tolerance and not \
										self.audio_player.player.playing:

								self.logger.debug("SeekTime: {}".format(seek_time))
								self.logger.debug("meas_time_start: {}".format(self.device_time[0]))
								self.logger.debug("global_time_gap_from_base: {}".format(global_time_gap_from_base))
								self.audio_player.playing_file = record["audio_file"]
								self.audio_player.play_sound(record["audio_file"])
								break

		def pause(self, time):
				try:
						if self.audio_player.playing_file is not None:
								self.logger.debug("Resuming audio file: %s", self.audio_player.playing_file)
								self.audio_player.player.pause()
				except Exception as e:
						print(e.message)

		def play(self, time):

				if not self.audio_data:
						self.logger.warning("Audio data not found")

				try:
						if self.audio_player.playing_file is not None:
								self.logger.debug("Resuming audio file: %s", self.audio_player.playing_file)
								self.audio_player.player.play()
				except Exception as e:
						print(e.message)

		def clean(self):
				try:
						self.logger.debug("Closing an audio player")
						self.audio_player.player.delete()
				except Exception as e:
						print(e.message)

