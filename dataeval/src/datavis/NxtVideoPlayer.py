# coding=utf-8
import StringIO
import datetime
import logging
import os
import sys
import time
from collections import OrderedDict
from threading import Thread
import math

import OpenGL.GLUT
import cv2
import numpy as np
import pytz
from OpenGL import GL
from OpenGL.GLU import *
from PIL import Image
from PySide import QtCore, QtGui, QtOpenGL
from PySide.QtCore import QEvent, QObject, QSize, Qt
from PySide.QtGui import QDesktopWidget, QFileDialog, QApplication, QDialog, \
	QDialogButtonBox, QFont, QFormLayout, QGroupBox, QHBoxLayout, QHeaderView, \
	QIcon, \
	QLabel, \
	QLineEdit, QMessageBox, \
	QPushButton, \
	QRadioButton, QSizePolicy, \
	QSlider, \
	QSpacerItem, \
	QStandardItem, QStandardItemModel, QStyle, \
	QStyleOptionSlider, QTreeView, QVBoxLayout, QFrame

import Group
import NxtOpenGLutil
import NxtOverlayShape
import figlib
from TrackNavigator import COLOR_NONE, NO_COLOR
from calibration_data import cCalibrationData

IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")

KeyTable = {}
AtoZ = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
_0to_9 = [chr(i) for i in range(ord('0'), ord('9') + 1)]
KeyCodes = [[c, c] for c in AtoZ]
KeyCodes += [[c, c] for c in _0to_9]
KeyTable.update(KeyCodes)
del KeyCodes, _0to_9, AtoZ

logger = logging.getLogger()


class IntEmittingSignal(QtCore.QObject):
		signal = QtCore.Signal(int)


class FloatEmittingSignal(QtCore.QObject):
		signal = QtCore.Signal(float)


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
				self.fontColor = (0, 0, 0)
				self.backgroundColor = (255, 255, 255, 220)

				# background
				GL.glDisable(GL.GL_TEXTURE_2D)
				GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
				GL.glEnable(GL.GL_BLEND)
				GL.glBegin(GL.GL_QUADS)
				GL.glColor4ub(*self.backgroundColor)
				GL.glVertex2f(x1, y1)
				GL.glVertex2f(x1, y2)
				GL.glVertex2f(x2, y2)
				GL.glVertex2f(x2, y1)
				GL.glEnd()
				GL.glDisable(GL.GL_BLEND)
				GL.glEnable(GL.GL_TEXTURE_2D)

				if not self.markers:
						# warning if nothing to show
						GL.glPushMatrix()
						GL.glTranslatef(x1 + 6 * self.innerMargin, y2 - 5 * self.innerMargin, 0.0)
						GL.glScalef(self.textSize, self.textSize, 0.0)
						NxtOpenGLutil.drawString('No objects to display', color = self.fontColor)
						GL.glPopMatrix()
				else:
						# objects and labels
						GL.glColor3ub(*self.fontColor)
						GL.glPushMatrix()
						GL.glTranslatef(x1 + 4 * self.innerMargin, y2 - self.innerMargin, 0.0)
						GL.glScalef(self.textSize, self.textSize, 0.0)
						for (label, style) in self.markers:
								self.shapes.draw(style[0]['shape'], NxtOpenGLutil.EDGE)  # draw object
								GL.glTranslatef(self.dx, 0.0, 0.0)
								GL.glPushMatrix()
								NxtOpenGLutil.drawString(label, color = self.fontColor, font = self.fontFamily)  # draw label
								GL.glPopMatrix()
								GL.glTranslatef(-self.dx, -self.dy, 0.0)
						GL.glPopMatrix()
				return

		def display_video_timestamp(self, video_timestamp):
				"""Render video timestamp labels in an OpenGL context.

				:Assumptions:
					OpenGL viewport and matrix modes are set properly for GUI drawing.
				"""

				x1 = self.x
				y1 = self.y
				x2 = self.x + self.width
				y2 = self.y + self.height
				self.fontColor = (255, 0, 0)
				self.backgroundColor = (255, 255, 255, 0)

				# background
				GL.glDisable(GL.GL_TEXTURE_2D)
				GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
				GL.glEnable(GL.GL_BLEND)

				GL.glColor3ub(*self.fontColor)
				GL.glPushMatrix()
				GL.glTranslatef(x1 - 2.4 * self.innerMargin, y2 - (self.innerMargin - 5), 0.0)
				GL.glScalef(self.textSize, self.textSize, 0.0)
				GL.glTranslatef(self.dx, 0.0, 0.0)
				GL.glPushMatrix()
				NxtOpenGLutil.drawString(video_timestamp, color = self.fontColor, font = self.fontFamily)  # draw label
				GL.glPopMatrix()
				GL.glTranslatef(-self.dx, -self.dy, 0.0)
				GL.glPopMatrix()
				GL.glDisable(GL.GL_BLEND)
				GL.glEnable(GL.GL_TEXTURE_2D)
				return

		def draw_ldw_legends(self, ldw_configuration):
				"""Render objects and their labels in an OpenGL context.

				:Assumptions:
					OpenGL viewport and matrix modes are set properly for GUI drawing.
				"""
				count = 1
				self.ldw_labels = ["Red   : Origin, Zero marker",
													 "Purple : Tire width (cm) from origin (RED mark)",
													 "Blue  : Distance from origin\t= {}cm \n\tDistance from Purple mark= {}cm".format(
																	 ldw_configuration.scale_len,
																	 ldw_configuration.scale_len - ldw_configuration.tire_width)]

				x1 = self.x
				y1 = self.y
				x2 = self.x + self.width
				y2 = self.y + self.height

				self.backgroundColor = (255, 255, 255, 100)
				self.fontFamily = OpenGL.GLUT.GLUT_STROKE_ROMAN
				self.fontColor = (255, 0, 0)

				# background
				GL.glDisable(GL.GL_TEXTURE_2D)
				GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
				GL.glEnable(GL.GL_BLEND)
				GL.glBegin(GL.GL_QUADS)
				GL.glColor4ub(*self.backgroundColor)
				GL.glVertex2f(x1, y1)
				GL.glVertex2f(x1, y2)
				GL.glVertex2f(x2, y2)
				GL.glVertex2f(x2, y1)
				GL.glEnd()
				GL.glDisable(GL.GL_BLEND)

				GL.glColor3ub(*self.fontColor)
				GL.glPushMatrix()
				GL.glTranslatef(x1, y2 - self.innerMargin, 0.0)
				GL.glScalef(self.textSize, self.textSize, 0.0)
				for label in self.ldw_labels:
						GL.glTranslatef(self.dx, 0.0, 0.0)
						GL.glPushMatrix()
						NxtOpenGLutil.drawString(label, color = self.fontColor, font = self.fontFamily)  # draw label
						count = count + 1  # Counter to change color for each label.
						GL.glPopMatrix()
						GL.glTranslatef(-self.dx, -self.dy, 0.0)
						if count == 2:
								self.fontColor = (128, 0, 128)
						elif count == 3:
								self.fontColor = (0, 0, 255)
				GL.glPopMatrix()
				GL.glEnable(GL.GL_TEXTURE_2D)
				return


