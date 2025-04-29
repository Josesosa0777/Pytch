"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright:
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial
  property. We reserve all rights of disposal such as copying and passing on to
  third parties.
"""
__docformat__ = "restructuredtext en"

'''Audio and video player with simple GUI controls and data overlay capabilities.
'''

__docformat__ = 'restructuredtext'

import pyglet_workaround  # necessary as early as possible (#164)

import logging
import collections
import StringIO

import numpy as np
import pyglet
import OpenGL.GLUT
import PIL
from PySide import QtGui, QtCore

import OpenGLutil
import OverlayShape
import Slider
import Group
from TrackNavigator import COLOR_NONE, NO_COLOR
import figlib
from calibration_data import cCalibrationData
from RecordingService import RecordingService

PygletKeyCrossTable = {}
AtoZ = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
_0to_9 = [chr(i) for i in range(ord('0'), ord('9') + 1)]
KeyCodes = [[c, getattr(pyglet.window.key, c)] for c in AtoZ]
KeyCodes += [[c, getattr(pyglet.window.key, '_' + c)] for c in _0to_9]
PygletKeyCrossTable.update(KeyCodes)
del KeyCodes, _0to_9, AtoZ


class ObjectEmittingSignal(QtCore.QObject):
		signal = QtCore.Signal(object)


class SimpleSignal(QtCore.QObject):
		signal = QtCore.Signal()


class cVideoLegend:
		"""Legend rendering in an OpenGL context."""

		def __init__(self):
				# initial dummy values
				self.x = 0
				self.y = 0
				self.width = 0
				self.height = 0
				self.margin = 0
				self.innerMargin = 0
				self.textSize = 0
				self.shapes = None
				self.markers = []

				# colors
				self.backgroundColor = (255, 255, 255, 220)
				self.fontColor = (0, 0, 0)
				self.fontFamily = OpenGL.GLUT.GLUT_STROKE_MONO_ROMAN

				# sizes - will be rescaled
				self.scale = 1.0
				self.widthRef = 792.0
				self.marginRef = 10.0
				self.innerMarginRef = 50.0
				self.textSizeRef = 20.0
				self.dx = 6.0
				self.dy = 2.0
				return

		def setMarkers(self, shapes, markers):
				"""Initialize lists for markers to render.

				:Parameters:
					shapes : OverlayShape.Shapes
					markers : dict
				"""
				self.shapes = shapes

				labels = []  # list for checking duplications
				styles = []  # list for checking duplications
				for (label, style) in markers.itervalues():
						if (label in labels and styles[labels.index(label)] == style) or style[0]['shape'] is None:
								continue  # avoid duplications and exclude NoneType objects
						labels.append(label)
						styles.append(style)
						self.markers.append((label, style))
				self.markers.sort()  # sort by labels

				# decrease marker and label size if count > 12
				nMarkers = len(self.markers)
				if nMarkers > 12:
						self.textSize *= np.max((0.5, 12.0 / nMarkers))
				return

		def on_resize(self, parentPosition):
				"""Update sizes on window resize event.

				:Assumptions:
					Aspect ratio of the video does not change.
				"""
				self.scale = parentPosition[2] / self.widthRef

				self.x = parentPosition[0] + self.margin
				self.y = parentPosition[1] + self.margin

				self.width = (self.widthRef - 2 * self.marginRef) * self.scale
				self.height = self.width * parentPosition[3] / parentPosition[2]
				self.margin = self.marginRef * self.scale
				self.innerMargin = self.innerMarginRef * self.scale
				self.textSize = self.textSizeRef * self.scale
				return

		def draw(self):
				"""Render objects and their labels in an OpenGL context.

				:Assumptions:
					OpenGL viewport and matrix modes are set properly for GUI drawing.
				"""
				x1 = self.x
				y1 = self.y
				x2 = self.x + self.width
				y2 = self.y + self.height

				# background
				pyglet.gl.glBegin(pyglet.gl.GL_QUADS)
				pyglet.gl.glColor4ub(*self.backgroundColor)
				pyglet.gl.glVertex2f(x1, y1)
				pyglet.gl.glVertex2f(x1, y2)
				pyglet.gl.glVertex2f(x2, y2)
				pyglet.gl.glVertex2f(x2, y1)
				pyglet.gl.glEnd()

				if not self.markers:
						# warning if nothing to show
						pyglet.gl.glPushMatrix()
						pyglet.gl.glTranslatef(x1 + 6 * self.innerMargin, y2 - 5 * self.innerMargin, 0.0)
						pyglet.gl.glScalef(self.textSize, self.textSize, 0.0)
						OpenGLutil.drawString('No objects to display', color = self.fontColor)
						pyglet.gl.glPopMatrix()
				else:
						# objects and labels
						pyglet.gl.glColor3ub(*self.fontColor)
						pyglet.gl.glPushMatrix()
						pyglet.gl.glTranslatef(x1 + 4 * self.innerMargin, y2 - self.innerMargin, 0.0)
						pyglet.gl.glScalef(self.textSize, self.textSize, 0.0)
						for (label, style) in self.markers:
								self.shapes.draw(style[0]['shape'], OpenGLutil.EDGE)  # draw object
								pyglet.gl.glTranslatef(self.dx, 0.0, 0.0)
								pyglet.gl.glPushMatrix()
								OpenGLutil.drawString(label, color = self.fontColor, font = self.fontFamily)  # draw label
								pyglet.gl.glPopMatrix()
								pyglet.gl.glTranslatef(-self.dx, -self.dy, 0.0)
						pyglet.gl.glPopMatrix()
				return


class cFpsCalculator:
		"""Adaptive video frame rate calculator."""

		def __init__(self, fpsInit):
				self.frameGaps = collections.deque([1.0 / fpsInit], maxlen = 10)
				self.lastVideoTimestamp = None
				self._updated = False
				self._lastCalculatedFrameGap = 1.0 / fpsInit
				return

		def tick(self, videoTimeStamp):
				"""
				Add a frame timestamp to calculate with.

				Assumption: tick is called at least once between each video frame (to avoid undersampling).
				"""
				if self.lastVideoTimestamp is None:  # seek might have happened before, unknown framegap
						self.lastVideoTimestamp = videoTimeStamp
				else:
						if videoTimeStamp > self.lastVideoTimestamp:
								self.frameGaps.append(videoTimeStamp - self.lastVideoTimestamp)
								self.lastVideoTimestamp = videoTimeStamp
								self._updated = True
				return

		def tickReset(self):
				"""Reset the tick state (e.g. after seeking)."""
				self.lastVideoTimestamp = None
				return

		def getFrameGap(self):
				"""Return the time between video frames, based on the available samples."""
				# Optimization: calculate only if changed
				if self._updated:
						self._lastCalculatedFrameGap = np.mean(self.frameGaps)
						self._updated = False
				return self._lastCalculatedFrameGap


class cVideoPlayer32(pyglet.window.Window, Group.iGroup):
		def __init__(self, filename, calibrations, framerate = 10.0, keyframegap = 10.0):
				# init parents
				pyglet.window.Window.__init__(self, caption = 'VideoPlayer', visible = False, resizable = True)
				Group.iGroup.__init__(self, PygletKeyCrossTable)

				self.logger = logging.getLogger()
				self.hold_key_state = pyglet.window.key.KeyStateHandler()
				self.push_handlers(self.hold_key_state)
				pyglet.clock.schedule_interval(self.check_key_held, 0.15)

				# Camera calib params
				self.calibration = False
				self.default_calib = cCalibrationData(0.24, 2.3, 0.0, 640, 480, 36.2,
																							0.249, -0.262, 0.0)
				self.calibrations = calibrations
				self.cali = self.default_calib
				self.calib_init_step = 0.001

				# LDW-overlay parameters
				self.ldw_tire_mode = False
				self.ldw_tire_overlay_calib = None

				# distance limit for label display [m]
				self.maxDisplDist = 100

				# Keyframe distance in video
				self.keyframegap = keyframegap

				# Frame rate calculator
				self.fpsCalculator = cFpsCalculator(framerate)

				# GUI sizes
				self.GUI_WIDTH = 328
				self.GUI_HEIGHT = 248
				self.GUI_PADDING = 4
				self.SLIDER_HEIGHT = 14
				self.mx = 0
				self.my = 0

				# Callbacks
				self.seekcallback = None
				self.playcallback = None
				self.pausecallback = None
				self.closecallback = None

				# Overlay objects
				self.objseektime = 0.0
				self.objects = None
				self.objects = []
				self.times = []
				self.accelcomp = None
				self.labellevel = 0
				self.displaytime = None

				# Overlay lanes
				self.lanesenabled = True
				self.lanes = []
				self.lanetodisplay = -1

				# Overlay SignalValues to display by pressing F4
				self.Signals = []

				# Video player
				source = pyglet.media.load(filename)
				self.filename = filename
				self.player = pyglet.media.Player()
				self.player.queue(source)

				self.player.push_handlers(self)
				self.player.eos_action = self.player.EOS_PAUSE
				self.player.push_handlers(on_eos = self.on_player_eos)
				self.seekbackduringplayback = False

				# Slow/fast/reversed playing
				self.speed = 0.5
				self.customspeed = False
				self.playing_reversed = False

				# Slider
				self.slider = Slider.Slider(self)
				# self.slider = Slider(self)
				self.slider.x = self.GUI_PADDING
				self.slider.y = self.GUI_PADDING
				self.slider.on_begin_scroll = lambda value: None
				self.slider.on_end_scroll = lambda value: self.seek(value, seekback = not self.player.playing)
				self.slider.on_change = lambda value: self.seek(value)

				# Timelabel
				self.showtimelabel = True
				self.timelabel = pyglet.text.Label('0000.00',
																					 font_name = 'Courier New',
																					 font_size = 10,
																					 x = self.GUI_PADDING * 2, y = self.GUI_PADDING * 2 + self.SLIDER_HEIGHT,
																					 anchor_x = 'left', anchor_y = 'bottom')

				self.messagelabel = pyglet.text.Label('',
																							font_name = 'Courier New',
																							font_size = 15,
																							bold = True,
																							color = (0, 255, 255, 255),
																							x = self.GUI_WIDTH - self.GUI_PADDING * 2,
																							y = self.GUI_HEIGHT - self.GUI_PADDING * 2,
																							anchor_x = 'right', anchor_y = 'top')
				# Helplabel
				self.showhelplabel = False
				self.helplabel = pyglet.text.Label("Control Keys:\n"
																					 "-------------\n"
																					 "SPACE:     Toggle play/pause\n"
																					 "s:         Toggle custom speed motion play/pause\n"
																					 "PGUP/PGDN: Change motion speed in custom speed mode\n"
																					 "->:        Forward  step frame by frame, forward search if held\n"
																					 "<-:        Backward step frame by frame, backward search if held\n"
																					 "SH+->:     Forward  step, no synchronization\n"
																					 "SH+<-:     Backward step, no synchronization\n"
																					 "t:         Toggle time label on/off\n"
																					 "l:         Toggle object labels on/off\n"
																					 "b:         Toggle video background image on/off\n"
																					 "h:         Toggle legend on/off\n"
																					 "r:         Toggle refresh of other navigators during playback\n"
																					 "c:         Toggle between calibration presets\n"
																					 "v:         Toggle field of view display on/off\n"
																					 "x:         Toggle between field of view modes\n"
																					 "n:         Toggle lanes on/off\n"
																					 "m:         Manual calibration (experimental)\n"
																					 "q:         Copy the current image to the clipboard\n"
																					 "F1:        Toggle this help screen\n"
																					 "F2:        Toggle statuslabel on/off\n"
																					 "F4:        Toggle optional signals on/off\n"
																					 "F10:       Print current time in log window\n",
																					 font_name = 'Courier New',
																					 font_size = 10,
																					 bold = True,
																					 multiline = True,
																					 width = self.GUI_WIDTH,
																					 color = (0, 255, 255, 255),
																					 x = 2 * self.GUI_PADDING, y = self.GUI_WIDTH - 2 * self.GUI_PADDING,
																					 anchor_x = 'left', anchor_y = 'top')
				# Help label for Manual Calibration
				self.show_calib_help = False
				self.calib_help_label = pyglet.text.Label("Control Keys:\n"
																									"-------------\n"
																									"q:         Increase Field of View\n"
																									"a:         Decrease Field of View\n"
																									"e:         Increase X - looking target.\n"
																									"d:         Decrease X - looking target.\n"
																									"w:         Increase Y - looking target.\n"
																									"s:         Decrease Y - looking target.\n"
																									"y:         Increase Camera's X value.\n"
																									"h:         Decrease Camera's X value.\n"
																									"u:         Increase Camera's Y value.\n"
																									"j:         Decrease Camera's Y value.\n"
																									"r:         Increase Camera's Z value.\n"
																									"f:         Decrease Camera's Z value.\n"
																									"t:         Increase UP-X Value for Camera.\n"
																									"g:         Decrease UP-X Value for Camera.\n",
																									font_name = 'Courier New',
																									font_size = 10,
																									bold = True,
																									multiline = True,
																									width = self.GUI_WIDTH,
																									color = (0, 255, 255, 255),
																									x = 2 * self.GUI_PADDING,
																									y = self.GUI_WIDTH - 2 * self.GUI_PADDING,
																									anchor_x = 'left', anchor_y = 'top')

				# Signal displaying
				self.showSignals = False
				self.signallabel = pyglet.text.Label("",
																						 font_name = 'Courier New',
																						 font_size = 10,
																						 bold = True,
																						 multiline = True,
																						 width = self.GUI_WIDTH,
																						 color = (0, 255, 255, 255),
																						 x = 2 * self.GUI_PADDING, y = self.GUI_WIDTH - 2 * self.GUI_PADDING,
																						 anchor_x = 'left', anchor_y = 'top')

				# Legend
				self.showLegend = False
				self.legend = cVideoLegend()

				# Statuslabel
				self.showstatuslabel = False
				self.statuslabel = pyglet.text.Label("",
																						 font_name = 'Courier New',
																						 font_size = 10,
																						 bold = True,
																						 multiline = True,
																						 width = self.GUI_WIDTH,
																						 color = (0, 255, 255, 255),
																						 x = 2 * self.GUI_PADDING, y = self.GUI_WIDTH - 2 * self.GUI_PADDING,
																						 anchor_x = 'left', anchor_y = 'top')

				# LDW-overlay marks. X, Y are set dynamically
				self.text_ldws_mark_zero = pyglet.text.Label("Red   : Origin, Zero marker.",
																										 font_name = 'Courier New',
																										 font_size = 14,
																										 bold = True,
																										 color = (255, 0, 0, 255),
																										 multiline = True,
																										 width = self.GUI_WIDTH,
																										 x = 2 * self.GUI_PADDING,
																										 y = self.GUI_WIDTH - 2 * self.GUI_PADDING,
																										 anchor_x = 'left', anchor_y = 'top')

				self.text_ldws_mark_tw = pyglet.text.Label("Purple: Tire width(cm) from origin(RED mark)",
																									 font_name = 'Courier New',
																									 font_size = 14,
																									 bold = True,
																									 color = (128, 0, 128, 255),
																									 multiline = True,
																									 width = self.GUI_WIDTH,
																									 x = 2 * self.GUI_PADDING,
																									 y = self.GUI_WIDTH - 2 * self.GUI_PADDING,
																									 anchor_x = 'left', anchor_y = 'top')

				self.text_ldws_mark_xcm = pyglet.text.Label("Blue  : Variable X distance from origin(RED mark)",
															font_name='Courier New',
															font_size=14,
															bold=True,
															color = (0, 0, 255, 255),
																multiline = True,
																width = self.GUI_WIDTH,
																x = 2 * self.GUI_PADDING,
																y = self.GUI_WIDTH - 2 * self.GUI_PADDING,
																anchor_x = 'left', anchor_y = 'top')
				# Video background image
				self.showVideoImage = True

				# Field of view
				self.showFOV = False
				self.FOVindex = 0
				self.FOVs = OpenGLutil.fovBuildProps.keys()

				self.Markers = {}
				""":type: dict
				Container of the shapes of the field of view display lists {shapeName<str> : <listID>, }"""

				self.recorder = RecordingService('VideoRecord')
				self.is_recording = False

				self.gui_update_source()
				self.prepare_video_size()

				self._initGL()

				self.Shapes = OverlayShape.Shapes(OpenGLutil.allShapeBuildProps)

				self.set_size(self.GUI_WIDTH, self.GUI_HEIGHT)

				self.imagedata_emitting_signal = ObjectEmittingSignal()
				self.calibNavNeededSignal = ObjectEmittingSignal()
				self.ldw_tire_calib_signal_show = ObjectEmittingSignal()
				self.ldw_tire_calib_signal_close = SimpleSignal()
				self.manual_calib_updated = SimpleSignal()
				return

		def _initGL(self):
				"""Initialize OpenGL properties
				"""
				pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
				pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
				return

		def selectCalibration(self, truck, date):
				"""
				Set the camera calibration based on `truck` and `date` identifiers.

				:Parameters:
					truck : str
					date : str
				:Exceptions:
					AssertionError : if `calibrations` does not contain `track` and `date`
				"""
				raise NotImplementedError("feature not yet supported with the new calib")
				return

		def setCalibration(self, calibration):
				if calibration is None:
						self.cali = self.default_calib
						return
				assert isinstance(calibration, cCalibrationData)
				self.cali = calibration
				return

		# def printCalibration(self):
		#     print "Current calibration (" + \
		#           ", ".join(self.cali.get_value_names()) + "):\n" + \
		#           ", ".join(str(val) for val in self.cali.get_values())
		#     return

		def _setVisible(self, GroupName, Visible, return_result = True):
				"""
				:Parameters:
					GroupName : str
						Key in `Groups`
					Visible : bool
						Flag to set invisible (False) or visible (True) the selected group.
					return_result : bool
						True if the call was insider.
						False if the call was outsider.
				"""
				self.statuslabel.text = '\n'.join(self.Labels)
				self.on_draw()
				if return_result:
						self.selectGroupCallback(GroupName)
				return

		def selectGroupCallback(self, GroupName):
				return

		def setLegend(self, Markers):
				markers = Markers.copy()  # shallow copy
				if markers:
						self.Markers = markers
						self.legend.setMarkers(self.Shapes, markers)
				return

		def setObject(self, objecttime, object):
				time_idx = self._addTime(objecttime)
				self.objects.append((object, time_idx))
				return

		def setLane(self, lanetime, lane):
				time_idx = self._addTime(lanetime)
				self.lanes.append((lane, time_idx))
				return

		def selectLane(self, lanenr):
				"""
				:Parameters:
					lanenr : int
						number of lane pair to display, -1 means all
				:Exceptions:
					AssertionError : invalid lane number
				"""
				self.lanetodisplay = 2 * lanenr + 1 if lanenr >= 0 else -1
				assert 0 < self.lanetodisplay < len(self.lanes) or self.lanetodisplay == -1, \
						'invalid lane number %d' % lanenr
				self.lanesenabled = True
				return

		def setDisplayTime(self, diplaytime, diplaytimevalue):
				self.displaytime = diplaytime, diplaytimevalue
				return

		def setobjects(self, objecttime, objectlist):
				for object in objectlist:
						if 'shape' not in object:
								self.setObject(objecttime, object)
				return

		def setAccelComp(self, time, accelcomp):
				time_idx = self._addTime(time)
				self.accelcomp = (accelcomp, time_idx)
				return

		def _addTime(self, time):
				for i, t in enumerate(self.times):
						if np.array_equal(t, time):
								break
				else:
						i = len(self.times)
						self.times.append(time)
				return i

		def seekTimes(self, seektime):
				ndxs = [max(0, time.searchsorted(seektime, side = 'right') - 1)
								for time in self.times]
				return ndxs

		def setLanes(self, lanetime, lanelist):
				for lane in lanelist:
						self.setLane(lanetime, lane)
				return

		def setSignal(self, name, time, signal, unit):
				time_idx = self._addTime(time)
				sig = name, signal, unit
				self.Signals.append((sig, time_idx))
				return

		def setcallbacks(self, seekcallback, playcallback, pausecallback, closecallback):
				self.seekcallback = seekcallback
				self.playcallback = playcallback
				self.pausecallback = pausecallback
				self.closecallback = closecallback
				return

		def gui_update_source(self):
				if self.player.source:
						self.slider.min = 0.0
						self.slider.max = self.player.source.duration
				return

		def prepare_video_size(self, x = None, y = None):
				if x is None or y is None:
						width, height = self.get_video_size()
				else:
						width, height = x, y
				self.video_width = width
				self.video_height = height
				self.GUI_WIDTH = width + 2 * self.GUI_PADDING
				self.GUI_HEIGHT = height + self.SLIDER_HEIGHT + 2 * self.GUI_PADDING
				self.video_x = self.GUI_PADDING
				self.video_y = self.GUI_HEIGHT - self.GUI_PADDING - self.video_height
				return

		def set_video_size(self, x = None, y = None):
				self.prepare_video_size(x, y)
				self.set_size(self.GUI_WIDTH, self.GUI_HEIGHT)
				return

		def get_video_size(self):
				if not self.player.source or not self.player.source.video_format:
						return 0, 0
				video_format = self.player.source.video_format
				width = video_format.width
				height = video_format.height
				if video_format.sample_aspect > 1:
						width *= video_format.sample_aspect
				elif video_format.sample_aspect < 1:
						height /= video_format.sample_aspect
				return width, height

		def setMessage(self, msg, timeout = 2.0, forceRedraw = False):
				pyglet.clock.unschedule(self._clearMessage)  # ignore previous clear request (if any)
				if timeout is not None and timeout > 0.0:  # do not hide message if timeout is None
						pyglet.clock.schedule_once(self._clearMessage, timeout)  # schedule clearing
				self.messagelabel.text = msg  # set message
				if forceRedraw:
						self.on_draw()  # ASSUMPTION: on_draw() is called outside, but can be forced here as well
				return

		def _clearMessage(self, dt = None, forceRedraw = False):
				if self.messagelabel.text or forceRedraw:
						self.messagelabel.text = ''
						if forceRedraw or not self.player.playing:
								self.on_draw()  # update required, but performed automatically while playing
				return

		def copyContentToClipboard(self):
				self._clearMessage(forceRedraw = True)
				# Save as png
				imageFileAsPng = StringIO.StringIO()
				colorBuffer = pyglet.image.get_buffer_manager().get_color_buffer()
				colorBuffer.save('png', file = imageFileAsPng)
				imageFileAsPng.seek(0)
				# Crop
				self.imagedata_emitting_signal.signal.emit(imageFileAsPng)
				return

		def copyContentToFile(self, file, format = 'png'):
				self._clearMessage(forceRedraw = True)
				colorBuffer = pyglet.image.get_buffer_manager().get_color_buffer()
				if isinstance(file, basestring):  # 'file' is the name of the file
						with open(file, 'wb') as f:
								colorBuffer.save(filename = format, file = f)
				else:  # 'file' is a file-like object
						colorBuffer.save(filename = format, file = file)
				return

		def on_resize(self, width, height):
				"""Position and size video image."""
				width = max(width, 1)
				height = max(height, 1)
				pyglet.window.Window.on_resize(self, width, height)
				self.slider.width = width - self.GUI_PADDING * 2

				video_width, video_height = self.get_video_size()
				if video_width == 0 or video_height == 0:
						return

				display_aspect = (width - self.GUI_PADDING * 2) / float(height - self.SLIDER_HEIGHT - self.GUI_PADDING * 2)
				video_aspect = video_width / float(video_height)
				if video_aspect > display_aspect:
						self.video_width = width - self.GUI_PADDING * 2
						self.video_height = self.video_width / video_aspect
				else:
						self.video_height = height - self.SLIDER_HEIGHT - self.GUI_PADDING * 2
						self.video_width = self.video_height * video_aspect
				self.video_x = (width - self.video_width) / 2
				self.video_y = (height - self.video_height) / 2 + self.SLIDER_HEIGHT / 2
				self.timelabel.x = self.video_x + self.GUI_PADDING
				self.timelabel.y = self.video_y + self.GUI_PADDING
				self.messagelabel.x = self.video_x + self.video_width - 2 * self.GUI_PADDING
				self.messagelabel.y = self.video_y + self.video_height - 2 * self.GUI_PADDING
				self.helplabel.x = self.video_x + self.GUI_PADDING
				self.helplabel.y = self.video_y + self.video_height - 2 * self.GUI_PADDING
				self.helplabel.width = self.video_width
				self.calib_help_label.x = self.video_x + self.GUI_PADDING
				self.calib_help_label.y = self.video_y + self.video_height - 2 * self.GUI_PADDING
				self.calib_help_label.width = self.video_width
				self.statuslabel.x = self.GUI_PADDING
				self.statuslabel.y = self.video_y + self.video_height - self.GUI_PADDING
				self.statuslabel.width = self.video_width
				self.legend.on_resize((self.video_x, self.video_y, self.video_width, self.video_height))
				self.on_draw()
				return

		def on_mouse_press(self, x, y, button, modifiers):
				if self.slider.hit_test(x, y):
						self.slider.on_mouse_press(x, y, button, modifiers)
				else:
						self.mx = x - self.GUI_PADDING;
						self.my = self.height - y - self.GUI_PADDING;
						self.on_draw()
				return

		def on_key_press(self, symbol, modifiers):
				"""
				Event handler for key press event.
				CONVENTION: Numbers and capital letters are reserved for enabling/disabling groups.

				:Return: None
				"""
				isNumber = symbol in (range(48, 58) + range(65456, 65466))  # 0-9 on keyboard and numpad
				isLetter = symbol in range(97, 123)  # a-z (including A-Z)
				isLowercase = not (
								bool(modifiers & pyglet.window.key.MOD_SHIFT) ^ bool(modifiers & pyglet.window.key.MOD_CAPSLOCK))

				if symbol == pyglet.window.key.SPACE:
						self.on_play_pause()
				elif symbol == pyglet.window.key.PAGEUP:
						if self.speed < 16.0:
								self.speed *= 2.0
								if self.speed == 1.0:
										self.speed *= 2.0
				elif symbol == pyglet.window.key.PAGEDOWN:
						if self.speed > 1 / 16.0:
								self.speed /= 2.0
								if self.speed == 1.0:
										self.speed /= 2.0
				elif symbol == pyglet.window.key.F1:
						if self.calibration:
								self.show_calib_help = not self.show_calib_help
						else:
								self.showhelplabel = not self.showhelplabel
				elif symbol == pyglet.window.key.F9:
						# Key for enabling the LDW Overlay check.
						# Handle also the calibration window opening
						if self.ldw_tire_mode:
								self.ldw_tire_mode = False
								self.setMessage("LDW TIRE MODE : OFF", timeout = 4.0)
								self.ldw_tire_calib_signal_close.signal.emit()
						else:
								self.ldw_tire_mode = True
								self.setMessage("LDW TIRE MODE : ON", timeout = 4.0)
								self.ldw_tire_calib_signal_show.signal.emit([self.video_width,
																														 self.video_height])
				elif symbol == pyglet.window.key.F2:
						self.showstatuslabel = not self.showstatuslabel
				elif symbol == pyglet.window.key.F3:
						print 'Warning: Showing/hiding legend by pressing "F3" is deprecated. Use "h" instead.'
						self.showLegend = not self.showLegend
				elif symbol == pyglet.window.key.F4:
						self.showSignals = not self.showSignals
				elif symbol == pyglet.window.key.F10:
						if self.displaytime is not None:
								displaytime, displaytimevalue = self.displaytime
								disptime = np.interp([self.objseektime], displaytimevalue,
																		 displaytime)[0]
						else:
								disptime = self.player.time
						self.logger.info(
								"Current time is " + str(disptime))
				elif symbol == pyglet.window.key.MOTION_RIGHT and not self.player.playing:
						self.setMessage('STEP FORWARD >>')
						pyglet.clock.schedule_once(self.startplay, -1.0)
						seekback = not (modifiers & pyglet.window.key.MOD_SHIFT)
						self.step(seekback)
				elif symbol == pyglet.window.key.MOTION_LEFT and not self.player.playing:
						self.setMessage('STEP BACKWARD <<')
						pyglet.clock.schedule_once(self.startplayreversed, 1.0)
						seekback = not (modifiers & pyglet.window.key.MOD_SHIFT)
						ts = self.player.source.get_next_video_timestamp()
						self.seek(ts - 0.2, seekback)
				elif isLetter and isLowercase:
						if symbol == pyglet.window.key.S and not self.calibration:
								self.customspeed_play_pause()
						elif symbol == pyglet.window.key.N:
								if self.lanes:
										if not self.lanesenabled:
												self.lanesenabled = True
												self.setMessage('LANES ENABLED: ALL')
										else:
												if self.lanetodisplay < len(self.lanes) - 1:
														self.lanetodisplay += 2
														self.setMessage('LANES ENABLED: %d' % (self.lanetodisplay // 2))
												else:
														self.lanesenabled = False
														self.lanetodisplay = -1
														self.setMessage('LANES DISABLED')
						elif symbol == pyglet.window.key.Q and not self.calibration:
								self.copyContentToClipboard()
						elif symbol == pyglet.window.key.L:
								self.labellevel += 1
								if self.labellevel > 2:
										self.labellevel = 0
						elif symbol == pyglet.window.key.T and not self.calibration:
								self.showtimelabel = not self.showtimelabel
						elif symbol == pyglet.window.key.H and not self.calibration:
								self.showLegend = not self.showLegend
						elif symbol == pyglet.window.key.R and not self.calibration:
								self.seekbackduringplayback = not self.seekbackduringplayback
								sbState = 'ON' if self.seekbackduringplayback else 'OFF'
								self.setMessage('Synchronization ' + sbState)
						# video background image on/off
						elif symbol == pyglet.window.key.B:
								self.showVideoImage = not self.showVideoImage
						# Field of view
						elif symbol == pyglet.window.key.V:
								self.showFOV = not self.showFOV
						elif symbol == pyglet.window.key.X:
								if self.showFOV:
										self.FOVindex = (0 if self.FOVindex >= len(self.FOVs) - 1 else self.FOVindex + 1)
						# Calibrate camera
						elif symbol == pyglet.window.key.C:
								if self.ldw_tire_mode:
										self.ldw_tire_calib_signal_show.signal.emit([self.video_width,
																																 self.video_height])
								else:
										self.calibNavNeededSignal.signal.emit([self.calibrations])
						elif symbol == pyglet.window.key.M and not self.ldw_tire_mode:
								self.calibration = not self.calibration

				# Show/hide groups - ASSUMPTION: Only numbers and capital letters are used for this purpose.
				elif symbol in self.KeyCodes and not (isNumber and bool(
								modifiers & pyglet.window.key.MOD_SHIFT)):  # Shift+Number is not a number - exclusion needed for
						# consistency with other navigators
						self.selectGroupCallback(self.KeyCodes[symbol])
				else:
						return

				self.on_draw()
				return

		def on_key_release(self, symbol, modifiers):
				if symbol == pyglet.window.key.MOTION_RIGHT:
						pyglet.clock.unschedule(self.startplay)
				elif symbol == pyglet.window.key.MOTION_LEFT:
						pyglet.clock.unschedule(self.startplayreversed)
				if symbol == pyglet.window.key.MOTION_RIGHT or symbol == pyglet.window.key.MOTION_LEFT:
						if self.player.playing:
								self.on_play_pause()
						if self.customspeed:
								self.customspeed_play_pause()
						if self.playing_reversed:
								self.reversed_play_pause()
				return

		def check_key_held(self, dt = None):
				if self.calibration:
						previous = self.calib_init_step
						# ( (x ** (x/3) ) / 1000 ) + 0.001
						# Custom equation for increasing value gradient
						self.calib_init_step = \
								((previous ** (previous / 3)) / 1000) + 0.001

						# Key-checks. This part handles keyboard output
						# Emit signal only when these keys are pressed.
						if self.hold_key_state[pyglet.window.key.A]:
								self.cali.fov -= self.calib_init_step * 100.0
								self.manual_calib_updated.signal.emit()
						elif self.hold_key_state[pyglet.window.key.Q]:
								self.cali.fov += self.calib_init_step * 100.0
								self.manual_calib_updated.signal.emit()
						elif self.hold_key_state[pyglet.window.key.S]:
								self.cali.looktoy -= self.calib_init_step
								self.manual_calib_updated.signal.emit()
						elif self.hold_key_state[pyglet.window.key.W]:
								self.cali.looktoy += self.calib_init_step
								self.manual_calib_updated.signal.emit()
						elif self.hold_key_state[pyglet.window.key.D]:
								self.cali.looktox -= self.calib_init_step
								self.manual_calib_updated.signal.emit()
						elif self.hold_key_state[pyglet.window.key.E]:
								self.cali.looktox += self.calib_init_step
								self.manual_calib_updated.signal.emit()
						elif self.hold_key_state[pyglet.window.key.F]:
								self.cali.cameraz -= self.calib_init_step * 10
								self.manual_calib_updated.signal.emit()
						elif self.hold_key_state[pyglet.window.key.R]:
								self.cali.cameraz += self.calib_init_step * 10
								self.manual_calib_updated.signal.emit()
						elif self.hold_key_state[pyglet.window.key.G]:
								self.cali.upx -= self.calib_init_step * 5
								self.manual_calib_updated.signal.emit()
						elif self.hold_key_state[pyglet.window.key.T]:
								self.cali.upx += self.calib_init_step * 5
								self.manual_calib_updated.signal.emit()
						elif self.hold_key_state[pyglet.window.key.Y]:
								self.cali.camerax += self.calib_init_step
								self.manual_calib_updated.signal.emit()
						elif self.hold_key_state[pyglet.window.key.H]:
								self.cali.camerax -= self.calib_init_step
								self.manual_calib_updated.signal.emit()
						elif self.hold_key_state[pyglet.window.key.U]:
								self.cali.cameray += self.calib_init_step * 10
								self.manual_calib_updated.signal.emit()
						elif self.hold_key_state[pyglet.window.key.J]:
								self.cali.cameray -= self.calib_init_step * 10
								self.manual_calib_updated.signal.emit()
						else:
								# Reset increment if key has been released
								self.calib_init_step = 0.001
						self.on_draw()
				return

		def on_close(self):
				self.calibrations = None  # to avoid sqlite programming error due thread handling
				self.ldw_tire_calib_signal_close.signal.emit()
				w, h = self.get_size()
				x, y = self.get_location()

				geometry = figlib.buildGeometryString(x, y, w, h)

				self.player.pause()
				pyglet.clock.unschedule(self.update)
				pyglet.clock.unschedule(self.update_customspeed)
				pyglet.clock.unschedule(self.update_reversed)

				self.on_draw()  # multiple VideoPlayer closing workaround #1277
				self.Shapes.closeResources()
				if self.closecallback is not None:
						self.closecallback(geometry)
				self.close()
				return

		def on_play_pause(self):
				self.on_play_pause_base()
				if self.player.playing:
						if self.playcallback is not None:
								self.playcallback(self.player.time)
				else:
						if self.pausecallback is not None:
								self.pausecallback(self.player.time)
				return

		def on_play_pause_base(self):
				if self.customspeed:
						self.customspeed = False
						pyglet.clock.unschedule(self.update_customspeed)
				if self.playing_reversed:
						self.playing_reversed = False
						pyglet.clock.unschedule(self.update_reversed)
				if self.player.playing:
						self.setMessage('PAUSE ||', forceRedraw = True)
						self.player.pause()
						pyglet.clock.unschedule(self.update)
				else:
						self.setMessage('PLAY >')
						if self.player.source.get_next_video_timestamp() is None:
								# seek to the beginning
								self.slider.on_mouse_press(self.slider.x, None, None, None)
								self.slider.on_mouse_release(self.slider.x, None, None, None)
						self.player.play()
						pyglet.clock.schedule(self.update)
				# pyglet.clock.schedule_interval(self.update, 1./40.)
				self.on_draw()
				return

		def customspeed_play_pause(self):
				if self.player.playing:
						self.player.pause()
						pyglet.clock.unschedule(self.update)
				if self.playing_reversed:
						self.playing_reversed = False
						pyglet.clock.unschedule(self.update_reversed)
				if self.customspeed:
						self.setMessage('PAUSE ||', forceRedraw = True)
						self.customspeed = False
						pyglet.clock.unschedule(self.update_customspeed)
						if self.pausecallback is not None:
								self.pausecallback(self.player.time)
				else:
						self.setMessage('CUSTOM SPEED PLAYING')
						if self.player.source.get_next_video_timestamp() is None:
								# seek to the beginning
								self.slider.on_mouse_press(self.slider.x, None, None, None)
								self.slider.on_mouse_release(self.slider.x, None, None, None)
						if self.playcallback is not None:
								self.playcallback(self.player.time)
						self.customspeed = True
						self.update_customspeed()
				return

		def reversed_play_pause(self):
				if self.player.playing:
						self.player.pause()
						pyglet.clock.unschedule(self.update)
				if self.customspeed:
						self.customspeed = False
						pyglet.clock.unschedule(self.update_customspeed)
				if self.playing_reversed:
						self.setMessage('PAUSE ||', forceRedraw = True)
						self.playing_reversed = False
						pyglet.clock.unschedule(self.update_reversed)
						if self.pausecallback is not None:
								self.pausecallback(self.player.time)
				else:
						self.setMessage('< PLAY')
						if self.playcallback is not None:
								self.playcallback(self.player.time)
						self.playing_reversed = True
						self.update_reversed()
				return

		def on_player_eos(self):
				pyglet.clock.unschedule(self.update)
				pyglet.clock.unschedule(self.update_customspeed)
				self.slider.on_mouse_press(self.slider.x + self.slider.width, None, None, None)  # important
				self.slider.on_mouse_release(self.slider.x + self.slider.width, None, None, None)
				return

		def on_draw(self):
				self.switch_to()
				self.clear()

				# Video
				pyglet.gl.glColor3ub(255, 255, 255)  # needed for video drawing
				pyglet.gl.glViewport(0, 0, int(self.width), int(self.height))
				if self.player.source and self.player.source.video_format and self.showVideoImage and \
								self.player.get_texture():
						self.player.get_texture().blit(self.video_x,
																					 self.video_y,
																					 width = self.video_width,
																					 height = self.video_height)

				# GUI
				pyglet.gl.glViewport(0, 0, int(self.width), int(self.height))  # restore after draw_objects()
				# slider value update when customspeed mode is enabled
				if self.customspeed:  # required to update slider value properly on 64-bit
						self.slider.value = self.player.source.get_next_video_timestamp()
				else:
						self.slider.value = self.player.time
				self.slider.draw()
				self.messagelabel.draw()
				if self.displaytime is not None:
						displaytime, displaytimevalue = self.displaytime
						disptime = np.interp([self.objseektime], displaytimevalue,
																 displaytime)[0]
				else:
						disptime = self.player.time
				ndxs = self.seekTimes(disptime)
				if self.calibration:
						# self.draw_calib()
						# pyglet.gl.glViewport(0, 0, int(self.width), int(self.height))  # restore after draw_calib()
						if self.show_calib_help:
								self.calib_help_label.draw()
						# Design Decision: Maximum 4 pieces of information.
						# Too much clutter does not fit.
						self.timelabel.text = 'FOV:%d CAM-X:%3.4f CAM-Y:%3.4f CAM-Z:%3.4f' % \
																	(self.cali.fov, self.cali.camerax, self.cali.cameray, self.cali.cameraz)

						self.timelabel.draw()
				else:
						if self.customspeed:
								if self.speed >= 1.0:
										speedtext = '[x %d]' % int(self.speed)
								else:
										speedtext = '[x 1/%d]' % int(1.0 / self.speed)
						if self.objects:
								if self.customspeed:
										self.timelabel.text = '%07.3f %s' % (disptime, speedtext)
								else:
										self.timelabel.text = '%07.3f' % disptime
						else:
								if self.customspeed:
										self.timelabel.text = '%07.3f %s (NO OBJECTS)' % (disptime, speedtext)
								else:
										self.timelabel.text = '%07.3f (NO OBJECTS)' % (disptime)
						if self.showFOV:
								self.timelabel.text += ', FOV: %s' % self.FOVs[self.FOVindex]
						if self.showhelplabel:
								self.helplabel.draw()
						if self.showtimelabel:
								self.timelabel.draw()
						if self.showstatuslabel:
								self.statuslabel.draw()
						if self.showSignals and self.Signals:
								self.signallabel.text = ""
								for (name, Signal, unit), time_idx in self.Signals:
										# search corresponding values
										ndx = ndxs[time_idx]
										# append signal data to the label
										self.signallabel.text += "\n%s: % .1f %s" % (name, Signal[ndx], unit)
								self.signallabel.draw()
						if self.showLegend:
								self.legend.draw()
				# Overlay with 3D rendering
				self.draw_objects(ndxs)  # Note: OpenGL attributes might change
				self.flip()
				if self.is_recording:
						colorBuffer = pyglet.image.get_buffer_manager().get_color_buffer()
						self.recorder.update_current_record(colorBuffer.image_data.data)
				return

		def draw_lanes(self, ndxs):
				for i, (lane, time_idx) in enumerate(self.lanes):
						if self.lanetodisplay == -1 or i == self.lanetodisplay or i == self.lanetodisplay - 1:
								ndx = ndxs[time_idx]
								if lane.get("color") is not None:
										color = lane["color"][ndx] if isinstance(lane["color"], np.ndarray) else lane["color"]
								else:
										color = (0, 0, 255)
								if lane.get("alpha") is not None:
										alpha = int(255 * lane["alpha"][ndx]) if isinstance(lane["alpha"], np.ndarray) else int(
														255 * lane["alpha"])
										if alpha > 255 or alpha < 0:
												alpha = 127
								else:
										alpha = 127
								if lane.get("width") is not None:
										width = lane["width"][ndx] if isinstance(lane["width"], np.ndarray) else 0.12
								else:
										width = 0.12

								pyglet.gl.glColor4ub(color[0], color[1], color[2], alpha)
								pyglet.gl.glBegin(pyglet.gl.GL_QUAD_STRIP)

								if lane.has_key("linex") and lane.has_key("liney"):
										dist = np.arange(0, lane["linex"][ndx][-1], .2)
										latdist = np.interp(dist, lane["linex"][ndx], lane["liney"][ndx])
								else:
										dist = np.arange(0, lane["range"][ndx], .2)
										latdist = lane["C1"][ndx] * dist + lane["C0"][ndx]
										if lane.get("C2") is not None:
												latdist += lane["C2"][ndx] * dist ** 2
										if lane.get("C3") is not None:
												latdist += lane["C3"][ndx] * dist ** 3
								point_range = len(dist)

								for i in range(0, point_range - 1, 2):
										x1, y1 = -latdist[i], -dist[i]
										x2, y2 = -latdist[i + 1], -dist[i + 1]
										dx, dy = x1 - x2, y1 - y2
										l = np.sqrt(dx * dx + dy * dy)
										x3, y3 = x2 + width * dy / l, y2 - width * dx / l
										x4, y4 = x1 + width * dy / l, y1 - width * dx / l
										pyglet.gl.glVertex3f(x1, 0.0, y1)
										pyglet.gl.glVertex3f(x4, 0.0, y4)
										pyglet.gl.glVertex3f(x2, 0.0, y2)
										pyglet.gl.glVertex3f(x3, 0.0, y3)
								pyglet.gl.glEnd()
				return

		def draw_objects(self, ndxs):
				if self.ldw_tire_mode and self.ldw_tire_overlay_calib is not None:
						self.draw_ldw_tire_overlay()

				if (not self.objects and not self.lanesenabled) or not self.times:
						return
				try:
						# Get index of objects according to video time
						# Set 3D rendering parameters
						pyglet.gl.glViewport(int(self.video_x), int(self.video_y), int(self.video_width), int(self.video_height))
						pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
						pyglet.gl.glPushMatrix()
						pyglet.gl.glLoadIdentity()
						pyglet.gl.gluPerspective(
										self.cali.fov,  # Field Of View
										float(self.video_width) / float(self.video_height),  # aspect ratio
										1.0,  # z near
										1000.0)  # z far
						pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
						pyglet.gl.glPushMatrix()
						pyglet.gl.glLoadIdentity()
						atx = self.cali.looktox
						aty_accelcomp = 0.0
						if self.accelcomp:
								accelcomp, time_idx = self.accelcomp
								ndx = ndxs[time_idx]
								aty_accelcomp = accelcomp[ndx]
						aty = self.cali.cameray + self.cali.looktoy + aty_accelcomp
						atz = -1.0
						pyglet.gl.gluLookAt(
										self.cali.camerax, self.cali.cameray, self.cali.cameraz,
										atx, aty, atz,
										self.cali.upx, 1.0, 0.0,
						)

						# Draw calibration reference if necessary
						if self.lanesenabled:
								self.draw_lanes(ndxs)
						if self.calibration:
								self.draw_reference()
						# Field of view rendering
						if self.showFOV:
								pyglet.gl.glColor3ub(255, 0, 0)
								pyglet.gl.glLineWidth(1)
								shapeName = self.FOVs[self.FOVindex]
								self.Shapes.draw(shapeName, OpenGLutil.EDGE)

						# OBJECT LOOP
						#   Assumptions:  OpenGL matrix mode is GL_MODELVIEW in the loop
						#                 Each object is responsible for its proper display style settings (color, linewidth, etc.)

						for o, time_idx in self.objects:
								ndx = ndxs[time_idx]
								if o.get("type") is not None:
										Type = o["type"][ndx] if isinstance(o["type"], np.ndarray) else o["type"]
										try:
												seqOfShapeProps = self.Markers[Type][1]
										except IndexError:
												self.logger.info('Missing drawing data, shape cannot be drawn.')
												continue
										if Type in self.Invisibles:
												continue
								else:
										continue
								dx = o["dx"][ndx]
								dy = o["dy"][ndx]
								if o.get("color") is not None:
										color = o["color"][ndx] if isinstance(o["color"], np.ndarray) else o["color"]
								else:
										color = NO_COLOR
								if o.get("alpha") is not None:
										alpha = int(255 * o["alpha"][ndx]) if isinstance(o["alpha"], np.ndarray) else int(255 * o["alpha"])
										if alpha > 255 or alpha < 0:
												alpha = None
								else:
										alpha = None
								if o.get("label") is not None:
										label = o["label"][ndx] if isinstance(o["label"], np.ndarray) else o["label"]
								else:
										label = None
								isDrawable = True

								# object coord transformation: radar -> OpenGL
								X, Y, Z = -dy, 0.0, -dx
								pyglet.gl.glPushMatrix()
								pyglet.gl.glTranslatef(X, Y, Z)

								# TEST: check object's real position (without height information)
								# pyglet.gl.glLineWidth(2)
								# pyglet.gl.glColor3ub(255,140,0)
								# self.Shapes.draw('debug', OpenGLutil.EDGE)

								# SHAPE RENDERING
								for shapeProps in seqOfShapeProps:
										style = {}
										# separate shape definition from display style description
										for propName, propValue in shapeProps.iteritems():
												if 'shape' == propName:
														shapeName = propValue
												elif 'type' == propName:
														shapeType = propValue
												else:
														style[propName] = propValue
										# skip object drawing if shape is not renderable
										if not shapeName or not self.Shapes.has_shape(shapeName):
												isDrawable = False
												break
										# set the color (with or without transparency)
										styleColor = False
										if COLOR_NONE in color:
												if 'color' not in style:
														self.logger.info('LegendValues does not contain type: %d!\n' % Type)
												else:
														color = style['color']
														styleColor = True
										if alpha is None:
												alpha = style['alpha'] if style.has_key('alpha') else None
										# transparency only in case of surfaces
										if alpha and OpenGLutil.FACE == shapeType:
												pyglet.gl.glColor4ub(color[0], color[1], color[2], alpha)
										else:
												pyglet.gl.glColor3ub(color[0], color[1], color[2])
										# set line width
										lineWidth = style['lw'] if style.has_key('lw') else None
										if lineWidth:
												pyglet.gl.glLineWidth(lineWidth)

										# draw the shape
										self.Shapes.draw(shapeName, shapeType)

										# if style color was apllied change color back to NO_COLOR
										if styleColor:
												color = NO_COLOR

								# TEXT RENDERING
								if label is not None \
												and self.labellevel > 0 \
												and dx < self.maxDisplDist \
												and isDrawable:
										# GLUT string rendering
										scale = 0.003 * self.labellevel
										scaleVec = (scale, scale, 0.0)
										OpenGLutil.drawString(label,
																					scale = scaleVec)  # extra properties supported (e.g. text translation,
								# rotation, color, transparency)

								pyglet.gl.glPopMatrix()
						# Reset rendering parameters
						pyglet.gl.glPopMatrix()
						pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
						pyglet.gl.glPopMatrix()
				except pyglet.gl.GLException, e:
						self.logger.error('OpenGL exception caught during object rendering, message: %s' % e.message)
				except Exception, e:
						self.logger.error('Exception caught during object rendering, message: %s' % e.message)
				return

		def draw_reference(self):
				pyglet.gl.glBegin(pyglet.gl.GL_LINES)
				pyglet.gl.glColor3f(1.0, 0.0, 0.0)

				# # objects from measurement comparison_all_sensors_2012-08-01_11-22-31_calib
				# pyglet.gl.glVertex3f(-1.27, 0.0, -5.21) # obj1
				# pyglet.gl.glVertex3f(-1.27, 0.8, -5.21) # obj1
				# pyglet.gl.glVertex3f(-1.27, 0.8, -5.21) # flag
				# pyglet.gl.glVertex3f(-1.17, 0.8, -5.21) # flag
				# pyglet.gl.glVertex3f(-1.27, 0.0, -9.95) # obj2
				# pyglet.gl.glVertex3f(-1.27, 2.2, -9.95) # obj2
				# pyglet.gl.glVertex3f(1.89, 0.0, -5.21) # obj3
				# pyglet.gl.glVertex3f(1.89, 0.79, -5.21) # obj3
				# pyglet.gl.glVertex3f(1.89, 0.0, -9.95) # obj4
				# pyglet.gl.glVertex3f(1.89, 2.1, -9.95) # obj4
				# pyglet.gl.glColor3f(0.0, 1.0, 0.0)
				# pyglet.gl.glVertex3f(-1.27, 0.0, -5.21) # line1
				# pyglet.gl.glVertex3f(-1.27, 0.0, -9.95) # line1
				# pyglet.gl.glVertex3f(1.89, 0.0, -5.21) # line2
				# pyglet.gl.glVertex3f(1.89, 0.0, -9.95) # line2
				# pyglet.gl.glVertex3f(-1.27, 0.0, -5.21) # line3
				# pyglet.gl.glVertex3f(1.89, 0.0, -5.21) # line3
				# pyglet.gl.glVertex3f(-1.27, 0.0, -9.95) # line4
				# pyglet.gl.glVertex3f(1.89, 0.0, -9.95) # line4

				# road
				pyglet.gl.glVertex3f(-1.5, 0., 0.)
				pyglet.gl.glVertex3f(-1.5, 0., -1000.)
				pyglet.gl.glVertex3f(1.5, 0., 0.)
				pyglet.gl.glVertex3f(1.5, 0., -1000.)

				# objects
				pyglet.gl.glVertex3f(-1.5, 0., -5.)
				pyglet.gl.glVertex3f(-1.5, 1.0, -5.)
				pyglet.gl.glVertex3f(1.5, 0., -5.)
				pyglet.gl.glVertex3f(1.5, 1.0, -5.)
				pyglet.gl.glVertex3f(-1.5, 0., -5.)
				pyglet.gl.glVertex3f(1.5, 0., -5.)
				pyglet.gl.glVertex3f(-1.5, 0., -10.)
				pyglet.gl.glVertex3f(-1.5, 1.0, -10.)
				pyglet.gl.glVertex3f(1.5, 0., -10.)
				pyglet.gl.glVertex3f(1.5, 1.0, -10.)
				pyglet.gl.glVertex3f(-1.5, 0., -10.)
				pyglet.gl.glVertex3f(1.5, 0., -10.)
				pyglet.gl.glVertex3f(-1.5, 0., -15.)
				pyglet.gl.glVertex3f(-1.5, 1.0, -15.)
				pyglet.gl.glVertex3f(1.5, 0., -15.)
				pyglet.gl.glVertex3f(1.5, 1.0, -15.)
				pyglet.gl.glVertex3f(-1.5, 0., -15.)
				pyglet.gl.glVertex3f(1.5, 0., -15.)

				pyglet.gl.glEnd()
				return

		def draw_ldw_tire_overlay(self):
				# For handling and readability purposes
				LENGTH = self.ldw_tire_overlay_calib.length
				X = self.ldw_tire_overlay_calib.x
				Y = self.ldw_tire_overlay_calib.y
				PCNT_ZM = self.ldw_tire_overlay_calib.zero_mark_offset
				PCNT_TW = self.ldw_tire_overlay_calib.tw_mark_offset

				MARK_SIZE = self.video_height / 16.0
				ANGLE_ROT = self.ldw_tire_overlay_calib.rotation

				BOX_WDT = self.video_width / 16.0
				BOX_HT = self.video_height / 17.0

				# TODO: Refactor
				self.text_ldws_mark_zero.x = self.video_x + self.GUI_PADDING + 10
				self.text_ldws_mark_zero.y = self.video_y + self.video_height - 2 * self.GUI_PADDING - 20
				self.text_ldws_mark_zero.width = self.video_width
				self.text_ldws_mark_zero.draw()

				self.text_ldws_mark_tw.x = self.video_x + self.GUI_PADDING + 10
				self.text_ldws_mark_tw.y = self.video_y + self.video_height - 2 * self.GUI_PADDING - 40
				self.text_ldws_mark_tw.width = self.video_width
				self.text_ldws_mark_tw.draw()

				self.text_ldws_mark_xcm.x = self.video_x + self.GUI_PADDING + 10
				self.text_ldws_mark_xcm.y = self.video_y + self.video_height - 2 * self.GUI_PADDING - 60
				self.text_ldws_mark_xcm.text = "Blue  : Distance from origin   \t= {} cm \n\t   Distance from Purple mark = {} cm".format(self.ldw_tire_overlay_calib.scale_len, self.ldw_tire_overlay_calib.scale_len - self.ldw_tire_overlay_calib.tire_width)
				self.text_ldws_mark_xcm.width = self.video_width
				self.text_ldws_mark_xcm.draw()

				# Overall figure settings

				pyglet.gl.glLineWidth(3)
				pyglet.gl.glPushMatrix()
				pyglet.gl.glTranslatef(X, Y, 0.0)
				pyglet.gl.glRotatef(ANGLE_ROT, 0.0, 0.0, 1.0)
				pyglet.gl.glTranslatef(-X, -Y, 0.0)
				pyglet.gl.glBegin(pyglet.gl.GL_LINES)

				# Main Line
				pyglet.gl.glColor3f(1, 1, 0)
				pyglet.gl.glVertex2f(X, Y)
				pyglet.gl.glVertex2f(X + LENGTH, Y)

				# Zero Mark
				pyglet.gl.glColor3f(0.9, 0.0, 0.0)
				zm_x = X + (LENGTH * PCNT_ZM / 100.0)
				pyglet.gl.glVertex2f(zm_x, Y + MARK_SIZE / 2.0)
				pyglet.gl.glVertex2f(zm_x, Y - MARK_SIZE / 2.0)

				# Tire Width Mark
				pyglet.gl.glColor3f(0.5, 0.0, 0.5)
				tw_x = X + (LENGTH * PCNT_TW / 100.0)
				pyglet.gl.glVertex2f(tw_x, Y + MARK_SIZE / 2.0)
				pyglet.gl.glVertex2f(tw_x, Y - MARK_SIZE / 2.0)

				# X CM Mark
				pyglet.gl.glColor3f(0.0, 0.1, 0.9)
				xcm_x = zm_x - self.ldw_tire_overlay_calib.get_size_x_offset_to_right(self.ldw_tire_overlay_calib.scale_len)
				pyglet.gl.glVertex2f(xcm_x, Y + MARK_SIZE / 2.5)
				pyglet.gl.glVertex2f(xcm_x, Y - MARK_SIZE / 2.5)


				# Wrapping up
				pyglet.gl.glEnd()

				# Boxes and text
				# TODO: activation in GUI
				y_boxes = Y + MARK_SIZE / 1.5


				pyglet.gl.glPopMatrix()

				return

		def draw_calib(self):
				pyglet.gl.glViewport(
								int(self.video_x),
								int(self.video_y),
								int(self.video_width),
								int(self.video_height))
				pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
				pyglet.gl.glPushMatrix()
				pyglet.gl.glLoadIdentity()
				pyglet.gl.glOrtho(
								0,
								int(self.video_width),
								0,
								int(self.video_height), 0, 1)
				pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
				pyglet.gl.glPushMatrix()
				pyglet.gl.glLoadIdentity()

				pyglet.gl.glBegin(pyglet.gl.GL_LINES)
				pyglet.gl.glColor3ub(0, 0, 255)

				# # objects from measurement comparison_all_sensors_2012-08-01_11-22-31_calib
				pyglet.gl.glVertex2f(143, self.video_height - 356)
				pyglet.gl.glVertex2f(139, self.video_height - 278)
				pyglet.gl.glVertex2f(139, self.video_height - 278)  # flag
				pyglet.gl.glVertex2f(149, self.video_height - 278)  # flag
				pyglet.gl.glVertex2f(211, self.video_height - 238)
				pyglet.gl.glVertex2f(211, self.video_height - 120)
				pyglet.gl.glVertex2f(462, self.video_height - 350)
				pyglet.gl.glVertex2f(465, self.video_height - 275)
				pyglet.gl.glVertex2f(376, self.video_height - 236)
				pyglet.gl.glVertex2f(383, self.video_height - 124)

				pyglet.gl.glColor3ub(255, 255, 255)
				pyglet.gl.glEnd()

				pyglet.gl.glPopMatrix()
				pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
				pyglet.gl.glPopMatrix()
				return

		def seek(self, value, seekback = False):
				self.seek_base(value, seekback)
				if self.seekcallback is not None:
						self.seekcallback(self.player.time)
				return

		def seek_base(self, value, seekback = False):
				"""
				Seek video to the given timestamp.

				self.player.seek() searches for _keyframes_ right after the timestamp,
				however, there is no keyframe for every video frame. Therefore, `searchstep`
				must be substracted for correct positioning, and then the desired video frame
				can be searched step-by-step. A proper `searchstep` value is found by a
				linear searching algorithm.

				The objects' seek time `objseektime` is usually set to the desired timestamp
				(i.e., `value`), however, if the previous frame is requested, it is set to
				the timestamp of the previous frame. (The situation is the same with the next
				frame, but that is implemented in self.step().)

				:Parameters:
					value : float
						Timestamp to seek to.
					seekback : bool
						Seek other navigators or not.
				"""
				if value <= 0.0:
						# seek to the beginning
						self.player.seek(-1.0)  # < 0.0 required
						self.player._timestamp = 0.0
						self.player.source._last_video_timestamp = 0.0
						self.objseektime = 0.0
				else:
						stepback = (value == self.player.time)  # important
						value = min(value, self.player.source.duration)
						self.player.seek(value)
						ts = self.player.source.get_next_video_timestamp()
						searchstep = 0.0
						# seek to the proper keyframe
						while ts is None or ts >= value:
								searchstep += 0.1
								if searchstep >= value:
										self.player.seek(-1.0)  # < 0.0 required
										self.player._timestamp = 0.0
										self.player.source._last_video_timestamp = 0.0
										break
								if searchstep > self.keyframegap:
										# worst-case limit for searching backwards
										self.logger.info('Cannot seek video to timestamp %f' % value)
										break
								self.player.seek(value - searchstep)
								ts = self.player.source.get_next_video_timestamp()
						last_img = None
						# seek exactly to the desired video frame
						while True:
								last_ts = ts
								ts = self.player.source.get_next_video_timestamp()
								if ts is None or ts >= value:
										break
								last_img = self.player.source.get_next_video_frame()
						if last_img is not None:
								self.player._texture.blit_into(last_img, 0, 0, 0)
								self.player._timestamp = last_ts
								self.player.source._last_video_timestamp = last_ts
						self.objseektime = last_ts if stepback else value

				self.fpsCalculator.tickReset()
				self.on_draw()
				return

		def step(self, seekback = False, count = 1):
				ts = self.player.source.get_next_video_timestamp()
				last_img = None
				for i in xrange(count):
						last_ts = ts
						ts = self.player.source.get_next_video_timestamp()
						if ts is None:
								break
						last_img = self.player.source.get_next_video_frame()  # implicit iter.next()
				else:
						last_ts = ts
				if last_img is not None:
						self.player._texture.blit_into(last_img, 0, 0, 0)
						self.player._timestamp = last_ts
						self.player.source._last_video_timestamp = last_ts
						self.objseektime = last_ts
						self.fpsCalculator.tickReset()
						self.on_draw()
						if seekback and self.seekcallback is not None:
								self.seekcallback(self.player.time)
				return

		def startplay(self, dt):
				if not self.player.playing:
						self.on_play_pause()
				return

		def startplayreversed(self, dt):
				if not self.playing_reversed:
						self.reversed_play_pause()
				return

		def update(self, dt):
				self.fpsCalculator.tick(self.player.source._last_video_timestamp)
				self.objseektime = self.player.time
				self.on_draw()
				if self.seekbackduringplayback and self.seekcallback is not None:
						self.seekcallback(self.player.time)
				return

		def update_customspeed(self, dt = 0.0):
				frameGap = self.fpsCalculator.getFrameGap() / self.speed
				if self.customspeed:
						pyglet.clock.schedule_once(self.update_customspeed, frameGap)
				nSteps = int(round(dt / frameGap))
				self.step(self.seekbackduringplayback, nSteps)
				return

		def update_reversed(self, dt = 0.0):
				reversedSpeed = 1.0
				frameGap = self.fpsCalculator.getFrameGap() / reversedSpeed
				if self.playing_reversed:
						pyglet.clock.schedule_once(self.update_reversed, frameGap)
				if dt < 1.2 * frameGap:  # sufficient update rate --> one step back
						self.seek(self.player.time, self.seekbackduringplayback)
				else:  # low update rate --> seek back
						self.seek(self.player.time - reversedSpeed * dt, self.seekbackduringplayback)
				return

		def close(self):
				pyglet.clock.unschedule(self.update)
				pyglet.clock.unschedule(self.update_customspeed)
				pyglet.clock.unschedule(self.update_reversed)
				pyglet.clock.unschedule(self._clearMessage)
				pyglet.clock.unschedule(self.check_key_held)
				return pyglet.window.Window.close(self)

		def setseekcallback(self, func):
				self.seekcallback = func
				return

		def playing(self):
				return self.player.playing

		def gettime(self):
				return self.player.time

		def begin_recording(self, filename_extra):
				colorBuffer = pyglet.image.get_buffer_manager().get_color_buffer()
				# Start only if no record is running
				if not self.is_recording:
						# Run a flipped recording at a FPS of 4 for easy visual
						self.recorder.record_start((colorBuffer.width, colorBuffer.height), fps = 30
																			 , flipped = True, filename_extra = filename_extra)
						self.is_recording = True
				return

		def stop_recording(self):
				# Stop record if there is a record running
				if self.is_recording:
						self.recorder.stop_current_record()
						self.is_recording = False
				return


class cVideoPlayer64(cVideoPlayer32):
		def __init__(self, filename, calibrations, framerate = 10.0, keyframegap = 10.0):
				super(cVideoPlayer64, self).__init__(filename, calibrations, framerate = framerate, keyframegap = keyframegap)
				return

		def on_play_pause_base(self):
				if self.customspeed:
						self.synchronize_time()  # required
						self.customspeed = False
						pyglet.clock.unschedule(self.update_customspeed)
				if self.playing_reversed:
						self.playing_reversed = False
						pyglet.clock.unschedule(self.update_reversed)
				if self.player.playing:
						self.setMessage('PAUSE ||', forceRedraw = True)
						self.player.pause()
						pyglet.clock.unschedule(self.update)
				else:
						self.setMessage('PLAY >')
						if self.player.source.get_next_video_timestamp() >= self.player.source.duration - 0.1:
								# seek to the beginning
								self.seek(0.001)
						self.player.play()
						pyglet.clock.schedule(self.update)
				self.on_draw()
				return

		def customspeed_play_pause(self):
				if self.player.playing:
						self.player.pause()
						pyglet.clock.unschedule(self.update)
				if self.playing_reversed:
						self.playing_reversed = False
						pyglet.clock.unschedule(self.update_reversed)
				if self.customspeed:
						self.synchronize_time()  # required
						self.setMessage('PAUSE ||', forceRedraw = True)
						self.customspeed = False
						pyglet.clock.unschedule(self.update_customspeed)
						if self.pausecallback is not None:
								self.pausecallback(self.player.time)
				else:
						self.setMessage('CUSTOM SPEED PLAYING')
						if self.player.source.get_next_video_timestamp() >= self.player.source.duration - 0.1:
								# seek to the beginning
								self.seek(0.001)
						if self.playcallback is not None:
								self.playcallback(self.player.time)
						self.customspeed = True
						self.update_customspeed()
				return

		def on_player_eos(self):
				pyglet.clock.unschedule(self.update)
				pyglet.clock.unschedule(self.update_customspeed)
				return

		def seek_base(self, value, seekback = False):
				"""
				Seek video to the given timestamp.

				self.player.seek() searches for _keyframes_ right after the timestamp,
				however, there is no keyframe for every video frame. Therefore, `searchstep`
				must be substracted for correct positioning, and then the desired video frame
				can be searched step-by-step. A proper `searchstep` value is found by a
				linear searching algorithm.

				The objects' seek time `objseektime` is usually set to the desired timestamp
				(i.e., `value`), however, if the previous frame is requested, it is set to
				the timestamp of the previous frame. (The situation is the same with the next
				frame, but that is implemented in self.step().)

				:Parameters:
					value : float
						Timestamp to seek to.
					seekback : bool
						Seek other navigators or not.
				"""
				if value <= 0.0:
						# seek to the beginning
						self.player.seek(-1.0)  # < 0.0 required
						self.player._timestamp = 0.0
						self.player._last_video_timestamp = 0.0  # MOD by BA
						self.objseektime = 0.0
				else:
						stepback = (value == self.player.time)  # important
						value = min(value, self.player.source.duration)
						self.player.seek(value)
						self.synchronize_time()  # required
						ts = self.player.source.get_next_video_timestamp()
						searchstep = 0.0
						# seek to the proper keyframe
						while ts is None or ts >= value:
								searchstep += 0.1
								if searchstep >= value:
										self.player.seek(-1.0)  # < 0.0 required
										self.player._timestamp = 0.0
										self.player._last_video_timestamp = 0.0  # MOD by BA
										break
								if searchstep > self.keyframegap:
										# worst-case limit for searching backwards
										self.logger.info('Cannot seek video to timestamp %f' % value)
										break
								self.player.seek(value - searchstep)
								ts = self.player.source.get_next_video_timestamp()
						last_img = None
						# seek exactly to the desired video frame
						while True:
								last_ts = ts
								ts = self.player.source.get_next_video_timestamp()
								if ts is None or ts >= value:
										break
								last_img = self.player.source.get_next_video_frame()
						if last_img is not None:
								self.player._texture.blit_into(last_img, 0, 0, 0)
								self.player._timestamp = last_ts
								self.player._last_video_timestamp = last_ts
						self.objseektime = last_ts if stepback else value

				self.fpsCalculator.tickReset()
				self.on_draw()
				return

		def synchronize_time(self):  # time synchronizer
				ts = self.player.source.get_next_video_timestamp()
				if self.player._audio_player is not None:
						self.player._audio_player.stop()
						self.player._audio_player._time = ts
						self.player._audio_player.play()

		def update(self, dt):
				if self.player.time >= self.player.source.duration - 0.1:  # required to check EOS
						self.on_play_pause()
						self.on_player_eos()
				self.fpsCalculator.tick(self.player._last_video_timestamp)
				self.objseektime = self.player.time
				self.on_draw()
				if self.seekbackduringplayback and self.seekcallback is not None:
						self.seekcallback(self.player.time)
				return

		def update_customspeed(self, dt = 0.0):
				if self.player.time >= self.player.source.duration - 0.1:  # required to check EOS
						self.customspeed_play_pause()
						self.on_player_eos()
				frameGap = self.fpsCalculator.getFrameGap() / self.speed
				if self.customspeed:
						pyglet.clock.schedule_once(self.update_customspeed, frameGap)
				nSteps = int(round(dt / frameGap))
				self.step(self.seekbackduringplayback, nSteps)
				return


if __name__ == '__main__':
		import optparse

		parser = optparse.OptionParser()
		parser.add_option('-v', '--video',
											help = 'video file, default is %default',
											default = 'd:/measurement/dataeval-test/CVR3_B1_2011-02-10_16-53_020.avi')
		opts, args = parser.parse_args()

		if pyglet.version == '1.1.4':
				window = cVideoPlayer32(opts.video)
		elif pyglet.version == '1.2.4':
				window = cVideoPlayer64(opts.video)
		window.set_visible(True)
		pyglet.app.run()
