"""
This module contains the implementation of ListNavigator, which can show
multiple signal values at the same time. The ListNavigator is synchronized
with the video player and has the capability
of updating the signal values as the measurement is played.
"""
import PIL
from datavis import figlib, NxtVideoPlayer
from datavis.Group import iGroup
from datavis.NxtVideoEventGrabber import cNxtVideoEventGrabber
from datavis.NxtVideoPlayer import cNxtVideoPlayer, cNxtVideoPlayerControl

__docformat__ = "restructuredtext en"

import logging

from PySide import QtCore, QtGui
from PySide.QtCore import Qt
from PySide.QtGui import QDesktopWidget
from PySide.phonon import Phonon
from Synchronizer import cNavigator, iSynchronizable
from figlib import generateWindowId

COLOR_TO_QT_COLOR = {
		'red': QtCore.Qt.red,
}

Debug = False
logger = logging.getLogger('NxtVideoNavigator')


class cNxtVideoEventGrabberNavigator(iGroup, iSynchronizable, QtCore.QObject):
		"""Lists several signal values with synchronizable time marker.
		Create an instance, add signals and pass it to a Synchronizer."""

		def __init__(self, filename, timevidtime, vidtime, calibrations, group = None, title = 'Signals'):
				iSynchronizable.__init__(self)
				iGroup.__init__(self, NxtVideoPlayer.KeyTable)
				QtCore.QObject.__init__(self)

				self.player = cNxtVideoEventGrabber(filename, calibrations, group)
				self.title = title
				self.filename = filename
				self.timevidtime = timevidtime
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
				self.player.imagedata_emitting_signal.signal.connect(self.save2clipboard)
				self.player.calibNavNeededSignal.signal.connect(self.calibNavNeeded)
				return

		def setCalibration(self, calibration):
				self.player.setCalibration(calibration)
				return

		def calibNavNeeded(self, vidcalibs):
				vidcalib, = vidcalibs
				self.calibNavNeededSignal.signal.emit((self, vidcalib))
				return

		def setDisplayTime(self, displaytime, displaytimevalue):
				"""
				Set time to be displayed on the video.

				:Parameters:
					displaytime : ndarray same shape as dx
						This gives the possibility to display measurement time instead of video time on the GUI.
				"""
				self.player.setDisplayTime(displaytime, displaytimevalue)
				return

		def seek(self, time):
				self.player.seek(time)
				return

		def play(self, time):
				self.player.play()
				return

		def pause(self, time):
				self.player.pause()
				self.player.seek(time)
				return

		def close(self):
				self.player.on_close()
				return

		def onSeek(self, time):
				if time == self.lastSeekTime:
						return
				self.lastSeekTime = time
				self.seekSignal.signal.emit(self.lastSeekTime)
				return

		def onPlay(self, time):
				self.playSignal.signal.emit(time)
				return

		def onPause(self, time):
				self.pauseSignal.signal.emit(time)
				return

		def onClose(self, geometry):
				self.closeSignal.signal.emit(geometry)
				return

		def start(self, selectedgroup = None):
				self.player.setcallbacks(self.onSeek, self.onPlay, self.onPause, self.onClose)
				self.player.copy(self)
				self.player.selectGroupCallback = self.onSelectGroup
				self.player._setVisible(None, None, return_result = False)

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

		def _setVisible(self, GroupName, Visible):
				"""
				:Parameters:
					GroupName : str
						Key in `Groups`
					Visible : bool
						Flag to set invisible (False) or visible (True) the selected group.
				"""
				self.player._setVisible(GroupName, Visible, return_result = False)
				return
		def setLegend(self, Markers):
				"""
				:Parameters:
					Markers : dict
						{Type<int>: (Label<str>, Style<dict>),}
				"""
				self.player.setLegend(Markers)
				return

		def getWindowTitle(self):
				return self.player.get_caption()

		def setWindowTitle(self, Measurement):
				self.player.set_caption(Measurement)

		def getWindowGeometry(self):
				w, h = self.player.get_size()
				x, y = self.player.get_location()
				return figlib.buildGeometryString(x, y, w, h)

		def setWindowGeometry(self, geometry):
				x, y, w, h = figlib.parseGeometryString(geometry)
				if w is not None and h is not None:
						self.player.set_size(w, h)
				if x is not None and y is not None:
						self.player.set_location(x, y)
				return

		def copyContentToClipboard(self):
				self.player.copyContentToClipboard()
				return

		def save2clipboard(self, imageFileAsPng):
				image = PIL.Image.open(imageFileAsPng)
				# width, height = image.size
				# data = image.tostring()
				# from http://stackoverflow.com/questions/13302908/better-way-of-going-from-pil-to-pyside-qimage
				# if i don't use this data mixing, the colors won't be the same
				# Hint: PIL uses RGBA format, but PySide uses ARGB format
				# data = ''.join([''.join(i) for i in zip(data[2::4], data[1::4], data[0::4], data[3::4])])
				# data = self.image.tostring('raw', 'RGBA')
				# image = QtGui.QImage.fromData(data)
				data = image.convert("RGBA").tostring("raw", "RGBA")
				qim = QtGui.QImage(data, image.size[0], image.size[1], QtGui.QImage.Format_ARGB32)
				pixmap = QtGui.QPixmap.fromImage(qim)
				# qt_image = QtGui.QImage(data, width, height, QtGui.QImage.Format_ARGB32)
				clipboard = QtGui.QApplication.clipboard()
				clipboard.clear()
				clipboard.setPixmap(pixmap)

				imageFileAsPng.close()
				return

		def copyContentToFile(self, file, format = 'png'):
				self.player.copyContentToFile(file, format)
				return

		def show(self):
				self.player.show()

		def setObjects(self, objecttime, objectlist):
				"""
				Set the object list for video overlay.

				:Parameters:
					objectlist : list of dict
						Object list for video overlay.
						Object properties can be described with the following keys:
						"dx"   : longitudinal distance from the radar, ndarray (mandatory)
						"dy"   : lateral distance from the radar, ndarray, same shape as dx (mandatory)
						"type" : defines how the object draws, ndarray, same shape as dx (default is 0):
						0 : An 1.5m * 1.4m shaded rectangle  with frame standing in dx distance, centered at dy on road surface.
						It
						also can have a label if "label" is defined.
						1 : An aiming sign used to indicate some important object
						2 : a simple X 0.6m above ground to indicate less important objects
						3 : A shaded diamond shape with frame
						4 : Sound signs for acoustical warning
						5 : A shaded triangle shape with frame
						6 : A simple + 0.6m above ground
						7 : A shaded hexagon shape with frame
						8 : 3 simple horizontal short lines over each other
						9 : pass for deleting special kind of objects from Video (ex. stationary objects)
						10: A unshaded interrupted frame to size around aiming sign (1)
						11: An shaded eye with frame
						12: A small unshaded bow
						13: A unshaded stick figure for pedestrians
						14: A shaded Cateye with frame
						15: A shaded almost round Circle with frame
						16: A shaded Polygon with frame (On top cut up triangle)
						17: A unshaded lying "Z" Symbol
						"color" : color of the sign (default is white) [Red, Green, Blue]
						"label" : A label of the object. (shown only when dx < 80)
						Type, color and label can be either a simple value or an ndarray with same shape as dx.
					objecttime : ndarray same shape as dx
						Signal that describes synchronization between video and data time.
					accelcomp : ndarray same shape as dx
						Acceleration compensation to filter cabin tilting. It should be aprox the tangent
						of the tilt angle.
				"""
				self.player.setobjects(objecttime, objectlist)
				return

		def setLanes(self, lanetime, lanelist):
				"""
				Set lanes as 3rd order polynomial curves. y = C3 * x ** 3 + C2 * x ** 2 + C1 * x + C0

				:Parameters:
					lanes : list of dict
						Lanes to display, given on the same time key as objects.
						Lane properties:
						"range" : range until the curve is valid, ndarray (mandatory)
						"C0" : C0, ndarray (mandatory)
						"C1" : C1, ndarray (mandatory)
						"C2" : C2, ndarray
						"C3" : C3, ndarray
						"color" : color of the lane [Red, Green, Blue] (default is blue)
						"width" : width of the lane (default is 0.12)
				"""
				self.player.setLanes(lanetime, lanelist)
				return

		def start_recording(self, path = None, filename_extra = ''):
				if path is not None:
						self.player.recorder.set_target_path(path)
				self.player.begin_recording(filename_extra)
				pass

		def stop_recording(self):
				self.player.stop_recording()
				pass