class cNxtVideoPlayer(QtOpenGL.QGLWidget, Group.iGroup):

		def __init__(self, file_name, calibrations, slave, group = None, parent = None):
				QtOpenGL.QGLWidget.__init__(self, QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers), parent)
				Group.iGroup.__init__(self, KeyTable)
				self.slave = slave  # and not self.slave
				self.filename = file_name
				self.capture = cv2.VideoCapture(self.filename)
				self.total_frames = self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
				self.fps = self.capture.get(cv2.cv.CV_CAP_PROP_FPS)
				self.video_width = self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)  # float `width`
				self.video_height = self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

				self.video_image_width = self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)  # float `width`
				self.video_image_height = self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
				# Camera calib params
				self.calibration = False

				act_calib = calibrations.get_calibration(file_name)
				if group is not None:
					if group == 'SLR25_RFB':
						act_calib = cCalibrationData(0.500, 3.500, 45.000, 640.000, 480.000, 45.000, 16.000, 15.000, 364.000)
					elif group == 'SLR25_Front':
						act_calib = cCalibrationData(-0.110, 1.600, 0.130, 640.000, 480.000, 36.300, -0.140, -0.110, 0.050)
				self.setCalibration(act_calib)

				self.calib_init_step = 0.001

				self.objseektime = 0.0
				self.objects = None
				self.objects = []
				self.times = []
				self.disptime = 0.0
				self.accelcomp = None
				# self.video_width = 640
				# self.video_height = 480
				# self.GUI_WIDTH = 640
				# self.GUI_HEIGHT = 480
				# self.GUI_PADDING = 4
				# self.SLIDER_HEIGHT = 14
				self.sample_aspect = 1.0
				# self.mx = 0
				# self.my = 0

				# LDW-overlay parameters
				self.ldw_tire_mode = False
				self.ldw_tire_overlay_calib = None

				# Overlay lanes
				self.lanesenabled = True
				self.lanes = []
				self.lanetodisplay = -1

				self.Markers = {}
				self.shapes = None
				# self.legend = cVideoLegend()
				self.external_markers = None

				self.video_thread = Thread(target = self.frame_update, args = ())

				self.display_sync_times = None
				self.current_frame = None
				self.image_frame = None
				self.X_AXIS = 0.0
				self.Y_AXIS = 0.0
				self.Z_AXIS = 0.0
				self.texture_id = 0
				self.sync_time = 0.0
				# self.setWindowTitle(self.tr("Play Video With Overlay"))
				self.startTimer(1)
				self.current_state = 'pause'
				self.previous_state = 'pause'
				self.frame_rate = 0
				self.current_index = 0
				self.seek_time = 0.0
				self.current_time = 0.0

				self.offset_x = -1
				self.offset_y = -1

				self.gl_width = 0
				self.gl_height = 0

				self.main_gl_widget_height = 0
				self.main_gl_widget_width = 0
				# Callbacks
				self.seekcallback = None
				self.playcallback = None
				self.pausecallback = None
				self.closecallback = None
				self.seekbackduringplayback = False

				if self.slave:
						self.seekbackduringplayback = True
				self.prepare_video_size()
				# print(self.GUI_WIDTH)
				# print(self.GUI_HEIGHT)
				# self.set_size(self.GUI_WIDTH, self.GUI_HEIGHT)
				self.helplabel = OrderedDict([
						("space", "Toggle play/pause "),
						("s", "Custom speed slow "),
						("f", "Custom speed fast "),
						("->", "Forward  step frame by framforward search if held "),
						("<-", "Backward step frame by framebackward search if held "),
						("p", "Play reverse frame by frame"),
						("r", "Toggle refresh of other navigators during playback"),
						("n", "Toggle lanes on/off"),
						("l", "Toggle object labels on/off"),
						("x", "Toggle object short labels on/off"),
						("b", "Toggle video background image on/off "),
						("u", "Toggle video background undistorted image on/off"),
						("t", "Toggle time label on/off"),
						("c", "Toggle between calibration presets "),
						("f10", "Print current time in log window and copy to notepad")
				])

				self.labellevel = 0
				self.shortenlabel = False
				self.maxDisplDist = 100
				self.showstatuslabel = False
				self.statuslabel = {}

				# Toggle video background image
				self.toggleVideoImage = True

				# Toggle distortion / undistortion
				self.undistortimage = False

				self.imagedata_emitting_signal = ObjectEmittingSignal()
				self.current_index_changed = IntEmittingSignal()
				self.current_timestamp_changed = FloatEmittingSignal()
				self.calibNavNeededSignal = ObjectEmittingSignal()
				self.manual_calib_updated = SimpleSignal()
				self.ldw_tire_calib_signal_show = ObjectEmittingSignal()
				self.ldw_tire_calib_signal_close = SimpleSignal()

				self.showtimelabel = True
				self.showLegend = False
				self.showLdwLegend = False
				self.legend = cVideoLegend()

		# self.Shapes = NxtOverlayShape.Shapes(NxtOpenGLutil.allShapeBuildProps)

		# <editor-fold desc="Player Threading">
		def start(self):
				self.video_thread.start()

		def frame_update(self):
				while True:
						if self.current_index == self.total_frames:
								self.current_index = 0
								self.current_state = 'pause'
						self.capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, self.current_index)
						self.current_time = self.capture.get(cv2.cv.CV_CAP_PROP_POS_MSEC) / 1000

						if self.display_sync_times is not None:

								displaytime, displaytimevalue = self.display_sync_times
								self.disptime = np.interp([self.current_time], displaytimevalue,
																					displaytime)[0]
						else:
								self.disptime = self.current_time
						self.current_timestamp_changed.signal.emit(self.disptime)
						ret, self.image_frame = self.capture.read()
						if self.undistortimage:
								self.current_frame = self.remove_distortion(self.image_frame)
						else:
								self.current_frame = self.image_frame

						if self.current_state == 'seek':
								self.capture.set(cv2.cv.CV_CAP_PROP_POS_MSEC, self.seek_time * 1000)
								self.current_index = self.capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
								self.current_state = self.previous_state
								# self.current_index_changed.signal.emit(self.current_index)
								self.current_time = self.capture.get(cv2.cv.CV_CAP_PROP_POS_MSEC) / 1000
								if self.seekcallback is not None and self.seekbackduringplayback:
										self.seekcallback(self.current_time)
						if self.current_state == 'play':
								self.current_index_changed.signal.emit(self.current_index)
								time.sleep((1 / self.fps) + self.frame_rate)
								if self.seekcallback is not None and self.seekbackduringplayback:
										self.seekcallback(self.current_time)
								self.current_index += 1
								continue
						if self.current_state == 'playreverse':
								self.current_index_changed.signal.emit(self.current_index)
								time.sleep((1 / self.fps) + self.frame_rate)
								if self.seekcallback is not None and self.seekbackduringplayback:
										self.seekcallback(self.current_time)
								if self.current_index > 0:
										self.current_index -= 1
								else:
										self.current_state = 'pause'
								continue
						if self.current_state == 'pause':
								self.current_index_changed.signal.emit(self.current_index)
								if self.seekcallback is not None and self.seekbackduringplayback:
										self.seekcallback(self.current_time)
						if self.current_state == 'exit':
								break
						if self.current_state == 'prev_frame':
								self.current_index -= 1
								self.current_index_changed.signal.emit(self.current_index)
								self.current_state = 'pause'
						if self.current_state == 'next_frame':
								self.current_index += 1
								self.current_index_changed.signal.emit(self.current_index)
								self.current_state = 'pause'
						if self.current_state == 'slow':
								self.frame_rate += -(self.frame_rate) + 0.1
								self.current_state = 'play'
						if self.current_state == 'fast':
								self.frame_rate -= self.frame_rate + 0.05
								self.current_state = 'play'
						if self.current_state == 'snap':
								tx_image = Image.fromarray(self.current_frame)
								tx_image.save(self.file_path, 'PNG')
								self.current_state = 'pause'
				self.capture.release()
				cv2.destroyAllWindows()

		def client_frame_update(self):

				if self.current_state == 'seek':
						self.capture.set(cv2.cv.CV_CAP_PROP_POS_MSEC, self.seek_time * 1000)
						self.current_index = self.capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
						self.current_state = self.previous_state
						# self.current_index_changed.signal.emit(self.current_index)
						self.current_time = self.capture.get(cv2.cv.CV_CAP_PROP_POS_MSEC) / 1000

				if self.current_state == 'play':
						self.current_index_changed.signal.emit(self.current_index)
						time.sleep((1 / self.fps) + self.frame_rate)
						self.current_index += 1
				if self.current_state == 'pause':
						self.current_index_changed.signal.emit(self.current_index)

				if self.current_state == 'prev_frame':
						self.current_index -= 1
						self.current_index_changed.signal.emit(self.current_index)
						self.current_state = 'pause'
				if self.current_state == 'next_frame':
						self.current_index += 1
						self.current_index_changed.signal.emit(self.current_index)
						self.current_state = 'pause'
				if self.current_state == 'slow':
						self.frame_rate += -(self.frame_rate) + 0.1
						self.current_state = 'play'
				if self.current_state == 'fast':
						self.frame_rate -= self.frame_rate + 0.05
						self.current_state = 'play'
				if self.current_state == 'snap':
						tx_image = Image.fromarray(self.current_frame)
						tx_image.save(self.file_path, 'PNG')
						self.current_state = 'pause'

				if self.current_index == self.total_frames:
						self.current_index = 0
						self.current_state = 'pause'
				self.capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, self.current_index)
				self.current_time = self.capture.get(cv2.cv.CV_CAP_PROP_POS_MSEC) / 1000

				if self.display_sync_times is not None:
						displaytime, displaytimevalue = self.display_sync_times
						self.disptime = np.interp([self.current_time], displaytimevalue,
																			displaytime)[0]
				else:
						self.disptime = self.current_time
				self.current_timestamp_changed.signal.emit(self.disptime)
				ret, self.image_frame = self.capture.read()
				if self.undistortimage:
						self.current_frame = self.remove_distortion(self.image_frame)
				else:
						self.current_frame = self.image_frame
				if self.seekcallback is not None and self.seekbackduringplayback:
						self.seekcallback(self.current_time)

		# </editor-fold>

		# <editor-fold desc="Player Control functions">
		def play(self):
				self.previous_state = self.current_state
				self.frame_rate = 0.0
				self.current_state = 'play'
				if self.slave:
						self.client_frame_update()

		# if self.playcallback is not None:
		# 		self.playcallback(self.current_time)

		def remove_distortion(self, rawimage):
				width = rawimage.shape[1]
				height = rawimage.shape[0]

				# assume unit matrix for camera
				camera_matrix = np.eye(3, dtype = np.float32)
				camera_matrix[0, 2] = width / 2.0  # define center x
				camera_matrix[1, 2] = height / 2.0  # define center y
				camera_matrix[0, 0] = 690.0  # define focal length x
				camera_matrix[1, 1] = 300.0  # define focal length y

				# TODO: add your coefficients here!
				k1 = -0.2  # negative to remove barrel distortion
				k2 = 0.0
				p1 = 0.0
				p2 = 0.0

				dist_coefs = np.zeros((4, 1), np.float64)
				dist_coefs[0, 0] = k1
				dist_coefs[1, 0] = k2
				dist_coefs[2, 0] = p1
				dist_coefs[3, 0] = p2
				image = cv2.undistort(rawimage, camera_matrix, dist_coefs)

				return image

		def play_reverse(self):
				self.previous_state = self.current_state
				self.frame_rate = 0.0
				self.current_state = 'playreverse'
				if self.slave:
						self.client_frame_update()

						if self.playcallback is not None:
								self.playcallback(self.current_time)

		def pause(self):
				self.previous_state = self.current_state
				self.current_state = 'pause'
				if self.slave:
						self.client_frame_update()

		# if self.pausecallback is not None:
		# 		self.pausecallback(self.current_time)

		def seek(self, time):
				self.previous_state = self.current_state
				self.current_state = 'seek'
				self.seek_time = time
				if self.slave:
						self.client_frame_update()

		def snap(self):
				self.previous_state = self.current_state
				self.current_state = 'snap'
				self.file_path = "abc.png"

		def stepback(self):
				self.previous_state = self.current_state
				self.current_state = 'prev_frame'
				if self.slave:
						self.client_frame_update()

		def stepforward(self):
				self.previous_state = self.current_state
				self.current_state = 'next_frame'
				if self.slave:
						self.client_frame_update()

		def speedfast(self):
				self.previous_state = self.current_state
				self.current_state = 'fast'
				if self.seekcallback is not None and self.seekbackduringplayback:
						self.seekcallback(self.current_time)

		def speedslow(self):
				self.previous_state = self.current_state
				self.current_state = 'slow'
				if self.seekcallback is not None and self.seekbackduringplayback:
						self.seekcallback(self.current_time)

		def copyContentToFile(self, file, format = 'png'):
				width = self.main_gl_widget_width
				height = self.main_gl_widget_height
				pixelset = (GL.GLubyte * (3 * width * height))(0)
				GL.glReadPixels(0, 0, width, height, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, pixelset)
				image = Image.fromstring(mode = "RGB", size = (width, height), data = pixelset)
				image = image.transpose(Image.FLIP_TOP_BOTTOM)

				if isinstance(file, basestring):  # 'file' is the name of the file
						with open(file, 'wb') as f:
								image.save(f, format)
				else:  # 'file' is a file-like object
						image.save(file, format)
				return

		def copyContentToClipboard(self):
				imageFileAsPng = StringIO.StringIO()

				width = self.main_gl_widget_width
				height = self.main_gl_widget_height
				pixelset = (GL.GLubyte * (3 * width * height))(0)
				GL.glReadPixels(0, 0, width, height, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, pixelset)
				image = Image.frombytes(mode = "RGB", size = (width, height), data = pixelset)
				image = image.transpose(Image.FLIP_TOP_BOTTOM)

				im_rgb = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
				Image.fromarray(im_rgb).save(imageFileAsPng, 'png')

				imageFileAsPng.seek(0)
				# Crop
				self.imagedata_emitting_signal.signal.emit(imageFileAsPng)
				return

		def on_close(self):
				w, h = self.size().toTuple()
				x, y = self.pos().toTuple()

				geometry = figlib.buildGeometryString(x, y, w, h)

				self.pause()

				if self.closecallback is not None:
						self.closecallback(geometry)
				self.close()

				if self.slave:
						self.capture.release()
						cv2.destroyAllWindows()
				elif self.video_thread.is_alive():
						self.current_state = 'exit'
						self.video_thread.join()
				return

		def setcallbacks(self, seekcallback, playcallback, pausecallback, closecallback):
				self.seekcallback = seekcallback
				self.playcallback = playcallback
				self.pausecallback = pausecallback
				self.closecallback = closecallback
				return

		def slider_seek(self, index):
				self.current_index = index
				if self.slave:
						self.client_frame_update()

		# print("Received" + str(index))

		# </editor-fold>

		# <editor-fold desc="Overloaded Methods">
		def initializeGL(self):
				# GL.glEnable(GL.GL_BLEND)
				# # GL.glDisable(GL.GL_BLEND)
				# GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
				# GL.glViewport(0, 0, int(self.video_width), int(self.video_height))
				# self.sample_aspect = round((self.video_width / self.video_height), 1)
				GL.glClearColor(0.0, 0.0, 0.0, 1.0)
				GL.glClearDepth(1.0)
				# GL.glDepthFunc(GL.GL_LESS)
				# GL.glEnable(GL.GL_DEPTH_TEST)
				# GL.glShadeModel(GL.GL_SMOOTH)
				# GL.glMatrixMode(GL.GL_PROJECTION)
				# GL.glLoadIdentity()
				# gluPerspective(45.0, self.sample_aspect, 1.0, 1000.0)
				# GL.glMatrixMode(GL.GL_MODELVIEW)
				GL.glEnable(GL.GL_TEXTURE_2D)

				self.texture_id = GL.glGenTextures(1)
				self.Shapes = NxtOverlayShape.Shapes(NxtOpenGLutil.allShapeBuildProps)

				if self.external_markers:
						self.Markers = self.external_markers
						self.legend.setMarkers(self.Shapes, self.external_markers)

		def timerEvent(self, event):
				self.update()

		def resizeGL(self, width, height):
				if height == 0:
						return
				self.main_gl_widget_height = height
				self.main_gl_widget_width = width
				self.gl_width = width
				self.gl_height = height
				ratioImg = float(self.video_image_width) / self.video_image_height
				ratioScreen = float(self.gl_width) / self.gl_height
				orig_width = self.gl_width
				orig_height = self.gl_height

				if ratioImg > ratioScreen:
						self.gl_height = self.gl_width / ratioImg
				else:
						self.gl_width = self.gl_height * ratioImg

				self.offset_x = 0 + (orig_width - self.gl_width) * 0.5
				self.offset_y = 0 + (orig_height - self.gl_height) * 0.5

				self.legend.on_resize((self.offset_x, self.offset_y, self.gl_width, self.gl_height))

		def paintGL(self):
				GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
				GL.glColor3ub(255, 255, 255)
				GL.glViewport(0, 0, self.main_gl_widget_width, self.main_gl_widget_height)
				# convert image to OpenGL texture format
				if self.current_frame is not None:
						if self.toggleVideoImage:
								tx_image = self.current_frame
						else:
								tx_image = np.zeros((512, 512, 3), dtype = "uint8")
						tx_image = Image.fromarray(tx_image)
						ix = tx_image.size[0]
						iy = tx_image.size[1]
						tx_image = tx_image.tobytes('raw', 'BGRX', 0, -1)

						# Setup texture
						GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)
						GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
						GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
						GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
						GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
						GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
						GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, ix, iy, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, tx_image)

						# Set 2D mode
						GL.glMatrixMode(GL.GL_PROJECTION)
						GL.glLoadIdentity()
						gluOrtho2D(0, self.main_gl_widget_width, 0, self.main_gl_widget_height)
						GL.glMatrixMode(GL.GL_MODELVIEW)
						GL.glLoadIdentity()
						GL.glBegin(GL.GL_QUADS)
						GL.glTexCoord2d(0.0, 0.0)
						GL.glVertex3f(self.offset_x, self.offset_y, 0.0)
						GL.glTexCoord2d(1.0, 0.0)
						GL.glVertex3f(self.offset_x + self.gl_width, self.offset_y, 0.0)
						GL.glTexCoord2d(1.0, 1.0)
						GL.glVertex3f(self.offset_x + self.gl_width, self.offset_y + self.gl_height, 0.0)
						GL.glTexCoord2d(0.0, 1.0)
						GL.glVertex3f(self.offset_x, self.offset_y + self.gl_height, 0.0)
						GL.glEnd()
						ndxs = self.seekTimes(self.disptime)
						self.nds = ndxs

						if self.showLegend:
								self.legend.draw()

						if self.showLdwLegend:
								self.legend.draw_ldw_legends(self.ldw_tire_overlay_calib)

						if self.showtimelabel:
								timestamp = str("%.3f" % self.disptime)
								self.legend.display_video_timestamp(timestamp)

						self.on_draw()

		def on_draw(self):
				self.draw_objects(self.nds)

		def setDisplayTime(self, diplaytime, diplaytimevalue):
				self.display_sync_times = diplaytime, diplaytimevalue
				return

		# </editor-fold>
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

				# self.statuslabel = "\n".join(self.Labels)
				status_key = []
				status_value = []
				if len(self.Labels) != 0:
						for label in self.Labels:
								status_key.append(label.split(':')[0])
						for label in self.Labels:
								status_value.append(label.split(':')[1])
						self.statuslabel = OrderedDict(zip(status_key, status_value))

				if return_result:
						self.selectGroupCallback(GroupName)
				return

		def selectGroupCallback(self, GroupName):
				return

		# <editor-fold desc="Object and Lane Overlay functions">
		def setLegend(self, Markers):
				self.external_markers = Markers.copy()  # shallow copy
				# if self.external_markers:
				# 		self.Markers = self.external_markers
				# 		self.legend.setMarkers(self.Shapes, self.external_markers)
				return

		def setobjects(self, objecttime, objectlist):
				for object in objectlist:
						if 'shape' not in object:
								self.setObject(objecttime, object)
				return

		def setObject(self, objecttime, object):
				time_idx = self._addTime(objecttime)
				self.objects.append((object, time_idx))
				return

		def _addTime(self, time):
				for i, t in enumerate(self.times):
						if np.array_equal(t, time):
								break
				else:
						i = len(self.times)
						self.times.append(time)
				return i

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

		def draw_objects(self, ndxs):
				if self.ldw_tire_mode and self.ldw_tire_overlay_calib is not None:
						self.draw_ldw_tire_overlay()
				# GL.glDisable(GL.GL_BLEND)
				if (not self.objects and not self.lanesenabled) or not self.times:
						return
				# try:
				# Get index of objects according to video time
				# # Set 3D rendering parameters
				GL.glViewport(int(self.offset_x), int(self.offset_y), int(self.gl_width), int(self.gl_height))
				# Set 3D mode
				GL.glMatrixMode(GL.GL_PROJECTION)
				# GL.glPushMatrix()
				GL.glLoadIdentity()
				gluPerspective(
								self.cali.fov,  # Field Of View
								float(self.video_image_width) / float(self.video_image_height),  # aspect ratio
								1.0,  # z near
								1000.0)  # z far
				GL.glMatrixMode(GL.GL_MODELVIEW)
				GL.glLoadIdentity()

				atx = self.cali.looktox
				aty_accelcomp = 0.0
				if self.accelcomp:
						accelcomp, time_idx = self.accelcomp
						ndx = ndxs[time_idx]
						aty_accelcomp = accelcomp[ndx]
				aty = self.cali.cameray + self.cali.looktoy + aty_accelcomp
				atz = -1.0
				gluLookAt(
								self.cali.camerax, self.cali.cameray, self.cali.cameraz,
								atx, aty, atz,
								self.cali.upx, 1.0, 0.0,
				)

				# Draw calibration reference if necessary
				if self.lanesenabled:
						self.draw_lanes(ndxs)
				# if self.calibration:
				# 		self.draw_reference()
				# Field of view rendering
				# if self.showFOV:
				# 		GL.glColor3ub(255, 0, 0)
				# 		GL.glLineWidth(1)
				# 		shapeName = self.FOVs[self.FOVindex]
				# 		self.Shapes.draw(shapeName, NxtOpenGLutil.EDGE)

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
										logger.info('Missing drawing data, shape cannot be drawn.')
										continue
								if Type in self.Invisibles:
										continue
						else:
								continue
						dx = o["dx"][ndx]
						dy = o["dy"][ndx]
						try:
							dz = o["dz"][ndx]
						except:
						  dz = 0
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
								if self.shortenlabel:
										labelList = label.split("_")
										try:
												label = labelList[-3] + labelList[-2]
										except:
												pass
						else:
								label = None
						isDrawable = True

						# object coord transformation: radar -> OpenGL
						X, Y, Z = -dy, dz, -dx
						GL.glPushMatrix()
						GL.glTranslatef(X, Y, Z)

						# TEST: check object's real position (without height information)
						# GL.glLineWidth(2)
						# GL.glColor3ub(255,140,0)
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
												logger.info('LegendValues does not contain type: %d!\n' % Type)
										else:
												color = style['color']
												styleColor = True
								if alpha is None:
										alpha = style['alpha'] if style.has_key('alpha') else None
								# transparency only in case of surfaces
								GL.glDisable(GL.GL_TEXTURE_2D)
								GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
								GL.glEnable(GL.GL_BLEND)

								if alpha and NxtOpenGLutil.FACE == shapeType:
										GL.glColor4ub(color[0], color[1], color[2], alpha)
								else:
										GL.glColor3ub(color[0], color[1], color[2])
								# set line width
								lineWidth = style['lw'] if style.has_key('lw') else None
								if lineWidth:
										GL.glLineWidth(lineWidth)

								# draw the shape
								self.Shapes.draw(shapeName, shapeType)

								GL.glDisable(GL.GL_BLEND)

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
								NxtOpenGLutil.drawString(label,
																				 scale = scaleVec)  # extra properties supported (e.g. text translation,
						# rotation, color, transparency)
						GL.glEnable(GL.GL_TEXTURE_2D)
						GL.glPopMatrix()
				# Reset rendering parameters
				# GL.glPopMatrix()
				# GL.glMatrixMode(GL.GL_PROJECTION)
				# GL.glPopMatrix()
				# except GLException, e:
				# 		logger.error('OpenGL exception caught during object rendering, message: %s' % e.message)
				# except Exception, e:
				# 		logger.error('Exception caught during object rendering, message: %s' % e.message)
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
								GL.glDisable(GL.GL_TEXTURE_2D)
								GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
								GL.glEnable(GL.GL_BLEND)

								GL.glColor4ub(color[0], color[1], color[2], alpha)
								GL.glBegin(GL.GL_QUAD_STRIP)

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
										GL.glVertex3f(x1, 0.0, y1)
										GL.glVertex3f(x4, 0.0, y4)
										GL.glVertex3f(x2, 0.0, y2)
										GL.glVertex3f(x3, 0.0, y3)
								GL.glEnd()
								GL.glDisable(GL.GL_BLEND)
								GL.glEnable(GL.GL_TEXTURE_2D)
				return

		def draw_ldw_tire_overlay(self):
				# For handling and readability purposes
				LENGTH = self.ldw_tire_overlay_calib.length
				X = self.ldw_tire_overlay_calib.x
				Y = self.ldw_tire_overlay_calib.y
				PCNT_ZM = self.ldw_tire_overlay_calib.zero_mark_offset
				PCNT_TW = self.ldw_tire_overlay_calib.tw_mark_offset

				MARK_SIZE = self.gl_height / 16.0
				ANGLE_ROT = self.ldw_tire_overlay_calib.rotation

				BOX_WDT = self.gl_width / 16.0
				BOX_HT = self.gl_height / 17.0

				# Overall figure settings

				GL.glDisable(GL.GL_TEXTURE_2D)
				GL.glLineWidth(3)
				GL.glPushMatrix()
				GL.glTranslatef(X, Y, 0.0)
				GL.glRotatef(ANGLE_ROT, 0.0, 0.0, 1.0)
				GL.glTranslatef(-X, -Y, 0.0)
				GL.glBegin(GL.GL_LINES)

				# Main Line
				GL.glColor3f(1, 1, 0)
				GL.glVertex2f(X, Y)
				GL.glVertex2f(X + LENGTH, Y)

				# Zero Mark
				GL.glColor3f(0.9, 0.0, 0.0)
				zm_x = X + (LENGTH * PCNT_ZM / 100.0)
				GL.glVertex2f(zm_x, Y + MARK_SIZE / 2.0)
				GL.glVertex2f(zm_x, Y - MARK_SIZE / 2.0)

				# Tire Width Mark
				GL.glColor3f(0.5, 0.0, 0.5)
				tw_x = X + (LENGTH * PCNT_TW / 100.0)
				GL.glVertex2f(tw_x, Y + MARK_SIZE / 2.0)
				GL.glVertex2f(tw_x, Y - MARK_SIZE / 2.0)

				# X CM Mark
				GL.glColor3f(0.0, 0.1, 0.9)
				xcm_x = zm_x - self.ldw_tire_overlay_calib.get_size_x_offset_to_right(self.ldw_tire_overlay_calib.scale_len)
				GL.glVertex2f(xcm_x, Y + MARK_SIZE / 2.5)
				GL.glVertex2f(xcm_x, Y - MARK_SIZE / 2.5)

				# Wrapping up
				GL.glEnd()

				# Boxes and text
				# TODO: activation in GUI
				y_boxes = Y + MARK_SIZE / 1.5

				GL.glPopMatrix()
				GL.glEnable(GL.GL_TEXTURE_2D)
				return

		def gettime(self):
				return self.current_time

		def getTimeFromIndex(self, index):
				time = index / self.fps
				return time

		def getindexFromRelativeTime(self, time):
				index = time * self.fps
				return index

		def seekTimes(self, seektime):
				ndxs = [max(0, time.searchsorted(seektime, side = 'right') - 1)
								for time in self.times]
				return ndxs

		def setLane(self, lanetime, lane):
				time_idx = self._addTime(lanetime)
				self.lanes.append((lane, time_idx))
				return

		def setLanes(self, lanetime, lanelist):
				for lane in lanelist:
						self.setLane(lanetime, lane)
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

		# </editor-fold>

		def prepare_video_size(self, x = None, y = None):
				if x is None or y is None:
						width, height = self.get_video_size()
				else:
						width, height = x, y

				self.video_width = width
				self.video_height = height
				# self.GUI_WIDTH = width + 2 * self.GUI_PADDING
				# self.GUI_HEIGHT = height  + 2 * self.GUI_PADDING
				# self.video_x = self.GUI_PADDING
				# self.video_y = self.GUI_HEIGHT - self.GUI_PADDING - self.video_height
				return

		def set_video_size(self, x = None, y = None):
				self.prepare_video_size(x, y)
				self.set_size(self.GUI_WIDTH, self.GUI_HEIGHT)
				return

		def get_video_size(self):
				video_width = 1
				video_height = 1
				if self.sample_aspect > 1:
						video_width = self.video_width * self.sample_aspect
				elif self.sample_aspect < 1:
						video_height = self.video_height / self.sample_aspect
				return video_width, video_height


