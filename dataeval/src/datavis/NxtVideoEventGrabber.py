import StringIO
import logging
import os
import time

import Group
import NxtOpenGLutil
import NxtOverlayShape
import cv2
import numpy as np
from OpenGL import GL, GLUT
from OpenGL.GLU import *
from PIL import Image
from PySide import QtCore
from TrackNavigator import COLOR_NONE, NO_COLOR
from calibration_data import cCalibrationData
from datavis.RecordingService import RecordingService

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
				self.fontFamily = GLUT.GLUT_STROKE_MONO_ROMAN

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


class cNxtVideoEventGrabber(Group.iGroup):

		def __init__(self, file_name, calibrations = None, group=None):
				Group.iGroup.__init__(self, KeyTable)
				self.filename = file_name
				self.capture = cv2.VideoCapture(self.filename)

				# Video Properties
				self.total_frames = self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
				self.fps = self.capture.get(cv2.cv.CV_CAP_PROP_FPS)
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

				# Overlay lanes
				self.lanesenabled = True
				self.lanes = []
				self.lanetodisplay = -1

				self.Markers = {}
				self.shapes = None
				self.legend = cVideoLegend()
				self.external_markers = None

				self.video_thread = None

				self.display_sync_times = None
				self.current_frame = None
				self.X_AXIS = 0.0
				self.Y_AXIS = 0.0
				self.Z_AXIS = 0.0
				self.texture_id = 0
				self.sync_time = 0.0
				# self.setWindowTitle(self.tr("Play Video With Overlay"))
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
				# print(self.GUI_WIDTH)
				# print(self.GUI_HEIGHT)
				# self.set_size(self.GUI_WIDTH, self.GUI_HEIGHT)
				self.helplabel = "_________________Control Keys_________________ \n" \
												 "space  : toggle play/pause \n " \
												 "s      : slowspeed \n " \
												 "f      : fastspeed \n " \
												 "q      : copytoClipboard \n " \
												 "c      : toggle calibration window \n " \
												 "->     : stepback video \n " \
												 "<-     : stepforward video \n " \
												 "n      : toggle lane display \n" \
												 "l      : toggle object label \n" \
												 "b      : toggle video backgound image on/off \n"\
												 "f10    : copy current time to notepad \n" \
												 "f2     : toggle statuslabel on\off \n"\

				self.labellevel = 0
				self.maxDisplDist = 100
				self.showstatuslabel = False
				self.statuslabel =[]

				# Video background image
				self.toggleVideoImage = True

				self.imagedata_emitting_signal = ObjectEmittingSignal()
				self.current_index_changed = IntEmittingSignal()
				self.current_timestamp_changed = FloatEmittingSignal()
				self.calibNavNeededSignal = ObjectEmittingSignal()
				self.manual_calib_updated = SimpleSignal()

				self.showtimelabel = True
				self.showLegend = False
				self.legend = cVideoLegend()

				self.recorder = RecordingService('VideoRecord')
				self.is_recording = False

				self.window_caption = ""
				GLUT.glutInit()
				GLUT.glutInitDisplayMode(GLUT.GLUT_SINGLE | GLUT.GLUT_RGB)

				GLUT.glutInitWindowSize(640, 360)
				# GLUT.glutInitWindowPosition(100, 100)
				GLUT.glutCreateWindow("My OpenGL Code")
				GLUT.glutHideWindow()
				# GLUT.glutDisplayFunc(self.paint)
				# GLUT.glutReshapeFunc(self.resize)
				# GLUT.glutIdleFunc(self.paint)
				# GLUT.glutKeyboardFunc(self.processNormalKeys)
				self.initialize()
				self.resize(640, 360)


				# self.Shapes = NxtOverlayShape.Shapes(NxtOpenGLutil.allShapeBuildProps)
		# <editor-fold desc="OpenGL Drawing">
		def initialize(self):
				GL.glClearColor(0.0, 0.0, 0.0, 0.0)
				GL.glClearDepth(1.0)
				GL.glEnable(GL.GL_TEXTURE_2D)

				self.texture_id = GL.glGenTextures(1)
				self.Shapes = NxtOverlayShape.Shapes(NxtOpenGLutil.allShapeBuildProps)


		def resize(self, width, height):
				if height==0:
						return
				self.main_gl_widget_height = height
				self.main_gl_widget_width = width
				self.gl_width = width
				self.gl_height = height
				image_ratio = float(self.video_image_width) / self.video_image_height
				screen_ratio = float(self.gl_width) / self.gl_height
				original_width = self.gl_width
				original_height = self.gl_height

				if image_ratio > screen_ratio:
						self.gl_height = self.gl_width / image_ratio
				else:
						self.gl_width = self.gl_height * image_ratio

				self.offset_x = 0 + (original_width - self.gl_width) * 0.5
				self.offset_y = 0 + (original_height - self.gl_height) * 0.5

				self.legend.on_resize((self.offset_x, self.offset_y, self.gl_width, self.gl_height))
				self.paint()

		def paint(self):
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
				ret, self.current_frame = self.capture.read()
				if self.showtimelabel:
						cv2.putText(self.current_frame, str("%.3f" % self.disptime), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
												(0, 0, 0), 1,
												cv2.CV_AA)

				GL.glClear(GL.GL_COLOR_BUFFER_BIT| GL.GL_DEPTH_BUFFER_BIT)
				GL.glColor3ub(255, 255, 255)
				GL.glViewport(0, 0, self.main_gl_widget_width, self.main_gl_widget_height)
				# convert image to OpenGL texture format
				if self.current_frame is not None:
						# Retrieve openGL compatible image from the frame
						tx_image = Image.fromarray(self.current_frame)
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

						self.draw_objects(self.nds)

						GL.glFlush()
						if self.is_recording:
								width = 640
								height = 360
								pixelset = (GL.GLubyte * (4 * width * height))(0)
								GL.glReadPixels(0, 0, width, height, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, pixelset)
								image = Image.fromstring(mode = "RGBA", size = (width, height), data = pixelset)
								# image.resize((640,360))
								img_data = image.tostring("raw", "RGBA")
								self.recorder.update_current_record(img_data)

		def draw_objects(self, ndxs):
				# if self.ldw_tire_mode and self.ldw_tire_overlay_calib is not None:
				# 		self.draw_ldw_tire_overlay()
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
								except KeyError:
										logger.info('Missing drawing data, shape cannot be drawn.')
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
								try:
									if alpha and NxtOpenGLutil.FACE == shapeType:
											GL.glColor4ub(color[0], color[1], color[2], alpha)
									else:
											GL.glColor3ub(color[0], color[1], color[2])
								except:
									logger.info("Video File: %s is corrupted. Please re-convert again",self.filename)
								# set line width
								lineWidth = style['lw'] if style.has_key('lw') else None
								if lineWidth:
										GL.glLineWidth(lineWidth)

								# draw the shape
								self.Shapes.draw(shapeName, shapeType)

								GL.glDisable(GL.GL_BLEND)
								GL.glEnable(GL.GL_TEXTURE_2D)
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
																			scale = scaleVec, color= (90, 97, 90))  # extra properties supported (e.g. text translation,
						# rotation, color, transparency)

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
								GL.glBlendFunc(GL.GL_SRC_ALPHA,GL.GL_ONE_MINUS_SRC_ALPHA)
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

		# </editor-fold>

		# <editor-fold desc="Recording">
		def begin_recording(self, filename_extra):
				if not self.is_recording:
						# Run a flipped recording at a FPS of 4 for easy visual
						self.recorder.record_start((640, 360), fps=30
								, flipped=True, filename_extra=filename_extra)
						self.is_recording = True
						self.counter = 0
				return

		def stop_recording(self):
				# Stop record if there is a record running
				if self.is_recording:
						self.recorder.stop_current_record()
						self.is_recording = False
				return

		# </editor-fold>

		# <editor-fold desc="OpenGL Drawing">
		def save_screenshot(self, name = 'screenshot.png'):
				width = GLUT.glutGet(GLUT.GLUT_WINDOW_WIDTH)
				height = GLUT.glutGet(GLUT.GLUT_WINDOW_HEIGHT)
				pixelset = (GL.GLubyte  * (3 * width * height))(0)
				GL.glReadPixels(0, 0, width, height, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, pixelset)
				image = Image.fromstring(mode = "RGBA", size = (width, height), data = pixelset)
				image = image.transpose(Image.FLIP_TOP_BOTTOM)
				image.save(name)
				# print("Screenshot saved as '{0}'.".format(name))



		# <editor-fold desc="Player Threading">
		def frame_update(self):
				# print("Called frame_update")
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
				ret, self.current_frame = self.capture.read()
				if self.showtimelabel:
						cv2.putText(self.current_frame, str("%.3f" % self.disptime), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
												(0, 0, 0), 1,
												cv2.CV_AA)
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
						time.sleep((0.1 - 1 / self.fps) + self.frame_rate)
						if self.seekcallback is not None and self.seekbackduringplayback:
								self.seekcallback(self.current_time)
						self.current_index += 1

				if self.current_state == 'pause':
						self.current_index_changed.signal.emit(self.current_index)
						if self.seekcallback is not None and self.seekbackduringplayback:
								self.seekcallback(self.current_time)
				if self.current_state == 'prev_frame':
						self.current_index -= 1
						self.current_index_changed.signal.emit(self.current_index)
						self.current_state = 'pause'
				if self.current_state == 'next_frame':
						self.current_index += 1
						self.current_index_changed.signal.emit(self.current_index)
						self.current_state = 'pause'
				if self.current_state == 'slow':
						self.frame_rate += self.frame_rate + 0.1
						self.current_state = 'play'
				if self.current_state == 'fast':
						self.frame_rate = max(self.frame_rate - 0.1, 0)
						self.current_state = 'play'
				if self.current_state == 'snap':
						tx_image = Image.fromarray(self.current_frame)
						tx_image.save(self.file_path, 'PNG')
						self.current_state = 'pause'
				# self.capture.release()
				# cv2.destroyAllWindows()

		# </editor-fold>

		# <editor-fold desc="Player Control functions">
		def play(self):
				# print("Called play")
				if self.seekcallback is not None and self.seekbackduringplayback:
						self.seekcallback(self.current_time)

		# if self.playcallback is not None:
		# 		self.playcallback(self.current_time)

		def pause(self):
				# print("Called pause")
				if self.seekcallback is not None and self.seekbackduringplayback:
						self.seekcallback(self.current_time)

		# if self.pausecallback is not None:
		# 		self.pausecallback(self.current_time)

		def seek(self, time):

				# print("Called seek: {}".format(time))
				self.seek_time = time
				self.capture.set(cv2.cv.CV_CAP_PROP_POS_MSEC, self.seek_time * 1000)
				self.current_index = self.capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
				self.current_time = self.capture.get(cv2.cv.CV_CAP_PROP_POS_MSEC) / 1000
				if self.seekcallback is not None and self.seekbackduringplayback:
						self.seekcallback(self.current_time)

				self.paint()

		def snap(self):
				self.previous_state = self.current_state
				self.current_state = 'snap'
				self.file_path = "abc.png"

		def stepback(self):
				self.previous_state = self.current_state
				self.current_state = 'prev_frame'

		def stepforward(self):
				self.previous_state = self.current_state
				self.current_state = 'next_frame'

		def speedfast(self):
				self.previous_state = self.current_state
				self.current_state = 'fast'

		def speedslow(self):
				self.previous_state = self.current_state
				self.current_state = 'slow'

		def copyContentToFile(self, file, format = 'png'):
				width = GLUT.glutGet(GLUT.GLUT_WINDOW_WIDTH)
				height = GLUT.glutGet(GLUT.GLUT_WINDOW_HEIGHT)
				pixelset = (GL.GLubyte * (3 * width * height))(0)
				GL.glReadPixels(0, 0, width, height, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, pixelset)
				image = Image.fromstring(mode="RGB", size=(width, height), data=pixelset)
				image = image.transpose(Image.FLIP_TOP_BOTTOM)

				if isinstance(file, basestring):  # 'file' is the name of the file
						with open(file, 'wb') as f:
								image.save(f, format)
				else:  # 'file' is a file-like object
						image.save(file, format)
				return

		def copyContentToClipboard(self):
				imageFileAsPng = StringIO.StringIO()

				width = GLUT.glutGet(GLUT.GLUT_WINDOW_WIDTH)
				height = GLUT.glutGet(GLUT.GLUT_WINDOW_HEIGHT)
				pixelset = (GL.GLubyte * (3 * width * height))(0)
				GL.glReadPixels(0, 0, width, height, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, pixelset)
				image = Image.fromstring(mode="RGB", size=(width, height), data=pixelset)
				image = image.transpose(Image.FLIP_TOP_BOTTOM)

				image.save('png', file=imageFileAsPng)
				imageFileAsPng.seek(0)
				# Crop
				self.imagedata_emitting_signal.signal.emit(imageFileAsPng)
				return

		def on_close(self):
				self.capture.release()
				pass
				# w, h = self.size().toTuple()
				# x, y = self.pos().toTuple()
				#
				# geometry = figlib.buildGeometryString(x, y, w, h)
				#
				# self.pause()
				#
				# if self.closecallback is not None:
				# 		self.closecallback(geometry)
				# if self.video_thread.is_alive():
				# 		self.current_state = 'exit'
				# 		self.video_thread.join()

				return

		def setcallbacks(self, seekcallback, playcallback, pausecallback, closecallback):
				# print("Called setcallbacks")
				self.seekcallback = seekcallback
				self.playcallback = playcallback
				self.pausecallback = pausecallback
				self.closecallback = closecallback
				return

		def slider_seek(self, index):
				self.current_index = index

		# print("Received" + str(index))

		# </editor-fold>

		# <editor-fold desc="Overloaded Methods">


		def timerEvent(self, event):
				self.update()


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

				self.statuslabel = "\n".join(self.Labels)

				if return_result:
						self.selectGroupCallback(GroupName)
				return

		def selectGroupCallback(self, GroupName):
				return

		# <editor-fold desc="Object and Lane Overlay functions">
		def setLegend(self, Markers):
				self.external_markers = Markers.copy()  # shallow copy
				markers = Markers.copy() # shallow copy
				if markers:
						self.Markers = markers
						self.legend.setMarkers(self.Shapes, self.external_markers)
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

		def get_caption(self):
				return self.window_caption

		def set_caption(self, Measurement):
				self.window_caption = Measurement
				# GLUT.glutSetWindowTitle(Measurement)

		def set_size(self, w,h):
				pass
				# GLUT.glutReshapeWindow(w, h)

		def set_location(self,x,y):
				pass
				# GLUT.glutPositionWindow(x, y)

		def get_size(self):
				return (20,20)
				# w = GLUT.glutGet(GLUT.GLUT_WINDOW_WIDTH)
				# h = GLUT.glutGet(GLUT.GLUT_WINDOW_HEIGHT)
				# return ((w, h))

		def get_location(self):
				pass
				# x = GLUT.glutGet(GLUT.GLUT_WINDOW_X)
				# y = GLUT.glutGet(GLUT.GLUT_WINDOW_Y)
				return (20, 20)

		def show(self):
				GLUT.glutInit()
				GLUT.glutInitDisplayMode(GLUT.GLUT_SINGLE | GLUT.GLUT_RGB)

				GLUT.glutInitWindowSize(640, 480)
				GLUT.glutInitWindowPosition(100, 100)
				GLUT.glutCreateWindow("")
				GLUT.glutDisplayFunc(self.paint)
				GLUT.glutReshapeFunc(self.resize)
				GLUT.glutIdleFunc(self.paint)
				GLUT.glutKeyboardFunc(self.processNormalKeys)
				self.initialize()
				self.resize(640, 480)
				self.paint()
				# GLUT.glutMainLoop()
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
		def processNormalKeys(self, key, x, y):
				# print(key)
				if key == 's':
						# print("calling screenshot")
						self.ScreenShot(r"C:\KBApps\pytch\abc.png")
		# def prepare_video_size(self, x = None, y = None):
		# 		if x is None or y is None:
		# 				width, height = self.get_video_size()
		# 		else:
		# 				width, height = x, y
		#
		# 		self.video_width = width
		# 		self.video_height = height
		# 		# self.GUI_WIDTH = width + 2 * self.GUI_PADDING
		# 		# self.GUI_HEIGHT = height  + 2 * self.GUI_PADDING
		# 		# self.video_x = self.GUI_PADDING
		# 		# self.video_y = self.GUI_HEIGHT - self.GUI_PADDING - self.video_height
		# 		return
		#
		# def set_video_size(self, x = None, y = None):
		# 		self.prepare_video_size(x, y)
		# 		self.set_size(self.GUI_WIDTH, self.GUI_HEIGHT)
		# 		return
		#

		#
		# def get_video_size(self):
		# 		video_width = 1
		# 		video_height = 1
		# 		if self.sample_aspect > 1:
		# 				video_width = self.video_width * self.sample_aspect
		# 		elif self.sample_aspect < 1:
		# 				video_height = self.video_height / self.sample_aspect
		# 		return video_width, video_height


if __name__ == '__main__':
		ObjNxtVideoGrabber = cNxtVideoEventGrabber(
				r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\videos\dcnvt.avi")

		GLUT.glutInit()
		GLUT.glutInitDisplayMode(GLUT.GLUT_SINGLE  | GLUT.GLUT_RGB)

		GLUT.glutInitWindowSize(640, 480)
		GLUT.glutInitWindowPosition(100, 100)
		GLUT.glutCreateWindow("My OpenGL Code")
		GLUT.glutDisplayFunc(ObjNxtVideoGrabber.paint)
		GLUT.glutReshapeFunc(ObjNxtVideoGrabber.resize)
		GLUT.glutIdleFunc(ObjNxtVideoGrabber.paint)
		GLUT.glutKeyboardFunc(ObjNxtVideoGrabber.processNormalKeys)
		ObjNxtVideoGrabber.initialize()
		ObjNxtVideoGrabber.resize(640,480)
		GLUT.glutMainLoop()

# width = GLUT.glutGet(GLUT.GLUT_WINDOW_WIDTH)
								# height = GLUT.glutGet(GLUT.GLUT_WINDOW_HEIGHT)
