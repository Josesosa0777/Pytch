"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright:
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial
  property. We reserve all rights of disposal such as copying and passing on to
  third parties.
"""
__docformat__ = "restructuredtext en"

import os
import shutil
import logging
from cStringIO import StringIO

import numpy

from PySide import QtGui, QtCore

from calibrator import Calibrator
from figlib import makeStringFromQtGeometry, buildQtGeometryFromString, \
		generateWindowId


class FloatEmittingSignal(QtCore.QObject):
		signal = QtCore.Signal(float)


class SimpleSignal(QtCore.QObject):
		signal = QtCore.Signal()


class SetROISignal(QtCore.QObject):
		signal = QtCore.Signal(object, float, float, str)


class StringEmittingSignal(QtCore.QObject):
		signal = QtCore.Signal(str)


class DoubleFloatEmittingSingal(QtCore.QObject):
		signal = QtCore.Signal(float, float)


class ObjectEmittingSignal(QtCore.QObject):
		signal = QtCore.Signal(object)


class iSynchronizable(object):
		"""
		Interface class for synchronizable data visualizers.
		Classes that providing this interface should inherit from this.
		"""

		def __init__(self, title = None):
				self.playSignal = FloatEmittingSignal()
				""":type: function
				Callback to call when play started."""
				self.pauseSignal = FloatEmittingSignal()
				""":type: function
				Callback to call when paused."""
				self.seekSignal = FloatEmittingSignal()
				""":type: function
				Callback to call when play seeked."""
				self.closeSignal = StringEmittingSignal()
				""":type: function
				Callback to call when client is closed."""
				self.setROISignal = SetROISignal()
				""":type: function
				Callback to get the Region Of Interest."""
				self.selectGroupSignal = StringEmittingSignal()
				self.setXLimOnlineSignal = DoubleFloatEmittingSingal()
				self.calibNavNeededSignal = ObjectEmittingSignal()
				self.userTitleSet = False
				""":type: bool
				Flag to signal if user set the title instead of the default."""
				self.ROIstart = 0.0
				self.ROIend = 0.0
				self.title = title
				self.logger = logging.getLogger()
				pass

		def start(self):
				"""
				Start the data visualizer's event loop.
				"""
				pass

		def seek(self, time):
				"""
				Set the time.
				"""
				pass

		def play(self, time):
				"""
				Start playing at time.
				"""
				pass

		def pause(self, time):
				"""
				Pause playing at time.
				"""
				pass

		def close(self):
				"""
				Close the data visualizer.
				"""
				pass

		def clean(self):
				"""
				Clean the data visualizer before closing.
				"""
				pass

		def setROI(self, client, start, end, color):
				"""
				Set the Region Of Interest.

				:Parameters:
					client : `iSynchronizable`
						The sender client client.
					start : float
						Timestamp of the start of the ROI.
					end : float
						Timestamp of the end of the ROI.
					color : str
						Color to mark the interval.
				"""
				self.ROIstart = start
				self.ROIend = end
				pass

		def onSelectGroup(self, GroupName):
				self.selectGroup(GroupName)
				self.selectGroupSignal.signal.emit(GroupName)
				return

		def selectGroup(self, GroupName):
				return

		def getROI(self):
				return self.ROIstart, self.ROIend

		def setAxesLimits(self, limits):
				pass

		def set_xlim_online(self, x_min, x_max):
				return

		def on_set_xlim_online(self, x_min, x_max):
				self.set_xlim_online(x_min, x_max)
				self.setXLimOnlineSignal.signal.emit(x_min, x_max)
				return

		def setUserWindowTitle(self, Measurement):
				self.setWindowTitle(Measurement)
				self.userTitleSet = True
				pass

		def setWindowTitle(self, Measurement):
				pass

		def getWindowTitle(self):
				return 'foo'

		def getWindowId(self):
				return self._windowId

		def getWindowGeometry(self):
				return 'foo'

		def setWindowGeometry(self, geometry):
				pass

		def start_recording(self,path=None, filename_extra = ''):
				pass

		def stop_recording(self):
				pass

		def copyContentToClipboard(self):
				"""
				Copy current figure to the clipboard as a bitmap image.
				"""
				pass

		def copyContentToFile(self, file, format = None):
				pass

		def copyContentToBuffer(self, buffer = None, format = 'png'):
				buff = StringIO() if not buffer else buffer
				self.copyContentToFile(buff, format)
				buff.seek(0)
				return buff

		def createWindowId(self, id, title = None):
				if not title:
						if not self.title:
								title = self.__class__.__module__.split('.')[-1]
						else:
								title = self.title
				self._windowId = generateWindowId('%s%s' % (title, id))
				return self._windowId


class cNavigator(QtGui.QMainWindow, iSynchronizable):
		def __init__(self, title = None):
				iSynchronizable.__init__(self, title = title)
				QtGui.QMainWindow.__init__(self)
				self.center()
				self.playing = False
				self.time = 0.0

		def center(self):
				# geometry of the main window
				qr = self.frameGeometry()

				# center point of screen
				cp = QtGui.QDesktopWidget().availableGeometry().center()

				# move rectangle's center point to screen's center point
				qr.moveCenter(cp)

				# top left of rectangle becomes top left of window centering it
				self.move(qr.topLeft())

		def seek(self, time):
				self.time = time
				self.seekWindow()
				pass

		def play(self, time):
				if not self.playing:
						self.playing = True
				pass

		def pause(self, time):
				if self.playing:
						self.playing = False
						self.seek(time)
				pass

		def closeEvent(self, event):
				geometry = self.getWindowGeometry()
				self.clean()
				self.closeSignal.signal.emit(geometry)
				QtGui.QMainWindow.closeEvent(self, event)
				pass

		def onPlay(self, time):
				self.play(time)
				self.playSignal.signal.emit(time)
				return

		def onPause(self, time):
				self.pause(time)
				self.pauseSignal.signal.emit(time)
				return

		def onSeek(self, time):
				self.seek(time)
				self.seekSignal.signal.emit(time)
				return

		def onSetROI(self, start, end, color):
				self.setROI(self, start, end, color)
				self.setROISignal.signal.emit(self, start, end, color)
				return

		def seekWindow(self):
				pass

		def getWindowTitle(self):
				return self.windowTitle()

		def getWindowGeometry(self):
				return makeStringFromQtGeometry(self.geometry())

		def setWindowGeometry(self, geometry):
				geom = self.geometry()
				left, top, w, h = geom.getRect()

				old_size = QtCore.QSize(w, h)

				self.setGeometry(buildQtGeometryFromString(geometry))
				geom = self.geometry()
				left, top, w, h = geom.getRect()
				new_size = QtCore.QSize(w, h)
				if self.isHidden():
						resizeEvent = QtGui.QResizeEvent(new_size, old_size)
						app = QtCore.QCoreApplication.instance()
						app.sendEvent(self, resizeEvent)
				pass

		def keyPressEvent(self, event):
				if event.key() == QtCore.Qt.Key_Space:
						if self.playing:
								self.onPause(self.time)
						else:
								self.onPlay(self.time)
				return


class cSynchronizer(QtCore.QObject):
		"""
		Synchronizes data visualizers.
		Create an instance, add clients and call run to start them synchronized.
		"""

		def __init__(self):
				"""
				Constructor of the class.
				"""
				QtCore.QObject.__init__(self)
				self.clients = {}
				""":type: dict
				Container of visualizers: {client<iSynchronizable> : timesyncfunc<tuple>, }"""
				self.clients2modulenames = {}
				""":type: dict
				Container of visualizers: {client<iSynchronizable> : module<iView>, }"""
				self.connections = {}
				""":type: dict
				Container of the connected iSynchronizable methods"""
				self.seektime = None
				""":type: float
				The last used seek time"""
				self.signal2client = {}
				self.ROIstart = 0.0
				self.ROIend = 0.0
				"Module name to regiter clients"
				self.DynamicClients = set()
				self.clientsBlocked = False
				self.module = ''
				self.layouts = {}
				self.allClosedSignal = SimpleSignal()
				self.method_queue = []
				self.client_window_titles = set()
				self.windowid2client = {}
				self.module2windowids = {}
				self.calibritators = {}
				self.manager_mediator = None
				pass

		def addClient(self, client, timesyncfunc = None, title = None):
				"""
				Adds a new client to the list of clients.

				:Parameters:
					client : object providing iSynchronizable
						Object to synchronize
					timesyncfunc : tuple of 2 ndarrays
						Function of time synchronization (None means 1:1)
				:Return: None
				"""
				self.clients[client] = timesyncfunc
				self.clients2modulenames[client] = self.module
				self.layouts[client] = client.getWindowGeometry()

				window_id = self.createClientWindowId(client, self.module, title = title)
				self.signal2client[client.playSignal] = client
				self.signal2client[client.pauseSignal] = client
				self.signal2client[client.seekSignal] = client
				self.signal2client[client.setROISignal] = client
				self.signal2client[client.closeSignal] = client
				self.signal2client[client.selectGroupSignal] = client
				self.signal2client[client.setXLimOnlineSignal] = client
				self.signal2client[client.calibNavNeededSignal] = client

				client.seekSignal.signal.connect(self.seek)
				client.playSignal.signal.connect(self.play)
				client.pauseSignal.signal.connect(self.pause)
				client.closeSignal.signal.connect(self.onClose)
				client.setROISignal.signal.connect(self.onSetROI)
				client.selectGroupSignal.signal.connect(self.selectGroup)
				client.setXLimOnlineSignal.signal.connect(self.set_xlim_online)
				client.calibNavNeededSignal.signal.connect(self.addCalibrator)

				self.DynamicClients.add(client)
				return window_id

		def addStaticClient(self, client, timesyncfunc = None, title = None):
				"""
				Adds a new static client to the list of clients. No callbacks will be set except for closeCallback.

				:Parameters:
					client : object providing iSynchronizable
						Object to synchronize
					timesyncfunc : tuple of 2 ndarrays
						Function of time synchronization (None means 1:1)
				:Return: None
				"""
				self.clients[client] = timesyncfunc
				self.clients2modulenames[client] = self.module
				self.signal2client[client.closeSignal] = client
				client.closeSignal.signal.connect(self.onCloseStaticClient)
				self.layouts[client] = client.getWindowGeometry()
				window_id = self.createClientWindowId(client, self.module, title = title)
				return window_id

		def createClientWindowId(self, client, module, title = None):
				i = 0
				window_id = client.createWindowId('', title = title)
				window_ids = self.module2windowids.get(module, set())
				while window_id in window_ids:
						window_id = client.createWindowId('-%d' % i, title = title)
						i += 1

				window_ids.add(window_id)
				self.module2windowids[module] = window_ids
				key = module, window_id
				self.windowid2client[key] = client
				return window_id

		def convertToCommonTime(self, client, time):
				"""
				Convert the `time` from `client` time domain to common time domain.

				:Parameters:
					client : `iSynchronizable`
					time : float
				:ReturnType: float
				"""
				if self.clients[client]:
						commontime, clienttime = self.clients[client]
						time = numpy.interp(time, clienttime, commontime)
				return time

		def convertToClientTime(self, client, time):
				"""
				Convert the `time` from common time domain to `client` time domain.

				:Parameters:
					client : `iSynchronizable`
					time : float
				:ReturnType: float
				"""
				if self.clients[client]:
						commontime, clienttime = self.clients[client]
						time = numpy.interp(time, commontime, clienttime)
				return time

		def others(self, sender, clients):
				"""
				Get the list of clients ecept `caller`.

				:Parameters:
					sender : `iSynchronizable`
				:ReturnType: iterable of `iSynchronizable`
				"""
				return [client for client in clients if client is not sender]

		def capture(self, capdir):
				client_2_picture = {}
				if not os.path.isdir(capdir):
						os.makedirs(capdir)
				for client in self.clients:
						module_name = self.clients2modulenames[client]
						window_id = client.getWindowTitle()
						title = '%s-%s.png' % (module_name, window_id)
						name = os.path.join(capdir, title)
						client_2_picture[(module_name, window_id)] = os.path.abspath(name)
						client.copyContentToFile(name, format = 'png')
				return client_2_picture

		def remove_pictures(self, client_2_picture):
				dirs = set()
				for picture in client_2_picture.itervalues():
						dirs.add(os.path.dirname(picture))
						os.remove(picture)

				for dir in dirs:
						files = [f for f in os.listdir(dir)
										 if os.path.isfile(os.path.join(dir, f))]
						if not files:
								shutil.rmtree(dir)
				return

		def callClientMethod(self, funcName, *args, **kwargs):
				if self.clientsBlocked:
						if funcName != 'seek':
								signal = self.sender()
								self.method_queue.append((funcName, signal, args, kwargs))
						return
				self.clientsBlocked = True
				sender = None
				signal = kwargs.get('signal', self.sender())

				if signal:
						sender = self.signal2client[signal]
						others = self.others(sender, self.DynamicClients)
				else:
						others = self.DynamicClients

				clienttime = None

				if 'time' in kwargs:
						time = kwargs['time']
						if sender:
								commontime = self.convertToCommonTime(sender, time)
						else:
								commontime = time
						clienttime = {}
						for client in others:
								clienttime[client] = self.convertToClientTime(client, commontime)
						self.seektime = time

				for client in others:
						func = getattr(client, funcName)
						if clienttime:
								args = clienttime[client],
						func(*args)

				QtCore.QCoreApplication.processEvents()

				self.clientsBlocked = False

				if self.method_queue:
						funcName, signal, args, kwargs = self.method_queue.pop(0)
						kwargs['signal'] = signal
						self.callClientMethod(funcName, *args, **kwargs)
				return

		def setAxesLimits(self, limits):
				for client in self.clients:
						client.setAxesLimits(limits)
				return

		def onClose(self, geometry):
				"""
				Removes the sender from the synchronized clients container.

				:Parameters:
				:Return: None
				"""

				sender = self.onCloseStaticClient(geometry, DynamicClient = True)
				self.signal2client.pop(sender.playSignal)
				self.signal2client.pop(sender.pauseSignal)
				self.signal2client.pop(sender.seekSignal)
				self.signal2client.pop(sender.setROISignal)
				self.signal2client.pop(sender.selectGroupSignal)
				self.signal2client.pop(sender.setXLimOnlineSignal)
				self.signal2client.pop(sender.calibNavNeededSignal)
				if sender in self.calibritators:
						calibrator = self.calibritators.pop(sender)
						calibrator.close()

				sender.playSignal.signal.disconnect()
				sender.pauseSignal.signal.disconnect()
				sender.seekSignal.signal.disconnect()
				sender.setROISignal.signal.disconnect()
				sender.closeSignal.signal.disconnect()
				sender.selectGroupSignal.signal.disconnect()
				sender.setXLimOnlineSignal.signal.disconnect()
				sender.calibNavNeededSignal.signal.disconnect()
				if self.manager_mediator is not None:
						self.manager_mediator.send_close(self.clients2modulenames[sender])
				try:
						# order is important
						self.DynamicClients.remove(sender)
						# Dismantle any information about closed client, carefully
						module_name_closed = self.clients2modulenames[sender]
						window_id_closed = self.module2windowids[module_name_closed]
						for id in window_id_closed:
								key_ = module_name_closed, id
								if key_ in self.windowid2client:
										self.windowid2client.pop(key_)
						if module_name_closed in self.module2windowids:
								self.module2windowids.pop(module_name_closed)
						if sender in self.layouts:
								self.layouts.pop(sender)
						if sender in self.clients2modulenames:
								self.clients2modulenames.pop(sender)
						# dismantling done, continue.
				except KeyError:
						pass
				if not self.clients:
						self.allClosedSignal.signal.emit()
				pass

		def onCloseStaticClient(self, geometry, DynamicClient = False):
				sender = self.signal2client[self.sender()]
				self.clients.pop(sender)
				self.signal2client.pop(sender.closeSignal)
				self.layouts[sender] = geometry
				if not self.clients and not DynamicClient:
						self.allClosedSignal.signal.emit()
				return sender

		def onSetROI(self, caller, start, end, color):
				"""
				Set the Region Of Interest for clients except `caller`.

				:Parameters:
					caller : `iSynchronizable`
						Client that call this callback function.
					start : float
						Start timestamp of the ROI.
					end : float
						End timestamp of the ROI.
					color : str
						Color to mark the interval.
				"""
				if self.sender():
						sender = self.signal2client[self.sender()]
						start = self.convertToCommonTime(sender, start)
						end = self.convertToCommonTime(sender, end)
				else:
						sender = caller

				self.ROIstart = start
				self.ROIend = end
				self.callClientMethod('setROI', sender, start, end, color)
				return

		def start(self, seektime = None):
				for client in self.clients:
						client.start()
						if seektime is not None and client in self.DynamicClients:
								clienttime = self.convertToClientTime(client, seektime)
								client.seek(clienttime)
				self.seektime = seektime
				return

		def show(self):
				for client in self.clients:
						client.show()
				return

		def seek(self, time):
				self.callClientMethod('seek', time = time)
				return

		def play(self, time):
				self.callClientMethod('play', time = time)
				return

		def pause(self, time):
				self.callClientMethod('pause', time = time)
				return

		def selectGroup(self, GroupName):
				self.callClientMethod('selectGroup', GroupName)
				return

		def play_by_step(self, start, limit, step = 0.03):
				time = start
				while time < limit:
						self.seek(time)
						time += step
				return

		def start_client_recording(self, path, prefix = ""):
				for index, client in enumerate(self.clients):
						# Add a numbered prefix to prevent file duplication.
						# There is no better solution at the moment.
						client.start_recording(path, prefix + str(index))
				return

		def stop_client_recording(self):
				self.callClientMethod('stop_recording')
				return

		def set_xlim_online(self, x_min, x_max):
				if self.sender():
						sender = self.signal2client[self.sender()]
						x_min = self.convertToCommonTime(sender, x_min)
						x_max = self.convertToCommonTime(sender, x_max)

				self.callClientMethod('set_xlim_online', x_min, x_max)
				return

		def addCalibrator(self, data):
				videoplayer, vidcalibs = data
				self.calibritators[videoplayer] = Calibrator(videoplayer, vidcalibs,
																										 videoplayer.player.filename)
				calibrator = self.calibritators[videoplayer]
				calibrator.show()
				return

		def close(self):
				"""
				Closes all the synchronized clients.

				:Return: None
				"""
				for client in self.clients.keys():
						client.close()
						QtCore.QCoreApplication.processEvents()

				self.clients2modulenames = {}
				self.layouts = {}
				self.module2windowids = {}
				self.windowid2client = {}
				pass

		def getModuleWindowIds(self, module_name):
				if module_name in self.module2windowids:
						winIds = [winId for winId in self.module2windowids[module_name]]
				else:
						winIds = []
				return winIds

		def getClient(self, module_name, window_id = None):
				if window_id is not None:
						try:
								client = self.windowid2client[(module_name, window_id)]
						except KeyError:
								raise ValueError('%s module does not have %s window id for client'
																 % (module_name, window_id))
				else:
						# find client based on module_name only
						clients = self.getClients(module_name)
						if len(clients) < 1:
								raise ValueError('%s module does not have registered client' % module_name)
						elif len(clients) > 1:
								raise ValueError('%s module has multiple clients registered' % module_name)
						else:
								client = clients[0]
				return client

		def getClients(self, module_name):
				winIds = self.getModuleWindowIds(module_name)
				clients = [self.getClient(module_name, winId) for winId in winIds]
				return clients

		def setWindowTitles(self, title):
				for client in self.clients:
						if not client.userTitleSet:
								window_title = '%s-%s' % (client.getWindowId(), title)
								client.setWindowTitle(window_title)
				return

		def getModuleNames(self):
				return self.clients2modulenames.values()

		def setModule(self, module):
				self.module = module
				return

		def getLayout(self, client):
				if client in self.clients:
						self.layouts[client] = client.getWindowGeometry()
				return self.layouts[client]

		def setMediator(self, manager_mediator):
				self.manager_mediator = manager_mediator
				return


if __name__ == '__main__':
		import VideoNavigator
		import PlotNavigator
		import TrackNavigator

		import numpy as np
		from PySide import QtGui
		import sys
		import optparse

		app = QtGui.QApplication([])

		parser = optparse.OptionParser()
		parser.add_option('-v', '--video',
											help = 'video file, default is %default',
											default = 'c:/KBData/measurement/test/CVR3_B1_2011-02-10_16-53_020.avi')
		parser.add_option('-p', '--hold-navigator',
											help = 'Hold the navigator, default is %default',
											default = False,
											action = 'store_true')
		opts, args = parser.parse_args()

		if not os.path.isfile(opts.video):
				sys.stderr.write('%s: %s is missing\n' % (__file__, opts.video))
				exit(1)

		t = np.arange(0, 400, 0.01)

		pn1 = PlotNavigator.cPlotNavigator("First plot window")
		pn1.addsignal('sine', [t, np.sin(t)])
		pn1.addsignal('cosine', [t, np.cos(t)])

		pn2 = PlotNavigator.cPlotNavigator("Second plot window")
		pn2.addsignal('sine', [t, np.sin(t)])
		pn2.addsignal('cosine', [t, np.cos(t)])

		pn3 = PlotNavigator.cPlotNavigator("Third delayed plot window")
		pn3.addsignal('sine', [t, np.sin(t)])
		pn3.addsignal('cosine', [t, np.cos(t)])

		Coeff = np.ones_like(t)
		R = 150.0 * Coeff
		Offset = 1.5 * Coeff

		TN = TrackNavigator.cTrackNavigator()
		for Name, Color, r, o in [['curve-left-letf-side', 'r', 1, 1],
															['curve-left-right-side', 'b', 1, -1],
															['curve-right-left-side', 'g', -1, 1],
															['curve-right-right-side', 'y', -1, -1]]:
				Track = TN.addTrack(Name, t, color = Color)
				FuncName = Track.addFunc(TrackNavigator.circle, LengthMax = TN.LengthMax)
				Track.addParam(FuncName, 'R', t, r * R)
				Track.addParam(FuncName, 'Offset', t, o * Offset)
		TN.setViewAngle(-15.0, 15.0)
		object = {}
		object['dx'] = np.arange(40.0, 80.0, 0.001)
		object['dy'] = np.arange(0.0, 20.0, 0.0005)
		object['type'] = 1
		object['label'] = 'Label'
		object['color'] = [102, 205, 170]
		TN.addObject(t, object)

		VN = VideoNavigator.cVideoNavigator(opts.video, {})

		sync = cSynchronizer()
		sync.addClient(pn1)
		sync.addClient(pn2)
		sync.addClient(pn3, [t, t + 5])
		sync.addClient(TN)
		sync.addClient(VN)
		sync.start()
		sync.show()
		if opts.hold_navigator:
				sys.exit(app.exec_())
		sync.close()