class HeaderViewFilter(QObject):
		def __init__(self, parent, header, *args):
				super(HeaderViewFilter, self).__init__(parent, *args)
				self.sliderValueChanged = FloatEmittingSignal()

				self.header = header

		def eventFilter(self, object, event):
				if event.type() == QEvent.HoverEnter or event.type() == QEvent.HoverMove or event.type() == QEvent.HoverLeave:
						self.sliderValueChanged.signal.emit(self.header.pixelPosToRangeValue(event.pos()))
						return True
				else:
						return super(HeaderViewFilter, self).eventFilter(object, event)


class Slider(QSlider):

		def __init__(self, *args, **kwargs):
				QSlider.__init__(self)
				self.styleprop = """ 

				QSlider::groove:horizontal { 
					background-color: #BABBBA ;
					border: 0px solid #e0ebeb; 
					height: 10px; 
					border-radius: 4px;
				}

				QSlider::handle:horizontal { 					
					border-radius: 4px; 
				}

				QSlider::sub-page:horizontal { 
					border-radius :4px; 
					background-color: #66c2ff;
				}

												"""
				self.setStyleSheet(self.styleprop)

		def mousePressEvent(self, event):
				super(QSlider, self).mousePressEvent(event)
				if event.button() == QtCore.Qt.LeftButton:
						val = self.pixelPosToRangeValue(event.pos())
						self.sliderMoved.emit(val)

		def mouseMoveEvent(self, event):
				super(QSlider, self).mousePressEvent(event)
				if event.button() == QtCore.Qt.NoButton:
						val = self.pixelPosToRangeValue(event.pos())
						self.sliderMoved.emit(val)

		def pixelPosToRangeValue(self, pos):
				opt = QStyleOptionSlider()
				self.initStyleOption(opt)
				gr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
				sr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)

				if self.orientation() == QtCore.Qt.Horizontal:
						sliderLength = sr.width()
						sliderMin = gr.x()
						sliderMax = gr.right() - sliderLength + 1
				else:
						sliderLength = sr.height()
						sliderMin = gr.y()
						sliderMax = gr.bottom() - sliderLength + 1
				pr = pos - sr.center() + sr.topLeft()
				p = pr.x() if self.orientation() == QtCore.Qt.Horizontal else pr.y()
				return QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), p - sliderMin,
																							sliderMax - sliderMin, opt.upsideDown)

		def close(self):
				self.close()


