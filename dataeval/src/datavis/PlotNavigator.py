"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright:
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial
  property. We reserve all rights of disposal such as copying and passing on to
  third parties.
"""
__docformat__ = "restructuredtext en"

import sys
import itertools
import math
from collections import OrderedDict, namedtuple
from numbers import Number
import logging

import matplotlib as mpl
if mpl.rcParams['backend.qt4']!='PySide':
  mpl.use('Qt4Agg')
  mpl.rcParams['backend.qt4']='PySide'
import numpy as np
from mpl_toolkits.axes_grid.parasite_axes import SubplotHost
from PySide import QtCore, QtGui

import figlib
import datavis
from datavis.Synchronizer import cNavigator
from RecordingService import RecordingService
from pyutils.cycle import BiCycle

# Block 'h', 'r'; 'c'; 'L' keys' default functions on graph, as they have different function here
mpl.rc("keymap", home="home", back="left, backspace", xscale="", yscale="")
QT_KEYS_TO_STRING = {
  QtCore.Qt.Key_F1: 'F1',
  QtCore.Qt.Key_Control: 'control',
  QtCore.Qt.Key_Shift: 'shift',
  QtCore.Qt.Key_End: 'end',
  QtCore.Qt.Key_Up: 'up',
  QtCore.Qt.Key_Down: 'down',
  QtCore.Qt.Key_Left: 'left',
  QtCore.Qt.Key_Right: 'right',
  QtCore.Qt.Key_Alt : 'alt',
  QtCore.Qt.Key_Return : 'enter',
  QtCore.Qt.Key_Home : 'home',
  QtCore.Qt.Key_Backspace : 'backspace',
}

SCALE_FACTOR = 0.75

DefaultLimits = namedtuple("DefaultLimits", ("xmin", "xmax", "ymin", "ymax"))

class DragPoint(object):
  def __init__(self, x, y, ax=None):
    self.x = x
    self.y = y
    self.ax = ax
    return

class FigureIndexError(BaseException):
  pass

class cCanvasWithF1Sensing(mpl.backends.backend_qt4agg.FigureCanvasQTAgg):
  keyvald = QT_KEYS_TO_STRING

class FigureManager(mpl.backends.backend_qt4agg.FigureManagerQT):
  _cidgcf = None
  def destroy( self, *args ):
    return

class cPylabNavigator(object):
  def __init__(self, title, figureNr, window_pattern):
    """
    :Parameters:
      title : str
      figureNr : int
        In case of None the last Figure number will be increased.
    """
    figureNr = figlib.det_figure_nr(title, figureNr)
    self.fig = mpl.pyplot.figure(figureNr)
    """:type: `matplotlib.figure.Figure`"""
    if title == 'BSIS/MOIS Evaluation Plot':
      if title:
        self.fig.suptitle(title, fontsize=30)
    else:
      if title:
        self.fig.suptitle(title)
    self.title = title
    """:type: str
    Main title of the plot window"""
    self.window_pattern = window_pattern
    self._windowId = figlib.generateWindowId(title)
    """:type: str
    String to identify the window"""
    self.canvas = cCanvasWithF1Sensing(self.fig)
    self.figure_manager = FigureManager(self.canvas, figureNr)
    self.toolbar = mpl.backends.backend_qt4agg.NavigationToolbar2QT(
                                                       self.canvas, self.canvas)
    return

  def setAxesLimits(self, limits):
    figlib.setAxesLimits(self.fig, limits)
    return

  def copyContentToClipboard(self):
    """Copy current figure to the clipboard as a bitmap image."""
    figlib.copyContentToClipboard(self.fig)
    return

  def copyContentToFile(self, file, format=None):
    """Copy figure to the specified file in the specified format."""
    figlib.copyContentToFile(self.fig, file, format)
    return

  def closePlot(self):
    """Close figure to prevent matplotlib RuntimeError: Could not allocate memory for image"""
    mpl.pyplot.close(self.fig)
    return

class cAxesNavigator(cPylabNavigator):

  MASKED_PRINT_OPTION = np.ma.masked_print_option.display()
  mpl.rcParams['axes.color_cycle'] = ['#0000FF', '#CC2529', '#3E9651', '#535154', '#6B4C9A', '#922428', '#396AB1',
                                      '#DA7C30',
                                      '#948B3D', '#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4',
                                      '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324',
                                      '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080']
  ALL_COLORS = mpl.rcParams['axes.color_cycle']
  ALL_TWINX_COLORS = ('DarkBlue', 'DarkGreen', 'DarkRed', 'DarkCyan',
                      'DarkMagenta', 'Orange', 'DarkGrey')
  ALL_LINE_STYLES = ('-', '--', '-.', ':')
  FONT_SIZES = ('xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large')
  PICK_TOLERANCE = 5
  DEFAULT_MARKER = '.'
  NO_MARKER = ''
  HOST_AX = 'host'
  TWIN_AX = 'twin'
  EXTERN_AX = 'external'
  DEFAULT_X_MIN = 0
  DEFAULT_X_MAX = 1

  def __init__(self, title, figureNr, window_title, subplotGeom=(0,0),
               twinAxAxisOffset=40, fontSize='x-small'):
    """
    :Parameters:
      title : str
      figureNr : int
        In case of None the last Figure number will be increased.
      subplotGeom : tuple
        geometry of subplot axes, two positive integers required if used
    :Exception:
      AssertionError : Invalid subplot geometry is given
    """
    self._numOfAxisRows, self._numOfAxisCols = subplotGeom
    assert    (self._numOfAxisRows == 0 and self._numOfAxisCols == 0)\
           or (self._numOfAxisRows > 0 and self._numOfAxisCols > 0),\
           'invalid axes dimensions: (%d, %d)' %subplotGeom
    assert fontSize in self.FONT_SIZES, 'invalid font size: %s' %fontSize
    cPylabNavigator.__init__(self, title, figureNr, window_title)
    self._isCustomSubplotMode = self._numOfAxisRows != 0 and self._numOfAxisCols != 0
    self.label_multi_col = False
    self.show_legend = True
    self.set_legend_position = False
    self.font=mpl.font_manager.FontProperties('sans-serif', 'normal', 'normal', 'normal', 'normal', fontSize)
    """:type: FontProperties
    Font for the labels"""
    self.font_sizes = BiCycle( self.FONT_SIZES, start=self.FONT_SIZES.index(fontSize) )
    """:type: list
    Named font sizes for the label size change"""
    self.x_min = 0
    """:type: float
    The minimum value of the shared x axis"""
    self.x_max = 0
    """:type: float
    The maximum value of the shared x axis"""
    self.twinAxAxisOffset = twinAxAxisOffset
    """:type: int
    The value of offset for y-axis of twin axes. It is actually the distance in pixels between the y-axis if
    there are more than one twin axes.
    """
    self.axPos = {}
    """:type: dict
    Buffer for storing original (before resize event) position of the axes in relative figure coordinates.
    """
    return

  def centralize(self, x):
    """
    Centralize the zoom around `x` if `x` is out of actual scope.

    :Parameters:
      x : float
    """
    x_min, x_max = self.fig.shared_sp.get_xlim()
    limit = (x_max - x_min) / 10. # 10-10% tail is discarded
    if x < x_min+limit or x > x_max-limit:
      x_diff = (x_max - x_min) * 0.5
      if x <= self.x_min or x >= self.x_max:
        # keep zoom even if `x` is "really" out of scope
        x_min  = x - x_diff
        x_max  = x + x_diff
      else:
        x_min  = max(x - x_diff, self.x_min)
        x_max  = min(x + x_diff, self.x_max)
      self.toolbar.push_current()
      self.fig.shared_sp.set_xlim(x_min, x_max)
    return

  def findLegend(self, ax, event):
    leg = ax.get_legend()
    if leg and leg.get_visible():
      if leg.legendPatch.contains(event)[0]:
        return leg
    raise ValueError

  def findLegendParts(self, leg, event):
    texts = leg.get_texts()
    lines = leg.get_lines()
    for text, line in zip(texts, lines):
      if text.contains(event)[0] or line.contains(event)[0]:
        return (text, line)
    raise ValueError

  def findBar(self, ax, event):
    for bar in ax.bar2text.iterkeys():
      if bar.contains(event)[0]:
        return bar
    raise ValueError

  def findLine(self, ax, text):
    """
    Find and return the corresponding line object for the given text.

    :Parameters:
      ax : `matplotlib.axes.AxesSubplot`
      text : `matplotlib.text.Text`
    :ReturnType: `matplotlib.lines.Line2D`
    """
    label = text.get_text()
    label = label.replace("$\\Delta$","").split('=')[0].strip()
    return ax.label2line[label]

  def _setCommonAxisProp(self, ax, ylim, visibleTimeMarker):
    if ylim:
      ax.set_ylim(ylim)
      ax.fix_y = True
    else:
      ax.fix_y = False

    x_min, x_max = self.fig.shared_sp.get_xlim()
    ax.timemarker = ax.axvline(x=x_min, color='r', visible=visibleTimeMarker)
    ax.timemarker.set_xdata(x_min)

    ax.label2line = OrderedDict()
    ax.bar2text = OrderedDict()
    ax.title2bar = OrderedDict()
    ax.bar_height = 0
    return

  def regAxis(self, hide_legend, ylim, rowNr, colNr, legend_alpha):
    i = len(self.fig.axes) + 1
    j = ((rowNr-1) * self._numOfAxisCols) + colNr
    if i == 1:
      if self._isCustomSubplotMode:
        ax = SubplotHost(self.fig, self._numOfAxisRows, self._numOfAxisCols, j)
      else:
        ax = SubplotHost(self.fig, i, 1, 1)
      self.fig.shared_sp = ax
    else:
      if self._isCustomSubplotMode:
        ax = SubplotHost(self.fig, self._numOfAxisRows, self._numOfAxisCols, j, sharex=self.fig.shared_sp)
      else:
        ax = SubplotHost(self.fig, i, 1, 1, sharex=self.fig.shared_sp)
    self.fig.add_subplot(ax)
    # set the limits of x-axes so that they don't start with negative numbers
    # (it is needed in the case of Matplotlib 1.2 but the error could arise with earlier versions too)
    self.fig.shared_sp.set_xlim(self.DEFAULT_X_MIN, self.DEFAULT_X_MAX)

    x_min, x_max = self.fig.shared_sp.get_xlim()
    axvspan = ax.axvspan(x_min, x_min, facecolor='g', alpha=0.3)
    ax.axvspans = {self:axvspan}

    self._setCommonAxisProp(ax, ylim, True)

    ax.hide_legend = hide_legend
    ax.legend_alpha = legend_alpha
    ax.all_report_colors = itertools.cycle(self.ALL_COLORS)
    return ax

  def regYticks(self, ax, yticks):
    if yticks:
      ax.yticks = dict( (k,str(v)) for k,v in yticks.iteritems() )
      validticks = dict( (k,v) for k,v in ax.yticks.iteritems() if isinstance(k, Number) )
      ax.set_yticks( validticks.keys() )
      ax.set_yticklabels( validticks.values() )
    else:
      ax.yticks = None
    return

  def addReport(self, ax, report, color=None):
    if color is None:
      color = ax.all_report_colors.next()

    limit = 0.5

    time = report.IntervalList.Time

    x_min, x_max = time.min(), time.max()
    ratio = (x_max - x_min) / len(report.IntervalList)

    groups = report.IntervalList.group(Margin=ratio)
    max_group_len = 0
    for group in groups:
      group_len = len(group)
      max_group_len = max(max_group_len, group_len)

    for intervals in groups:
      for i, interval in enumerate(intervals):
        i += ax.bar_height
        comment = report.getComment(interval)
        lower, upper = interval
        circle = upper - lower == 1
        lower = time[lower]
        upper = time[upper-1]
        diff  = abs(upper-lower)
        if circle:
          patch = mpl.patches.Ellipse((lower+limit, i+limit), 2*limit*ratio, 2*limit, color=color, edgecolor=color)
          bar = ax.add_patch(patch)
        else:
          bar, = ax.bar(lower, 0.9, diff, i, color=color, edgecolor=color)
        text = ax.text(lower, i, comment, bbox=dict(facecolor='LightYellow', pad=20))
        text.set_visible(False)
        ax.bar2text[bar] = text

    if max_group_len:
      title = report.getTitle()
      ax.title2bar[title] = bar

    ax.autoscale()
    ax.bar_height += max_group_len
    return

  def addReports(self, ax, reports):
    for report in reports:
      self.addReport(ax, report)
    return

  def setXlim(self, ax, x_min, x_max):
    if len(ax.lines) > 1:
      shared_x_min,\
      shared_x_max = ax.get_xlim()
      shared_x_min = min(shared_x_min, x_min)
      shared_x_max = max(shared_x_max, x_max)
      x_lim = shared_x_min, shared_x_max
    else:
      x_lim = x_min, x_max
    ax.set_xlim(x_lim)
    # TODO addXTick delete the original ticks
    # self.addXTick(ax, 'min', x_min, 'horizontal')
    # self.addXTick(ax, 'max', x_max, 'horizontal')
    return

  def addXTick(self, ax, name, value, rotation=None):
    labels = [label.get_text() for label in ax.get_xticklabels()]
    labels.append(name)

    values = ax.get_xticks()
    values = values.tolist()
    values.append(value)
    ax.set_xticks(values)
    ax.set_xticklabels(labels)

    if rotation is not None:
      for label in ax.get_xticklabels():
        if label.get_text() == name:
          label.set_rotation(rotation)
    return

  def resizeAxes(self, ax, resizeEvent=None):
    if len(ax.parasites) <= 1:
      return
    yaxisOffsets = []
    for parAx in ax.parasites:
      yaxisOffsets.append(parAx.axis["right"].offset_transform.get_matrix()[0][-1])
    yaxisOffset = max(yaxisOffsets) / self._numOfAxisCols if self._numOfAxisCols != 0 else max(yaxisOffsets)
    if resizeEvent is None:
      (ax_X0, ax_Y0), (ax_X1, ax_Y1) = ax.get_position().get_points()
      self.axPos[ax] = (ax_X0, ax_Y0, ax_X1, ax_Y1)
    else:
      ax_X0, ax_Y0, ax_X1, ax_Y1 = self.axPos[ax]
    yaxisOffsetT = self.fig.transFigure.inverted().transform((yaxisOffset, 0))[0]
    axT_X1 = ax_X1 - yaxisOffsetT
    width = axT_X1 - ax_X0
    height = ax_Y1 - ax_Y0
    ax.set_position([ax_X0, ax_Y0, width, height])
    return

  def start(self):
    """
    Plots the signals and starts the event loop.

    :Return: None
    """
    assert self.fig.axes, 'No axis registered to navigator %s with title: %s' %(self, self.title)
    x_min, x_max = None, None
    subnr = len(self.fig.axes)
    i = 1
    for ax in self.fig.axes:
      if not self._isCustomSubplotMode:
        ax.change_geometry(subnr, 1, i)
      self.resizeAxes(ax)
      for parAx in ax.parasites:
        ax.label2line.update(parAx.label2line)
        for parLine in parAx.lines:
          if isinstance(parLine.get_xdata(), np.ndarray):
            ax.add_line(parLine)
        if not parAx.fix_y:
          y_min, y_max = parAx.get_ylim()
          y_lim = stretch(0.05, y_min, y_max)
          parAx.set_ylim(y_lim)
      self.setLegend(ax)
      if ax.hide_legend:
        ax.get_legend().set_visible(False)
      else:
        self.setValueForLegend(ax, self.time)
      if not ax.fix_y:
        y_min, y_max = ax.get_ylim()
        y_lim = stretch(0.05, y_min, y_max)
        ax.set_ylim(y_lim)
      # Calculate limits of x axes - only data lines are considered
      for line in ax.lines:
        lineXData = line.get_xdata()
        # axvlines and axhlines are excluded from calculation as they return list
        if isinstance(lineXData, np.ndarray) and lineXData.size > 0:
          line_x_min = lineXData.min()
          line_x_max = lineXData.max()
          x_min = line_x_min if x_min is None else min(line_x_min, x_min)
          x_max = line_x_max if x_max is None else max(line_x_max, x_max)
      i += 1
    # set x limits to default if they're still None
    def_x_min, def_x_max = self.fig.shared_sp.get_xlim()
    x_min = def_x_min if x_min is None else x_min
    x_max = def_x_max if x_max is None else x_max
    # update figure x limits
    self.fig.shared_sp.set_xlim(x_min, x_max)
    # set axis time markers
    for ax in self.fig.axes:
      ax.timemarker.set_xdata(x_min)
    self.x_min = x_min
    self.x_max = x_max
    mpl._pylab_helpers.Gcf.set_active(self.figure_manager)
    return

  def setLegend(self, ax, *args):
    labels = ax.label2line.keys()
    lines = [ax.label2line[label] for label in labels]
    titles = ax.title2bar.keys()
    for title in titles:
      bar = ax.title2bar[title]
      lines.append(bar)
      labels.append(title)
    if self.label_multi_col:
      ncol = len(ax.lines) / 5 + 1
    else:
      ncol = 1
    if bool(args):
      if args[0] == 'RSP':
        leg = ax.legend(lines, labels, prop=self.font, ncol=ncol, bbox_to_anchor=(1.35, 1.00))
        self.set_legend_position = True
    else:
      if self.set_legend_position:
        leg = ax.legend(lines, labels, prop=self.font, ncol=ncol, bbox_to_anchor=(1.35, 1.00))
      else:
        leg = ax.legend(lines, labels, prop=self.font, ncol=ncol)
    leg.draggable(True)
    leg.get_frame().set_alpha(ax.legend_alpha)
    return

  def setValueForLegend(self, ax, x):
    raise NotImplementedError()


class cPlotNavigator(cAxesNavigator, cNavigator):  # order important for several inherited functions
  """Plots several signals with synchronizable time marker. Create an instance,
  add plots and pass it to a Synchronizer."""
  changeNumberSystem = True
  def __init__(self, title='', figureNr=None, subplotGeom=(0,0), yAutoZoom=False,
               fontSize='x-small'):
    """
    Constructor of the class.

    :Parameters:
      title : str
        Main title of the plot window. If the default value is left, then no
        title will be added.
      figureNr : int
        Identification number of the instance pylab figure. If the default value
        is left, then the `LastFigureNr`+1 will be its value. Default is None.
      subplotGeom : tuple
        Geometry of subplot axes, two positive integers required if used.
      yAutoZoom : bool
        Toggle automatic rescaling of vertical data axis on seek events.
      fontSize : str
        Legend font size. Default is "x-small".
    :Exception:
      AssertionError : Invalid subplot geometry is given
    """
    cNavigator.__init__(self)
    cAxesNavigator.__init__(self, title, figureNr, 'PN %d %s',
                            subplotGeom=subplotGeom, fontSize=fontSize)

    self.x = 0
    """:type: int
    Pixel position of the last mouse press in x direction."""
    self.y = 0
    """:type: int
    Pixel position of the last mouse press in y direction."""
    self.xdata = 0.0
    """:type: float
    Value of the last mouse press in x direction."""
    self.ydata = 0.0
    """:type: float
    Value of the last mouse press in y direction."""
    self.xSelectLimit = 1
    """:type: int
    Pixel difference between mouse click and mouse drag event."""
    self.ySelectLimit = 1
    """:type: int
    Pixel difference between mouse click and mouse drag event."""
    self.formats = {np.dtype('bool')    : '%d',
                    np.dtype('uint8')   : '%d',
                    np.dtype('uint16')  : '%d',
                    np.dtype('uint32')  : '%d',
                    np.dtype('uint64')  : '%d',
                    np.dtype('int8')    : '%d',
                    np.dtype('int16')   : '%d',
                    np.dtype('int32')   : '%d',
                    np.dtype('int64')   : '%d',
                    np.dtype('float32') : '%.3f',
                    np.dtype('float64') : '%.3f',
                    }
    """:type: dict
    Suggested formats for each signal."""
    self.help_font=mpl.font_manager.FontProperties('monospace', 'normal', 'normal', 'normal', 'normal', 'small')
    """:type: FontProperties
    Font for the help"""
    self.help = self.fig.text(0.1,0.5,
    'Keyboard shortcuts:\n\n'
    'F1                  Show/hide this help screen\n'
    'F10                 Save current time to clipboard and also show it in log window\n'
    'Home                Back to original data view\n'
    'Backspace/LeftArrow Navigate back in historical data view\n'
    'v/RightArrow        Navigate forward in historical data view\n'
    'p                   Toggle pan-zoom mode\n'
    'o                   Toggle rectangle-zoom mode\n'
    'z                   Autoscale each y axis\n'
    'g                   Toggle grid on the selected axis\n'
    'k                   Toggle x axis scale (log/linear) on each axis\n'
    'l                   Toggle y axis scale (log/linear) on the selected axis\n'
    'Space               Start/stop playback*\n'
    'h                   Show/hide legend(s)\n'
    'r                   Reset legend position(s)\n'
    'm                   Toggle multi-column legend(s)\n'
    'n                   Toggle number system of values in legends between DEC and HEX \n'
    '<, >                Zoom/unzoom label fonts\n'
    'c                   Show/hide intervals\n'
    's                   Save the current figure into file\n'
    'q                   Copy the current figure to the clipboard\n'
    'i                   Display interpolated values in legend(s)\n'
    'd                   Toggle Delta mode for timestamp and values in legend\n'
    't                   Toggle markers between On, Off and Custom\n'
    'a                   Synchronize the domain of other PlotNavigator clients with this one\n\n'    
    'Mouse interactions:\n\n'
    'Left click on plot                   Seek to cursor position**\n'
    'Hold mouse over axis                 Select the axis\n'
    'Ctrl + left click on signal          Toggle data marker\n'
    'Ctrl + right click on signal         Toggle data line style thin/thick/invisible\n'
    'Left click on signal in legend       Toggle data marker\n'
    'Right click on signal in legend      Toggle data line style thin/thick/invisible\n'
    'Drag and drop legend                 Move legend**\n'
    'Hold x while panning/zooming         Constrain pan/zoom to x axis\n'
    'Hold y while panning/zooming         Constrain pan/zoom to y axis\n'
    'Shift + interval selection on plot   Define a new interval**\n\n'
    '* Works only when VideoNavigator is synchronized with this client\n'
    '** Works only when pan/zoom mode is inactive\n'
    , visible=False, fontproperties=self.help_font, bbox=dict(facecolor='LightYellow', pad=20))
    """:type: Text
    Online help text"""
    self.interpolate = False
    self.control_is_pressed = False
    self.shift_is_pressed = False
    """:type: bool
    Toggle switch to interpoalte between the datapoint for legend display or not"""
    self.timeText = self.fig.text(0.025,0.025,"")
    self.yAutoZoom = yAutoZoom
    """:type: bool
    Toggle if rescaling of vertical data axis is intended during seek or not."""
    self.selected_axes = None
    """:type: bool
    Toggle delta mode for legends."""
    self.show_legend_delta = False
    self.xKeyPressed = False
    """:type: bool
    Bool to toggle between zoom only along X-axis or not
    """
    self.yKeyPressed = False
    """:type: bool
        Bool to toggle between zoom only along Y-axis or not
    """
    self.dragPoint = None
    self.defaultLimits = []

    self.is_recording = False
    self.recorder = RecordingService('PlotRecord')
    self.toggled_plots = {}
    """:type: Dict
    Toggled markers for each line/plot"""
    self.toggle_state = 0

    self.canvas.mpl_connect('button_press_event', self.onFigureClickPress)
    self.canvas.mpl_connect('button_release_event', self.onFigureClickRelease)
    self.canvas.mpl_connect('pick_event', self.onPick)
    self.canvas.mpl_connect('key_press_event', self.onFigureKeyPress)
    self.canvas.mpl_connect('key_release_event', self.onFigureKeyRelease)
    self.fig.canvas.mpl_connect('motion_notify_event', self.onMotion)
    self.fig.canvas.mpl_connect('scroll_event', self.onFigureScroll)

    # override the home button of the toolbar
    self.toolbar.home = self.home

    self.setCentralWidget(self.canvas)
    self.addToolBar(QtCore.Qt.BottomToolBarArea, self.toolbar)
    return

  def home(self):
    axes = self.fig.axes
    for i, limits in enumerate(self.defaultLimits):
      axes[i].set_ylim(limits.ymin, limits.ymax)
    self.fig.shared_sp.set_xlim(limits.xmin, limits.xmax)
    self.canvas.draw()
    return

  def setAxesLimits(self, limits):
    figlib.setAxesLimits(self.fig, limits, yAutoZoom=self.yAutoZoom)
    return

  def resizeHelp(self):
    if self.help.get_visible():
      bx = self.help.get_window_extent()
      bx = bx.inverse_transformed(self.fig.transFigure)
      self.help.set_position(((1-bx.width)/2.,(1-bx.height)/2.))
    return

  def changeFloatDigits(self, digits):
    """
    :Parameters:
      digits : int
    """
    self.formats[np.dtype('float32')] = '%.' + str(digits) + 'f'
    self.formats[np.dtype('float64')] = '%.' + str(digits) + 'f'
    return

  def setXlim(self, x_min, x_max):
    """
    Sets the limit on the horizontal axes.

    :Parameters:
      x_min : float
        Lower limit
      x_max : float
        Upper limit

    :Return: None
    """
    self.x_min = x_min
    self.x_max = x_max
    return

  def set_xlim_online(self, x_min, x_max):
    """
    :Parameters:
      x_min : float
        Lower limit
      x_max : float
        Upper limit
    """
    self.toolbar.push_current()
    self.fig.shared_sp.set_xlim(x_min, x_max)
    self.canvas.draw()
    return

  def addsignal(self, name, signal, *args, **kwargs):
    """
    Add a single signal to plots.

    :Parameters:
      name : str
        Name to display on plots. If empty string is added, then no legend will
        be shown.
      signal : two element list of ndarrays
        The signal values in [time, value] orded.
      args : arbitrary arguments
        Repeated (`name`, `signal`, ...) list.
    :Keywords:
      xlabel : str
        Label of the x axis.
      ylabel : str
        Label of the y axis.
      grid : bool
        Enable flag of grid. Default is True.
      offset : list
        This offsets will be added to the values of `signal`s. Length of `offset`
        must be the same like number of the added `signal`s.
      factor : list
        The values of `signal`s will be multiped with this factors. Length of
        `factor` must be the same like number of the added `signal`s.
      threshold : float or list
        A horizontal line will be plotted on `threshold` beside the `signal`s.
        If threshold is a list then the following form have to be followed:
        [Threshold<int>, Color<str>,...]
      yticks : dict
        Dictionary to set the tick values labels of the y axis. Where the keys
        of the `yticks` are the values of the tick and the values of the
        `yticks` are the labels of the tick.
      ylim : len(2) sequence of floats
        Set the data limits for the yaxis
      color : str or list
        Plotting format for the signals. List can be added for multiple signals.
        If more signal is added than plotting fomat then blue will be used for
        the rests.
      linewidth : int or list
        Width of the plotted line.
      displayscaled : bool or list
        Display the scaled value for the legend or the initial raw value.
    :Return: None
    """
    grid        = True  if 'grid'        not in kwargs else kwargs['grid']
    hide_legend = False if 'hide_legend' not in kwargs else kwargs['legend']
    ylim        = None  if 'ylim'        not in kwargs else kwargs['ylim']
    yticks      = None  if 'yticks'      not in kwargs else kwargs['yticks']
    ylabel      = None  if 'ylabel'      not in kwargs else kwargs['ylabel']
    xlabel      = None  if 'xlabel'      not in kwargs else kwargs['xlabel']

    ax = self.addAxis(grid, hide_legend, ylim, yticks, ylabel, xlabel)

    labels = [name]
    signals = [signal]
    for i in xrange(len(args) / 2):
      labels.append(args[i*2])
      signals.append(args[i*2+1])

    fitlen = len(labels)
    fitKWArgsLen(fitlen, kwargs, 'offset',        None)
    fitKWArgsLen(fitlen, kwargs, 'factor',        None)
    fitKWArgsLen(fitlen, kwargs, 'color',         '-')
    fitKWArgsLen(fitlen, kwargs, 'linewidth',     1)
    fitKWArgsLen(fitlen, kwargs, 'displayscaled', True)

    for time_value, label, factor, offset, color, linewidth, displayscaled in zip(signals, labels, kwargs['factor'], kwargs['offset'], kwargs['color'], kwargs['linewidth'], kwargs['displayscaled']):
      time, value = time_value
      if '[' in label and ']' in label:
        start = label.rfind('[')
        end   = label.rfind(']')
        unit = label[start+1:end]
        unit = unit.strip()
        label = label[:start]
        label = label.strip()
      else:
        unit = ''
      new_kwargs = dict(offset=offset, factor=factor, displayscaled=displayscaled,
                        unit=unit, linewidth=linewidth)
      if color != '-':
        # add color only if it is recognized by matplotlib
        new_kwargs['color'] = color
      self.addSignal2Axis(ax, label, time, value, **new_kwargs)

    if 'threshold' in kwargs:
      thresholds = kwargs['threshold']
      if isinstance(thresholds, list):
        for ii in xrange(len(thresholds)/2):
          threshold = thresholds[2*ii]
          color     = thresholds[2*ii+1]
          self.addThreshold2Axis(ax, 'threshold%d' %ii, threshold, color, '')
      else:
        self.addThreshold2Axis(ax, 'threshold', thresholds, 'r', '')
    return

  def addAxis(self, grid=True, hide_legend=False, legend_alpha=.5, ylim=None,
              yticks=None, ylabel=None, xlabel=None, rowNr=0, colNr=0):
    """
    Add and register the axis to the figure

    :Parameters:
      grid : bool
        Enable or disable the grid.
      hide_legend : bool
        Enable or disable to show the legend.
      legend_alpha : float
        Set alpha (transparency) level of legend background, in 0..1
        (transparent..opaque) range. Default is 0.5 (semi-transparent).
      ylim : len(2) sequence of floats
        Set the data limits for the yaxis.
      yticks : dict
        Dictionary to set the tick values labels of the y axis. Where the keys
        of the `yticks` are the values of the tick and the values of the
        `yticks` are the labels of the tick.
      ylabel : str
        Label of the y axis.
      xlabel : str
        Label of the x axis.
      rowNr : int
        Row index of the axis, used only in custom subplot mode.
      colNr : int
        Column index of the axis, used only in custom subplot mode.
    :Exception:
      FigureIndexError : Index of the axis is out of range.
    """
    if (     self._isCustomSubplotMode
         and (    rowNr not in range(1,self._numOfAxisRows+1)
               or colNr not in range(1,self._numOfAxisCols+1) )):
      raise FigureIndexError("Axis index (%d,%d) out of range (%d,%d)!"
              %(rowNr, colNr, self._numOfAxisRows, self._numOfAxisCols))
    ax = self.regAxis(hide_legend, ylim, rowNr, colNr, legend_alpha)
    self.regYticks(ax, yticks)
    if xlabel:
      ax.set_xlabel(xlabel)
    if ylabel:
      ax.set_ylabel(ylabel)
    ax.grid(grid)
    return ax

  def addTwinAxis(self, ax, color=None, ylim=None, yticks=None, ylabel=None):
    """
    Add twin axis to an already existing host axis.

    :Parameters:
      ax: `matplotlib.axes.AxesSubplot`
        The host axis to which the twin axis would be joined.
      color: str
        Set the color for the twin axis. The color of the lines will be the same.
      ylim : len(2) sequence of floats
        Set the data limits for the y axis.
      yticks : dict
        Dictionary to set custom tick labels for the y axis. The keys
        of the `yticks` are the values of the tick and the values of the
        `yticks` are the labels of the tick.
      ylabel : str
        Label of the y axis.
    :Exception:
      AssertionError : if `ax` does not belong to this instance
    :ReturnType: `mpl_toolkits.axes_grid1.parasite_axes.AxesParasite`
    :Return: The new twin axis.
    """
    ax_type = self._getAxisType(ax)
    assert ax_type == self.HOST_AX or ax_type == self.TWIN_AX,\
           'Axis does not belong to this instance!'
    if ax_type == self.TWIN_AX:
      ax = self._findHostAxis(ax)
      self.logger.warning("Attempting to assign twin axis to another twin axis!")
    if not ax.parasites:
      # define twin colors of host axis if it has no twin yet
      ax.all_twin_colors = itertools.cycle(self.ALL_TWINX_COLORS)

    offset = self.twinAxAxisOffset * len(ax.parasites)

    axTwin = ax.twinx()

    axTwin.all_linestyles = itertools.cycle(self.ALL_LINE_STYLES)

    if not color:
      color = ax.all_twin_colors.next()
    axTwin.twin_color = color

    axTwin.axis["right"] = axTwin.new_fixed_axis(loc="right", offset=(offset, 0))
    axTwin.axis["right"].toggle(all=True)

    axTwin.axis["right"].label.set_color(axTwin.twin_color)
    axTwin.axis["right"].line.set_color(axTwin.twin_color)
    axTwin.axis["right"].major_ticks.set_color(axTwin.twin_color)
    axTwin.axis["right"].minor_ticks.set_color(axTwin.twin_color)
    axTwin.axis["right"].major_ticklabels.set_color(axTwin.twin_color)
    axTwin.axis["right"].minor_ticklabels.set_color(axTwin.twin_color)

    self.regYticks(axTwin, yticks)

    if ylabel:
      axTwin.set_ylabel(ylabel)

    self._setCommonAxisProp(axTwin, ylim, False)

    return axTwin

  def addSignal2Axis(self, ax, label, time, value, offset=None, factor=None,
                     displayscaled=True, unit=None, **kwargs):
    """
    Add signal to the given axis.

    :Parameters:
      ax: `matplotlib.axes.AxesSubplot`
        The axis where the signal is to be added
      label: str
        Signal label to be displayed in legend
      time : `numpy.ndarray`
        Domain array
      value : `numpy.ndarray`
        Value array
      offset : int or float, optional
        Offset to be added to value array
      factor : int or float, optional
        Factor for multiplying value array
      displayscaled : bool, optional
        Display the scaled (offset/factor affected) value in legend. Default is
        True. If False is given, the original value is displayed in legend
        (while the scaled value is plotted on the axis).
      unit : str, optional
        Physical unit of the signal (displayed in legend)
    :Keywords:
      Line properties accepted by `matplotlib.axes.Axes.plot` method (except
      the `label` property, which is a required argument).
    :Exceptions:
      AssertionError : if `ax` does not belong to this instance, or `label` is
        already registered to `ax`
      Exceptions raised by `matplotlib.axes.Axes.plot` method.
    """
    ax_type = self._getAxisType(ax)
    assert ax_type == self.HOST_AX or ax_type == self.TWIN_AX,\
           'Axis does not belong to this instance!'
    assert label not in ax.label2line, 'Label "%s" already in use!' %label
    raw_value = value
    if factor is not None:
      value = value * factor
    if offset is not None:
      value = value + offset
    # set picker tolerance to activate pick event
    kwargs.setdefault('picker', self.PICK_TOLERANCE)
    # plot line
    line, = ax.plot(time, value, drawstyle='steps-post',label=label, **kwargs)
    # if ax is a twinaxis, set default line properties
    if ax_type == self.TWIN_AX:
      self._setTwinAxisLineProps(ax, line, **kwargs)
    # remember default line properties
    marker = line.get_marker()
    is_marker_set = 'marker' in kwargs
    def_marker = marker if is_marker_set else self.DEFAULT_MARKER
    line.marker_states = itertools.cycle( [def_marker, self.NO_MARKER] )
    if is_marker_set:
      line.marker_states.next() # adjust marker state
    def_lw = line.get_linewidth()
    if def_lw > 0:
      line.linewidth_states = itertools.cycle( [2*def_lw, 0, def_lw] )
    else:
      line.linewidth_states = itertools.cycle( [1, 2, 0] )
    # register line supplementary attributes
    try:
      if np.issubdtype(raw_value.dtype, np.float):
        line_format = self._get_format(np.ptp(value))
      else:
        line_format = self.formats[raw_value.dtype]
    except KeyError, error:
      line_format = '%d'
      self.logger.warning("%s (%s) signal's legend string formatting"\
                          " is set to default (decimal)" %(label,error.message))
    except ValueError:
      line_format = '%d'
      self.logger.debug("'%s' signal has no valid entries at all; "\
                        "default format will be used instead." %label)
    unit = '[%s]' %unit if unit else ''
    line.value = value if displayscaled else raw_value
    line.format = line_format
    line.unit = unit
    ax.label2line[label] = line
    return

  def _findHostAxis(self, ax):
    for hostAx in self.fig.axes:
      if ax in hostAx.parasites:
        return hostAx
    raise ValueError

  def _getAxisType(self, ax):
    ax_type = self.EXTERN_AX
    if ax in self.fig.axes:
      ax_type = self.HOST_AX
    else:
      try:
        self._findHostAxis(ax)
      except ValueError:
        pass
      else:
        ax_type = self.TWIN_AX
    return ax_type

  def _setTwinAxisLineProps(self, ax, line, **kwargs):
    if 'color' not in kwargs:
      line.set_color(ax.twin_color)
    if 'linestyle' not in kwargs and 'ls' not in kwargs:
      line.set_linestyle( ax.all_linestyles.next() )
    return

  def addThreshold2Axis(self, ax, label, value, color='r', unit=''):
    if isinstance(value, int):
      format = self.formats[np.dtype('int32')]
    else:
      format = self.formats[np.dtype('float32')]
    value_str = format % value
    label_list = [label, '=', value_str]
    if unit != '':
      unit = '[%s]' %unit
      label_list.append(unit)
    label = ' '.join(label_list)

    ax.axhline(value, color=color, label=label)
    return

  def onFigureResize(self, event):
    """
    Event handler for figure resize event. Figure is adjusted automatically,
    but figure's help text needs to be resized if displayed at the time of event.

    :Parameters:
      event : matplotlib.backend_bases.ResizeEvent
    :Return: None
    """
    self.resizeHelp()
    for ax in self.fig.axes:
      self.resizeAxes(ax, resizeEvent=event)
    self.canvas.draw()
    return

  def resizeEvent(self, event):
    if not self.defaultLimits:
      for ax in self.fig.axes:
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        self.defaultLimits.append(DefaultLimits(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax))

    cNavigator.resizeEvent(self, event)
    new_size = event.size()
    canvas_width = new_size.width()
    # Extra minimum padding to offset QtAgg's clipping
    canvas_height = new_size.height() - (self.toolbar.height() * 1.01)
    self.canvas.resizeEvent(event)
    self.canvas.resize(canvas_width, canvas_height)
    self.onFigureResize(event)
    return

  def onFigureClickPress(self, event):
    """
    Event handler for mouse click press event.
    Stores the event's position, both the canvas (pixel) and data coordinates.

    :Parameters:
      event : matplotlib.backend_bases.MouseEvent
    :Return: None
    """
    if event.button == 2 and event.inaxes in self.fig.axes:
      self.dragPoint = DragPoint(event.xdata, event.ydata, ax=event.inaxes)
      return

    if not self.control_is_pressed:
      self.x     = event.x
      self.xdata = event.xdata
      self.y     = event.y
      self.ydata = event.ydata
    return

  def onFigureClickRelease(self, event):
    """
    Event handler for mouse click press event.
    Single mouse click: call `seekCallback` and repositioning `timemarker` of
    the `fig.axes`.
    Area selection: call `setROI` and `setROICallback`.

    :Parameters:
      event : matplotlib.backend_bases.MouseEvent
    :Return: None
    """
    if self.dragPoint and event.button == 2:
      self.dragPoint = None
      return

    ax = event.inaxes
    if ax in self.fig.axes and not self.control_is_pressed:
      try:
        leg = self.findLegend(ax, event)
      except ValueError:
        if self.toolbar.mode not in ['zoom rect', 'pan/zoom']:
          try:
            bar = self.findBar(ax, event)
          except ValueError:  # click on the plot itself
            if event.button == 1 and not self.control_is_pressed:
              if abs(event.x - self.x) < self.xSelectLimit:
                self.onSeek(event.xdata)
              else:
                if self.shift_is_pressed:
                  if self.setROISignal is not None:
                    bounds = [self.xdata, event.xdata]
                    bounds.sort()
                    start, end = bounds
                    self.onSetROI(start, end, 'g')
          else:
            if event.button == 1:
              text = ax.bar2text[bar]
              vis = text.get_visible()
              vis = not vis
              text.set_visible(vis)
              self.canvas.draw()
      else:  # click on the legend
        try:
          textOnLegend, lineOnLegend = self.findLegendParts(leg, event)
          line = self.findLine(ax, textOnLegend)
        except (ValueError, KeyError):  # click on empty area
          pass
        else:  # click on a signal (line or its label)
          if abs(event.x - self.x) < self.xSelectLimit and abs(event.y - self.y) < self.ySelectLimit:  # legend not moved
            if event.button == 1:
              if self.toggle_state == 0:
                self.switchMarker(line, lineOnLegend)
              else:
                self.toolbar.set_message("Set markers manually ONLY in CUSTOM mode")
            elif event.button == 3:
              self.switchLineWidth(line, lineOnLegend)
            self.canvas.draw()
    return

  def onFigureScroll(self, event):
    ax = event.inaxes
    if ax in self.fig.axes:
      if event.button == 'up':
        scale_factor = SCALE_FACTOR
      else:
        scale_factor = 1 / SCALE_FACTOR
      xdata = event.xdata
      ydata = event.ydata
      xlim = ax.get_xlim()
      ylim = ax.get_ylim()

      curr_x_range = abs(xlim[0] - xlim[1])
      curr_y_range = abs(ylim[0] - ylim[1])

      x_pos_ratio = (xdata - xlim[0]) / curr_x_range
      y_pos_ratio = (ydata - ylim[0]) / curr_y_range

      new_x_range = curr_x_range * scale_factor
      new_y_range = curr_y_range * scale_factor

      new_x_min_limit = xdata - new_x_range * x_pos_ratio
      new_x_max_limit = xdata + new_x_range * (1 - x_pos_ratio)

      new_y_min_limit = ydata - new_y_range * y_pos_ratio
      new_y_max_limit = ydata + new_y_range * (1 - y_pos_ratio)

      if not self.yKeyPressed:
        self.fig.shared_sp.set_xlim(new_x_min_limit, new_x_max_limit)

      if not self.xKeyPressed:
        ax.set_ylim(new_y_min_limit, new_y_max_limit)
      self.canvas.draw()
    return

  def getKeyName(self, event):
    if event.key() in QT_KEYS_TO_STRING:
      event.key_text = QT_KEYS_TO_STRING[event.key()]
    else:
      event.key_text = event.text()
    return event

  def keyPressEvent(self, event):
    self.canvas.keyPressEvent(event)
    return

  def keyReleaseEvent(self, event):
    self.canvas.keyReleaseEvent(event)
    return

  def onFigureKeyPress(self, event):
    """
    Event handler for key press event.
    CONVENTION: Numbers and capital letters are reserved in order to be consistent with other Navigators.

    :Parameters:
      event : matplotlib.backend_bases.KeyEvent
    :Return: None
    """
    if not hasattr(event, 'key_text'):
      setattr(event, 'key_text', event.key)
    if event.key_text == ' ':
      # synchronizable interface callback
      if self.playing:
        self.onPause(self.time)
      else:
        self.onPlay(self.time)
    elif event.key_text == 'h':
      # pressing 'h' toggles legends on/off
      self.show_legend = not self.show_legend
      if self.show_legend:
        for ax in self.fig.axes:
          if not ax.hide_legend:
            ax.get_legend().set_visible(True)
            self.setValueForLegend(ax, self.time)
      else:
        for ax in self.fig.axes:
          ax.get_legend().set_visible(False)
      self.canvas.draw()
    elif event.key_text == 'r':
      # pressing 'r' resets the legends
      for ax in self.fig.axes:
        if not ax.hide_legend:
          self.setLegend(ax)
          self.setValueForLegend(ax, self.time)
      self.canvas.draw()
    elif event.key_text == 'c':
      # clear the  axvspans
      self.clearAxvspans()
    elif event.key_text == 'n':
      self.changeNumberSystem = not self.changeNumberSystem
      for ax in self.fig.axes:
        if not ax.hide_legend:
          self.setValueForLegend(ax, self.time)
          self.seekWindow()
    elif event.key_text == 'd':
      if not self.show_legend_delta and not self._is_delta_possible():
        self.toolbar.set_message("Can't enable Delta mode: select interval first")
      else:
        if self.show_legend_delta:
          self.show_legend_delta = False
          self.toolbar.set_message("Delta mode OFF")
        else:
          self.show_legend_delta = True
          self.toolbar.set_message("Delta mode ON")
        for ax in self.fig.axes:
          self.setValueForLegend(ax, self.time)
        self.setValueForTimeText()
        self.canvas.draw()
    elif event.key_text == 'm':
      if self.show_legend:
        self.label_multi_col = not self.label_multi_col
        for ax in self.fig.axes:
          if not ax.hide_legend:
            self.setLegend(ax)
            self.setValueForLegend(ax, self.time)
        self.canvas.draw()
    elif event.key_text == '<':
      self.font.set_size( self.font_sizes.prev() )
      self.canvas.draw()
    elif event.key_text == '>':
      self.font.set_size( self.font_sizes.next() )
      self.canvas.draw()
    elif event.key_text == 'F1' or event.key_text == 'f1':
      self.help.set_visible(not self.help.get_visible())
      self.resizeHelp()
      self.canvas.draw()
    elif event.key_text == 'i':
      if self.interpolate:
        self.interpolate = False
        message = 'Interpolation OFF'
      else:
        self.interpolate = True
        message = 'Interpolation ON'
      self.toolbar.set_message(message)
      for ax in self.fig.axes:
        if not ax.hide_legend:
          self.setValueForLegend(ax, self.time)
      self.canvas.draw()
    elif event.key_text == 'a':
      left, right = self.fig.shared_sp.get_xlim()
      self.on_set_xlim_online(left, right)
    elif event.key_text == 'q':
      self.copyContentToClipboard()
      self.toolbar.set_message('Figure copied to clipboard')
    elif event.key_text == 'z':
      figlib.adjustYLimits(self.fig)
      self.toolbar.set_message('Limits of y axes adjusted')
    elif event.key_text == 'control':
      self.control_is_pressed = True
    elif event.key_text == 'shift':
      self.shift_is_pressed = True
    elif event.key_text == 'k':
      for ax in self.fig.axes:
        if ax.get_xscale() == 'linear':
          ax.set_xscale('log')
        else:
          ax.set_xscale('linear')
      self.canvas.draw()
    elif event.key_text == 'l':
      if self.selected_axes is None: return
      ax = self.selected_axes
      if ax.get_yscale() == 'linear':
        ax.set_yscale('log')
      else:
        ax.set_yscale('linear')
      self.canvas.draw()
    elif event.key_text == 't':
      self._handle_mark_toggle()
    elif event.key_text == 'x':
      self.xKeyPressed = True
    elif event.key_text == 'y':
      self.yKeyPressed = True
    elif event.key_text == 'delete':
      self.onSetROI(0.0, 0.0, 'g')
    elif event.key_text == 'F10' or event.key_text == 'f10':
      clipboard = QtGui.QApplication.clipboard()
      clipboard.setText(str(self.time))
      self.logger.info("Current time[%s] is saved to clipboard. Use Ctrl + V /Paste to use it in other application " % self.time)
    return

  def onFigureKeyRelease(self, event):
    if not hasattr(event, 'key_text'):
      setattr(event, 'key_text', event.key)
    if event.key_text == 'control':
      self.control_is_pressed = False
    elif event.key_text == 'shift':
      self.shift_is_pressed = False
    elif event.key_text == 'x':
      self.xKeyPressed = False
    elif event.key_text == 'y':
      self.yKeyPressed = False
    return

  def onMotion(self, event):
    if self.dragPoint and not self.playing:
      # change limits
      xdata, ydata = self.dragPoint.ax.transData.inverted().transform((event.x, event.y))

      x_change = xdata - self.dragPoint.x
      y_change = ydata - self.dragPoint.y
      xlim = self.dragPoint.ax.get_xlim()
      ylim = self.dragPoint.ax.get_ylim()
      if not self.yKeyPressed:
        self.fig.shared_sp.set_xlim(xlim[0] - x_change, xlim[1] - x_change)
      if not self.xKeyPressed:
        self.dragPoint.ax.set_ylim(ylim[0] - y_change, ylim[1] - y_change)
      self.canvas.draw()

    self.selected_axes = event.inaxes
    return

  def onPick(self, event):
    mouse = event.mouseevent
    if self.control_is_pressed: # only if control pressed
      ax = mouse.inaxes
      if ax in self.fig.axes:
        try:
          leg = self.findLegend(ax, mouse)
        except ValueError:
          leg = ax.get_legend()
          texts = leg.get_texts()
          lines = leg.get_lines()
          pickedLine = event.artist
          pickedLineText = ""
          for k, v in ax.label2line.iteritems():
            if v == pickedLine:
              pickedLineText = k
          for text,line in zip(texts,lines):
            tmp_text = text.get_text()
            tmp_text = tmp_text.split('=')[0].strip()
            if tmp_text == pickedLineText:
              if mouse.button == 1:
                self.switchMarker(pickedLine, line)
              elif mouse.button == 3:
                self.switchLineWidth(pickedLine, line)
              break
        self.canvas.draw()
    return

  def setValueForLegend(self, ax, x):
    """
    Set the label of the lines of the `ax` to 'label = <value at `x`>'

    :Parameters:
      ax : matplotlib.axes.AxesSubPlot
      x: float
    """
    texts = ax.get_legend().get_texts()
    labels = map(lambda t:
            t.get_text().replace("$\\Delta$","").split('=')[0].strip(), texts)  # cut the value
    # Delta tag also has to be removed (replaced) if it exists: otherwise brings KeyError.
    for text, label in zip(texts, labels):
      # find axis of signal exactly (considering the corresponding twin axes)
      concrete_ax = None
      for par_ax in ax.parasites:
        if label in par_ax.label2line:
          assert concrete_ax is None, "Multiple twin axes found for signal '%s'" % label
          concrete_ax = par_ax
      if concrete_ax is None:
        concrete_ax = ax
      # get values
      line = concrete_ax.label2line[label]
      textValue = ''
      if self.show_legend_delta:
        # get left (ROIstart) and right (ROIend) values and convert if needed (to avoid overflow)
        value_left = self.get_value_from_line(ax, line, self.ROIstart)
        if isinstance(value_left, np.integer):
          value_left = int(value_left)
        value_right = self.get_value_from_line(ax, line, self.ROIend)
        if isinstance(value_right, np.integer):
          value_right = int(value_right)
        # setting the text...
        if value_left is not None and value_right is not None:
          if value_left is np.ma.masked or value_right is np.ma.masked:
            textValue = self.MASKED_PRINT_OPTION
          #elif ax.yticks:
            #tbd TODO is it nessesary?
          else:
            textValue = line.format % (value_right - value_left)
          displayedLabel = self._set_legend_label(textValue, label, line.unit, r"$\Delta$")
          text.set_text(displayedLabel)
        else:
          text.set_text(label)
      else:
        value = self.get_value_from_line(ax, line, x)
        if value is not None:
          if value is np.ma.masked:
            textValue = self.MASKED_PRINT_OPTION
          elif concrete_ax.yticks:
            if value in concrete_ax.yticks:
              textValue = concrete_ax.yticks[value]
            else:
              textValue = line.format % value
              if 'default' in concrete_ax.yticks:
                textValue += ' (%s)' % concrete_ax.yticks['default']
          else:
            textValue = line.format % value
          if self.changeNumberSystem:#Decimal
            displayedLabel = self._set_legend_label(textValue, label, line.unit)
          else:#Hexa decimal
            if textValue.__contains__('.'):
              val=hex(int(float(textValue)))
              if len(val) < 8:
                val = (val).replace('x', 'x0')
              displayedLabel = self._set_legend_label(val, label, line.unit)
            else:
              try:
                val = hex(int(textValue))
                if len(val) < 8:
                  val = (val).replace('x', 'x0')
                displayedLabel = self._set_legend_label(val, label, line.unit)
              except Exception as e:
                displayedLabel = self._set_legend_label(textValue, label, line.unit)

          text.set_text(displayedLabel)
        else:  # no data on the current position
          text.set_text(label)
    return

  def _set_legend_label(self, text, label, unit=None, prefix=None):
    displayedLabel = [label, '=', text]
    if prefix:
      displayedLabel = [prefix] + displayedLabel
    if unit:
      # only possible in Python 2  str(type(unit)) != "<type 'unicode'> or  if isinstance(s, unicode)
      # it checks for unicode unit if not then convert it or if any escape seq. then convert it to unicode character
      if not isinstance(unit, unicode):
        unit = unit.decode('unicode_escape')
      displayedLabel.append(unit)
    displayedLabel = ' '.join(displayedLabel)
    return displayedLabel

  def get_value_from_line(self, ax, line, x):
    """
    Gets the Y value from an specific line hosted in a given axes.
    :Parameters:
      ax : matplotlib.axes.AxesHostAxesSubplot
        Axis to which the line belongs.
      label : 'matplotlib.lines.Line2D'
        Line from which the value will be extracted
      x : numpy.float64
        Value in the X axis.
    """
    xdata = line.get_xdata()
    value = None
    if xdata.size < 1:
      return value
    pos = xdata.searchsorted(x)
    # find value based on seek timestamp
    if pos < xdata.size and x == xdata[pos]:
      value = line.value[pos]
    elif xdata[0] < x < xdata[-1]:
      pos = max(pos-1, 0)
      value = line.value[pos]
      if (    self.interpolate
          and value is not np.ma.masked
          and not ax.yticks
          and np.issubdtype(value.dtype, np.float) ):
        nextpos = pos+1
        nextvalue = line.value[nextpos]
        if nextpos < xdata.size and nextvalue is not np.ma.masked:
          time = xdata[pos]
          nexttime = xdata[nextpos]
          value += (nextvalue - value) / (nexttime - time) * (x - time)
    return value

  def setValueForTimeText(self):
    if self.show_legend_delta:
      prefix = r"$\Delta$"
      msg = " {0:.3f}  ({1:.3f} -> {2:.3f})"
      displayed = prefix + msg.format((self.ROIend - self.ROIstart) , self.ROIstart, self.ROIend)
      self.timeText.set_text(displayed)
    else:
      self.timeText.set_text("%.3f"%self.time)
    return

  @staticmethod
  def _get_format(delta):
    """
    Calculates the best precision for the displayed values in labels.

    :Parameters:
      delta : float
        Delta between the signal's maximum and minimum values

    """
    fractional_part, decimal_part = math.modf(delta)
    rounding = 3
    if fractional_part and decimal_part == 0:
      rounding = ((-1) * math.floor(math.log10(fractional_part) ) ) + (rounding - 1)
      # +2, because the floor of any decimal part will be -1
    f_format = '%.{0}f'.format(int(rounding))
    return f_format

  def switchLineWidth(self, line, lineOnLegend):
    """
    Switch the linewidth of the the `line` between the original / double the
    original / zero.
    :Parameters:
      line : matplotlib.lines.Line2D
      lineOnLegend : matplotlib.lines.Line2D
    """
    linewidth = line.linewidth_states.next()
    line.set_linewidth(linewidth)
    lineOnLegend.set_linewidth(linewidth)
    return

  def switchMarker(self, line, lineOnLegend):
    """
    Switch on/off the marker of the `line`.
    :Parameters:
      line : matplotlib.lines.Line2D
      lineOnLegend : matplotlib.lines.Line2D
    """
    marker = line.marker_states.next()
    line.set_marker(marker)
    lineOnLegend._legmarker.set_marker(marker)
    mark_id = "{0}-{1}-{2}".format(line.axes.colNum, line.axes.rowNum, line.get_label())
    if mark_id not in self.toggled_plots:
      self.toggled_plots[mark_id] = True
    else:
      self.toggled_plots[mark_id] = not self.toggled_plots[mark_id]
    return

  def clearAxvspans(self):
    """
    Toggles on/off the interval marks on the plot.
    """
    for ax in self.fig.axes:
      for axvspan in ax.axvspans.itervalues():
        axvspan.set_visible(not axvspan.get_visible())
    self.toolbar.set_message('Show intervals' if axvspan.get_visible() else 'Hide intervals')
    self.canvas.draw()
    return

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
    cNavigator.setROI(self, client, start, end, color)
    if isinstance(client, (cPlotNavigator, datavis.MapNavigator)):
      client = self
    for ax in self.fig.axes:
      if client not in ax.axvspans:
        ax.axvspans[client] = ax.axvspan(start, end, facecolor=color, alpha=0.3)
      else:
        xy = ax.axvspans[client].get_xy()
        xy[0][0] = start
        xy[1][0] = start
        xy[2][0] = end
        xy[3][0] = end
        ax.axvspans[client].set_xy(xy)
      if self.show_legend and not ax.hide_legend:
        self.setValueForLegend(ax, self.time)
    self.setValueForTimeText()
    self.canvas.draw()
    cNavigator.setROI(self, client, start, end, color)
    return

  def seekWindow(self):
    for ax in self.fig.axes:
      ax.timemarker.set_xdata(self.time)
      if self.show_legend and not ax.hide_legend:
        self.setValueForLegend(ax, self.time)
    self.setValueForTimeText()
    self.centralize(self.time)
    self.canvas.draw()
    if self.is_recording:
      width, height = self.canvas.get_width_height()
      frame = np.fromstring(self.canvas.tostring_argb(), dtype=np.uint8)
      frame.shape = (width, height, 4)
      # Transformation to RGBA for FFMPEG
      frame = np.roll(frame, 3, axis=2)
      self.recorder.update_current_record(frame)
    return

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

  def _is_delta_possible(self):
    """
    Indicates wheter or not it's possible to activate the delta mode for
    the legend. Delta mode can only be activated if intervals are visible
    AND if there is an existing one.
    """
    able = True
    for ax in self.fig.axes:
      for axvspan in ax.axvspans.itervalues():
        if not axvspan.get_visible():
          able = False
          break
    if self.ROIstart == 0.0 and self.ROIend == 0.0:
      # Interval values are set to default : No interval
      able = False
    return able

  def clean(self):
    mpl.pyplot.close(self.fig)
    return


  def _handle_mark_toggle(self):
    self.toggle_state += 1
    self.toggle_state %= 3
    message = ''
    if self.toggle_state == 0:
      message = 'Showing CUSTOM markings'
      self._set_custom_markers()
    elif self.toggle_state == 1:
      message = 'Showing ALL markers'
      self._set_all_markers(self.DEFAULT_MARKER)
    else:
      message = 'Showing NO markers'
      self._set_all_markers(self.NO_MARKER)
    self.toolbar.set_message(message)
    return

  def _set_all_markers(self, mark):
    for ax in self.fig.axes:
      for line in ax.lines:
        if line.get_label() != '_line0':
          line.set_marker(mark)
      for leg_line in ax.get_legend().get_lines():
        leg_line._legmarker.set_marker(mark)
    self.canvas.draw()
    return

  def _set_custom_markers(self):
    for ax in self.fig.axes:
      for line in ax.lines:
        if line.get_label() != '_line0':
          mark_id = "{0}-{1}-{2}".format(ax.colNum, ax.rowNum, line.get_label())
          lineLeg = None
          for leg_line, leg_text in zip(ax.get_legend().get_lines(),
                                        ax.get_legend().get_texts()):
            if leg_text.get_text().split('=')[0].strip() == line.get_label():
              lineLeg = leg_line

          if mark_id in self.toggled_plots and self.toggled_plots[mark_id]:
            line.set_marker(self.DEFAULT_MARKER)
            lineLeg._legmarker.set_marker(self.DEFAULT_MARKER)
          else:
            line.set_marker(self.NO_MARKER)
            lineLeg._legmarker.set_marker(self.NO_MARKER)
    self.canvas.draw()
    return

def fitKWArgsLen(fitlen, kwargs, kw, default):
  """
  Fit the legth of the `kw` keyword argument to the `fitlen`. Fill the
  remainded keyword arguments with `default`.

  :Parameters:
    fitlen : int
      requested length of the keyword parameter
    kwargs : dict
    kw : str
    default : arbitrary
      Like kwargs[kw] or kwargs[kw][0]
  """
  if kw in kwargs:
    kwarg = kwargs[kw]
    if isinstance(kwarg, list):
      kwarg_len   = len(kwarg)
      more_signal = fitlen - kwarg_len
      if more_signal > 0:
        kwargs[kw] += [default] * more_signal
        self.logger.info('more signal are added %(fitlen)d than %(kw)s (%(kwarg_len)d) default %(kw)s (%(default)s) is set for them!\n' %locals())
      elif more_signal < 0:
        self.logger.info('more %(kw)s are added (%(kwarg_len)d) than signals (%(fitlen)d) the rest of them are ignored!\n' %locals())
    else:
      kwargs[kw] = [kwarg]*fitlen
  else:
    kwargs[kw] = [default]*fitlen
  return

def stretch(margin, y_min, y_max):
  """
  Stretch the `y_min`, `y_max` interval bounds with `margin`.

  :Parameters:
    margin : float
      Margin of the stretching.
    y_min : float
      Lower bound of the interval.
    y_max : float
      Upper bound of the interval.
  :ReturnType: float, float
  :Return: The stretched interval bounds.
  """
  margin *= y_max - y_min
  y_min -= margin
  y_max += margin
  return y_min, y_max

if __name__ == '__main__':
  import optparse

  app = QtGui.QApplication([])
  parser = optparse.OptionParser()
  parser.add_option('-p', '--hold-navigator',
                    help='Hold the navigator, default is %default',
                    default=False,
                    action='store_true')
  opts, args = parser.parse_args()
  pn = cPlotNavigator( "Test PlotNavigator")

  t  = np.arange(0, 10, 0.01)
  pn.addsignal('sin', (t , np.sin(t)), threshold=0.5)
  pn.addsignal('sin', (t , np.sin(t)),
               'cos', (t , np.cos(t)),
               threshold=[0.6,'b', 0.7,'c',0.8,'m',0.9,'r'])
  pn.addsignal('atan', (t , np.arctan(t)),
               xlabel='time [s]',
               grid=False)
  pn.addsignal('sin+1', (t , np.sin(t)),
               'sin+2', (t , np.sin(t)),
               offset=[1,2],
               displayscaled=[True, False])
  pn.start()
  pn.setWindowGeometry('1800x1800+100+100')
  pn.show()
  if opts.hold_navigator:
    sys.exit(app.exec_())

