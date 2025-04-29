"""
This module contains the implementation of ListNavigator, which can show
multiple signal values at the same time. The ListNavigator is synchronized
with the video player and has the capability
of updating the signal values as the measurement is played.
"""

__docformat__ = "restructuredtext en"

import logging

from PySide import QtCore, QtGui
from PySide.QtCore import Qt
from PySide.QtGui import QDesktopWidget
from PySide.phonon import Phonon
from Synchronizer import cNavigator
from figlib import generateWindowId

COLOR_TO_QT_COLOR = {
		'red': QtCore.Qt.red,
}
logger = logging.getLogger('SimpleVideoNavigator')


class cSimpleVideoNavigator(cNavigator):
		"""Lists several signal values with synchronizable time marker.
		Create an instance, add signals and pass it to a Synchronizer."""

		def __init__(self, filename,timevidtime,vidtime, title = 'Signals'):

				cNavigator.__init__(self)

				self.title = title
				self.filename = filename
				self.timevidtime =timevidtime
				self.vidtime = vidtime
				self.lastSeekTime = 0.0
				""":type: str
				Main title of the list window."""
				self.playing = False
				""":type: bool
				Playing state."""
				self.groups = {'Default': {"frame": None, "signals": []}}
				""":type: dictionary
				List of the signal groups."""
				self.selectedgroup = None
				""":type: dictionary
				List of the signal groups."""
				self.time = 0.
				""":type: float
				The time of the displayed signals"""
				self.seeked = False
				""":type: bool
				Flag to indicate outer seek"""
				self._windowId = generateWindowId(title)
				""":type: str
				String to identify the window"""
				self.timeScale = None
				""":type: TableNavigator.Slider
				Slider along time scale"""
				self.pw = None
				self.objects = []  # list of dict of objects [{trackid : {list of signals}}]
				self.timeseries = []  # Common time
				self.table_headers = []  # Table headers to show
				""":type: QtGui.QTabWidget"""
				self.setWindowTitle(title)
				self.center()
				return

		def center(self):
				qr = self.frameGeometry()
				cp = QDesktopWidget().availableGeometry().center()
				qr.moveCenter(cp)
				self.move(qr.topLeft())



		def seek(self, time):
				self.time = time
				self.seeked = True
				cNavigator.seek(self, time)
				time= time * 1000
				self.media.seek(time)
				return

		def play(self, time):
				self.time = time
				cNavigator.play(self, time)
				self.seeked = True
				self.media.play()
				# self.setMessage('PLAY >')
				return

		def pause(self, time):
				self.time = time
				cNavigator.pause(self, time)
				self.seeked = True
				self.media.pause()
				# self.setMessage('PAUSE ||', forceRedraw = True)
				return

		def onPlay(self, time):
				self.playSignal.signal.emit(time)
				return

		def onSeek(self, time):
				if time == self.lastSeekTime:
						return
				self.lastSeekTime = time
				self.seekSignal.signal.emit(self.lastSeekTime)
				return

		def onPause(self, time):
				self.pauseSignal.signal.emit(time)
				return


		def refreshValues(self):
				"""
				Refresh the displayed values.

				:Return: None
				"""
				pass

		def phononSeek(self,time):
				time = time/1000
				self.onSeek(time)


		def tick(self, time):
				time= (self.media.currentTime()/1000) + self.timevidtime[0]
				self.timeLcd.setText(str(time))




		def start(self, selectedgroup = None):

				self.selectedgroup = selectedgroup
				self.mainframe = QtGui.QFrame()
				main_layout = QtGui.QVBoxLayout()


				self.source =Phonon.MediaSource(self.filename)
				self.media = Phonon.MediaObject(self)
				self.media.setCurrentSource(self.source)
				self.media.tick.connect(self.tick)
				self.media.tick.connect(self.phononSeek)
				self.video = Phonon.VideoWidget(self)
				self.video.setMinimumSize(400, 400)
				Phonon.createPath(self.media, self.video)


				self.slider = Phonon.SeekSlider()
				self.slider.setMediaObject(self.media)
				self.timeLcd = QtGui.QLabel()


				layout = QtGui.QGridLayout(self)
				layout.addWidget(self.video, 0, 0, 1, 2)
				layout.addWidget(self.timeLcd,1,1)
				layout.addWidget(self.slider, 2, 0, 1, 2)
				layout.setRowStretch(0, 1)



				main_layout.addLayout(layout)
				self.mainframe.setLayout(main_layout)
				self.setCentralWidget(self.mainframe)





		def keyPressEvent(self, event):
				key = event.key()
				if (key == QtCore.Qt.Key_Space and self.media.state()==Phonon.PausedState) or (key == QtCore.Qt.Key_Space and self.media.state()==Phonon.StoppedState):
						self.media.play()
						self.onPlay(float(self.media.currentTime()/1000))


				elif (key == QtCore.Qt.Key_Space and self.media.state()==Phonon.PlayingState):
						self.media.pause()
						self.onPause(float(self.media.currentTime()/1000))


				if (key == QtCore.Qt.Key_S):
						self.media.stop()


