"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright:
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial
  property. We reserve all rights of disposal such as copying and passing on to
  third parties.
"""
import datetime
import logging

import numpy as np
from PySide.QtCore import QPoint, Qt

__docformat__ = "restructuredtext en"

import os
import sys
import math
import datavis
import time
from PySide.QtGui import QComboBox, QHeaderView, QIcon, QCursor, QDialog, \
    QListWidget, \
    QTableWidget, \
    QTableWidgetItem, QVBoxLayout, QGroupBox, QPushButton, QDesktopWidget, \
    QListWidgetItem, QLabel, QLineEdit, QTreeWidgetItem, QTreeWidget, QDialogButtonBox, QFormLayout

import matplotlib
from aebs.fill.dspace_exporter.dspace_resim_export_utils import preprocess_dspace_resimulation_data

if matplotlib.rcParams['backend.qt4'] != 'PySide':
    matplotlib.use('Qt4Agg')
    matplotlib.rcParams['backend.qt4'] = 'PySide'

from matplotlib.figure import Figure
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle, Polygon
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT
import matplotlib.pyplot as plot
from matplotlib.patches import Circle
import matplotlib.image as Image
from matplotlib.offsetbox import (TextArea, DrawingArea, OffsetImage,
                                  AnnotationBbox)
from PySide import QtCore, QtGui
import numpy
from Group import iGroup
from Synchronizer import cNavigator
import measparser
from measproc.IntervalList import maskToIntervals, intervalsToMask
from figlib import copyContentToClipboard, copyContentToFile, setAxesLimits
from PlotNavigator import FigureManager, cCanvasWithF1Sensing, DragPoint
from RecordingService import RecordingService
from functools import partial

LABELBOX_ALPHA = 0.2
COLOR_NONE = -1
NO_COLOR = (COLOR_NONE, COLOR_NONE, COLOR_NONE)
MAX_HISTORY_LENGTH = 30
SCALE_FACTOR = 0.75

# to avoid to change the scales to logarithmic scale
matplotlib.rc("keymap", yscale="", xscale="")
# new key to already used function
matplotlib.rc("keymap", home="home", forward="right")
# matplotlib.rc("grid" , color = 'k', linestyle = '-')

IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")
special_object_info = ['custom_labels', 'image_mapping_data', 'signal_mapping']

aliasMapping = {"dx": 'long. dist.', "dy": 'lat. dist.', "vx_abs": "Abs Long. Velocity", "vy_abs": "Abs Lat. Velocity",
                "vx": "Rel Long. Velocity", "vy": "Rel Lat. Velocity",
                "ax_abs": "Abs Long. Acceleration", "ay_abs": "Abs Lat. Acceleration", "ax": "Rel Long. Acceleration",
                "ay": "Rel Lat. Acceleration", "lane": "Lane", "mov_state": "Moving State",
                "video_conf": "Video Confidence", "lane_conf": "Lane Confidence", "radar_conf": "Radar Confidence",
                "obj_type": "Object Type", "measured_by": "Measured By", "contributing_sensors": "Contributing Sensors",
                "aeb_obj_quality": "AEB Object Quality", "acc_obj_quality": "ACC Object Quality", "dz": "dz",
                "dz_std": "dz_std", "yaw": "Yaw", "yaw_std": "Yaw std", "traffic_sign_id": "Traffic Sign ID",
                "universal_id": "Universal ID", "traffic_sign_confidence": "Traffic Sign Confidence",
                "traffic_existence_probability": "Traffic Existence Probability", "tracking_state": "Tracking State",
                "cut_in_cut_out": "Cut In Cut Out"}


class cTracks:
    def __init__(self):
        self.Visible = True
        self.FuncName = ''
        self.Tracks = []
        pass

    def changeVisiblity(self, QAction):
        self.Visible = QAction.isChecked()
        return

    def setFuncName(self, FuncName):
        self.FuncName = FuncName
        return


class cTrack:
    def __init__(self, Line, Time):
        self.Line = Line
        self.Time = Time
        self.FuncName = None
        self.Coeffs = {}
        self.Funcs = {}
        self.Defaults = {}
        self.ParamNames = {}
        pass

    def __call__(self, Index):
        func = self.Funcs[self.FuncName]
        Coeffs = self.Coeffs[func]
        Coeffs = Coeffs[Index, :]
        Defaults = self.Defaults[self.FuncName]
        X, Y = func(*Coeffs, **Defaults)
        self.Line.set_xdata(X)
        self.Line.set_ydata(Y)
        pass

    def addFunc(self, func, FuncName=None, dtype=None, **Defaults):
        if not isinstance(FuncName, str):
            FuncName = func.__name__
        if func.func_defaults is not None:
            NoDefParams = len(func.func_defaults)
        else:
            NoDefParams = 0
        NoParams = func.func_code.co_argcount - NoDefParams
        ParamNames = func.func_code.co_varnames[:NoParams]
        ParamNames = list(ParamNames)
        Coeffs = numpy.zeros((self.Time.size, len(ParamNames)), dtype=object)
        self.Coeffs[func] = Coeffs
        self.ParamNames[func] = ParamNames
        self.Funcs[FuncName] = func
        self.Defaults[FuncName] = Defaults
        self.FuncName = FuncName
        return FuncName

    def joinFunc(self, MasterFuncName, FuncName, **Defaults):
        self.Funcs[FuncName] = self.Funcs[MasterFuncName]
        self.Defaults[FuncName] = Defaults
        self.FuncName = FuncName
        return FuncName

    def addParam(self, FuncName, ParamName, Time, Value):
        Time, Value = measparser.cSignalSource.rescale(Time, Value, self.Time)
        self._addParam(FuncName, ParamName, Value)
        pass

    def addConstParam(self, FuncName, ParamName, Value):
        self._addParam(FuncName, ParamName, Value)
        pass

    def _addParam(self, FuncName, ParamName, Value):
        func = self.Funcs[FuncName]
        ParamNames = self.ParamNames[func]
        Column = ParamNames.index(ParamName)
        Coeffs = self.Coeffs[func]
        try:
            Coeffs[:, Column] = Value
        except ValueError:
            Coeffs[:, Column] = Value[:, 0]
        except Exception as e:
            print(e.message)
        pass

    def setFunc(self, FuncName):
        self.FuncName = FuncName
        pass

    def getIndex(self, Time):
        return max(0, self.Time.searchsorted(Time, side='right') - 1)


class cDataset:
    """
    Store and update any user-defined data to be plotted.

    Visibility can be controlled two ways, either showing/hiding the dataset or
    activating/deactivating its lines individually, where deactivated refers to
    display the line in grey color.
    """

    def __init__(self, Time, Xdata, Ydata, LineObjects):
        """
        :Parameters:
          Parent : QtGui.QWidget
          Time : <numpy.ndarray>
            Timestamps for `Xdata`, `Ydata`.
          Xdata : list or tuple or <numpy.ndarray>
            List or tuple of x coordinates. Every item is an array of
            x coordinates at a specific timestamp. In case the array is
            two-dimensional, the corresponding columns are considered together,
            i.e., an n-by-m matrix results in m line objects, each containing
            n points.
            [<numpy.ndarray>, ]
            The list or tuple of 1D-arrays is exchangable with a single 2D-array,
            and the list or tuple of 2D-arrays is exchangeable with a single
            3D-array.
          Ydata : list or tuple or <numpy.ndarray>
            See Xdata.
          LineObjects : list or tuple
            Objects to be drawn.
            [<matplotlib.lines.Line2D>, ]
        """
        self.Xdata = Xdata
        self.Ydata = Ydata
        self.Time = Time
        self.LineObjects = LineObjects

        self.Visible = True

        self.DatasetActivity = 'ALL'  # or 'NONE' or 'CUSTOM'
        [setattr(line, 'activity', True) for line in self.LineObjects]  # added attribute
        self._colorActive = self.LineObjects[0].get_color() if self.LineObjects else (0.0, 0.0, 0.0)
        self._colorInactive = (0.9, 0.9, 0.9)

        self._nLineObjects = len(LineObjects)  # optimization: calculate only once

        pass

    def contains(self, Line):
        """
        Check if the given line belongs to the dataset.

        :Parameters:
          Line : <matplotlib.lines.Line2D>
        :ReturnType: bool
        """
        return (Line in self.LineObjects)

    def update(self, ts):
        """
        Update coordinates of the current line object.

        :Parameters:
          ts : float
            Timestamp used for updating the current line object.
        """
        idx = max(0, self.Time.searchsorted(ts, side='right') - 1)
        nCurrentLineObjects = self.Xdata[idx].shape[1]
        # update lines
        for i in xrange(nCurrentLineObjects):
            self.LineObjects[i].set_xdata(self.Xdata[idx][:, i])
            self.LineObjects[i].set_ydata(self.Ydata[idx][:, i])
        # invalidate unnecessary lines
        for i in xrange(nCurrentLineObjects + 1, self._nLineObjects):
            self.LineObjects[i].set_xdata(numpy.nan)
            self.LineObjects[i].set_ydata(numpy.nan)
        pass

    def toggleLineActivity(self, Line):
        """
        Set line active/inactive, depending on the current state.

        :Parameters:
          Line : <matplotlib.lines.Line2D>
        """
        if Line not in self.LineObjects:
            return
        if self.DatasetActivity == 'ALL':
            for ln in self.LineObjects:
                ln.activity = True
                ln.set_color(self._colorActive)
        elif self.DatasetActivity == 'NONE':
            for ln in self.LineObjects:
                ln.activity = False
                ln.set_color(self._colorInactive)
        self.DatasetActivity = 'CUSTOM'
        Line.activity = not Line.activity
        color = self._colorActive if Line.activity else self._colorInactive
        Line.set_color(color)
        pass

    def showLinesActive(self):
        """Show lines as they were active."""
        self.DatasetActivity = 'ALL'
        [line.set_color(self._colorActive) for line in self.LineObjects]
        pass

    def showLinesInactive(self):
        """Show lines as they were inactive."""
        self.DatasetActivity = 'NONE'
        [line.set_color(self._colorInactive) for line in self.LineObjects]
        pass

    def showLinesRestored(self):
        """Show lines regarding the selected activity state."""
        self.DatasetActivity = 'CUSTOM'
        for line in self.LineObjects:
            color = self._colorActive if line.activity else self._colorInactive
            line.set_color(color)

    def getVisible(self):
        """
        Return visibility state.

        :ReturnType: bool
        """
        return self.Visible

    def updateVisible(self):
        """Apply visibility state."""
        visible = self.Visible
        map(lambda line: line.set_visible(visible), self.LineObjects)
        pass

    def changeVisiblity(self, QAction):
        self.Visible = QAction.isChecked()
        return


class cObjectData(object):
    """Object data container"""

    def __init__(self, Time, dX, dY, Color, Type, Point, Label, LabelBox, Valid, Init, ExtraData=None):
        self.Time = Time
        self.X = dX
        self.Y = dY
        self.Color = Color
        self.Type = Type
        self.Point = Point
        self.Label = Label
        self.LabelBox = LabelBox
        self.Valid = Valid
        self.Init = Init
        self.extraData = ExtraData
        self.ShowLabel = False
        self.ShowHistory = False
        self.HistoryLine = None
        self.HistoryMarkers = None

        return

    def removeObjectHistory(self):
        if self.HistoryMarkers:
            self.HistoryMarkers.remove()
            self.HistoryMarkers = None

        if self.HistoryLine:
            self.HistoryLine[0].remove()
            self.HistoryLine = None
        return


class cShapeData(object):
    def __init__(self, Time, Valid, Type, Vertices, DrawFunction, Attributes):
        self.Time = Time
        self.Valid = Valid
        self.Type = Type
        self.Vertices = Vertices
        self.Draw = DrawFunction
        self.Attributes = Attributes
        self.Attributes.update(closed=1)
        self.DrawnShape = None
        return

    def removeShape(self):
        if self.DrawnShape:
            self.DrawnShape.remove()
            self.DrawnShape = None
        return


class cTrackNavigator(iGroup, cNavigator):
    """Plot the tracks and the detected objects."""

    def __init__(self, Title='', FgNr=None,
                 LengthMin=0.0, LengthMax=150.0, WidthMin=-55.0, WidthMax=55.0,
                 EgoWidth=2.5, EgoLength=5.0,
                 EgoXOffset=0.0, EgoYOffset=0.0):
        """
        :Parameters:
          Title : str
          FgNr : int
            Default is None.
        """
        cNavigator.__init__(self)
        iGroup.__init__(self)
        self.is_slr = True
        self.selected_object_list = {}
        if isinstance(FgNr, int):
            self.figureNr = FgNr
        else:
            self.figureNr = 0

        if Title:
            self.Name = Title
        else:
            self.Name = 'TN'

        self.synchronizer = None
        self.commonTimestamp = None
        self.Menu = self.menuBar()
        self.setWindowIcon(QtGui.QIcon(os.path.join(IMAGE_DIRECTORY, 'track.png')))
        self.GroupMenu = QtGui.QMenu('Groups')
        self.Menu.addMenu(self.GroupMenu)
        self.TrackMenu = QtGui.QMenu('Tracks')
        self.Menu.addMenu(self.TrackMenu)
        self.Tracks = {}

        self.DatasetMenu = QtGui.QMenu('Datasets')
        self.Menu.addMenu(self.DatasetMenu)
        self.Datasets = []
        self.InstantNavigators = []
        self.HistoryLength = 10
        self.HistorySettings = None
        self.RangeSettings = None
        self.SignalMapping = None
        self.SignalMappingInfo = {}
        self.HistoryLengthSlider = None
        self.HistoryLengthLabel = None
        self.ViewMenu = None
        self.ViewActions = []
        self.createViewMenu()

        self.fig = Figure()
        self.Canvas = cCanvasWithF1Sensing(self.fig)
        self.Toolbar = NavigationToolbar2QT(self.Canvas, self)
        self.Toolbar.update()

        # override the callback for the home button of the toolbar
        self.Toolbar.home = self.home

        self.Objects = []
        """:type: list
        Container of the objects"""
        self.Shapes = []
        self.Curves = {}
        """:type: dict
        Container of curves {CurveType<int> : matplotlib.lines.Line2D instance}"""
        self.BindZones = {}
        """:type: dict
        Container of the bindzones {'LRR3': matplotlib.patches.PathPatch}"""
        self.LengthMin = LengthMin
        """:type: float
        Lower bound of the longitudinal direction."""
        self.LengthMax = LengthMax
        """:type: float
        Upper bound of the longitudinal direction."""
        self.WidthMin = WidthMin
        """:type: float
        Lower bound of the horizontal direction"""
        self.WidthMax = WidthMax
        """:type: float
        Upper bound of the horizontal direction"""
        self.EgoWidth = EgoWidth
        """:type: float
        Length of the ego vehicle"""
        self.EgoLength = EgoLength
        """:type: float
        Width of the ego vehicle"""
        self.EgoXOffset = EgoXOffset
        """:type: float
        X offset of the ego vehicle"""
        self.EgoYOffset = EgoYOffset
        """:type: float
        Y offset of the ego vehicle"""
        self.Markers = {}
        """:type: dict
        Container of the object markers"""
        self.MarkerLabels = {}
        self.MarkerTypesInUse = set()
        self.MarkerDtype = numpy.array(self.Markers.values()).dtype
        """:type: numpy.dtype
        stype for addObject method"""
        self.FOVs = []
        """:type: list
        List of Field of Views to be displayed"""
        self.aspectRatio = 'equal'
        """:type: str
        type of axis aspect ratio"""
        self.stateLabel = "ALL"
        """:type: int
        State indicator for All/Custom/None state of ObjectLabels"""
        self.showHistory = "NONE"
        """:type: str
        State indicator for All/Custom/None state of Objects' history"""
        self.DatasetActivity = "ALL"
        """:type: int
        State indicator for All/Custom/None state of datasets' activity"""
        self.showPosition = False
        """:type: bool
        Bool to toggle Objectposition in ObjectLabel on/off"""
        self.controlKeys = {'F1': 'Show/hide this help screen',
                            'Home': 'Back to original zoom',
                            'Backspace/LeftArrow': 'Undo in zoom',
                            'RightArrow': 'Do in zoom',
                            'p': 'Toggle pan-zoom mode',
                            'o': 'Toggle rectangle-zoom mode',
                            'g': 'Toggle grid on the selected axis',
                            'space': 'Start/stop playback',
                            'a': 'Toggle between auto/equal aspect ratio',
                            'h': 'Show/hide plot legend',
                            'm': 'Toggle object label shortening ON/OFF',
                            'v': 'Show/hide field of views',
                            'u': 'Change object label state ALL/CUSTOM/NONE',
                            'i': 'Change datasets\' activity state ALL/CUSTOM/NONE',
                            'z': 'Show/hide object position',
                            '.': 'Enable/disable floating object info function (does not work during playback)',
                            '_': 'Enable/disable floating object image info function (does not work during playback)',
                            'q': 'Copy current figure to the clipboard',
                            'l': 'Change history state ALL/CUSTOM/NONE ',
                            'Ctrl+l': 'History settings',
                            'Ctrl+r': 'Range settings'}
        """:type: dict
        Control keys {controlKey<str> : explanation<str>,}"""
        self.help_font = matplotlib.font_manager.FontProperties('monospace', 'normal', 'normal', 'normal', 'normal',
                                                                'small')
        """:type: FontProperties
        Font for the help"""
        self.help = self.fig.text(0.1, 0.5,
                                  'Keyboard shortcuts:\n\n'
                                  'F1                  %(F1)s\n'
                                  'F10                 Save current time to clipboard and also show it in log window\n'
                                  'Home                %(Home)s\n'
                                  'Backspace/LeftArrow %(Backspace/LeftArrow)s\n'
                                  'RightArrow          %(RightArrow)s\n'
                                  'p                   %(p)s\n'
                                  'o                   %(o)s\n'
                                  'g                   %(g)s\n'
                                  'Space               %(space)s\n'
                                  'a                   %(a)s\n'
                                  'h                   %(h)s\n'
                                  'm                   %(m)s\n'
                                  'v                   %(v)s\n'
                                  'u                   %(u)s\n'
                                  'i                   %(i)s\n'
                                  'z                   %(z)s\n'
                                  '.                   %(.)s\n'
                                  '_                   %(_)s\n'
                                  'q                   %(q)s\n'
                                  'l                   %(l)s\n'
                                  'Ctrl+l              %(Ctrl+l)s\n'
                                  'Ctrl+r              %(Ctrl+r)s\n\n'
                                  'Color coding for Objects: Stationary=RED, Ongoing=GREEN, Oncoming=BLUE\n' % self.controlKeys,
                                  visible=False, fontproperties=self.help_font,
                                  bbox=dict(facecolor='LightYellow', pad=20))
        """:type: matplotlib.text.Text
        Online help text"""

        self.SP = self.fig.add_subplot(1, 1, 1)
        self.SP.grid(True)  # background grid for subplot
        self.SP.set_aspect(self.aspectRatio)
        # reversed x axis
        self.SP.set_xlim(self.WidthMax, self.WidthMin)
        self.SP.set_ylim(self.LengthMin, self.LengthMax)

        self.ObjInfo = self.SP.annotate("", (0, 0), xycoords='data',
                                        xytext=(40, 40), textcoords='offset points', fontproperties=self.help_font,
                                        bbox=dict(boxstyle='square', facecolor='LightYellow'),
                                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
                                        visible=False, zorder=10)

        self.sign_icon_path = plot.imread(os.path.join(IMAGE_DIRECTORY, 'NoImageAvailable.png'))
        self.imagebox = OffsetImage(self.sign_icon_path, zoom=1)
        self.imagebox.image.axes = self.fig.axes[0]
        self.image_xy_position = (0, 0)
        self.ObjImageInfo = AnnotationBbox(self.imagebox, self.image_xy_position,
                                           xybox=(200., 80.), xycoords='data',
                                           boxcoords="offset points", pad=0.5,
                                           arrowprops=dict(arrowstyle="->",
                                                           connectionstyle="angle,angleA=0,angleB=90,rad=3"),
                                           )
        self.ObjImageInfo.set_visible(False)
        self.shortenlabel = False
        """:type: matplotlib.text.Annotation
        Floating annotation for objects"""
        self.showObjInfo = True
        """:type: bool
        Bool to toggle  Floating annotation for image objects"
        """
        self.showObjImageInfo = True
        """:type: bool
        Bool to toggle floating object information on/off"""
        self.xKeyPressed = False
        """:type: bool
        Bool to toggle between zoom only along X-axis or not
        """
        self.yKeyPressed = False
        """:type: bool
            Bool to toggle between zoom only along Y-axis or not
        """
        self.dragPoint = None
        self.str2drawfunctions = {
            'POLYGON': self.drawPolygon,
            'RECTANGLE': self.drawRectangle,
        }

        self.Traj = numpy.arange(self.WidthMax, self.WidthMin, 1e-1)

        self.fig.canvas.mpl_connect('pick_event', self.onPick)
        self.fig.canvas.mpl_connect('motion_notify_event', self.onMotion)
        self.fig.canvas.mpl_connect('key_press_event', self.onFigureKeyPress)
        self.fig.canvas.mpl_connect('key_release_event', self.onFigureKeyRelease)
        self.fig.canvas.mpl_connect('scroll_event', self.onFigureScroll)
        self.fig.canvas.mpl_connect('button_press_event', self.onFigureClickPress)
        self.fig.canvas.mpl_connect('button_release_event', self.onFigureClickRelease)
        self.figure_manager = FigureManager(self.Canvas, self.figureNr)

        self.is_recording = False
        self.recorder = RecordingService('TrackRecord')

        self.last_right_click_time = time.time()
        """:type: cObjectData
            Stores selected object for quick plotting of dx and dy values
        """

        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.Toolbar)
        self.setCentralWidget(self.Canvas)
        self.drawEgo()
        pass

    def AddSynchronizer(self, sync):
        self.synchronizer = sync

    def keyPressEvent(self, event):
        self.Canvas.keyPressEvent(event)
        self.seekWindow()
        return

    def keyReleaseEvent(self, event):
        self.Canvas.keyReleaseEvent(event)
        self.seekWindow()
        return

    def seek(self, time):
        # Overloaded to catch the event of a play from outside
        self.ObjInfo.set_visible(False)
        cNavigator.seek(self, time)
        return

    def close(self):
        # Halt the recording first
        if self.is_recording:
            self.stop_recording()
        for pn in self.InstantNavigators:
            pn.close()
        cNavigator.close(self)
        matplotlib.pyplot.close('all')
        self.Canvas.close()
        self.Toolbar.close()
        QtGui.QMainWindow.close(self)
        return

    def addStyles(self, Styles):
        if not Styles:
            return
        for Type, (LegendName, Style) in Styles.iteritems():
            self.Markers[Type] = Style
            self.MarkerLabels[Type] = LegendName
        return

    def setLegend(self):
        """
        Sets the markers for object drawing and generates the legend
        :Parameters:
          Markers : dict
            Defines the legend name and the display style of the objects
            {Type<int>: (LegendName<str>, style<dict>),}
        """

        Lines = []
        Labels = []
        Styles = []

        for Type, Style in self.Markers.iteritems():
            style = Style.copy()
            style.pop('fill', None)
            LegendName = self.MarkerLabels[Type]
            if Type not in self.MarkerTypesInUse:
                continue  # no legend for objects which aren't used by TrackNavigator
            if LegendName in Labels and Styles[Labels.index(LegendName)] == style:
                continue  # avoid duplications
            marker = style['marker']
            if marker == '' or marker == ' ' or marker is None:
                continue  # no legend for 'NoneType' objects
            Lines.append(matplotlib.lines.Line2D([0], [0], **dict(style)))
            Labels.append(LegendName)
            Styles.append(style)
        if not Lines or not Labels or not Styles:  # in case of empty lists return
            return
        # sort by labels
        hl = sorted(zip(Lines, Labels), key=lambda x: x[1])
        Lines, Labels = zip(*hl)

        leg = self.SP.legend(Lines, Labels, loc=(1.1, 0.2), prop={'family': 'monospace'}, numpoints=1)
        leg.set_visible(False)
        leg.draggable(True)
        pass

    def setViewAngle(self, LeftAngle, RightAngle, GroupName=None, **kwargs):
        """
        :Parameters:
          LeftAngle : float
            Left view angle in degree
          RightAngle : float
            Right view angle in degree
          GroupName : str
            GroupName to associate the bind zone with setVisible method. Default
            value is the length of `BindZones`.
        :Keywords:
          facecolor : str
            facecolor for axvspan call
          alpha : float
            alpha for axvspan call
        """
        if GroupName is None:
            GroupName = len(self.BindZones)

        MAXDIST = 5000  # arbitrary large number
        tan_phiLeft = numpy.tan(LeftAngle / 180.0 * numpy.pi)
        tan_phiRight = numpy.tan(RightAngle / 180.0 * numpy.pi)
        BindZone = PathPatch(Path(numpy.array([[0, 0],
                                               [-MAXDIST * tan_phiLeft, MAXDIST],
                                               [-MAXDIST * tan_phiLeft, -MAXDIST],
                                               [-MAXDIST * tan_phiRight, -MAXDIST],
                                               [-MAXDIST * tan_phiRight, MAXDIST],
                                               [0, 0]])), **kwargs)
        self.SP.add_patch(BindZone)
        self.BindZones[GroupName] = BindZone
        pass

    def _setVisible(self, GroupName, Visible):
        """
        :Parameters:
          GroupName : str
            Key in `Groups`
          Visible : bool
            Flag to set invisible (False) or visible (True) the selected group.
        """
        try:
            BindZone = self.BindZones[GroupName]
        except KeyError:
            pass
        else:
            BindZone.set_visible(Visible)
        self.seekWindow()
        pass

    def setGroup(self, GroupName, Visible, KeyCode):
        action = QtGui.QAction(GroupName, self)
        action.setCheckable(True)

        action.triggered.connect(lambda n=GroupName, _action=action:
                                 (self._setVisible(n, _action.isChecked()),
                                  self.onSelectGroup(n),))

        self.GroupMenu.addAction(action)
        action.setChecked(Visible)
        self._setVisible(GroupName, Visible)
        pass

    def addFOV(self, X, Y, color=(0, 0, 0), linestyle='-'):
        Point, = self.SP.plot(X, Y, marker=',', mew=1, ms=1, linestyle=linestyle,
                              visible=False, mfc=color, mec=color, color=color)
        self.FOVs.append(Point)
        pass

    def addTrack(self, Name, Time, **kwargs):
        """
        :Parameters:
          func : function
            function to calculate the track at timestamp.
          Time : numpy.ndarray
          Coeffs: arbitrary argument list
            (numpy.ndarray, )
        :Keywords:
          color : str
            'b' for blue, 'm' for magenta etc. Default is 'b'.
        """
        if self.commonTimestamp is None:
            self.commonTimestamp = Time
        if 'color' not in kwargs:
            kwargs['color'] = 'b'
        Line, = self.SP.plot(self.Traj, self.Traj, **kwargs)
        Track = cTrack(Line, Time)
        Key = Name, kwargs['color']
        try:
            Tracks = self.Tracks[Key]
        except KeyError:
            Tracks = cTracks()
            self.Tracks[Key] = Tracks
        Tracks.Tracks.append(Track)
        return Track

    def setTrack(self, TrackKey):
        Tracks = self.Tracks[TrackKey]
        TrackName, accelerator = TrackKey
        Tracks.setFuncName(TrackName)

        action = QtGui.QAction(TrackName, self)
        action.setCheckable(True)
        action.setChecked(True)
        action.triggered.connect(lambda tk=TrackKey, action=action:
                                 (Tracks.changeVisiblity(action),
                                  self.toggleVisibile(tk),))
        self.TrackMenu.addAction(action)

        Track = Tracks.Tracks[0]
        FuncName = Track.FuncName
        FuncNames = set(Track.Funcs.iterkeys())
        for Track in Tracks.Tracks:
            FuncNames = FuncNames.intersection(Track.Funcs.iterkeys())
        if len(FuncNames) > 1:

            FuncNames = list(FuncNames)
            FuncNames.sort()
            if FuncName not in FuncNames:
                FuncName = FuncNames[0]
            for Track in Tracks.Tracks:
                Track.setFunc(FuncName)
            Tracks.FuncName = (FuncName)
            for FuncName in FuncNames:
                action = QtGui.QAction(TrackName, self)
                action.setCheckable(True)
                action.triggered.connect(lambda tk=TrackKey, fn=FuncName:
                                         self.toggleTrackFunc(tk, fn))
                self.TrackMenu.addAction(action)

        self.TrackMenu.addSeparator()
        pass

    def toggleTrackFunc(self, TrackKey, FuncName):
        Tracks = self.Tracks[TrackKey]
        for Track in Tracks.Tracks:
            Track.setFunc(FuncName)
        self.seekWindow()
        pass

    def toggleVisibile(self, TrackKey):
        Tracks = self.Tracks[TrackKey]
        Visible = Tracks.Visible
        for Track in Tracks.Tracks:
            Track.Line.set_visible(Visible)
        self.seekWindow()
        pass

    def addSignalMappingInfo(self, name, signalMapping):
        self.SignalMappingInfo[name] = signalMapping

    def addObject(self, Time, Object):
        """
        :Parameters:
          Time : numpy.ndarray
          Object : dict
            {'dx':<numpy.ndarray>, 'dy':<numpy.ndarray>, 'label':<str>,
             'type':<numpy.ndarray or int>,
             'color':<numpy.ndarray or (Red<uint8>, Green<uint8>, Blue<uint8>)>}
        """
        if self.commonTimestamp is None:
            self.commonTimestamp = Time
        extraData = {}
        for key in Object.keys():
            if key not in special_object_info:
                extraData[key] = fitSize(Time, Object[key])
            else:
                extraData[key] = Object[key]

                # coordinate transformation
        dY = fitSize(Time, Object['dx'])
        dX = fitSize(Time, Object['dy'])

        Type = fitSize(Time, Object['type'])
        Label = Object['label']

        if 'color' in Object:
            Color = fitSize(Time, Object['color'])
        else:
            Color = initColor(Time)

        Valid = Object.get('valid', (Object['dx'] != 0.0) & (Object['dy'] != 0.0))  # backward compatibility

        if 'init' in Object:
            Init = Object['init']
        else:
            init_intervals = [(st, st + 1) for st, end in maskToIntervals(Valid)]
            Init = intervalsToMask(init_intervals, Valid.size)

        UniqueTypes = set(numpy.unique(Type))
        CurveTypes = self.CurveTypes
        PointTypes = UniqueTypes.difference(CurveTypes)
        UsedCurveTypes = set(self.Curves.keys())
        NewCurveTypes = (UniqueTypes.intersection(CurveTypes)).difference(UsedCurveTypes)

        self.MarkerTypesInUse.update(UniqueTypes)

        # create line object for each new curve type
        for CurveType in NewCurveTypes:
            line = matplotlib.lines.Line2D([0], [0])
            line.set(**self.Markers[CurveType])
            self.SP.add_line(line)
            self.Curves[CurveType] = line

        # check if each type has marker associated
        if not self.Markers:
            self.logger.warning('Marker definitions are not set in TrackNavigator!')
        else:
            for actType in UniqueTypes:
                if actType not in self.Markers:
                    self.logger.warning('Warning: %(label)s object with type %(acttype)d has no marker,'
                                        ' object drawing is disabled in TrackNavigator!' \
                                        % {'label': Label, 'acttype': actType})

        # create point geometry if needed
        if PointTypes:
            Point, = self.SP.plot(0, 0, 'o', picker=5)
        else:
            Point = None

        bbox_props = dict(boxstyle="round", fc="w", ec="0.5", alpha=0.3)
        LabelBox = self.SP.annotate("", (0, 0), xycoords='data',
                                    xytext=(0, 16), textcoords='offset points',
                                    ha="center", va="center", size=10, bbox=bbox_props, visible=False)

        if COLOR_NONE in Color:
            ColorMask = Color != COLOR_NONE
            Color = numpy.where(ColorMask, Color / 255.0, Color)
        else:
            Color = Color / 255.0

        self.Objects.append(cObjectData(Time, dX, dY, Color, Type, Point, Label, LabelBox, Valid, Init, extraData))
        return

    def addShape(self, Time, Shape):
        # TODO: try to add area colors and properties to legendvalues and try to save them here
        Type = fitSize(Time, Shape['type'])
        self.MarkerTypesInUse.update(set(numpy.unique(Type)))

        Valid = Shape['valid']
        Vertices = Shape['vertices']
        DrawFunction = self.str2drawfunctions[Shape['shape']]
        Attributes = {key: val for key, val in self.Markers[Type[0]].iteritems()
                      if key not in ['marker', 'ms', 'mew', 'mec', 'mfc', 'ls', 'lw']}

        self.Shapes.append(cShapeData(Time, Valid, Type, Vertices, DrawFunction, Attributes))
        return

    def addTrajectory(self, Time, Trajectory):
        traj_style = self.Markers[Trajectory.pop('type')]
        Track = self.addTrack(Trajectory.pop('name'), Time=Time, **traj_style)
        FuncName = Track.addFunc(Trajectory.pop('func'), dtype=object)
        for name, value in Trajectory.iteritems():
            Track.addParam(FuncName, name, Time, value)
        return

    def iterActualObjects(self, ObjList=None):
        PrevTime = None
        PrevIndex = None
        ObjList = self.Objects if ObjList is None else ObjList
        for Obj in ObjList:
            Time = Obj.Time
            if Time is not PrevTime:
                Index = max(Time.searchsorted(self.time, side='right') - 1, 0)
                PrevTime = Time
                PrevIndex = Index
            else:  # no search required (optimization)
                Index = PrevIndex

            yield (Index, Obj)

    def addDataset(self, Time, Xdata, Ydata, Label=None, **kwargs):
        """
        :Parameters:
          Time : list or tuple or <numpy.ndarray>
            Timestamps for `Xdata`, `Ydata`.
          Xdata : list or tuple or <numpy.ndarray>
            List or tuple of x coordinates. Every item is an array of
            x coordinates at a specific timestamp. In case the array is
            two-dimensional, the corresponding columns are considered together,
            i.e., an n-by-m matrix results in m line objects, each containing
            n points.
            [<numpy.ndarray>, ]
            The list or tuple of 1D-arrays is exchangable with a single 2D-array,
            and the list or tuple of 2D-arrays is exchangeable with a single
            3D-array.
          Ydata : list or tuple or <numpy.ndarray>
            See Xdata.
          Label : str
            Title of the corresponding menu entry.
        :Keywords:
          Any valid keyword argument for <matplotlib.lines.Line2D> objects.
        """
        kwargs.setdefault('color', 'k')
        kwargs.setdefault('linestyle', '-')
        kwargs.setdefault('marker', 'o')
        kwargs.setdefault('markersize', 2.0)
        Time = numpy.array(Time)
        if Label is None:
            Label = 'Dataset %d' % (len(self.Datasets) + 1)
        # convert all data list items to 2D arrays
        converter = lambda x: x.reshape((x.size, 1)) if x.ndim < 2 else x
        Xdata = map(converter, Xdata)
        Ydata = map(converter, Ydata)
        # max. number of simultaneously displayed lines
        nMaxObjs = numpy.max(map(lambda x: x.shape[1], Xdata))
        # create and initialize line objects
        zeroArray = numpy.zeros((1, nMaxObjs))
        lines = self.SP.plot(zeroArray, zeroArray, **kwargs)
        [line.set_picker(2) for line in lines]
        # store data set - NOTE: coordinate transformation is applied
        dataset = cDataset(Time=Time, Xdata=Ydata, Ydata=Xdata, LineObjects=lines)
        self.Datasets.append(dataset)
        # add menu entry
        action = QtGui.QAction(Label, self)
        action.setCheckable(True)
        action.setChecked(True)
        action.triggered.connect(lambda label=Label, _action=action:
                                 (dataset.changeVisiblity(_action),
                                  dataset.updateVisible(),

                                  self.seekWindow()))

        self.DatasetMenu.addAction(action)

        pass

    def copyContentToClipboard(self):  # declared in Synchronizer.iSynchronizable
        copyContentToClipboard(self.fig)
        pass

    def copyContentToFile(self, file, format=None):  # declared in Synchronizer.iSynchronizable
        copyContentToFile(self.fig, file, format)
        pass

    def setAxesLimits(self, limits):
        setAxesLimits(self.fig, limits)
        pass

    def onFigureKeyPress(self, event):
        """
        Event handler for key press event.
        CONVENTION: Numbers and capital letters are reserved for enabling/disabling groups.

        :Return: None
        """
        if not hasattr(event, 'keysim'):
            setattr(event, 'keysim', event.key)
        if event.keysim == ' ':
            # synchronizable interface callback
            if self.playing:
                self.onPause(self.time)
            else:
                self.onPlay(self.time)
        elif event.keysim == 'a':
            # pressing 'a' toggles between auto/equal aspect ratio
            self.setAspectRatio()
        elif event.keysim == 'v':
            for Point in self.FOVs:
                Point.set_visible(not Point.get_visible())
            self.fig.canvas.draw()
        elif event.keysim == 'i':
            self.setDatasetActivity()
        elif event.keysim == 'u':
            self.setLabelState()
        elif event.keysim == 'q':
            self.copyContentToClipboard()
            self.Toolbar.set_message('Figure copied to clipboard')
        elif event.keysim == 'l':
            self.setHistoryState()
        elif event.keysim == 'x':
            self.xKeyPressed = True
        elif event.keysim == 'y':
            self.yKeyPressed = True
        elif event.keysim == 'm':
            self.shortenlabel = not self.shortenlabel
        elif event.keysim == 'F10' or event.keysim == 'f10':
            Index = max(
                self.commonTimestamp.searchsorted(self.time, side='right') - 1, 0)
            relativeTimestamp = self.commonTimestamp - self.commonTimestamp[0]
            display_time = relativeTimestamp[Index]
            dt_obj = datetime.datetime.utcfromtimestamp(display_time)
            minutes_in_ms = dt_obj.minute * 60000000
            seconds_in_ms = dt_obj.second * 1000000
            microseconds = dt_obj.microsecond
            minutes_ = int(display_time) / 60
            minutes = str(int(display_time) / 60).zfill(2)
            seconds = str(int(display_time - minutes_ * 60)).zfill(2)
            time_in_microseconds = minutes_in_ms + seconds_in_ms + microseconds
            time_in_string = "Abs: " + str(
                self.time) + "; Rel: " + str(
                time_in_microseconds) + "ms" + "; Rel: {}:{}s".format(minutes, seconds)
            self.logger.info(time_in_string)
            clipboard = QtGui.QApplication.clipboard()
            clipboard.setText(time_in_string)
        elif event.keysim in self.KeyCodes:
            self.onSelectGroup(self.KeyCodes[event.keysim])
        pass

    def onFigureKeyRelease(self, event):
        if not hasattr(event, 'keysim'):
            setattr(event, 'keysim', event.key)
        if event.keysim == 'x':
            self.xKeyPressed = False
        elif event.keysim == 'y':
            self.yKeyPressed = False
        return

    def onFigureClickPress(self, event):
        if event.button == 2 and event.inaxes == self.SP:
            self.dragPoint = DragPoint(event.xdata, event.ydata, ax=event.inaxes)
        return

    def onFigureClickRelease(self, event):
        if self.dragPoint:
            self.dragPoint = None
        return

    def onFigureScroll(self, event):
        if event.button == 'up':
            scale_factor = SCALE_FACTOR
        else:
            scale_factor = 1 / SCALE_FACTOR

        xdata, ydata = self.SP.transData.inverted().transform((event.x, event.y))

        xlim = self.SP.get_xlim()
        ylim = self.SP.get_ylim()

        curr_x_range = abs(xlim[0] - xlim[1])
        curr_y_range = abs(ylim[0] - ylim[1])

        x_pos_ratio = (xdata - xlim[1]) / curr_x_range
        y_pos_ratio = (ydata - ylim[0]) / curr_y_range

        new_x_range = curr_x_range * scale_factor
        new_y_range = curr_y_range * scale_factor

        new_x_min_limit = xdata - new_x_range * x_pos_ratio
        new_x_max_limit = xdata + new_x_range * (1 - x_pos_ratio)

        new_y_min_limit = ydata - new_y_range * y_pos_ratio
        new_y_max_limit = ydata + new_y_range * (1 - y_pos_ratio)

        if not self.yKeyPressed:
            self.SP.set_xlim(new_x_max_limit, new_x_min_limit)
        if not self.xKeyPressed:
            self.SP.set_ylim(new_y_min_limit, new_y_max_limit)
        self.seekWindow()
        return

    def home(self):
        self.SP.set_xlim(self.WidthMax, self.WidthMin)
        self.SP.set_ylim(self.LengthMin, self.LengthMax)
        self.seekWindow()
        return

    def setAspectRatio(self, value=None):
        '''
        Method for changing aspect ratio.
        The method can toggle between aspect values (equal, auto) and can set
        the aspect ratio to a specific value.
        '''
        if value:
            self.aspectRatio = value
        else:
            if self.aspectRatio == 'equal':
                self.aspectRatio = 'auto'
                # Set the state on the view menu too
                self.aspectRatioMenu.actions()[1].setChecked(True)
            else:
                self.aspectRatio = 'equal'
                # Set the state on the view menu too
                self.aspectRatioMenu.actions()[0].setChecked(True)
        self.SP.set_aspect(self.aspectRatio)
        self.Toolbar.set_message("Aspect ratio set to %s." % self.aspectRatio)
        self.fig.canvas.draw()

    def setLabelState(self, value=None):
        '''
        Method for changing label state.
        The method can change label state to All, Custom or None and can set
        the label state to a specific value.
        '''
        if value:
            self.stateLabel = value
        else:
            if self.stateLabel == "ALL":
                self.stateLabel = "CUSTOM"
                # Set the state on the view menu too
                self.labelStateMenu.actions()[1].setChecked(True)
            elif self.stateLabel == "CUSTOM":
                self.stateLabel = "NONE"
                # Set the state on the view menu too
                self.labelStateMenu.actions()[2].setChecked(True)
            else:
                self.stateLabel = "ALL"
                # Set the state on the view menu too
                self.labelStateMenu.actions()[0].setChecked(True)
        self.Toolbar.set_message("Label state set to %s." % (self.stateLabel))
        self.seekWindow()

    def setDatasetActivity(self, value=None):
        '''
        Method for changing dataset activity.
        The method can change dataset activity to All, Custom or None and can set
        the dataset activity to a specific value.
        '''
        if value:
            self.DatasetActivity = value
            for ds in self.Datasets:
                if value == 'CUSTOM':
                    ds.showLinesRestored()
                elif value == 'NONE':
                    ds.showLinesInactive()
                elif value == 'ALL':
                    ds.showLinesActive()
        else:
            if self.DatasetActivity == "ALL":
                self.DatasetActivity = "CUSTOM"
                # Set the state on the view menu too
                self.datasetStateMenu.actions()[1].setChecked(True)
                for ds in self.Datasets:
                    ds.showLinesRestored()
            elif self.DatasetActivity == "CUSTOM":
                self.DatasetActivity = "NONE"
                # Set the state on the view menu too
                self.datasetStateMenu.actions()[2].setChecked(True)
                for ds in self.Datasets:
                    ds.showLinesInactive()
            else:
                self.DatasetActivity = "ALL"
                # Set the state on the view menu too
                self.datasetStateMenu.actions()[0].setChecked(True)
                for ds in self.Datasets:
                    ds.showLinesActive()
        self.Toolbar.set_message("Datasets' activity set to %s." % (self.DatasetActivity))
        self.seekWindow()

    def setHistoryState(self, value=None):
        '''
        Method for changing object history state.
        The method can change object history states to All, Custom or None and can set
        the object history state to a specific value.
        '''
        if value:
            self.showHistory = value
        else:
            if self.showHistory == "ALL":
                self.showHistory = "CUSTOM"
                # Set the state on the view menu too
                self.historyStateMenu.actions()[1].setChecked(True)
            elif self.showHistory == "CUSTOM":
                self.showHistory = "NONE"
                # Set the state on the view menu too
                self.historyStateMenu.actions()[2].setChecked(True)
            else:
                self.showHistory = "ALL"
                # Set the state on the view menu too
                self.historyStateMenu.actions()[0].setChecked(True)
        self.Toolbar.set_message("History state set to %s." % (self.showHistory))
        self.seekWindow()

    def setObjPositionState(self):
        '''
        Method for changing object position state.
        The method can toggle between object position states (ON, OFF).
        '''
        self.showPosition = self.objPositionAction.isChecked()
        self.Toolbar.set_message("Show position in labels is %s." % ("ON" if self.showPosition else "OFF"))
        self.seekWindow()

    def setObjInfoState(self):
        '''
        Method for changing object info state.
        The method can toggle between object info states (ON, OFF).
        '''
        self.showObjInfo = self.objInfoAction.isChecked()
        self.ObjInfo.set_visible(self.showObjInfo)
        if self.showObjInfo == False:
            self.seekWindow()
        self.Toolbar.set_message("Show floating object info is %s." % ("ON" if self.showObjInfo else "OFF"))

    def setObjImageInfoState(self):
        '''
            Method for changing object info state.
            The method can toggle between object info states (ON, OFF).
        '''
        self.showObjImageInfo = self.objImageInfoAction.isChecked()
        self.ObjImageInfo.set_visible(self.showObjImageInfo)
        if self.showObjImageInfo == False:
            self.seekWindow()
        self.Toolbar.set_message("Show floating object image info is %s." % ("ON" if self.showObjImageInfo else "OFF"))

    def setLegendState(self):
        '''
        Method for changing legend state.
        The method can toggle between legend states (ON, OFF).
        '''
        for Axe in self.fig.axes:
            Legend = Axe.get_legend()
            if Legend:
                Legend.set_visible(self.legendAction.isChecked())
        self.fig.canvas.draw()

    def setHelpState(self):
        '''
        Method for changing help state.
        The method can toggle between help states (ON, OFF).
        '''
        self.help.set_visible(self.helpAction.isChecked())
        bx = self.help.get_window_extent()
        bx = bx.inverse_transformed(self.fig.transFigure)
        self.help.set_position(((1 - bx.width) / 2., (1 - bx.height) / 2.))
        self.fig.canvas.draw()

    def selectGroup(self, GroupName):
        iGroup.selectGroup(self, GroupName)
        [group.setChecked(not self.Toggles[GroupName])
         for group in self.GroupMenu.actions() if group.text() == GroupName]
        return

    def resizeEvent(self, event):
        cNavigator.resizeEvent(self, event)
        new_size = event.size()
        canvas_width = new_size.width()
        canvas_height = new_size.height() - self.Toolbar.height()
        self.Canvas.resizeEvent(event)
        self.Canvas.resize(canvas_width, canvas_height)
        self.onFigureResize(event)
        return

    def onFigureResize(self, event):
        if self.help.get_visible():
            bx = self.help.get_window_extent()
            bx = bx.inverse_transformed(self.fig.transFigure)
            self.help.set_position(((1 - bx.width) / 2., (1 - bx.height) / 2.))
        self.seekWindow()
        pass

    def onPick(self, event):
        Mice = event.mouseevent
        if Mice.button == 1:
            Picked = event.artist
            for obj in self.Objects:
                if obj.Point == Picked:
                    if self.stateLabel != "CUSTOM":
                        for o in self.Objects:
                            o.ShowLabel = self.stateLabel == "ALL"
                        self.stateLabel = "CUSTOM"
                        # Set the state on the view menu too
                        self.labelStateMenu.actions()[1].setChecked(True)
                        self.Toolbar.set_message("Label state set to %s." % (self.stateLabel))
                    obj.ShowLabel = not obj.ShowLabel
                    self.seekWindow()
                    return
            for dataset in self.Datasets:
                if dataset.contains(Picked):
                    dataset.toggleLineActivity(Picked)
                    self.DatasetActivity = "CUSTOM"
                    # Set the state on the view menu too
                    self.datasetStateMenu.actions()[1].setChecked(True)
                    self.Toolbar.set_message("Datasets' activity set to %s." % (self.DatasetActivity))
                    self.seekWindow()
                    return
        elif Mice.button == 3:
            difference = time.time() - self.last_right_click_time
            self.last_right_click_time = time.time()
            if difference > 1:
                MouseEvent = event.mouseevent
                if MouseEvent.inaxes == self.SP:
                    ObjsUnderCursor = {}
                    otherObjects = {}
                    for Index, Obj in self.iterActualObjects(self.Objects):
                        ActType = Obj.Type[Index]
                        if ActType not in self.Invisibles:
                            otherObjects[Obj.Label if isinstance(Obj.Label, basestring) else Obj.Label[Index]] = Obj
                            Dx, Dy = Obj.Point.get_transform().transform([Obj.X[Index], Obj.Y[Index]])
                            Dist = math.sqrt((Dx - MouseEvent.x) ** 2 + (Dy - MouseEvent.y) ** 2)
                            if Dist < 10:
                                ObjsUnderCursor[
                                    Obj.Label if isinstance(Obj.Label, basestring) else Obj.Label[Index]] = Obj

                    ctx_menu = QtGui.QMenu()
                    for object_key, object_value in ObjsUnderCursor.iteritems():
                        action_show_plot = QtGui.QAction("Show History Plot : " + object_key, self,
                                                         triggered=partial(self.showInfo, object_value))
                        action_show_plot.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'plot_16.png')))
                        ctx_menu.addAction(action_show_plot)
                    ctx_menu.addSeparator()
                    for object_key, object_value in ObjsUnderCursor.iteritems():
                        action_show_history = QtGui.QAction("Toggle History Trail : " + object_key, self,
                                                            triggered=partial(self.showHistoryTrail, object_value))
                        action_show_history.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'history_trail_16.png')))
                        ctx_menu.addAction(action_show_history)
                    ctx_menu.addSeparator()
                    action_compare_selected_plots = QtGui.QAction("Compare Plots", self,
                                                                  triggered=partial(self.showSelectedObjects,
                                                                                    ObjsUnderCursor, otherObjects))
                    action_compare_selected_plots.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'compare_16.png')))
                    ctx_menu.addAction(action_compare_selected_plots)
                    ctx_menu.addSeparator()
                    allObjects = {}
                    allObjects = ObjsUnderCursor.copy()
                    allObjects.update(otherObjects)
                    action_resim_export_selected_objects = QtGui.QAction("Select Resim Objects", self,
                                                                         triggered=partial(
                                                                             self.showResimSelectedObjects, allObjects))
                    action_resim_export_selected_objects.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'compare_16.png')))
                    ctx_menu.addAction(action_resim_export_selected_objects)

                    cursor = QCursor()
                    ctx_menu.exec_(cursor.pos())
                    self.last_right_click_time = time.time()
                    return

    def onMotion(self, event):
        if self.playing:
            pass
        elif self.dragPoint:
            # change limits
            xdata, ydata = self.SP.transData.inverted().transform((event.x, event.y))

            x_change = xdata - self.dragPoint.x
            y_change = ydata - self.dragPoint.y

            xlim = self.SP.get_xlim()
            ylim = self.SP.get_ylim()
            if not self.yKeyPressed:
                self.SP.set_xlim(xlim[0] - x_change, xlim[1] - x_change)
            if not self.xKeyPressed:
                self.SP.set_ylim(ylim[0] - y_change, ylim[1] - y_change)
            self.seekWindow()
        # while realtime playback is on this function should be disabled, as causes performance issues
        else:
            if self.showObjInfo:
                if event.inaxes == self.SP:
                    ObjsUnderCursor = []
                    for Index, Obj in self.iterActualObjects(self.Objects):
                        ActType = Obj.Type[Index]
                        if ActType not in self.Invisibles:
                            Dx, Dy = Obj.Point.get_transform().transform([Obj.X[Index], Obj.Y[Index]])
                            Dist = math.sqrt((Dx - event.x) ** 2 + (Dy - event.y) ** 2)
                            if Dist < 10:
                                ObjsUnderCursor.append("%s\ndx=%.2f dy=%.2f" %
                                                       ((Obj.Label if isinstance(Obj.Label, basestring) else Obj.Label[
                                                           Index]),
                                                        Obj.Y[Index],
                                                        Obj.X[Index]))
                    if ObjsUnderCursor:
                        self.ObjInfo.xy = (event.xdata, event.ydata)
                        self.ObjInfo.set_text(("\n%s\n" % ("-" * 16)).join(ObjsUnderCursor))
                        self.ObjInfo.set_visible(True)
                    else:
                        self.ObjInfo.set_visible(False)
                    self.seekWindow()

            if self.showObjImageInfo:
                if event.inaxes == self.SP:
                    ObjsUnderCursorDict = {}
                    for Index, Obj in self.iterActualObjects(self.Objects):
                        if 'image_mapping_data' in Obj.extraData.keys():
                            ActType = Obj.Type[Index]
                            if ActType not in self.Invisibles:
                                Dx, Dy = Obj.Point.get_transform().transform([Obj.X[Index], Obj.Y[Index]])
                                Dist = math.sqrt((Dx - event.x) ** 2 + (Dy - event.y) ** 2)
                                if Dist < 10:
                                    ObjsUnderCursorDict[
                                        Obj.Label if isinstance(Obj.Label, basestring) else Obj.Label[Index]] = Obj
                                    index = max(0, Obj.Time.searchsorted(self.time, side='right') - 1)
                                    try:  # TODO cahnge hard coded 'traffic_sign_id' to more generic
                                        image_data_to_load = Obj.extraData["image_mapping_data"][
                                            str(int(Obj.extraData["traffic_sign_id"][index]))]
                                    except:
                                        image_data_to_load = "NoImageAvailable"
                                    try:
                                        self.sign_icon_path = plot.imread(image_data_to_load)
                                    except:
                                        self.sign_icon_path = plot.imread(
                                            os.path.join(IMAGE_DIRECTORY, "NoImageAvailable.png"))
                    if bool(ObjsUnderCursorDict):
                        self.ObjImageInfo.xy = (event.xdata, event.ydata)
                        self.imagebox = OffsetImage(self.sign_icon_path, zoom=1)
                        self.ObjImageInfo.offsetbox = self.imagebox
                        self.imagebox.image.axes = self.fig.axes[0]
                        self.fig.axes[0].add_artist(self.ObjImageInfo)
                        self.ObjImageInfo.set_visible(True)
                    else:
                        self.ObjImageInfo.set_visible(False)
                    self.seekWindow()
        return

    def drawEgo(self):
        self.drawRectangle((-self.EgoWidth / 2.0 - self.EgoXOffset, 0.0 - self.EgoYOffset),
                           self.EgoWidth, -self.EgoLength,
                           color='blue', fill=False, facecolor=None, linewidth=5)
        pass

    def drawRectangle(self, topleft, width, height, **kwargs):
        return self.SP.add_patch(Rectangle(topleft, width, height, **kwargs))

    def drawPolygon(self, vertices, **kwargs):
        return self.SP.add_patch(Polygon(vertices, **kwargs))

    def seekWindow(self):
        curveDict = {}  # mapping curve types to object points
        for Tracks in self.Tracks.itervalues():
            for Track in Tracks.Tracks:
                if Track.Line.get_visible():
                    Index = Track.getIndex(self.time)
                    Track(Index)
        for Index, Obj in self.iterActualObjects(self.Objects):
            # remove the object history before redraw
            Obj.removeObjectHistory()

            ActType = Obj.Type[Index]
            # color spec
            ActColor = Obj.Color[Index]
            if COLOR_NONE in ActColor:
                ActColor = self.Markers[ActType]['color']
            R, G, B = matplotlib.colors.colorConverter.to_rgb(ActColor)

            if ActType in self.Curves:
                if ActType not in self.Invisibles:
                    # add the current object's coordinates to the corresponding curve
                    coordLists = curveDict.setdefault(ActType, ([], []))
                    coordLists[0].append(Obj.X[Index])
                    coordLists[1].append(Obj.Y[Index])
            else:
                if ActType in self.Invisibles or not Obj.Valid[Index]:
                    Obj.Point.set_visible(False)
                    Obj.LabelBox.set_visible(False)
                else:

                    Obj.Point.set_visible(True)

                    if Obj.Label[0] == 'SLR25_Front':
                        Obj.Point.set_xdata(round(Obj.extraData['BSD5_LatDispMIOFront_D0'][Index], 3))
                        Obj.Point.set_ydata(round(Obj.extraData['BSD5_LonDispMIOFront_D0'][Index], 3))
                    elif Obj.Label[0] == 'SLR25_RFB':
                        Obj.Point.set_xdata(round(Obj.extraData['BSD4_LatDispMIORightSide_D0'][Index], 3))
                        Obj.Point.set_ydata(round(Obj.extraData['BSD4_LonDispMIORightSide_D0'][Index], 3))
                    else:
                        Obj.Point.set_xdata(Obj.X[Index])
                        Obj.Point.set_ydata(Obj.Y[Index])

                    # set the predefined marker styles
                    if self.Markers:
                        Obj.Point.set(**self.Markers[ActType])
                    else:
                        Obj.Point.set()
                    # override edge color if it is different than default
                    Obj.Point.set_mec((R, G, B))

                    if Obj.Point.get_mfc() != 'None':
                        Obj.Point.set_mfc((R, G, B))

                    # draw object history
                    if (self.showHistory == "ALL" or (self.showHistory == "CUSTOM" and Obj.ShowHistory)
                            and (self.scatterCheckbox.isChecked() or self.lineCheckbox.isChecked())):
                        deltaTime = Obj.Time[Index] - self.HistoryLength
                        import numpy as np
                        history_index = np.argmax(Obj.Time > deltaTime)
                        samples = Index - history_index
                        for i in range(0, samples):
                            if Index - i <= 0 or Obj.Init[Index - i] or not Obj.Valid[Index - i]:
                                break
                        x_coords = Obj.X[Index - i:Index + 1]
                        y_coords = Obj.Y[Index - i:Index + 1]

                        # Draw the history line if needed
                        if self.lineCheckbox.isChecked() and len(x_coords) > 1:
                            Obj.HistoryLine = self.SP.plot(x_coords, y_coords,
                                                           linestyle='-',
                                                           color=(R, G, B),
                                                           marker=None)

                        # Draw the history markers if needed
                        if self.scatterCheckbox.isChecked() and len(x_coords) > 1:
                            alphas = numpy.linspace(0.05, 1, self.HistoryLength)
                            rgba = numpy.zeros((self.HistoryLength, 4))
                            rgba[:, 0:3] = [R, G, B]
                            rgba[:, 3] = alphas

                            Obj.HistoryMarkers = self.SP.scatter(x_coords, y_coords,
                                                                 s=self.Markers[ActType]['ms'] ** 2,
                                                                 # points^2 to points conversion
                                                                 color=rgba,
                                                                 marker=self.Markers[ActType]['marker'],
                                                                 edgecolors=rgba,
                                                                 facecolors=self.Markers[ActType]['mfc'],
                                                                 linewidths=self.Markers[ActType]['mew'])
                            Obj.Point.set_visible(False)  # When scatter is enabled the point is unnecessary

                    if ((self.stateLabel == "ALL"
                         or (self.stateLabel == "CUSTOM" and Obj.ShowLabel))
                            and Obj.Valid[Index]
                            and not (isinstance(Obj.Label, str) and not Obj.Label)):
                        Obj.LabelBox.set_visible(True)
                        if Obj.Label[0] == 'SLR25_Front':
                            Obj.LabelBox.xy = (Obj.extraData['BSD5_LatDispMIOFront_D0'][Index],
                                               Obj.extraData['BSD5_LonDispMIOFront_D0'][Index])
                        elif Obj.Label[0] == 'SLR25_RFB':
                            Obj.LabelBox.xy = (Obj.extraData['BSD4_LatDispMIORightSide_D0'][Index],
                                               Obj.extraData['BSD4_LonDispMIORightSide_D0'][Index])
                        else:
                            Obj.LabelBox.xy = (Obj.X[Index], Obj.Y[Index])
                        Obj.LabelBox.set_backgroundcolor((R, G, B, LABELBOX_ALPHA))
                        LabelBoxText = Obj.Label if isinstance(Obj.Label, str) else Obj.Label[Index]
                        if self.shortenlabel:
                            labelList = LabelBoxText.split("_")
                            try:
                                LabelBoxText = labelList[-3] + labelList[-2]
                            except:
                                pass
                        if self.showPosition:
                            if Obj.Label[0] == 'SLR25_Front':
                                LabelBoxText += ' (%.2f|%.2f)' % ((Obj.extraData['BSD5_LatDispMIOFront_D0'][Index],
                                                                   Obj.extraData['BSD5_LonDispMIOFront_D0'][Index],))
                            elif Obj.Label[0] == 'SLR25_RFB':
                                LabelBoxText += ' (%.2f|%.2f)' % ((Obj.extraData['BSD4_LatDispMIORightSide_D0'][Index],
                                                                   Obj.extraData['BSD4_LonDispMIORightSide_D0'][Index]))
                            else:
                                LabelBoxText += ' (%.2f|%.2f)' % (Obj.X[Index], Obj.Y[Index])
                        Obj.LabelBox.set_text(LabelBoxText)
                    else:
                        Obj.LabelBox.set_visible(False)

        for Index, Shape in self.iterActualObjects(self.Shapes):
            # remove shape before redraw
            Shape.removeShape()
            if Shape.Valid[Index] and not Shape.DrawnShape and Shape.Type[Index] not in self.Invisibles:
                vertices = Shape.Vertices(Index)
                Shape.DrawnShape = Shape.Draw(vertices, **Shape.Attributes)

        self.prepareCurves(curveDict)

        for dataset in self.Datasets:
            if dataset.getVisible():  # optimization: update only visible data
                dataset.update(self.time)

        self.fig.canvas.draw()
        if self.is_recording:
            width, height = self.fig.canvas.get_width_height()
            frame = numpy.fromstring(self.fig.canvas.tostring_argb(), dtype=numpy.uint8)
            frame.shape = (width, height, 4)
            # Transform to RGBA for the codec
            frame = numpy.roll(frame, 3, axis=2)
            self.recorder.update_current_record(frame)
        pass

    def createViewMenu(self):
        '''
        This menu creates View menu on the menu bar and
        sets it's actions according to the default state.
        '''
        self.ViewMenu = QtGui.QMenu('View')
        self.Menu.addMenu(self.ViewMenu)

        # Creating history settings window
        self.HistorySettings = QtGui.QWidget()
        self.HistorySettings.resize(200, 70)
        self.HistorySettings.setWindowTitle('History settings')

        self.HistoryLengthSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self.HistorySettings)
        self.HistoryLengthSlider.setMaximum(MAX_HISTORY_LENGTH)
        self.HistoryLengthSlider.setMinimum(0)
        self.HistoryLengthSlider.valueChanged[int].connect(self.setHistoryValue)
        label = QtGui.QLabel('History length [Seconds]:', self.HistorySettings)
        self.HistoryLengthLabel = QtGui.QLabel('0', self.HistorySettings)

        close_button = QtGui.QPushButton('Close', self)
        close_button.clicked.connect(self.closeHistoryWindow)
        close_button.resize(close_button.sizeHint())

        apply_button = QtGui.QPushButton('Apply', self)
        apply_button.clicked.connect(self.seekWindow)
        apply_button.resize(apply_button.sizeHint())

        self.lineCheckbox = QtGui.QCheckBox('Line', self)
        self.lineCheckbox.toggle()

        self.scatterCheckbox = QtGui.QCheckBox('Markers', self)
        self.scatterCheckbox.toggle()

        grid = QtGui.QGridLayout()
        grid.addWidget(self.lineCheckbox, 0, 0, 1, 2)
        grid.addWidget(self.scatterCheckbox, 1, 0, 1, 2)
        grid.addWidget(label, 2, 0, 1, 2)
        grid.addWidget(self.HistoryLengthSlider, 3, 0, 1, 2)
        grid.addWidget(self.HistoryLengthLabel, 3, 3)
        grid.addWidget(close_button, 4, 0)
        grid.addWidget(apply_button, 4, 1)
        self.HistorySettings.setLayout(grid)

        # Creating range settings window
        self.RangeSettings = QtGui.QWidget()
        self.RangeSettings.resize(200, 70)
        self.RangeSettings.setWindowTitle('Range settings')

        self.RangeLengthSliderMin = QtGui.QSlider(QtCore.Qt.Horizontal,
                                                  self.RangeSettings)
        self.RangeLengthSliderMin.setMaximum(0)
        self.RangeLengthSliderMin.setMinimum(-100)
        self.RangeLengthSliderMin.valueChanged[int].connect(self.setRangeLengthValueMin)
        label_range_x_min = QtGui.QLabel('Distance behind the ego vehicle [Meter]:', self.RangeSettings)
        self.RangeLengthSliderLabelMin = QtGui.QLabel('0', self.RangeSettings)

        self.RangeLengthSlider = QtGui.QSlider(QtCore.Qt.Horizontal,
                                               self.RangeSettings)
        self.RangeLengthSlider.setMaximum(500)
        self.RangeLengthSlider.setMinimum(0)
        self.RangeLengthSlider.valueChanged[int].connect(self.setRangeLengthValue)
        label_range_x = QtGui.QLabel('Distance ahead of ego vehicle [Meter]:', self.RangeSettings)
        self.RangeLengthSliderLabel = QtGui.QLabel('0', self.RangeSettings)

        self.RangeWidthSlider = QtGui.QSlider(QtCore.Qt.Horizontal,
                                              self.RangeSettings)
        self.RangeWidthSlider.setMaximum(200)
        self.RangeWidthSlider.setMinimum(20)
        self.RangeWidthSlider.valueChanged[int].connect(self.setRangeWidthValue)
        label_range_y = QtGui.QLabel('Width [Meter]:', self.RangeSettings)
        self.RangeWidthSliderLabel = QtGui.QLabel('0', self.RangeSettings)

        range_settings_close_button = QtGui.QPushButton('Close', self)
        range_settings_close_button.clicked.connect(self.closeRangeWindow)
        range_settings_close_button.resize(range_settings_close_button.sizeHint())

        range_settings_apply_button = QtGui.QPushButton('Apply', self)
        range_settings_apply_button.clicked.connect(self.seekWindow)
        range_settings_apply_button.resize(range_settings_apply_button.sizeHint())

        grid_range = QtGui.QGridLayout()
        grid_range.addWidget(label_range_x_min, 0, 0, 1, 2)
        grid_range.addWidget(self.RangeLengthSliderMin, 1, 0, 1, 2)
        grid_range.addWidget(label_range_x, 2, 0, 1, 2)
        grid_range.addWidget(self.RangeLengthSlider, 3, 0, 1, 2)
        grid_range.addWidget(label_range_y, 4, 0, 1, 2)
        grid_range.addWidget(self.RangeWidthSlider, 5, 0, 1, 2)
        grid_range.addWidget(self.RangeLengthSliderLabelMin, 1, 3)
        grid_range.addWidget(self.RangeLengthSliderLabel, 3, 3)
        grid_range.addWidget(self.RangeWidthSliderLabel, 5, 3)
        grid_range.addWidget(range_settings_close_button, 6, 0)
        grid_range.addWidget(range_settings_apply_button, 6, 1)
        self.RangeSettings.setLayout(grid_range)

        # Creating range settings window
        self.SignalMapping = QtGui.QWidget()
        self.SignalMapping.resize(1024, 768)
        self.SignalMapping.setWindowIcon(QtGui.QIcon(os.path.join(IMAGE_DIRECTORY, 'signal_mapping_24.png')))
        self.SignalMapping.setWindowTitle('Signal Mapping')
        self.SignalMappingComboStatusNames = QComboBox()
        self.SignalMappingComboStatusNames.currentIndexChanged.connect(
            self.signalMappingComboStatusNamesSelectionChange)

        self.SignalMappingTableWidget = QTableWidget()
        self.SignalMappingTableWidget.setSortingEnabled(True)
        self.SignalMappingTableWidget.setAlternatingRowColors(True)
        self.SignalMappingTableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.SignalMappingTableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        signalMappinglayout = QVBoxLayout()
        signalMappinglayout.addWidget(self.SignalMappingComboStatusNames)
        signalMappinglayout.addWidget(self.SignalMappingTableWidget)
        self.SignalMapping.setLayout(signalMappinglayout)

        # Creating view menu's actions
        self.helpAction = QtGui.QAction('Help', self, triggered=lambda: self.setHelpState())
        self.helpAction.setShortcut(self.tr('F1'))
        self.helpAction.setCheckable(True)
        self.ViewMenu.addAction(self.helpAction)

        self.ViewMenu.addAction(self.ViewMenu.addSeparator())

        self.legendAction = QtGui.QAction('Legend', self, triggered=lambda: self.setLegendState())
        self.legendAction.setShortcut(self.tr('h'))
        self.legendAction.setCheckable(True)
        self.ViewMenu.addAction(self.legendAction)

        self.aspectRatioMenu = QtGui.QMenu('Aspect Ratio')
        aspectActionGroup = QtGui.QActionGroup(self)
        equalState = QtGui.QAction('Equal', self, triggered=lambda: self.setAspectRatio(value='equal'))
        equalState.setCheckable(True)
        equalState.setChecked(True)
        autoState = QtGui.QAction('Auto', self, triggered=lambda: self.setAspectRatio(value='auto'))
        autoState.setCheckable(True)
        aspectActionGroup.addAction(equalState)
        aspectActionGroup.addAction(autoState)
        self.aspectRatioMenu.addActions([equalState, autoState])
        self.ViewMenu.addMenu(self.aspectRatioMenu)

        self.ViewMenu.addAction(self.ViewMenu.addSeparator())

        self.objInfoAction = QtGui.QAction('Floating Object Info', self, triggered=lambda: self.setObjInfoState())
        self.objInfoAction.setShortcut(self.tr('.'))
        self.objInfoAction.setCheckable(True)
        self.objInfoAction.setChecked(True)
        self.ViewMenu.addAction(self.objInfoAction)

        self.objImageInfoAction = QtGui.QAction('Floating Object Image Info', self,
                                                triggered=lambda: self.setObjImageInfoState())
        self.objImageInfoAction.setShortcut(self.tr('_'))
        self.objImageInfoAction.setCheckable(True)
        self.objImageInfoAction.setChecked(True)
        self.ViewMenu.addAction(self.objImageInfoAction)

        self.labelStateMenu = QtGui.QMenu('Object Label State')
        labelActionGroup = QtGui.QActionGroup(self)
        allLabelState = QtGui.QAction('All', self, triggered=lambda: self.setLabelState(value='ALL'))
        allLabelState.setCheckable(True)
        allLabelState.setChecked(True)
        customLabelState = QtGui.QAction('Custom', self, triggered=lambda: self.setLabelState(value='CUSTOM'))
        customLabelState.setCheckable(True)
        noneLabelState = QtGui.QAction('None', self, triggered=lambda: self.setLabelState(value='NONE'))
        noneLabelState.setCheckable(True)
        labelActionGroup.addAction(allLabelState)
        labelActionGroup.addAction(customLabelState)
        labelActionGroup.addAction(noneLabelState)
        self.labelStateMenu.addActions([allLabelState, customLabelState, noneLabelState])
        self.ViewMenu.addMenu(self.labelStateMenu)

        self.objPositionAction = QtGui.QAction('Object Position in Label', self,
                                               triggered=lambda: self.setObjPositionState())
        self.objPositionAction.setShortcut(self.tr('z'))
        self.objPositionAction.setCheckable(True)
        self.ViewMenu.addAction(self.objPositionAction)

        self.historyStateMenu = QtGui.QMenu('History State')
        historyActionGroup = QtGui.QActionGroup(self)
        allHistState = QtGui.QAction('All', self, triggered=lambda: self.setHistoryState(value='ALL'))
        allHistState.setCheckable(True)
        customHistState = QtGui.QAction('Custom', self, triggered=lambda: self.setHistoryState(value='CUSTOM'))
        customHistState.setCheckable(True)
        noneHistState = QtGui.QAction('None', self, triggered=lambda: self.setHistoryState(value='NONE'))
        noneHistState.setCheckable(True)
        noneHistState.setChecked(True)
        historyActionGroup.addAction(allHistState)
        historyActionGroup.addAction(customHistState)
        historyActionGroup.addAction(noneHistState)
        self.historyStateMenu.addActions([allHistState, customHistState, noneHistState])
        self.ViewMenu.addMenu(self.historyStateMenu)

        settings = QtGui.QAction('History Settings...', self, triggered=self.showHistorySettings,
                                 shortcut=self.tr('Ctrl+l'))
        self.ViewMenu.addAction(settings)

        rangeSettings = QtGui.QAction('Change Range...', self,
                                      triggered=self.showRangeSettings,
                                      shortcut=self.tr('Ctrl+r'))
        self.ViewMenu.addAction(rangeSettings)

        self.ViewMenu.addAction(self.ViewMenu.addSeparator())

        self.datasetStateMenu = QtGui.QMenu('Dataset State')
        datasetActionGroup = QtGui.QActionGroup(self)
        allDataState = QtGui.QAction('All', self, triggered=lambda: self.setDatasetActivity(value='ALL'))
        allDataState.setCheckable(True)
        allDataState.setChecked(True)
        customDataState = QtGui.QAction('Custom', self, triggered=lambda: self.setDatasetActivity(value='CUSTOM'))
        customDataState.setCheckable(True)
        noneDataState = QtGui.QAction('None', self, triggered=lambda: self.setDatasetActivity(value='NONE'))
        noneDataState.setCheckable(True)
        datasetActionGroup.addAction(allDataState)
        datasetActionGroup.addAction(customDataState)
        datasetActionGroup.addAction(noneDataState)
        self.datasetStateMenu.addActions([allDataState, customDataState, noneDataState])
        self.ViewMenu.addMenu(self.datasetStateMenu)
        self.ViewMenu.addAction(self.ViewMenu.addSeparator())
        signalMapping = QtGui.QAction('Signal Mapping', self,
                                      triggered=self.showSignalMapping,
                                      shortcut=self.tr('Ctrl+s'))
        self.ViewMenu.addAction(signalMapping)

    def on_accept(self):
        checked = []
        root = self.treeview_widget.invisibleRootItem()
        count = root.childCount()
        for i in range(count):
            object = root.child(i)
            if object.checkState(0) == QtCore.Qt.Checked:
                checked.append(object.text(0))
        self.get_resim_objects(checked, self.txt_start_time.text(), self.txt_end_time.text())

    def on_reject(self):
        self.treeview_widget.clear()
        self.ResimObjectExport.close()

    def createContextMenu(self):
        self.action_show_plot = QtGui.QAction("Show Info ", self, triggered=self.showInfo)
        self.action_show_plot.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'plot_16.png')))

    def showHistoryTrail(self, SelectedObject):
        if self.showHistory != "CUSTOM":

            for o in self.Objects:
                o.ShowHistory = self.showHistory == "ALL"
            self.showHistory = "CUSTOM"
            self.historyStateMenu.actions()[1].setChecked(True)
            self.Toolbar.set_message("History state set to %s." % (self.showHistory))

        SelectedObject.ShowHistory = not SelectedObject.ShowHistory
        self.seekWindow()

    def showSelectedObjects(self, SelectedObjects, otherObjects):
        objShowSelectedObjectsDialog = FrmShowSelectedObjects(SelectedObjects, otherObjects)
        objShowSelectedObjectsDialog.show()
        selectedObjectsForPlotting = []
        if objShowSelectedObjectsDialog.exec_():
            selectedObjectsForPlotting = objShowSelectedObjectsDialog.return_selected_objects()
        self.comparePlots(selectedObjectsForPlotting)

    def showResimSelectedObjects(self, allObjects):
        valid_selected_objects = self.validObjects(allObjects)
        videoclient = None
        for client, value in self.synchronizer.clients.items():
            if "NxtVideoNavigator" in client.__repr__():
                videoclient = client
                break
        objShowSelectedObjectsDialog = FrmResimObjectSelection(valid_selected_objects, self.selected_object_list,
                                                               self.Objects[0].Time,
                                                               self.synchronizer.manager_mediator.target.source.FileName,
                                                               self.logger, videoclient)
        objShowSelectedObjectsDialog.show()
        if objShowSelectedObjectsDialog.exec_():
            self.selected_object_list, self.resim_start_time, self.resim_end_time = objShowSelectedObjectsDialog.return_selected_objects()

    def validObjects(self, selectedObjects):

        if len(selectedObjects) == 0:
            return

        plottingData = {}
        for objKey, objValue in selectedObjects.iteritems():
            for Index, Obj in self.iterActualObjects(self.Objects):
                if Obj == objValue:
                    for i in range(100000):
                        if Index - i <= 0 or Obj.Init[Index - i] or not Obj.Valid[Index - i]:
                            break
                    for j in range(10000):
                        # if (Index == 0 and j == 0):
                        #   j = j + 1
                        if Index + j >= (len(Obj.Time)) or Obj.Init[Index + j] or not \
                                Obj.Valid[Index + j]:
                            break
                    data = {}
                    data['lateral_distance'] = Obj.X[Index - i:Index + j]
                    data['longitudinal_distance'] = Obj.Y[Index - i:Index + j]
                    # Check is extraData exists
                    extraData = {}
                    if bool(Obj.extraData):
                        for key, value in Obj.extraData.items():
                            if key not in special_object_info:
                                extraData[key] = Obj.extraData[key][Index - i:Index + j]
                            else:
                                extraData[key] = Obj.extraData[key]
                    data['extraData'] = extraData
                    data['time'] = Obj.Time[Index - i:Index + j]
                    if len(data['time']) == 0:
                        continue
                    else:
                        plottingData[Obj.Label[Index] + " " + str(data['time'][0]) + "-" + str(data['time'][-1])] = data
        return plottingData

    def showInfo(self, SelectedObject):
        for Index, Obj in self.iterActualObjects(self.Objects):
            if Obj == SelectedObject:
                for i in range(10000):
                    if Index - i <= 0 or Obj.Init[Index - i] or not Obj.Valid[Index - i]:
                        break
                for j in range(10000):
                    if Index + j >= (len(Obj.Time)) or Obj.Init[Index + j] or not Obj.Valid[Index + j]:
                        break
                lateral_distance = Obj.X[Index - i:Index + j]
                longitudinal_distance = Obj.Y[Index - i:Index + j]
                # Check is extraData exists
                extraData = {}
                if bool(Obj.extraData):
                    for key, value in Obj.extraData.items():
                        if key not in special_object_info:
                            extraData[key] = Obj.extraData[key][Index - i:Index + j]
                        else:
                            extraData[key] = Obj.extraData[key]

                time = Obj.Time[Index - i:Index + j]

                pn = datavis.PlotNavigator.cPlotNavigator(title='Object History :' + Obj.Label[Index])

                # Distinguish between different Fill-Objects and adapt History Plot individually
                # Case 1: Paebs Debug Object
                if 'FLC25_PAEBS_DEBUG' in Obj.Label[0]:

                    # Plot 1: Longitudinal Object Distances
                    # Left Axis
                    ax = pn.addAxis(ylabel='Lon. Object Distance')
                    pn.addSignal2Axis(ax, 'dx', time, longitudinal_distance, unit='m', color='b', ls='-')
                    pn.addSignal2Axis(ax, 'Cascade Distance', time, extraData['casc_dist'], unit='m', color='m', ls='-')
                    pn.addSignal2Axis(ax, 'Lon. Distance along Ego Path', time, extraData['dist_path'], unit='m',
                                      color='r', ls='-')
                    # Right Axis
                    ax = pn.addTwinAxis(ax, ylabel='TTC', color='g')
                    pn.addSignal2Axis(ax, "Time to Collision (TTC)", time, extraData['ttc'], unit='s', color='g',
                                      ls='-')

                    # Plot 2: Longitudinal Object Velocity
                    ax = pn.addAxis(ylabel='Velocity', ylim=(-15, 15))
                    pn.addSignal2Axis(ax, "Abs Long. Velocity", time, extraData['vx_abs'], unit='m/s', color='b',
                                      ls='-')
                    pn.addSignal2Axis(ax, "Rel Long. Velocity", time, extraData['vx'], unit='m/s', color='b', ls='--')
                    pn.addSignal2Axis(ax, "Rel. Long. transf. Velocity", time, extraData['vx_ref'], unit='m/s',
                                      color='r', ls='-')

                    # Plot 3: Classifications
                    # Left Axis
                    ylabel_text = "Motion State"
                    mapping = {0: 'Not Detected', 1: 'Moving', 2: 'Stopped', 3: 'Static', 4: 'Crossing', 5: 'Oncoming',
                               6: 'Default', 15: 'Not Available'}
                    ax = pn.addAxis(ylabel=ylabel_text, yticks=mapping, ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
                    pn.addSignal2Axis(ax, ylabel_text, time, extraData['mov_state'], unit='', color='b', ls='-')
                    # Right Axis
                    ylabel_text = "Lane"
                    mapping = {0: 'Unknown', 1: 'Ego', 2: 'Left', 3: 'Right', 4: 'Outside Left', 5: 'Outside Right',
                               6: 'Outside of Road Right', 7: 'Outside of Road Left', 8: 'Not Available'}
                    ylabel_text = 'Associated Lane'
                    ax = pn.addTwinAxis(ax, ylabel=ylabel_text, yticks=mapping,
                                        ylim=(min(mapping) - 0.5, max(mapping) + 0.5), color='g')
                    pn.addSignal2Axis(ax, ylabel_text, time, extraData['lane'], unit='', color='g', ls='-')

                    # Plot 4: Probabilities
                    # Left Axis
                    ticks = {k: str(k) for k in range(0, 110, 10)}
                    ax = pn.addAxis(ylabel='Probability', yticks=ticks, ylim=(min(ticks) - 5, max(ticks) + 5))
                    data = extraData['collision_prob'] * 100
                    pn.addSignal2Axis(ax, "Collision Probability", time, data.astype(int), unit='%', color='r', ls='-')
                    data = extraData['prob_exist']
                    pn.addSignal2Axis(ax, "Probability of Existance", time, data.astype(int), unit='%', color='g',
                                      ls='-')
                    data = extraData['class_conf_paebs']
                    pn.addSignal2Axis(ax, "Confidence of Classification", time, data.astype(int), unit='%', color='b',
                                      ls='-')
                    data = extraData['lane_conf_paebs']
                    pn.addSignal2Axis(ax, "Associated Lane Confidence", time, data.astype(int), unit='%', color='m',
                                      ls='-')
                    # Right Axis
                    mapping = {0: 'False', 1: 'True'}
                    ax = pn.addTwinAxis(ax, ylabel='Status', yticks=mapping,
                                        ylim=(min(mapping) - 0.5, max(mapping) + 0.5), color='g')
                    pn.addSignal2Axis(ax, "in Path Flag", time, extraData['in_path'], unit='', color='g', ls='--')

                    # Plot 5: Lateral Object Properties
                    # Left Axis
                    ax = pn.addAxis(ylabel='Lat. Distance')
                    pn.addSignal2Axis(ax, "dy", time, extraData['dy'], unit='m', color='b', ls='-')
                    # Right Axis
                    ax = pn.addTwinAxis(ax, ylabel="Lat. Velocities", color='g')
                    pn.addSignal2Axis(ax, "Rel. Lat. Velocity", time, extraData['vy'], unit='m/s', color='r', ls='-')
                    pn.addSignal2Axis(ax, "Abs. Lat. Velocity", time, extraData['vy_abs'], unit='m/s', color='g',
                                      ls='-')

                    # Plot 6: Object Detection
                    # Left Axis
                    ylabel_text = "Object Type"
                    mapping = {0: 'Point', 1: 'Car', 2: 'Truck', 3: 'Pedestrian', 4: 'Motorcycle', 5: 'Bicycle',
                               6: 'Wide', 7: 'Unclassified', 8: 'Other Vehicle', 15: 'Not Available'}
                    ax = pn.addAxis(ylabel=ylabel_text, yticks=mapping, ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
                    pn.addSignal2Axis(ax, ylabel_text, time, extraData['obj_type'], unit='', color='b', ls='-')
                    # Right Axis
                    ylabel_text = "Sensor Source"
                    mapping = {0: 'Unkown', 1: 'Radar only', 2: 'Camera only', 3: 'Fused', 4: 'Not Available'}
                    ax = pn.addTwinAxis(ax, ylabel=ylabel_text, yticks=mapping,
                                        ylim=(min(mapping) - 0.5, max(mapping) + 0.5), color='g')
                    pn.addSignal2Axis(ax, ylabel_text, time, extraData['obj_src'], unit='', color='g', ls='-')


                # All other Objects
                else:
                    ax = pn.addAxis(ylabel='long. dist.')
                    pn.addSignal2Axis(ax, 'dx', time, longitudinal_distance, unit='m', color='b', ls='-')
                    ax = pn.addTwinAxis(ax, ylabel='lat. dist.', ylim=(-15, 15), color='g')
                    pn.addSignal2Axis(ax, 'dy', time, lateral_distance, unit='m', color='g', ls='-')

                    if bool(Obj.extraData):
                        if ("vx_abs" in Obj.extraData.keys()) or ("vy_abs" in Obj.extraData.keys()) or (
                                "vx" in Obj.extraData.keys()) or ("vy" in Obj.extraData.keys()):
                            ax = pn.addAxis(ylabel='Velocity', ylim=(-15, 15))
                            if "vx_abs" in Obj.extraData.keys():
                                pn.addSignal2Axis(ax, "Abs Long. Velocity", time, extraData['vx_abs'], unit='m/s',
                                                  color='b', ls='-')
                            if "vx" in Obj.extraData.keys():
                                pn.addSignal2Axis(ax, "Rel Long. Velocity", time, extraData['vx'], unit='m/s',
                                                  color='b', ls='--')
                            if "vy_abs" in Obj.extraData.keys():
                                pn.addSignal2Axis(ax, "Abs Lat. Velocity", time, extraData['vy_abs'], unit='m/s',
                                                  color='g', ls='-')
                            if "vy" in Obj.extraData.keys():
                                pn.addSignal2Axis(ax, "Rel Lat. Velocity", time, extraData['vy'], unit='m/s', color='g',
                                                  ls='--')

                        if ("ax_abs" in Obj.extraData.keys()) or ("ay_abs" in Obj.extraData.keys()) or (
                                "ax" in Obj.extraData.keys()) or ("ay" in Obj.extraData.keys()):
                            ax = pn.addAxis(ylabel='Acceleration')
                            if "ax_abs" in Obj.extraData.keys():
                                pn.addSignal2Axis(ax, "Abs Long. Acceleration", time, extraData['ax_abs'], unit='m/s^2')
                            if "ay_abs" in Obj.extraData.keys():
                                pn.addSignal2Axis(ax, "Abs Lat. Acceleration", time, extraData['ay_abs'], unit='m/s^2')
                            if "ax" in Obj.extraData.keys():
                                pn.addSignal2Axis(ax, "Rel Long. Acceleration", time, extraData['ax'], unit='m/s^2')
                            if "ay" in Obj.extraData.keys():
                                pn.addSignal2Axis(ax, "Rel Lat. Acceleration", time, extraData['ay'], unit='m/s^2')

                        if ("dx_std" in Obj.extraData.keys()) or ("dy_std" in Obj.extraData.keys()) or \
                                ("vx_abs_std" in Obj.extraData.keys()) or ("vx_rel_std" in Obj.extraData.keys()) or \
                                ("vy_abs_std" in Obj.extraData.keys()) or ("vy_rel_std" in Obj.extraData.keys()):
                            ax = pn.addAxis(ylabel='Std. Dev. Distance')
                            if "dx_std" in Obj.extraData.keys():
                                pn.addSignal2Axis(ax, "Std. Dev. dx", time, extraData['dx_std'], unit='m', color='b',
                                                  ls='-')
                            if "dy_std" in Obj.extraData.keys():
                                pn.addSignal2Axis(ax, "Std. Dev. dy", time, extraData['dy_std'], unit='m', color='b',
                                                  ls='--')
                            ax = pn.addTwinAxis(ax, ylabel='Std. Dev. Vel.', color='g')
                            if "vx_abs_std" in Obj.extraData.keys():
                                pn.addSignal2Axis(ax, "Std. Dev. Lon. Velocity", time, extraData['vx_abs_std'],
                                                  unit='m/s', color='g', ls='-')
                            if "vx_rel_std" in Obj.extraData.keys():
                                pn.addSignal2Axis(ax, "Std. Dev. Lon. Rel. Velocity", time, extraData['vx_rel_std'],
                                                  unit='m/s', color='g', ls='--')
                            if "vy_abs_std" in Obj.extraData.keys():
                                pn.addSignal2Axis(ax, "Std. Dev. Lat. Velocity", time, extraData['vy_abs_std'],
                                                  unit='m/s', color='r', ls='-')
                            if "vy_rel_std" in Obj.extraData.keys():
                                pn.addSignal2Axis(ax, "Std. Dev. Lat. Rel. Velocity", time, extraData['vy_rel_std'],
                                                  unit='m/s', color='r', ls='--')

                        if "mov_state" in Obj.extraData.keys():
                            ylabel_text = "Moving State"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'mov_state' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['mov_state']
                            mapping = {0: 'stat', 1: 'stopped', 2: 'moving', 3: 'unknown', 4: 'crossing',
                                       5: 'crossing_left', 6: 'crossing_right', 7: 'oncoming'}
                            ax = pn.addAxis(ylabel=ylabel_text, yticks=mapping,
                                            ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['mov_state'], unit='', color='b', ls='-')

                        if "lane" in Obj.extraData.keys():
                            ylabel_text = "Lane"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'lane' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['lane']
                            mapping = {0: 'Ego', 1: 'Left', 2: 'Right', 3: 'Outside Left', 4: 'Outside Right',
                                       5: 'Unknown'}
                            if 'FLC25_CEM_TPF' in Obj.Label[0]:
                                mapping = {0: 'Ego', 1: 'Left', 2: 'Right', 3: 'Outside Left', 4: 'Outside Right',
                                           5: 'Unknown',
                                           6: 'Outside Road Left', 7: 'Outside Road Right'}
                            ax = pn.addTwinAxis(ax, ylabel=ylabel_text, yticks=mapping,
                                                ylim=(min(mapping) - 0.5, max(mapping) + 0.5), color='g')
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['lane'], unit='', color='g', ls='-')

                        if "video_conf" in Obj.extraData.keys():
                            ylabel_text = "Video Confidence"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'video_conf' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['video_conf']
                            ax = pn.addAxis(ylabel=ylabel_text)
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['video_conf'], unit='%')

                        if "lane_conf" in Obj.extraData.keys():
                            ylabel_text = "Associated Lane Confidence"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'lane_conf' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['lane_conf']
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['lane_conf'], unit='%')

                        if "class_conf" in Obj.extraData.keys():
                            ylabel_text = "Class Confidence"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'class_conf' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['class_conf']
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['class_conf'], unit='%')

                        if "radar_conf" in Obj.extraData.keys():
                            ylabel_text = "Radar Confidence"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'radar_conf' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['radar_conf']
                            ax = pn.addAxis(ylabel=ylabel_text)
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['radar_conf'], unit='%')

                        if "obj_type" in Obj.extraData.keys():
                            ylabel_text = "Object Type"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'obj_type' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['obj_type']
                            if "obj_type_mapping" in Obj.extraData.keys():
                                mapping = extraData["obj_type_mapping"][0]
                            else:
                                mapping = {
                                    0: 'Car', 1: 'Truck', 2: 'Motorcycle', 3: 'Pedestrian', 4: 'Bicycle', 5: 'Unknown',
                                    6: 'point',
                                    7: 'wide'
                                }

                            # mapping = {0: 'Car', 1: 'Truck', 2: 'Motorcycle', 3: 'Pedestrian', 4: 'Bicycle', 5: 'Unknown', 6:'point', 7:'wide'}
                            ax = pn.addAxis(ylabel=ylabel_text, yticks=mapping,
                                            ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['obj_type'], unit='')

                        if "measured_by" in Obj.extraData.keys():
                            ylabel_text = "Measured By"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'measured_by' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['measured_by']
                            mapping = {0: 'None', 1: 'Prediction', 2: 'Radar Only', 3: 'Camera Only', 4: 'Fused'}
                            ax = pn.addAxis(ylabel=ylabel_text, yticks=mapping,
                                            ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['measured_by'], unit='')

                        if "contributing_sensors" in Obj.extraData.keys():
                            ylabel_text = "Contributing Sensors"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'contributing_sensors' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['contributing_sensors']
                            mapping = {0: 'None', 1: 'Radar Only', 2: 'Camera Only', 3: 'Fused'}
                            ax = pn.addTwinAxis(ax, ylabel=ylabel_text, yticks=mapping,
                                                ylim=(min(mapping) - 0.5, max(mapping) + 0.5), color="g")
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['contributing_sensors'], unit='')

                        if "life_time" in Obj.extraData.keys():
                            ylabel_text = "Life Time"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'life_time' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['life_time']
                            ax = pn.addAxis()
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['life_time'], unit='')

                        if "camera_id" in Obj.extraData.keys():
                            ylabel_text = "Camera Id"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'camera_id' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['camera_id']
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['camera_id'], unit='')

                        if "radar_id" in Obj.extraData.keys():
                            ylabel_text = "Radar Id"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'radar_id' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['radar_id']
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['radar_id'], unit='')

                        if "aeb_obj_quality" in Obj.extraData.keys():
                            ylabel_text = "AEB Object Quality"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'aeb_obj_quality' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['aeb_obj_quality']

                            ax = pn.addAxis()
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['aeb_obj_quality'], unit='%')

                        if "acc_obj_quality" in Obj.extraData.keys():
                            ylabel_text = "ACC Object Quality"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'acc_obj_quality' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['acc_obj_quality']
                            ax = pn.addAxis()
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['acc_obj_quality'], unit='%')

                        if "fusion_quality" in Obj.extraData.keys():
                            ylabel_text = "Fusion Quality"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'fusion_quality' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['fusion_quality']
                            ax = pn.addAxis(ylabel=ylabel_text)
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['fusion_quality'], unit='%')

                        if "dz" in Obj.extraData.keys():
                            ylabel_text = "dz"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'dz' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['dz']
                            ax = pn.addAxis()
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['dz'], unit='m')

                        if "dz_std" in Obj.extraData.keys():
                            ylabel_text = "dz_std"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'dz_std' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['dz_std']
                            ax = pn.addAxis()
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['dz_std'], unit='m')

                        if "yaw" in Obj.extraData.keys():
                            ylabel_text = "Yaw"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'yaw' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['yaw']
                            ax = pn.addAxis()
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['yaw'], unit='m/s')

                        if "yaw_std" in Obj.extraData.keys():
                            ylabel_text = "Yaw std"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'yaw_std' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['yaw_std']
                            ax = pn.addAxis()
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['yaw_std'], unit='m/s')

                        if "traffic_sign_id" in Obj.extraData.keys():
                            ylabel_text = "Traffic Sign ID"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'traffic_sign_id' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['traffic_sign_id']
                            ax = pn.addAxis()
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['traffic_sign_id'], unit='m/s')

                        if "universal_id" in Obj.extraData.keys():
                            ylabel_text = "Universal ID"
                            try:
                                if "custom_labels" in Obj.extraData.keys():
                                    if 'universal_id' in extraData["custom_labels"].keys():
                                        ylabel_text = extraData["custom_labels"]['universal_id']
                                ax = pn.addAxis()
                                pn.addSignal2Axis(ax, ylabel_text, time, extraData['universal_id'], unit='m/s')
                            except:
                                pass

                        if "traffic_sign_confidence" in Obj.extraData.keys():
                            ylabel_text = "Traffic Sign Confidence"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'traffic_sign_confidence' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['traffic_sign_confidence']
                            ax = pn.addAxis()
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['traffic_sign_confidence'], unit='m/s')

                        if "traffic_existence_probability" in Obj.extraData.keys():
                            ylabel_text = "Traffic Existence Probability"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'traffic_existence_probability' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['traffic_existence_probability']
                            ax = pn.addAxis()
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['traffic_existence_probability'],
                                              unit='m/s')

                        if "tracking_state" in Obj.extraData.keys():
                            ylabel_text = "Tracking State"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'tracking_state' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['tracking_state']
                            mapping = {
                                0: 'No Track', 1: 'New Track', 2: 'Updated Track', 3: 'Predicted Track', 4: 'Deleted',
                                5: 'Sensor Fault (Unknown)'
                            }
                            ax = pn.addAxis(ylabel=ylabel_text, yticks=mapping,
                                            ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['tracking_state'], unit='')

                        if "cut_in_cut_out" in Obj.extraData.keys():
                            ylabel_text = "Cut In Cut Out"
                            if "custom_labels" in Obj.extraData.keys():
                                if 'cut_in_cut_out' in extraData["custom_labels"].keys():
                                    ylabel_text = extraData["custom_labels"]['cut_in_cut_out']
                            mapping = {
                                0: 'Unknown', 1: 'In Ego Lane', 2: 'In Left Lane', 3: 'Left Cut In', 4: 'Left Cut Out',
                                5: 'In Right Lane', 6: 'Right Cut In', 7: 'Right Cut Out', 8: 'Error'
                            }
                            ax = pn.addAxis(ylabel=ylabel_text, yticks=mapping,
                                            ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
                            pn.addSignal2Axis(ax, ylabel_text, time, extraData['cut_in_cut_out'], unit='')

                pn.start()
                pn.show()
                if self.synchronizer is not None:
                    self.synchronizer.addClient(pn)
                self.InstantNavigators.append(pn)

    def comparePlots(self, selectedObjectsForPlotting):
        if len(selectedObjectsForPlotting) == 0:
            return

        plottingData = {}
        for objKey, objValue in selectedObjectsForPlotting.iteritems():
            for Index, Obj in self.iterActualObjects(self.Objects):
                if Obj == objValue:
                    for i in range(100000):
                        if Index - i <= 0 or Obj.Init[Index - i] or not Obj.Valid[Index - i]:
                            break
                    for j in range(10000):
                        if Index + j >= (len(Obj.Time)) or Obj.Init[Index + j] or not \
                                Obj.Valid[Index + j]:
                            break
                    data = {}
                    data['lateral_distance'] = Obj.X[Index - i:Index + j]
                    data['longitudinal_distance'] = Obj.Y[Index - i:Index + j]
                    # Check is extraData exists
                    extraData = {}
                    if bool(Obj.extraData):
                        for key, value in Obj.extraData.items():
                            if key not in special_object_info:
                                extraData[key] = Obj.extraData[key][Index - i:Index + j]
                            else:
                                extraData[key] = Obj.extraData[key]
                    data['extraData'] = extraData
                    data['time'] = Obj.Time[Index - i:Index + j]
                    plottingData[Obj.Label[Index]] = data

        title = 'Compare object history :'
        for label, data in plottingData.iteritems():
            title = title + label + " vs "
        title = title[:-4]
        pn = datavis.PlotNavigator.cPlotNavigator(title=title)

        ax = pn.addAxis(ylabel='long. dist.')
        for label, data in plottingData.iteritems():
            pn.addSignal2Axis(ax, label + ': dx', data['time'], data['longitudinal_distance'], unit='m')

        ax = pn.addTwinAxis(ax, ylabel='lat. dist.', ylim=(-15, 15), color='g')
        for label, data in plottingData.iteritems():
            pn.addSignal2Axis(ax, label + ': dy', data['time'], data['lateral_distance'], unit='m')

        ax = pn.addAxis(ylabel='Velocity')
        for label, data in plottingData.iteritems():
            extraData = data['extraData']
            if bool(extraData):
                if "vx" in extraData.keys():
                    pn.addSignal2Axis(ax, label + ": Rel Long. Velocity", data['time'], extraData['vx'], unit='m/s')
                if "vy" in extraData.keys():
                    pn.addSignal2Axis(ax, label + ": Rel Lat. Velocity", data['time'], extraData['vy'], unit='m/s')

        ax = pn.addAxis(ylabel='Acceleration')
        for label, data in plottingData.iteritems():
            extraData = data['extraData']
            if bool(extraData):
                if "ax" in extraData.keys():
                    pn.addSignal2Axis(ax, label + ": Rel Long. Acceleration", data['time'], extraData['ax'],
                                      unit='m/s^2')
                if "ay" in extraData.keys():
                    pn.addSignal2Axis(ax, label + ": Rel Lat. Acceleration", data['time'], extraData['ay'],
                                      unit='m/s^2')

        is_available = False
        ylabel_text = "Lane"
        if "custom_labels" in extraData.keys():
            if 'lane' in extraData["custom_labels"].keys():
                ylabel_text = extraData["custom_labels"]['lane']
        for label, data in plottingData.iteritems():
            extraData = data['extraData']
            if bool(extraData):
                if "lane" in extraData.keys():
                    if is_available is False:
                        mapping = {0: 'Ego', 1: 'Left', 2: 'Right', 3: 'Outside Left', 4: 'Outside Right', 5: 'Unknown'}
                        if 'FLC25_CEM_TPF' in extraData['label'][0]:
                            mapping = {0: 'Ego', 1: 'Left', 2: 'Right', 3: 'Outside Left', 4: 'Outside Right',
                                       5: 'Unknown',
                                       6: 'Outside Road Left', 7: 'Outside Road Right'}
                        ax = pn.addAxis(ylabel=ylabel_text, yticks=mapping,
                                        ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
                        is_available = True
                    pn.addSignal2Axis(ax, label + ": " + ylabel_text, data['time'], extraData['lane'], unit='')

        is_available = False
        ylabel_text = "Moving State"
        if "custom_labels" in extraData.keys():
            if 'mov_state' in extraData["custom_labels"].keys():
                ylabel_text = extraData["custom_labels"]['mov_state']
        for label, data in plottingData.iteritems():
            extraData = data['extraData']
            if bool(extraData):
                if "mov_state" in extraData.keys():
                    if 'FLC25_ARS620' not in extraData['label'][0]:
                        if is_available is False:
                            mapping = {
                                0: 'stat', 1: 'stopped', 2: 'moving', 3: 'unknown', 4: 'crossing', 5: 'crossing_left',
                                6: 'crossing_right', 7: 'oncoming'
                            }
                            ax = pn.addAxis(ylabel=ylabel_text, yticks=mapping,
                                            ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
                            is_available = True
                        pn.addSignal2Axis(ax, label + ": " + ylabel_text, data['time'], extraData['mov_state'], unit='')

        for label, data in plottingData.iteritems():
            extraData = data['extraData']
            if bool(extraData):
                if "mov_state" in extraData.keys():
                    if 'FLC25_ARS620' in extraData['label'][0]:
                        mapping = {
                            0: 'unknown', 1: 'moving', 2: 'oncoming', 3: 'stat', 4: 'stopped', 5: 'crossing_left',
                            6: 'crossing_right'
                        }
                        ax = pn.addTwinAxis(ax, ylabel=ylabel_text, yticks=mapping,
                                            ylim=(min(mapping) - 0.5, max(mapping) + 0.5), color='g')
                        pn.addSignal2Axis(ax, label + ": " + ylabel_text, data['time'], extraData['mov_state'], unit='')

        is_available = False
        ylabel_text = "Maintenance State"
        for label, data in plottingData.iteritems():
          extraData = data['extraData']
          if bool(extraData):
            if "maintenance_state" in extraData.keys():
                if is_available is False:
                  mapping = {
                    0: 'empty', 1: 'new', 2: 'measured', 3: 'predicted', 4: 'deleted', 5: 'invalid'
                  }
                  ax = pn.addAxis(ylabel=ylabel_text, yticks=mapping,
                                  ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
                  is_available = True
                pn.addSignal2Axis(ax, label + ": " + ylabel_text, data['time'], extraData['mov_state'], unit='')

        is_available = False
        ylabel_text = "Video Confidence"
        if "custom_labels" in extraData.keys():
            if 'video_conf' in extraData["custom_labels"].keys():
                ylabel_text = extraData["custom_labels"]['video_conf']
        for label, data in plottingData.iteritems():
            extraData = data['extraData']
            if bool(extraData):
                if "video_conf" in extraData.keys():
                    if is_available is False:
                        ax = pn.addAxis(ylabel=ylabel_text)
                        is_available = True
                    pn.addSignal2Axis(ax, label + ": " + ylabel_text, data['time'], extraData['video_conf'], unit='%')

        ylabel_text = "Associated Lane Confidence"
        if "custom_labels" in extraData.keys():
            if 'lane_conf' in extraData["custom_labels"].keys():
                ylabel_text = extraData["custom_labels"]['lane_conf']
        for label, data in plottingData.iteritems():
            extraData = data['extraData']
            if bool(extraData):
                if "lane_conf" in extraData.keys():
                    pn.addSignal2Axis(ax, label + ": " + ylabel_text, data['time'], extraData['lane_conf'], unit='%')

        is_available = False
        ylabel_text = "Radar Confidence"
        if "custom_labels" in extraData.keys():
            if 'radar_conf' in extraData["custom_labels"].keys():
                ylabel_text = extraData["custom_labels"]['radar_conf']
        for label, data in plottingData.iteritems():
            extraData = data['extraData']
            if bool(extraData):
                if "radar_conf" in extraData.keys():
                    if is_available is False:
                        ax = pn.addAxis(ylabel=ylabel_text)
                        is_available = True
                    pn.addSignal2Axis(ax, label + ": " + ylabel_text, data['time'], extraData['radar_conf'], unit='%')

        is_available = False

        ylabel_text = "Object Type"
        if "custom_labels" in extraData.keys():
            if 'obj_type' in extraData["custom_labels"].keys():
                ylabel_text = extraData["custom_labels"]['obj_type']
        for label, data in plottingData.iteritems():
            extraData = data['extraData']
            if bool(extraData):
                if "obj_type_mapping" not in extraData.keys():
                    if "obj_type" in extraData.keys():
                        if is_available is False:
                            mapping = {0: 'Car', 1: 'Truck', 2: 'Motorcycle', 3: 'Pedestrian', 4: 'Bicycle',
                                       5: 'Unknown', 6: 'point', 7: 'wide'}
                            ax = pn.addAxis(ylabel=ylabel_text, yticks=mapping,
                                            ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
                            is_available = True
                        pn.addSignal2Axis(ax, label + ": " + ylabel_text, data['time'], extraData['obj_type'], unit='')
                        self.is_slr = False
                else:
                    if (self.is_slr):
                        ax = pn.addAxis(ylabel=ylabel_text)

        is_available = False
        ylabel_text = "Object Type"
        if "custom_labels" in extraData.keys():
            if 'obj_type' in extraData["custom_labels"].keys():
                ylabel_text = extraData["custom_labels"]['obj_type']
        for label, data in plottingData.iteritems():
            extraData = data['extraData']
            if bool(extraData):
                if "obj_type_mapping" in extraData.keys():
                    if is_available is False:
                        mapping = extraData['obj_type_mapping'][0]
                        ax = pn.addTwinAxis(ax, ylabel=ylabel_text, yticks=mapping,
                                            ylim=(min(mapping) - 0.5, max(mapping) + 0.5),
                                            color="g")
                        is_available = True
                    pn.addSignal2Axis(ax, label + ": " + ylabel_text, data['time'], extraData['obj_type'], unit='')

        is_available = False
        ylabel_text = "Measured By"
        if "custom_labels" in extraData.keys():
            if 'measured_by' in extraData["custom_labels"].keys():
                ylabel_text = extraData["custom_labels"]['measured_by']
        for label, data in plottingData.iteritems():
            extraData = data['extraData']
            if bool(extraData):
                if "measured_by" in extraData.keys():
                    if is_available is False:
                        mapping = {0: 'None', 1: 'Prediction', 2: 'Radar Only', 3: 'Camera Only', 4: 'Fused'}
                        ax = pn.addAxis(ylabel=ylabel_text, yticks=mapping,
                                        ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
                        is_available = True
                    pn.addSignal2Axis(ax, label + ": " + ylabel_text, data['time'], extraData['measured_by'], unit='')

        is_available = False
        ylabel_text = "Contributing Sensors"
        if "custom_labels" in extraData.keys():
            if 'contributing_sensors' in extraData["custom_labels"].keys():
                ylabel_text = extraData["custom_labels"]['contributing_sensors']
        for label, data in plottingData.iteritems():
            extraData = data['extraData']
            if bool(extraData):
                if "contributing_sensors" in extraData.keys():
                    if is_available is False:
                        mapping = {0: 'None', 1: 'Radar Only', 2: 'Camera Only', 3: 'Fused'}
                        ax = pn.addTwinAxis(ax, ylabel=ylabel_text, yticks=mapping,
                                            ylim=(min(mapping) - 0.5, max(mapping) + 0.5), color="g")
                        is_available = True
                    pn.addSignal2Axis(ax, label + ": " + ylabel_text, data['time'], extraData['contributing_sensors'],
                                      unit='')

        pn.start()
        pn.show()
        if self.synchronizer is not None:
            self.synchronizer.addClient(pn)
        self.InstantNavigators.append(pn)

    def showHistorySettings(self):
        '''
        Method for open history settings window at the center of the tracknavigator window.
        '''
        self.HistoryLengthSlider.setValue(self.HistoryLength)
        center = self.frameGeometry().center()
        center.setX(center.x() - self.HistorySettings.rect().width() / 2)
        center.setY(center.y() - self.HistorySettings.rect().height() / 2)
        self.HistorySettings.move(center)
        self.HistorySettings.show()
        pass

    def showRangeSettings(self):
        '''
        Method for open history settings window at the center of the tracknavigator window.
        '''

        self.RangeLengthSlider.setValue(self.LengthMax)
        self.RangeWidthSlider.setValue(self.WidthMax)
        center = self.frameGeometry().center()
        center.setX(center.x() - self.HistorySettings.rect().width() / 2)
        center.setY(center.y() - self.HistorySettings.rect().height() / 2)
        self.RangeSettings.move(center)
        self.RangeSettings.show()
        pass

    def showSignalMapping(self):
        '''
        Method for show signal mapping window at the center of the tracknavigator window.
        '''
        if len(self.SignalMappingInfo) != 0:
            self.SignalMappingComboStatusNames.clear()
            for statusName, signalInfoMapping in self.SignalMappingInfo.items():
                self.SignalMappingComboStatusNames.addItem(statusName)
            center = self.frameGeometry().center()
            center.setX(center.x() - self.HistorySettings.rect().width() / 2)
            center.setY(center.y() - self.HistorySettings.rect().height() / 2)
            self.SignalMapping.move(center)
            self.SignalMapping.show()
        else:
            logging.warning("Signal information mapping is not present for status names")
        pass

    def signalMappingComboStatusNamesSelectionChange(self):
        self.SignalMappingTableWidget.clearContents()
        self.SignalMappingTableWidget.setRowCount(0)
        self.SignalMappingTableWidget.setColumnCount(4)
        self.SignalMappingTableWidget.setHorizontalHeaderLabels(
            ['Name', 'Alias', 'Device Name', 'Signal Name'])
        for statusName, signalInfoMapping in self.SignalMappingInfo.items():
            if statusName == self.SignalMappingComboStatusNames.currentText():
                for signalAlias, signalInfo in signalInfoMapping.items():
                    self.SignalMappingTableWidget.insertRow(self.SignalMappingTableWidget.rowCount())
                    if signalAlias in aliasMapping.keys():
                        self.SignalMappingTableWidget.setItem(self.SignalMappingTableWidget.rowCount() - 1,
                                                              0, QTableWidgetItem(aliasMapping[signalAlias]))
                    else:
                        self.SignalMappingTableWidget.setItem(
                            self.SignalMappingTableWidget.rowCount() - 1,
                            0, QTableWidgetItem(signalAlias))
                    self.SignalMappingTableWidget.setItem(
                        self.SignalMappingTableWidget.rowCount() - 1,
                        1, QTableWidgetItem(signalAlias))
                    self.SignalMappingTableWidget.setItem(
                        self.SignalMappingTableWidget.rowCount() - 1,
                        2, QTableWidgetItem(signalInfo[0]))
                    self.SignalMappingTableWidget.setItem(
                        self.SignalMappingTableWidget.rowCount() - 1,
                        3, QTableWidgetItem(signalInfo[1]))
        self.SignalMappingTableWidget.horizontalHeader().setStretchLastSection(
            True)
        self.SignalMappingTableWidget.resizeColumnsToContents()
        self.SignalMappingTableWidget.scrollToBottom()

    def setHistoryValue(self, value):
        '''
        Method for changing object history length when the slider of history setting window changes.
        '''
        self.HistoryLength = value
        self.HistoryLengthLabel.setText(str(value))
        pass

    def setRangeLengthValue(self, value):
        '''
        Method for changing object history length when the slider of history setting window changes.
        '''
        self.LengthMax = value
        self.SP.set_ylim(self.LengthMin, self.LengthMax)
        self.RangeLengthSliderLabel.setText(str(value))
        pass

    def setRangeLengthValueMin(self, value):
        '''
           Method for changing object history length when the slider of history setting window changes.
           '''
        self.LengthMin = value
        self.SP.set_ylim(self.LengthMin, self.LengthMax)
        self.RangeLengthSliderLabelMin.setText(str(value))
        pass

    def setRangeWidthValue(self, value):
        '''
        Method for changing object history length when the slider of history setting window changes.
        '''
        self.WidthMin = -(value)
        self.WidthMax = value
        self.SP.set_xlim(self.WidthMax, self.WidthMin)
        self.RangeWidthSliderLabel.setText(str(value))
        pass

    def closeHistoryWindow(self):
        '''
        Method for closing history setting window and redraw the figure with the new settings.
        '''
        self.HistorySettings.close()
        self.seekWindow()
        pass

    def closeRangeWindow(self):
        '''
        Method for closing history setting window and redraw the figure with the new settings.
        '''
        self.RangeSettings.close()
        self.seekWindow()
        pass

    def closeSignalMappingWindow(self):
        '''
        Method for closing history setting window and redraw the figure with the new settings.
        '''
        self.SignalMapping.close()
        pass

    def closeEvent(self, event):
        '''
        In case of close event close the HistorySettings window.
        '''
        self.HistorySettings.close()
        self.RangeSettings.close()
        self.SignalMapping.close()
        cNavigator.closeEvent(self, event)

    def prepareCurves(self, curveDict):
        """
        Prepare curves to be shown or hidden. The method assumes that the dictionary in parameter
        has at least 2 values for each key and the first values are ordered.

        :Parameters:
          curveDict : dict
        """
        VisibleCurveTypes = curveDict.keys()
        InvisibleCurveTypes = set(self.Curves.keys()).difference(VisibleCurveTypes)

        for CurveType in InvisibleCurveTypes:
            line = self.Curves[CurveType]
            line.set_visible(False)

        for CurveType in VisibleCurveTypes:
            xData, yData = curveDict[CurveType]
            xData = numpy.array(xData)
            yData = numpy.array(yData)

            line = self.Curves[CurveType]
            line.set_visible(True)
            line.set_xdata(xData)
            line.set_ydata(yData)

        pass

    def resetGroupMenu(self):
        if self.GroupMenu.actions():
            self.GroupMenu.clear()
        GroupNames = self.Toggles.keys()
        GroupNames.sort()
        for GroupName in GroupNames:
            KeyCode = self.getKeyCode(GroupName)
            Visible = self.OrigVisibility[GroupName]
            self.setGroup(GroupName, Visible, KeyCode)
        pass

    def resetTrackMenu(self):
        if self.TrackMenu.actions():
            self.TrackMenu.clear()
        TrackKeys = self.Tracks.keys()
        TrackKeys.sort()
        for TrackKey in TrackKeys:
            self.setTrack(TrackKey)
        pass

    def start(self):
        self.resetGroupMenu()
        self.resetTrackMenu()
        self.seekWindow()
        matplotlib._pylab_helpers.Gcf.set_active(self.figure_manager)
        pass

    def stop_recording(self):
        self.recorder.stop_current_record()
        self.is_recording = False
        return

    def start_recording(self, path=None, filename_extra=''):
        if path is not None:
            self.recorder.set_target_path(path)
        size = self.fig.canvas.get_width_height()
        self.recorder.record_start(size, filename_extra=filename_extra)
        self.is_recording = True
        return

    def clean(self):
        pass


class FrmShowSelectedObjects(QDialog):
    def __init__(self, selectedObjects, otherObjects):
        super(FrmShowSelectedObjects, self).__init__()
        self.setWindowTitle("Select objects for comparison")
        self.setFixedWidth(500)
        self.setFixedHeight(400)
        # self.setWindowFlags(
        #         QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'compare_24.png')))
        self.setModal(False)

        self.selected_items = []
        vbox = QVBoxLayout(self)
        vbox.addWidget(QLabel("Select Objects from nearby vicinity"))

        self.listWidgetselectedObjects = QListWidget()
        self.listWidgetselectedObjects.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidgetselectedObjects.itemSelectionChanged.connect(self.on_change)
        for object_key in sorted(selectedObjects.keys()):
            item_to_add = QListWidgetItem()
            item_to_add.setText(object_key)
            item_to_add.setData(QtCore.Qt.UserRole, selectedObjects[object_key])
            self.listWidgetselectedObjects.addItem(item_to_add)
        vbox.addWidget(self.listWidgetselectedObjects)
        vbox.addWidget(QLabel("                             Or                         "))
        vbox.addWidget(QLabel("Select Objects from out of vicinity"))
        self.listWidgetOtherObjects = QListWidget()
        self.listWidgetOtherObjects.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidgetOtherObjects.itemSelectionChanged.connect(self.on_change)
        for object_key in sorted(otherObjects.keys()):
            item_to_add = QListWidgetItem()
            item_to_add.setText(object_key)
            item_to_add.setData(QtCore.Qt.UserRole, otherObjects[object_key])
            self.listWidgetOtherObjects.addItem(item_to_add)
        vbox.addWidget(self.listWidgetOtherObjects)

        gbox_buttons = QGroupBox('')
        hboxlayout_buttons = QtGui.QHBoxLayout()

        pbutoon_compare = QPushButton("Compare")
        pbutoon_compare.setToolTip('Compare Plots')
        pbutoon_compare.clicked.connect(self.compare_plots)
        hboxlayout_buttons.addWidget(pbutoon_compare, 1, Qt.AlignRight)

        pbutton_close = QPushButton("Close")
        pbutton_close.setToolTip('Close this window')
        pbutton_close.clicked.connect(self.close_clicked)
        hboxlayout_buttons.addWidget(pbutton_close, 0, Qt.AlignRight)
        gbox_buttons.setLayout(hboxlayout_buttons)

        vbox.addWidget(gbox_buttons, 0, Qt.AlignBottom)

        self.setLayout(vbox)
        self.center()

    def on_change(self):
        self.selected_items = {}
        for item in self.listWidgetselectedObjects.selectedItems():
            self.selected_items[item.text()] = item.data(QtCore.Qt.UserRole)

        for item in self.listWidgetOtherObjects.selectedItems():
            self.selected_items[item.text()] = item.data(QtCore.Qt.UserRole)

    def compare_plots(self):
        self.accept()

    def return_selected_objects(self):
        return self.selected_items

    def close_clicked(self):
        self.close()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class FrmResimObjectSelection(QDialog):

    def __init__(self, allObjects, selected_object_list, common_time, file_name, logger, videonav):
        super(FrmResimObjectSelection, self).__init__()
        self.logger = logger
        self.videnav = videonav
        self.ResimObjects = allObjects
        self.selected_object_list = selected_object_list
        self.common_time = common_time
        self.meas_path = file_name

        self.setModal(False)
        self.setWindowTitle("Resimulation Object Export")
        self.center()

        vboxlayout_main = QtGui.QVBoxLayout()
        gbox_horizontal_main = QGroupBox('')
        hboxlayout_main = QtGui.QHBoxLayout()
        hboxlayout_main.setSpacing(0)
        hboxlayout_main.setContentsMargins(1, 1, 1, 1)

        # <editor-fold desc="Select Resim Objects">
        gbox_object_selector = QGroupBox('Select resimulation objects')
        vboxlayout_object_selector = QtGui.QVBoxLayout()
        vboxlayout_object_selector.setSpacing(0)
        vboxlayout_object_selector.setContentsMargins(1, 1, 1, 1)
        self.listWidgetselectedObjects = QListWidget()
        self.listWidgetselectedObjects.setMinimumWidth(self.listWidgetselectedObjects.sizeHintForColumn(0))
        self.listWidgetselectedObjects.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidgetselectedObjects.itemSelectionChanged.connect(self.on_change)

        for object_key in sorted(self.ResimObjects.keys()):
            item_to_add = QListWidgetItem()
            item_to_add.setText(object_key)
            item_to_add.setData(QtCore.Qt.UserRole, self.ResimObjects[object_key])
            self.listWidgetselectedObjects.addItem(item_to_add)
        vboxlayout_object_selector.addWidget(self.listWidgetselectedObjects)

        gbox_object_selector.setLayout(vboxlayout_object_selector)
        hboxlayout_main.addWidget(gbox_object_selector)
        # </editor-fold>

        # <editor-fold desc="Object Operations">
        gbox_object_operation = QGroupBox('Object Operations')
        vboxlayout_object_operations = QtGui.QVBoxLayout()
        vboxlayout_object_operations.setSpacing(0)
        vboxlayout_object_operations.setContentsMargins(1, 1, 1, 1)
        gbox_object_selector.setLayout(vboxlayout_object_operations)
        gridlayout_object_operations = QtGui.QGridLayout()
        gridlayout_object_operations.setContentsMargins(1, 1, 1, 1)
        self.pbutton_add_object = QPushButton("Add")
        self.pbutton_add_object.setToolTip('Add Selected Objects')
        self.pbutton_add_object.clicked.connect(self.add_selected_objects)
        gridlayout_object_operations.addWidget(self.pbutton_add_object, 1, 1)
        self.pbutton_remove_object = QPushButton("Remove")
        self.pbutton_remove_object.setToolTip('Remove Selected Objects')
        self.pbutton_remove_object.clicked.connect(self.remove_selected_objects)
        gridlayout_object_operations.addWidget(self.pbutton_remove_object, 2, 1)
        gbox_object_operation.setLayout(gridlayout_object_operations)
        hboxlayout_main.addWidget(gbox_object_operation)
        # </editor-fold>

        # <editor-fold desc=" Resim Object Export">
        gbox_object_export = QGroupBox('')
        vboxlayout_object_export = QtGui.QVBoxLayout()
        vboxlayout_object_export.setSpacing(0)
        vboxlayout_object_export.setContentsMargins(1, 1, 1, 1)

        self.group_box_resim_details = QGroupBox("Select resimulation time slot")
        self.form_layout_resim_details = QFormLayout()
        self.txt_start_time = QLineEdit()

        self.txt_start_time.setToolTip("Provide resim strat time")
        self.form_layout_resim_details.addRow(QLabel("Start Timestamp:"), self.txt_start_time)
        self.txt_end_time = QLineEdit()

        self.txt_end_time.setToolTip("Provide resim end time")
        self.form_layout_resim_details.addRow(QLabel("End Timestamp:"), self.txt_end_time)
        self.group_box_resim_details.setLayout(self.form_layout_resim_details)
        vboxlayout_object_export.addWidget(self.group_box_resim_details)

        group_box_selectd_object = QGroupBox("Selected resimulation objects")
        vbox = QVBoxLayout()
        self.treeview_selected_objects = QListWidget()
        self.treeview_selected_objects.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        vbox.addWidget(self.treeview_selected_objects)
        group_box_selectd_object.setLayout(vbox)
        vboxlayout_object_export.addWidget(group_box_selectd_object)

        gbox_object_export.setLayout(vboxlayout_object_export)
        hboxlayout_main.addWidget(gbox_object_export)
        # </editor-fold>

        gbox_horizontal_main.setLayout(hboxlayout_main)
        vboxlayout_main.addWidget(gbox_horizontal_main)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Ok).setText("Export Resim Objects")
        self.button_box.button(QDialogButtonBox.Ok).setVisible(True)
        self.button_box.accepted.connect(self.on_accept)
        self.button_box.rejected.connect(self.on_reject)
        vboxlayout_main.addWidget(self.button_box)

        self.setLayout(vboxlayout_main)
        self.update_selected_objects(self.selected_object_list)

    def remove_selected_objects(self):
        for item in self.treeview_selected_objects.selectedItems():
            self.selected_object_list.pop(item.text())
        print(self.selected_object_list)
        self.update_selected_objects(self.selected_object_list)

    def update_selected_objects(self, selected_object_list):
        self.treeview_selected_objects.clear()
        for key, value in selected_object_list.iteritems():
            item_to_add = QListWidgetItem(self.treeview_selected_objects)
            item_to_add.setText(key)
            item_to_add.setData(QtCore.Qt.UserRole, value)
            self.treeview_selected_objects.addItem(item_to_add)
        start_time = 0
        end_time = 0
        for key in selected_object_list.keys():
            start_value, end_value = key.split(" ")[-1].split("-")
            # end_value = key.split(" ")[-1].split("-")[1]
            if start_time == 0:
                start_time = start_value
            if end_time == 0:
                end_time = end_value
            else:
                start_time = min(start_time, start_value)
                end_time = max(end_time, end_value)
        self.txt_start_time.setText(str(start_time))
        self.txt_end_time.setText(str(end_time))

    def add_selected_objects(self):
        if len(self.selected_items) != 0:
            for key, value in self.selected_items.iteritems():
                if not self.selected_object_list.has_key(key):
                    self.selected_object_list[key] = value

        self.update_selected_objects(self.selected_object_list)
        self.treeview_selected_objects.show()

    def on_change(self):
        self.selected_items = {}
        for item in self.listWidgetselectedObjects.selectedItems():
            self.selected_items[item.text()] = item.data(QtCore.Qt.UserRole)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def on_accept(self):
        if self.videnav is not None:
            self.videnav.close()
        selected = {}
        for x in range(self.treeview_selected_objects.count()):
            selected[self.treeview_selected_objects.item(x).text()] = self.treeview_selected_objects.item(x).data(
                QtCore.Qt.UserRole)
        self.get_resim_objects(selected, self.txt_start_time.text(), self.txt_end_time.text())

    def get_resim_objects(self, SelectedObjectBuffers, ResimStartTime, ResimEndtTime):
        preprocess_dspace_resimulation_data(SelectedObjectBuffers, self.common_time, ResimStartTime, ResimEndtTime,
                                            self.meas_path, self.logger)
        return

    def return_selected_objects(self):
        return self.selected_object_list

    def on_reject(self):
        self.close()


Angle = numpy.arange(0.0, 2 * numpy.pi, 1e-2)
AngleCos = numpy.cos(Angle)
AngleSin = numpy.sin(Angle)


def circle(R, Offset, LengthMax=180.0):
    """
    Calculates the X, Y coordinates of a circle where the origin is at
    (-`R`+`Offset`, 0) and the radiues is abs(`R`), `R` can be negative.

    :Parameters:
      R : float
      Offset : float
    :ReturnType: numpy.ndarray, numpy.ndarray
    :Return:
      X coordinates of the circle.
      Y coordinates of the circle.
    """
    if numpy.isinf(R):
        X = numpy.array([Offset, Offset])
        Y = numpy.array([0.0, LengthMax])
    else:
        X = numpy.abs(R) * AngleCos + R + Offset
        Y = numpy.abs(R) * AngleSin
    return X, Y


def fitSize(Time, Param):
    """
    Extend the constans `Param` to fit to `Time` in shape.

    :Parameters:
      Time : numpy.ndarray
      Param : float
    :ReturnType: numpy.ndarray
    :Exeptions:
      ValueError : if `Param` is numpy.ndarray and its size does not fit to `Time`
    """
    if not isinstance(Param, numpy.ndarray):
        Param = numpy.array([Param])
        Param = Param.repeat(Time.size, 0)
    elif Param.shape[0] != Time.shape[0]:
        raise ValueError, 'The size of the Param not fits to the Time'
    else:
        Param = Param.copy()
    return Param


def initColor(Time):
    return fitSize(Time, NO_COLOR)


if __name__ == '__main__':
    import numpy
    import optparse

    app = QtGui.QApplication([])
    parser = optparse.OptionParser()
    parser.add_option('-p', '--hold-navigator',
                      help='Hold the navigator, default is %default',
                      default=False,
                      action='store_true')
    opts, args = parser.parse_args()

    Time = numpy.arange(0.0, 42.0, 0.1)
    x = numpy.arange(50.0, 71.0, 0.05)
    y = numpy.arange(0.0, 21.0, 0.05)
    Coeff = numpy.ones_like(Time)
    R = 150.0 * Coeff
    Offset = 1.5 * Coeff

    Obj = {
        'dx': x,
        'dy': y,
        'label': 'object',
        'type': 0,
        'color': (90, 60, 90),
    }

    TN = cTrackNavigator()
    for Name, Color, r, o in [['curve-left-letf-side', 'r', 1, 1],
                              ['curve-left-right-side', 'b', 1, -1],
                              ['curve-right-left-side', 'g', -1, 1],
                              ['curve-right-right-side', 'y', -1, -1]]:
        Track = TN.addTrack(Name, Time, color=Color)
        FuncName = Track.addFunc(circle, LengthMax=TN.LengthMax)
        Track.addParam(FuncName, 'R', Time, r * R)
        Track.addParam(FuncName, 'Offset', Time, o * Offset)
    TN.setViewAngle(-15.0, 15.0)
    TN.addObject(Time, Obj)
    TN.start()
    TN.resetTrackMenu()
    TN.setWindowGeometry('1500x1800+500+200')
    TN.show()
    if opts.hold_navigator:
        sys.exit(app.exec_())
    TN.close()
    pass