class cNxtVideoPlayerControl(QtGui.QWidget):

		def __init__(self, file_name, calibrations = None, slave = False, group = None):
				QtGui.QWidget.__init__(self)  # call the init for the parent class

				self.objNxtVideoPlayer = cNxtVideoPlayer(file_name, calibrations, slave, group)
				self.slave = slave
				self.calibrations = calibrations
				self.previous_value = 0
				self.measurement_name = "Default"
				self.initGUI()
				self.objNxtVideoPlayer.current_index_changed.signal.connect(self.set_slider_value)

				self.objNxtVideoPlayer.current_timestamp_changed.signal.connect(self.set_timestamp_value)
				self.resize(640, 480)
				self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'video_player_48.png')))

		def initGUI(self):
				sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
				sizePolicy.setHorizontalStretch(0)
				sizePolicy.setVerticalStretch(0)
				# sizePolicy.setHeightForWidth(self.objNxtVideoPlayer.sizePolicy().hasHeightForWidth())
				self.objNxtVideoPlayer.setSizePolicy(sizePolicy)

				gui_layout = QtGui.QVBoxLayout()
				gui_layout.setSpacing(1)
				gui_layout.setContentsMargins(0, 0, 0, 0)
				# central_widget = QtGui.QWidget()
				# central_widget.setLayout(gui_layout)
				# self.setCentralWidget(central_widget)

				gui_layout.addWidget(self.objNxtVideoPlayer)

				# gbox_slider_control = QGroupBox('')
				# hboxlayout_slider_control = QtGui.QHBoxLayout()
				# hboxlayout_slider_control.setSpacing(0)
				# hboxlayout_slider_control.setContentsMargins(1, 1, 1, 1)
				# self.lbl_timer = QLabel("00:00")
				# lbl_signal_name.setPixmap(QPixmap(os.path.join(IMAGE_DIRECTORY, 'search_24.png')))

				# hboxlayout_slider_control.addWidget(self.lbl_timer, 0, Qt.AlignVCenter)
				# lbl_spacer = QLabel("")
				# hboxlayout_slider_control.addWidget(lbl_spacer, 0, Qt.AlignVCenter)

				self.video_slider = Slider()

				self.video_slider.setOrientation(QtCore.Qt.Horizontal)
				self.video_slider.setMinimum(0)
				self.video_slider.setMaximum(self.objNxtVideoPlayer.total_frames)
				self.video_slider.setFocusPolicy(Qt.NoFocus)
				self.filter = HeaderViewFilter(self, self.video_slider)
				self.video_slider.installEventFilter(self.filter)
				# self.video_slider.setTickInterval(1)
				# self.video_slider.singleStep()
				# self.video_slider.setTickPosition(QSlider.TicksAbove)

				# self.video_slider.valueChanged.connect(lambda val: self.objNxtVideoPlayer.slider_seek(val))
				self.video_slider.sliderMoved.connect(lambda val: self.objNxtVideoPlayer.slider_seek(val))
				self.filter.sliderValueChanged.signal.connect(self.set_tooltip)
				# self.video_slider.sliderPressed.connect(lambda val: self.objNxtVideoPlayer.slider_seek())
				# self.video_slider.sliderReleased.connect(lambda val: self.objNxtVideoPlayer.slider_seek())
				# hboxlayout_slider_control.addWidget(self.video_slider, 0, Qt.AlignVCenter)
				# gbox_slider_control.setLayout(hboxlayout_slider_control)
				gui_layout.addWidget(self.video_slider)

				gbox_player_control = QGroupBox('')
				hboxlayout_player_control = QtGui.QHBoxLayout()
				hboxlayout_player_control.setSpacing(0)
				hboxlayout_player_control.setContentsMargins(1, 1, 1, 1)

				self.play_pause_button = QPushButton("")
				self.play_pause_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'play_48.png')))
				self.play_pause_button.setIconSize(QSize(24, 24))
				self.play_pause_button.setToolTip('Play Pause video')
				self.play_pause_button.clicked.connect(lambda: self.on_play_pause())
				self.play_pause_button.setFocusPolicy(Qt.NoFocus)
				hboxlayout_player_control.addWidget(self.play_pause_button, 0, Qt.AlignVCenter)

				self.reverse_play_pause_button = QPushButton("")
				self.reverse_play_pause_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'reverse_play_48.png')))
				self.reverse_play_pause_button.setIconSize(QSize(24, 24))
				self.reverse_play_pause_button.setToolTip('Reverse Play Pause video')
				self.reverse_play_pause_button.clicked.connect(lambda: self.on_reverse_play_pause())
				self.reverse_play_pause_button.setFocusPolicy(Qt.NoFocus)
				hboxlayout_player_control.addWidget(self.reverse_play_pause_button, 0, Qt.AlignVCenter)

				self.speed_slow_button = QPushButton("")
				self.speed_slow_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'slow_play_48.png')))
				self.speed_slow_button.setIconSize(QSize(24, 24))
				self.speed_slow_button.setToolTip('Fast Reverse')
				self.speed_slow_button.clicked.connect(lambda: self.on_speed_slow())
				self.speed_slow_button.setFocusPolicy(Qt.NoFocus)
				hboxlayout_player_control.addWidget(self.speed_slow_button, 0, Qt.AlignVCenter)

				self.speed_fast_button = QPushButton("")
				self.speed_fast_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'fast_play_48.png')))
				self.speed_fast_button.setIconSize(QSize(24, 24))
				self.speed_fast_button.setToolTip('Fast Forward')
				self.speed_fast_button.clicked.connect(lambda: self.on_speed_fast())
				self.speed_fast_button.setFocusPolicy(Qt.NoFocus)
				hboxlayout_player_control.addWidget(self.speed_fast_button, 0, Qt.AlignVCenter)

				if self.slave:
						self.play_pause_button.setVisible(False)
						self.speed_slow_button.setVisible(False)
						self.speed_fast_button.setVisible(False)
						self.reverse_play_pause_button.setVisible(False)
				self.step_back_button = QPushButton("")
				self.step_back_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'step_back_48.png')))
				self.step_back_button.setIconSize(QSize(24, 24))
				self.step_back_button.setToolTip('Step Back')
				self.step_back_button.clicked.connect(lambda: self.on_step_back())
				self.step_back_button.setFocusPolicy(Qt.NoFocus)
				hboxlayout_player_control.addWidget(self.step_back_button, 0, Qt.AlignVCenter)

				self.step_forward_button = QPushButton("")
				self.step_forward_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'step_forward_48.png')))
				self.step_forward_button.setIconSize(QSize(24, 24))
				self.step_forward_button.setToolTip('Step Forward')
				self.step_forward_button.clicked.connect(lambda: self.on_step_forward())
				self.step_forward_button.setFocusPolicy(Qt.NoFocus)
				hboxlayout_player_control.addWidget(self.step_forward_button, 0, Qt.AlignVCenter)

				self.manual_seek_button = QPushButton("")
				self.manual_seek_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'seek_48.png')))
				self.manual_seek_button.setIconSize(QSize(24, 24))
				self.manual_seek_button.setToolTip('Manual seek to given timestamp')
				self.manual_seek_button.clicked.connect(lambda: self.manual_seek())
				self.manual_seek_button.setFocusPolicy(Qt.NoFocus)
				hboxlayout_player_control.addWidget(self.manual_seek_button, 0, Qt.AlignVCenter)

				self.copy_to_clipboard_button = QPushButton("")
				self.copy_to_clipboard_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'copy_to_clipboard_48.png')))
				self.copy_to_clipboard_button.setIconSize(QSize(24, 24))
				self.copy_to_clipboard_button.setToolTip('Copy to clipboard')
				self.copy_to_clipboard_button.clicked.connect(lambda: self.copy_to_clipboard())
				self.copy_to_clipboard_button.setFocusPolicy(Qt.NoFocus)
				hboxlayout_player_control.addWidget(self.copy_to_clipboard_button, 0, Qt.AlignVCenter)

				self.copy_to_disk_button = QPushButton("")
				self.copy_to_disk_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'save_48.png')))
				self.copy_to_disk_button.setIconSize(QSize(24, 24))
				self.copy_to_disk_button.setToolTip('Copy to drive')
				self.copy_to_disk_button.clicked.connect(lambda: self.copy_to_drive())
				self.copy_to_disk_button.setFocusPolicy(Qt.NoFocus)
				hboxlayout_player_control.addWidget(self.copy_to_disk_button, 0, Qt.AlignVCenter)

				self.status_button = QPushButton("")
				self.status_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'status_48.png')))
				self.status_button.setIconSize(QSize(24, 24))
				self.status_button.setToolTip('Status Names')
				self.status_button.clicked.connect(
								lambda: self.show_information(OrderedDict(self.objNxtVideoPlayer.statuslabel),
																							self.status_button.toolTip(),
																							["Status Names", "State"], self.status_button.icon()))
				self.status_button.setFocusPolicy(Qt.NoFocus)
				hboxlayout_player_control.addWidget(self.status_button, 0, Qt.AlignVCenter)

				self.help_button = QPushButton("")
				self.help_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'help_48.png')))
				self.help_button.setIconSize(QSize(24, 24))
				self.help_button.setToolTip('Help Document')
				self.help_button.clicked.connect(
								lambda: self.show_information(OrderedDict(self.objNxtVideoPlayer.helplabel),
																							self.help_button.toolTip(),
																							["Control Key", "Information"], self.help_button.icon()))
				self.help_button.setFocusPolicy(Qt.NoFocus)
				hboxlayout_player_control.addWidget(self.help_button, 0, Qt.AlignVCenter)

				horizontal_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding)
				hboxlayout_player_control.addItem(horizontal_spacer)

				self.lbl_message = QLabel("PAUSE ||")
				self.lbl_message.setStyleSheet("background-color: white; inset grey; min-height: 20px;")
				self.lbl_message.setFrameShape(QFrame.Panel)
				self.lbl_message.setFrameShadow(QFrame.Sunken)
				self.lbl_message.setLineWidth(1)
				hboxlayout_player_control.addWidget(self.lbl_message, 0, Qt.AlignVCenter)

				self.lbl_timer = QLabel("00:00")
				self.lbl_relative_timer = QLabel("00:00")
				hboxlayout_player_control.addWidget(self.lbl_timer, 0, Qt.AlignVCenter)
				hboxlayout_player_control.addWidget(self.lbl_relative_timer, 0, Qt.AlignVCenter)
				gbox_player_control.setLayout(hboxlayout_player_control)
				gui_layout.addWidget(gbox_player_control)

				self.setLayout(gui_layout)
				self.setFocusPolicy(Qt.StrongFocus)

		def manual_seek(self):
				obj_frm_get_abs_rel_timestamp_input = FrmGetAbsRelTimestampInput()
				result = obj_frm_get_abs_rel_timestamp_input.exec_()
				if obj_frm_get_abs_rel_timestamp_input.user_accepted is True:
						timestamp_type, timestamp_user_input = obj_frm_get_abs_rel_timestamp_input.get_timestamp()
						# text, ok = QtGui.QInputDialog.getText(self, 'Manual seek', 'Enter Timestamp e.g 1000.234')
						if timestamp_user_input == "":
								logger.warning("Please enter valid timestamp")
								return
						try:
								if timestamp_type == "relative":
										timestamp = int(timestamp_user_input)
								else:
										timestamp = float(timestamp_user_input)
						except ValueError:
								logger.warning("Please enter valid timestamp, you have entered: {}".format(timestamp_user_input))
								return
						except Exception as e:
								logger.warning(str(e))
								return
						if timestamp_type == "absolute":
								video_commontime = self.objNxtVideoPlayer.display_sync_times[0]
								if timestamp < video_commontime[0] or timestamp > video_commontime[-1]:
										logger.warning(
														"Please enter valid timestamp in bound: ({}, {})".format(video_commontime[0], video_commontime[
																-1]))
										return
								relative_time = timestamp - video_commontime[0]
								time_index = math.ceil(self.objNxtVideoPlayer.getindexFromRelativeTime(relative_time))
								self.objNxtVideoPlayer.slider_seek(time_index)

						elif timestamp_type == "relative":
								minutes = timestamp / 60000000
								timestamp = timestamp - (minutes * 60000000)
								second = timestamp / 1000000
								total = timestamp - (second * 1000000)
								microseconds = total

								relative_time = float(str((minutes * 60) + second) + "." + str(microseconds))
								time_index = math.ceil(
									self.objNxtVideoPlayer.getindexFromRelativeTime(
										relative_time))
								self.objNxtVideoPlayer.slider_seek(time_index)

		def on_play_pause(self):
				if self.objNxtVideoPlayer.current_state == 'pause':
						self.objNxtVideoPlayer.play()
						self.lbl_message.setText("PLAY >")
						self.play_pause_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'pause_48.png')))
				elif self.objNxtVideoPlayer.current_state == 'play':
						self.objNxtVideoPlayer.pause()
						self.lbl_message.setText("PAUSE ||")
						self.play_pause_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'play_48.png')))

		def on_reverse_play_pause(self):
				if self.objNxtVideoPlayer.current_state == 'pause':
						self.objNxtVideoPlayer.play_reverse()
						self.lbl_message.setText("PLAY REVERSE>")
						self.reverse_play_pause_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'pause_48.png')))
				elif self.objNxtVideoPlayer.current_state == 'playreverse':
						self.objNxtVideoPlayer.pause()
						self.lbl_message.setText("PAUSE ||")
						self.reverse_play_pause_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'reverse_play_48.png')))

		def on_speed_fast(self):
				self.play_pause_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'pause_48.png')))
				self.objNxtVideoPlayer.speedfast()
				self.lbl_message.setText("SPEED FAST")

		def on_speed_slow(self):
				self.play_pause_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'pause_48.png')))
				self.objNxtVideoPlayer.speedslow()
				self.lbl_message.setText("SPEED SLOW")

		def on_step_back(self):
				# self.play_pause_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'play_48.png')))
				self.objNxtVideoPlayer.stepback()
				self.lbl_message.setText('STEP BACKWARD <<')

		def on_step_forward(self):
				# self.play_pause_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'play_48.png')))
				self.objNxtVideoPlayer.stepforward()
				self.lbl_message.setText('STEP FORWARD >>')

		def copy_to_clipboard(self):
				self.objNxtVideoPlayer.copyContentToClipboard()

		def copy_to_drive(self):
				import os
				home = os.getenv("HOME")
				file_path_selected = QFileDialog.getExistingDirectory(self, "Select folder", home,
																															QtGui.QFileDialog.ShowDirsOnly)
				file_name = self.measurement_name + "_" + str(self.objNxtVideoPlayer.disptime) + ".png"
				full_file_name = os.path.join(file_path_selected, file_name)
				self.objNxtVideoPlayer.copyContentToFile(full_file_name)
				logger.info("Saved snapshot at " + full_file_name)

		def set_tooltip(self, value):
				timestamp_value, minutes, seconds, time_in_microseconds = self.get_relative_and_abs_timestamp(value)

				self.video_slider.setToolTip("Abs: {} /Rel: {}ms /{}:{}".format(timestamp_value, time_in_microseconds, minutes, seconds))

		def get_relative_and_abs_timestamp(self, value):
				display_time = self.objNxtVideoPlayer.getTimeFromIndex(value)
				timestamp_value = display_time + \
													self.objNxtVideoPlayer.display_sync_times[0][0]

				minutes_ = int(display_time) / 60
				minutes = str(int(display_time) / 60).zfill(2)
				seconds = str(int(display_time - minutes_ * 60)).zfill(2)
				# calculate time in ms
				dt_obj = datetime.datetime.utcfromtimestamp(display_time)
				minutes_in_ms = dt_obj.minute * 60000000
				seconds_in_ms = dt_obj.second * 1000000
				microseconds = dt_obj.microsecond
				time_in_microseconds = minutes_in_ms + seconds_in_ms + microseconds
				return timestamp_value, minutes, seconds, time_in_microseconds

		def show_information(self, text, title, header, icon):
				dialog = FrmShowInformation(text, header, icon)
				dialog.setWindowTitle(title)
				dialog.exec_()

		def keyPressEvent(self, event):
				key = event.key()
				isNumber = key in (range(48, 58) + range(65456, 65466))  # 0-9 on keyboard and numpad
				try:
					if key == QtCore.Qt.Key_Space and self.objNxtVideoPlayer.current_state == 'pause' and not self.slave:
							self.lbl_message.setText("PAUSE ||")
							self.objNxtVideoPlayer.play()
							self.play_pause_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'pause_48.png')))
					elif key == QtCore.Qt.Key_Space and self.objNxtVideoPlayer.current_state == 'play' and not self.slave:
							self.lbl_message.setText("PLAY >")
							self.objNxtVideoPlayer.pause()
							self.play_pause_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'play_48.png')))
					elif key == QtCore.Qt.Key_P and self.objNxtVideoPlayer.current_state == 'pause' and not self.slave:
							self.lbl_message.setText("PAUSE ||")
							self.objNxtVideoPlayer.play_reverse()
							self.reverse_play_pause_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'pause_48.png')))
					elif key == QtCore.Qt.Key_P and self.objNxtVideoPlayer.current_state == 'playreverse' and not self.slave:
							self.lbl_message.setText("PLAY REVERSE>")
							self.objNxtVideoPlayer.pause()
							self.reverse_play_pause_button.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'reverse_play_48.png')))
					elif key == QtCore.Qt.Key_F and not self.slave:
							self.lbl_message.setText("SPEED FAST")
							self.objNxtVideoPlayer.speedfast()
					elif key == QtCore.Qt.Key_S and not self.slave:  # '83'
							self.lbl_message.setText("SPEED SLOW")
							self.objNxtVideoPlayer.speedslow()
					elif key == QtCore.Qt.Key_Q:
							self.objNxtVideoPlayer.copyContentToClipboard()
					elif key == QtCore.Qt.Key_Left:
							self.lbl_message.setText('STEP BACKWARD <<')
							self.objNxtVideoPlayer.stepback()
					elif key == QtCore.Qt.Key_Right:
							self.lbl_message.setText('STEP FORWARD >>')
							self.objNxtVideoPlayer.stepforward()
					elif key == QtCore.Qt.Key_N:
							if self.objNxtVideoPlayer.lanes:
									if not self.objNxtVideoPlayer.lanesenabled:
											self.objNxtVideoPlayer.lanesenabled = True
											self.lbl_message.setText('LANES ENABLED: ALL')
									# self.setMessage('LANES ENABLED: ALL')
									else:
											if self.objNxtVideoPlayer.lanetodisplay < len(self.objNxtVideoPlayer.lanes) - 1:
													self.objNxtVideoPlayer.lanetodisplay += 2
													self.lbl_message.setText(
																	'LANES ENABLED: %d' % (self.objNxtVideoPlayer.lanetodisplay // 2))
											else:
													self.objNxtVideoPlayer.lanesenabled = False
													self.objNxtVideoPlayer.lanetodisplay = -1
													self.lbl_message.setText('LANES DISABLED')
					elif key == QtCore.Qt.Key_C:
							self.objNxtVideoPlayer.calibNavNeededSignal.signal.emit([self.calibrations])
					elif key == QtCore.Qt.Key_X:
							self.objNxtVideoPlayer.shortenlabel = True
							self.lbl_message.setText("SHORTED LABEL ENABLED")
							self.objNxtVideoPlayer.labellevel += 1
							if self.objNxtVideoPlayer.labellevel > 2:
									self.objNxtVideoPlayer.labellevel = 0
									self.objNxtVideoPlayer.shortenlabel = False
									self.lbl_message.setText("SHORTED LABEL DISABLED")

					elif key == QtCore.Qt.Key_L:
							self.lbl_message.setText("LABEL ENABLED")
							self.objNxtVideoPlayer.shortenlabel = False
							self.objNxtVideoPlayer.labellevel += 1
							if self.objNxtVideoPlayer.labellevel > 2:
									self.objNxtVideoPlayer.labellevel = 0
									self.lbl_message.setText("LABEL DISABLED")

					elif key == QtCore.Qt.Key_B:
							self.objNxtVideoPlayer.toggleVideoImage = not self.objNxtVideoPlayer.toggleVideoImage

					elif key == QtCore.Qt.Key_U:
							self.objNxtVideoPlayer.undistortimage = not self.objNxtVideoPlayer.undistortimage

					elif key == QtCore.Qt.Key_F9:
							# Key for enabling the LDW Overlay check.
							# Handle also the calibration window opening
							if self.objNxtVideoPlayer.ldw_tire_mode:
									self.objNxtVideoPlayer.showLdwLegend = not self.objNxtVideoPlayer.showLdwLegend
									self.objNxtVideoPlayer.ldw_tire_mode = False
									self.lbl_message.setText("LDW TIRE MODE : OFF")
									self.objNxtVideoPlayer.ldw_tire_calib_signal_close.signal.emit()
							else:
									self.objNxtVideoPlayer.showLdwLegend = not self.objNxtVideoPlayer.showLdwLegend
									self.objNxtVideoPlayer.ldw_tire_mode = True
									self.lbl_message.setText("LDW TIRE MODE : ON")
									self.objNxtVideoPlayer.ldw_tire_calib_signal_show.signal.emit([self.objNxtVideoPlayer.gl_width,
																																								 self.objNxtVideoPlayer.gl_height])
					elif key == QtCore.Qt.Key_F10:
							display_time = self.objNxtVideoPlayer.getTimeFromIndex(self.objNxtVideoPlayer.current_index)

							dt_obj = datetime.datetime.utcfromtimestamp(display_time)
							minutes_in_ms = dt_obj.minute * 60000000
							seconds_in_ms = dt_obj.second * 1000000
							microseconds = dt_obj.microsecond
							minutes_ = int(display_time) / 60
							minutes = str(int(display_time) / 60).zfill(2)
							seconds = str(int(display_time - minutes_ * 60)).zfill(2)
							time_in_microseconds = minutes_in_ms + seconds_in_ms + microseconds
							time_in_string = "Abs: " + str(self.objNxtVideoPlayer.disptime) + "; Rel: " + str(time_in_microseconds) + u"μs" + "; Rel: {}:{}min".format(minutes, seconds)
							logger.info(time_in_string)
							clipboard = QApplication.clipboard()
							clipboard.setText(time_in_string)
					elif key == QtCore.Qt.Key_R and not self.slave:
							self.objNxtVideoPlayer.seekbackduringplayback = not self.objNxtVideoPlayer.seekbackduringplayback
							sbState = 'ON' if self.objNxtVideoPlayer.seekbackduringplayback else 'OFF'
							self.lbl_message.setText('Synchronization ' + sbState)
					elif key == QtCore.Qt.Key_T:
							self.objNxtVideoPlayer.showtimelabel = not self.objNxtVideoPlayer.showtimelabel
					elif key == QtCore.Qt.Key_H:
							self.objNxtVideoPlayer.showLegend = not self.objNxtVideoPlayer.showLegend
					# Show/hide groups - ASSUMPTION: Only numbers and capital letters are used for this purpose.
					elif (unichr(key) in self.objNxtVideoPlayer.KeyCodes and not (
									isNumber and key == QtCore.Qt.Key_Shift)):  # Shift+Number is not a number - exclusion needed for
							# consistency with other navigators
							self.objNxtVideoPlayer.selectGroupCallback(self.objNxtVideoPlayer.KeyCodes[str(unichr(key))])
					else:
						return
				except Exception as e:
					return
				return

		def set_size(self, w, h):
				self.resize(w, h)

		def set_location(self, x, y):
				self.move(x, y)

		def get_size(self):
				return self.size().toTuple()

		def get_location(self):
				return self.pos().toTuple()

		def set_caption(self, caption):
				self.measurement_name = caption
				self.setWindowTitle(caption)

		def get_caption(self):
				self.windowTitle()

		def set_slider_value(self, index):
				if self.previous_value != index:
						if self.video_slider.value() != index:
								self.video_slider.setValue(index)
								# QToolTip.setFont(QFont("Times", 12))
								self.previous_value = index

		def set_timestamp_value(self, timestamp):
				display_time = timestamp - self.objNxtVideoPlayer.display_sync_times[0][0]
				minutes_ = int(display_time) / 60
				minutes = str(int(display_time) / 60).zfill(2)
				seconds = str(int(display_time - minutes_ * 60)).zfill(2)
				self.lbl_timer.setText(str("%.3f / " % timestamp))
				self.lbl_relative_timer.setText("{}:{}".format(minutes, seconds))

		def closeEvent(self, event):
				self.objNxtVideoPlayer.on_close()
				super(cNxtVideoPlayerControl, self).closeEvent(event)


class FrmShowInformation(QDialog):

		def __init__(self, text_info, header, icon):
				super(FrmShowInformation, self).__init__()
				self.setModal(False)

				text_dict = OrderedDict(text_info)
				self.setWindowIcon(icon)
				button_box = QDialogButtonBox(QDialogButtonBox.Ok)
				button_box.accepted.connect(self.ok_clicked)

				mainLayout = QtGui.QVBoxLayout()
				table = QTreeView()
				table.setSortingEnabled(False)
				table.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
				table.setAlternatingRowColors(True)
				model = QStandardItemModel()
				model.setHorizontalHeaderLabels(header)
				table.setModel(model)
				for key in text_dict:
						item_measurement_path = QStandardItem(key)
						item_measurement_path.setEditable(False)
						item_start_time = QStandardItem(str(text_dict[key]))
						item_start_time.setEditable(False)

						model.appendRow([item_measurement_path, item_start_time])
				mainLayout.addWidget(table)
				mainLayout.addWidget(button_box)
				self.setLayout(mainLayout)

		def ok_clicked(self):
				self.close()


class FrmGetAbsRelTimestampInput(QDialog):

	def __init__(self):
		super(FrmGetAbsRelTimestampInput, self).__init__()
		self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'seek_48.png')))
		self.setModal(True)
		self.center()
		self.user_accepted = False
		self.setWindowTitle("Select timestamp ")
		group_box_module_summary = QGroupBox(" ")
		form_layout_module_summary = QFormLayout()

		self.line_edit_user_timestamp_input = QLineEdit()
		self.line_edit_user_timestamp_input.setToolTip("Enter  Timestamp here.. for example 1000.234")
		form_layout_module_summary.addRow(QLabel("(*) Enter Timestamp:"), self.line_edit_user_timestamp_input)

		hboxlayout_abs_rel = QHBoxLayout()

		self.radio_button_absolute = QRadioButton("Absolute (time)")
		self.radio_button_absolute.setToolTip("Select if you have absolute timestamp")
		self.radio_button_absolute.setChecked(True)
		self.radio_button_relative = QRadioButton("Relative (in ms)")
		self.radio_button_relative.setToolTip(
			"Select if you have relative timestamp")
		hboxlayout_abs_rel.addWidget(self.radio_button_absolute)
		hboxlayout_abs_rel.addWidget(self.radio_button_relative)
		hboxlayout_abs_rel.addStretch()
		form_layout_module_summary.addRow(QLabel(" "), hboxlayout_abs_rel)

		group_box_module_summary.setLayout(form_layout_module_summary)

		button_box = QDialogButtonBox(QDialogButtonBox.Ok |
																	QDialogButtonBox.Cancel)
		button_box.accepted.connect(self.store)
		button_box.rejected.connect(self.cancel)

		main_layout = QVBoxLayout()
		main_layout.setSpacing(0)
		main_layout.setContentsMargins(1, 1, 1, 1)

		main_layout.addWidget(group_box_module_summary)
		main_layout.addWidget(button_box)
		main_layout.addWidget(button_box)
		self.setLayout(main_layout)
		self.setTabOrder(self.line_edit_user_timestamp_input, self.radio_button_absolute)
		self.setTabOrder(self.radio_button_absolute, self.radio_button_relative)
		self.setTabOrder(self.radio_button_relative, self.line_edit_user_timestamp_input)
		self.line_edit_user_timestamp_input.setFocus()

	def get_timestamp(self):
		if self.radio_button_absolute.isChecked():
			return "absolute", self.line_edit_user_timestamp_input.text()
		elif self.radio_button_relative.isChecked():
			return "relative", self.line_edit_user_timestamp_input.text()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def store(self):
		self.user_accepted = True
		self.accept()

	def cancel(self):
		self.close()

