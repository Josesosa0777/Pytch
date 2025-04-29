"""
:Organization: Knorr-Bremse TCI Pune
:Copyright:
  Knorr-Bremse TCI pune reserves all rights even in the event of industrial
  property. We reserve all rights of disposal such as copying and passing on to
  third parties.
"""

__docformat__ = "restructuredtext en"

'''Audio player.
'''
import logging

import pyglet


class cAudioPlayer:
		def __init__(self):
				self.logger = logging.getLogger()
				self.player = pyglet.media.Player()
				self.playing_file = None
				self.current_audio_duration = 0

		def play_sound(self, file_name):
				try:
						source = pyglet.media.StaticSource(pyglet.media.load(file_name, streaming = False))
						self.current_audio_duration = source.duration
						self.player.queue(source)
						self.player.play()
						self.logger.debug("Playing an audio file %s" % file_name)
						pyglet.app.run()
				except Exception as e:
						print(e.message)


if __name__ == "__main__":
		file_name = r"C:\KBData\__Evaluation\audio_eval\FLR25_2020-08-07_12-49-41_audio.mp3"
		ap = cAudioPlayer()
		# T1 = Thread(target=ap.play_sound)
		# # T1.setDaemon(True)
		# T1.start()
		ap.play_sound(file_name)
		print("End")
