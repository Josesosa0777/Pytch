import PIL
from PySide import QtGui, QtCore
import pyglet

from Synchronizer import iSynchronizable

import VideoPlayer
from Group import iGroup
import background_pyglet
import figlib
from ldw_overlay_calibrator import LdwOverlayCalibrator


class cVideoNavigator(iGroup, iSynchronizable, QtCore.QObject):
    """
    A synchronizable video player

    :IVariables:
      filename : string
        Name of the avi file.
      player : cVideoPlayer instance
        the controlled video player.
    """

    def __init__(self, fn, calibrations):
        """
        Constructor of the class.

        :Parameters:
          fn : string
            Name of the avi file to play.
        """
        iSynchronizable.__init__(self)
        iGroup.__init__(self, VideoPlayer.PygletKeyCrossTable)
        QtCore.QObject.__init__(self)

        ###
        # TODO: remove hack
        # This line is introduced to avoid dead thread in case of invalid video
        # file.
        # Background: VideoPlayer uses pyglet.media.load() in a background thread.
        # If the file cannot be opened for any reason, exception is raised in
        # the thread, which does not stop the main application and cannot be caught.
        pyglet.media.load(fn)
        ###

        self.filename = fn

        # required because version compatibility
        if pyglet.version == '1.1.4':  # 32 bit version
            self.player = background_pyglet.PygletProxy(VideoPlayer.cVideoPlayer32,
                                                        self.filename, calibrations)
        elif pyglet.version == '1.2.4':  # 64 bit version
            self.player = background_pyglet.PygletProxy(VideoPlayer.cVideoPlayer64,
                                                        self.filename, calibrations)

        self.displaytime = None

        self.Markers = {}
        self.lastSeekTime = 0.0
        """:type: dict
        Container of the object markers {GroupType<int> : (Property<dict>,) , }"""
        self.player.imagedata_emitting_signal.signal.connect(self.save2clipboard)
        self.player.calibNavNeededSignal.signal.connect(self.calibNavNeeded)
        self.player.ldw_tire_calib_signal_show.signal.connect(
            self.start_ldw_tire_calibrator)
        self.player.ldw_tire_calib_signal_close.signal.connect(
            self.shutdown_ldw_tire_calibrator)

        # load calibration
        act_calib = calibrations.get_calibration(fn)
        self.setCalibration(act_calib)
        self.ldw_tire_calib = None
        return

    def setCalibration(self, calibration):
        self.player.setCalibration(calibration)
        return

    def calibNavNeeded(self, vidcalibs):
        vidcalib, = vidcalibs
        self.calibNavNeededSignal.signal.emit((self, vidcalib))
        return

    def start_ldw_tire_calibrator(self, video_data):
        '''
    Opens and shows the calibrator for the ldw tire overlay
    '''
        video_width, video_height = video_data
        self.ldw_tire_calib = LdwOverlayCalibrator(video_width, video_height)
        self.player.ldw_tire_overlay_calib = self.ldw_tire_calib.get_overlay_state()
        self.player.on_draw()
        self.ldw_tire_calib.show()
        self.ldw_tire_calib.signal_status_updated.signal.connect(
            self.refresh_ldw_tire_calibration)
        return

    def refresh_ldw_tire_calibration(self, new_data):
        '''
    Function to handle the update from ldw_tire_calib
    '''
        self.player.ldw_tire_overlay_calib = new_data
        self.player.on_draw()
        return

    def shutdown_ldw_tire_calibrator(self):
        '''
    Shuts down the calibrator for the ldw tire overlay
    '''
        if self.ldw_tire_calib is not None:
            self.ldw_tire_calib.close()
        return

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
            0 : An 1.5m * 1.4m shaded rectangle  with frame standing in dx distance, centered at dy on road surface. It also can have a label if "label" is defined.
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

    def setDisplayTime(self, displaytime, displaytimevalue):
        """
        Set time to be displayed on the video.

        :Parameters:
          displaytime : ndarray same shape as dx
            This gives the possibility to display measurement time instead of video time on the GUI.
        """
        self.player.setDisplayTime(displaytime, displaytimevalue)
        return

    def setLegend(self, Markers):
        """
        :Parameters:
          Markers : dict
            {Type<int>: (Label<str>, Style<dict>),}
        """
        self.player.setLegend(Markers)
        return

    def setSignal(self, name, time, signal, unit=''):
        """
        :Parameters:
          :name: str
            Name of the added Signal as String
          :Signal: ndarray
            Signal as an array. The corresponding time values must equal to `self.objecttime`.
          :unit: str
            Unit of the added Signal as String
        """
        self.player.setSignal(name, time, signal, unit)
        return

    def setAccelComp(self, acceltime, accelcomp):
        self.player.setAccelComp(acceltime, accelcomp)
        return

    def selectCalibration(self, truck, date):
        self.player.selectCalibration(truck, date)
        return

    def selectLane(self, lanenr):
        self.player.selectLane(lanenr)
        return

    def seek(self, time):
        self.player.seek_base(time)
        return

    def play(self, time):
        self.player.on_play_pause_base()
        return

    def pause(self, time):
        self.player.on_play_pause_base()
        self.seekSignal.signal.emit(self.player.player.time)
        self.seek(time)
        return

    def close(self):
        self.player.on_close()
        return

    def onSeek(self, time):
        if time == self.lastSeekTime: return
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

    def copyContentToClipboard(self):
        self.player.copyContentToClipboard()
        return

    def start_recording(self, path=None, filename_extra=''):
        if path is not None:
            self.player.recorder.set_target_path(path)
        self.player.begin_recording(filename_extra)
        pass

    def stop_recording(self):
        self.player.stop_recording()
        pass

    def save2clipboard(self, imageFileAsPng):
        image = PIL.Image.open(imageFileAsPng)
        width, height = image.size
        data = image.tostring('raw', 'RGBA')
        # from http://stackoverflow.com/questions/13302908/better-way-of-going-from-pil-to-pyside-qimage
        # if i don't use this data mixing, the colors won't be the same
        # Hint: PIL uses RGBA format, but PySide uses ARGB format
        data = ''.join([''.join(i) for i in zip(data[2::4], data[1::4], data[0::4], data[3::4])])

        qt_image = QtGui.QImage(data, width, height, QtGui.QImage.Format_ARGB32)
        clipboard = QtGui.QApplication.clipboard()
        clipboard.clear()
        clipboard.setPixmap(QtGui.QPixmap.fromImage(qt_image))

        imageFileAsPng.close()
        return

    def copyContentToFile(self, file, format='png'):
        self.player.copyContentToFile(file, format)
        return

    def getWindowTitle(self):
        return self.player.caption

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

    def start(self):
        self.player.setcallbacks(self.onSeek, self.onPlay, self.onPause, self.onClose)
        self.player.copy(self)
        self.player.selectGroupCallback = self.onSelectGroup
        self.player._setVisible(None, None, return_result=False)
        self.app = QtCore.QCoreApplication.instance()
        if not isinstance(self.app, QtGui.QApplication):
            self.app = QtGui.QApplication([])
        return

    def show(self):
        self.player.set_visible(True)
        return

    def _setVisible(self, GroupName, Visible):
        """
        :Parameters:
          GroupName : str
            Key in `Groups`
          Visible : bool
            Flag to set invisible (False) or visible (True) the selected group.
        """
        self.player._setVisible(GroupName, Visible, return_result=False)
        return


if __name__ == '__main__':
    import optparse
    import os
    import sys


    def close(data):
        a = QtCore.QCoreApplication.instance()
        a.quit()


    app = QtGui.QApplication([])

    parser = optparse.OptionParser()
    parser.add_option('-v', '--video',
                      help='video file, default is %default',
                      default='d:/measurement/dataeval-test/CVR3_B1_2011-02-10_16-53_020.avi')
    parser.add_option('-p', '--hold-navigator',
                      help='Hold the navigator, default is %default',
                      default=False,
                      action='store_true')
    opts, args = parser.parse_args()

    if not os.path.isfile(opts.video):
        sys.stderr.write('%s: %s is missing\n' % (__file__, opts.video))
        exit(1)
    VN = cVideoNavigator(opts.video, {})
    VN.start()
    VN.seek(3)
    VN.closeSignal.signal.connect(close)

    if opts.hold_navigator:
        sys.exit(app.exec_())
    VN.close()
