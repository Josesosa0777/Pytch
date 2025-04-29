# -*- dataeval: init -*-
from datavis.AudioNavigator import cAudioNavigator
from interface import iView
import interface
from view_videonav import SignalGroups as multimedia_sgs


class View(iView):

		def check(self):
				# multimedia signal
				vidtime_group = self.source.selectLazySignalGroup(multimedia_sgs,
						StrictTime=interface.StrictlyGrowingTimeCheck, TimeMonGapIdx=5)
				if 'VidTime' not in vidtime_group:
						vidtime_group = self.source.selectSignalGroup(multimedia_sgs, StrictTime=False, TimeMonGapIdx=5)
				return vidtime_group

		def view(self, vidtime_group):
				if 'VidTime' in vidtime_group:
						_, audio_time = vidtime_group.get_signal('VidTime')
				elif 'Time' in vidtime_group:
						audio_time = vidtime_group.get_time('Time')
				else:
						self.logger.info("No Time signal found for the audio player. Could not play the audio.")
						raise AssertionError("Audio time signal missing")

				audio_nav = cAudioNavigator(audio_time)
				audio_nav.parse_audio_data(self.source)
				audio_nav.tolerance = 1 #sec

				self.sync.addClient(audio_nav)
				return