if __name__ == '__main__':
		app = QtGui.QApplication(sys.argv)

		if not QtOpenGL.QGLFormat.hasOpenGL():
				QMessageBox.information(0, "Play Video With Overlay",
																"This system does not support OpenGL.",
																QMessageBox.Ok)
				sys.exit(1)

		f = QtOpenGL.QGLFormat.defaultFormat()
		f.setSampleBuffers(True)

		# print str(f.majorVersion()) + "." + str(f.minorVersion())
		f.setVersion(1, 0)
		# print str(f.majorVersion()) + "." + str(f.minorVersion())
		QtOpenGL.QGLFormat.setDefaultFormat(f)

		win = cNxtVideoPlayerControl(r"C:\KBData\videos_through_dcnvt\test_2\2021.02.09_at_20.32.03_radar-mi_5031.avi")
		# win = cNxtVideoPlayerControl(r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport
		# \mfc525_interface\measurements\2020_08_27\NY00__2020-08-27_08-36-16.avi")

		# widget = cNxtVideoPlayer(r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\fcw_end_run
		# \2020-05-13\FCW__2020-05-13_05-39-39.avi")
		win.objNxtVideoPlayer.start()
		win.show()
		sys.exit(app.exec_())

# elif key==QtCore.Qt.Key_Up:
# 		if self.speed < 16.0:
# 				self.speed *= 2.0
# 				if self.speed == 1.0:
# 						self.speed *= 2.0
# elif key == QtCore.Qt.Key_Down:
# 		if self.speed > 1 / 16.0:
# 				self.speed /= 2.0
# 				if self.speed == 1.0:
# 						self.speed /= 2.0
# elif key == QtCore.Qt.Key_F10:
# 		if self.displaytime is not None:
# 				displaytime, displaytimevalue = self.displaytime
# 				disptime = np.interp([self.objseektime], displaytimevalue,
# 														 displaytime)[0]
# 		else:
# 				disptime = self.player.time
# 		logger.info(
# 				"Current time is " + str(disptime))
# elif key == QtCore.Qt.Key_S:
# 		self.seek(133235.294128)
# elif key == QtCore.Qt.Key_N:
# 		self.snap()
# self.onPause(float(self.media.currentTime()/1000))


# if (key == QtCore.Qt.Key_S):
# 		self.media.stop()
