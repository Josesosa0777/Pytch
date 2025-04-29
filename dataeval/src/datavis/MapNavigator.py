"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright:
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial
  property. We reserve all rights of disposal such as copying and passing on to
  third parties.
"""
__docformat__ = "restructuredtext en"

from PIL import Image
from PySide import QtCore, QtGui
import matplotlib as mpl
from matplotlib.collections import LineCollection
from matplotlib.patches import Polygon
if mpl.rcParams['backend.qt4']!='PySide':
  mpl.use('Qt4Agg')
  mpl.rcParams['backend.qt4']='PySide'
import numpy as np

from datavis import cNavigator
from datavis.Group import iGroup
from datavis.PlotNavigator import FigureManager
from datavis.backend_map import LonDegreeFormatter, LatDegreeFormatter,\
    CanvasWithSpecButtonSensing, NavigationTools, XFormatter, YFormatter
import measproc.MapTileCalculation as mtc
import measproc.mapbbox as mbox
import figlib

GREY = (220.0/255.0, 220.0/255.0, 220.0/255.0)


class VehiclePosition(object):
  def __init__(self, x, y):
    self.x = x
    self.y = y
    return

  def set_coords(self, x, y):
    self.x = x
    self.y = y
    return


class TrajectoryData(object):
  def __init__(self, time, longitude, latitude, heading, type_, color):
    self.time = time
    self.coords = mtc.Coord(longitude, latitude)
    self.heading = heading
    self.type = type_
    self.color = color
    self.line = None
    return


class HighlightedSection(object):
  prop = dict(c='g', s=100.0, marker='D')
  label = 'Region Of Interest'

  def __init__(self, map_axis):
    self.start_idx = None
    self.end_idx = None
    self.selected = False
    self.start_pos = map_axis.scatter([], [], zorder=5, **self.prop)
    self.line = map_axis.plot([], [], zorder=25, linestyle='-', linewidth=5.0, color=self.prop['c'])[0]
    return

  def isSectionAvailable(self):
    return self.start_idx and self.end_idx

  def isStartPoint(self):
    if self.end_idx is not None or self.start_idx is None:
      return True
    else:
      return False

  def setStartPoint(self, index):
    self.start_idx = index
    self.end_idx = None
    return

  def setMarkerAndLine(self, x, y):
    start_point = (x[self.start_idx], y[self.start_idx])
    self.start_pos.set_offsets(start_point)
    if self.end_idx:
      self.line.set_xdata(x[self.start_idx:self.end_idx])
      self.line.set_ydata(y[self.start_idx:self.end_idx])
    self.line.set_visible(True if self.end_idx else False)
    return

  def setEndPoint(self, index):
    self.end_idx = index
    self.sortIndexes()
    return

  def sortIndexes(self):
    if not self.start_idx or not self.end_idx:
      return
    elif self.end_idx < self.start_idx:
      self.start_idx, self.end_idx = self.end_idx, self.start_idx
    return

  def setSelected(self, state):
    self.selected = state
    alpha = 1.0 if self.selected else 0.1
    self.start_pos.set_alpha(alpha)
    self.line.set_alpha(alpha)
    return

  def removeArtists(self):
    self.start_pos.set_offsets([])
    self.line.set_xdata([])
    self.line.set_ydata([])
    self.start_idx, self.end_idx = None, None
    return


class Events(object):
  def __init__(self, map_axis, intervals, label, x, y, **properties):
    self.intervals = intervals
    self.label = label
    self.prop = properties
    self.selected = False
    self.start_indices = [start for start, _ in intervals]
    self.start_pos = map_axis.scatter(x[self.start_indices], y[self.start_indices], zorder=2, **properties)
    self.lines = []
    for start, end in self.intervals:
      self.lines.append(map_axis.plot(x[start:end], y[start:end],
                        zorder=25, linestyle='-', linewidth=5.0, color=self.prop['c'])[0])
    return

  def setSelected(self, state):
    self.selected = state
    alpha = 1.0 if self.selected else 0.1
    self.start_pos.set_alpha(alpha)
    for line in self.lines:
      line.set_alpha(alpha)
    return

  def removeArtists(self):
    self.start_pos.remove()
    for line in self.lines:
      line.remove()
    return


class MapCanvas(cNavigator):
  def __init__(self, title, figureNr, window_pattern, map_manager):
    """
    :Parameters:
      title : str
      figureNr : int
        In case of None the last Figure number will be increased.
    """
    cNavigator.__init__(self)
    figureNr = figlib.det_figure_nr(title, figureNr)
    self.fig = mpl.pyplot.figure(figureNr)
    self.map_axis = self.fig.add_subplot(1, 1, 1)
    """:type: `matplotlib.figure.Figure`"""
    if title:
      self.fig.suptitle(title)
    self.title = title
    """:type: str
    Main title of the plot window"""
    self.window_pattern = window_pattern
    self._windowId = figlib.generateWindowId(title)
    """:type: str
    String to identify the window"""

    self.map_axis.set_axis_bgcolor(GREY)
    self.canvas = CanvasWithSpecButtonSensing(self.fig)
    self.figure_manager = FigureManager(self.canvas, figureNr)
    self.setCentralWidget(self.canvas)
    self.nav_tools = NavigationTools(self.canvas, self.canvas,
                                     map_manager, self.map_axis)
    self.addToolBar(QtCore.Qt.BottomToolBarArea, self.nav_tools)
    return
  
  def setAxesLimits(self, limits):
    figlib.setAxesLimits(self.fig, limits)
    return
  
  def copyContentToClipboard(self):
    """Copy current figure to the clipboard as a bitmap image."""
    figlib.copyContentToClipboard(self.fig)
    return
  
  def copyContentToFile(self, fname, format=None):
    """Copy figure to the specified file in the specified format."""
    figlib.copyContentToFile(self.fig, fname, format)
    return
  
  def getWindowId(self):
    return self._windowId
  
  def setWindowTitle(self, Measurement):
    """
    :Parameters:
      Measurement : str
    """
    try:
      window_title = (self.window_pattern %
                      (self.fig.number, Measurement))
    except TypeError:
      window_title = self.window_pattern
    QtGui.QMainWindow.setWindowTitle(self, window_title)
    return

  def _convertGpsToPixCoords(self, Lon, Lat):
    GPS_coords = mtc.Coord(Lon, Lat)
    road_pix = GPS_coords.to_pixel(self.nav_tools.zoom_level)
    return self.nav_tools.map_orig_tile.norm_pixel(road_pix)


class StaticMapNavigator(MapCanvas):
  """
  Queries map database for tiles to be drawn for a map region. Assembles map
  tiles into one map image and draws it. Transforms route to the map and draws
  it. It creates static plots which means that they provide only rendered maps
  with route plots, markers and arrows but no actual navigation capabilities
  (seeking and other event handling functions)
  :Parameters:
    map_manager: measproc.MapManager.cMapManager
      Instantiation of cMapManager class.
    figure_num: int
      Number of the figure used for map and route plotting.
    max_resolution: int
      70MP is the max resolution matplotlib can handle
  :Exception:
    cMapNavigatorError:
      Missing map database, tiles or map drawing omitted before route plotting.
  """
  def __init__(self, map_manager, title='', figureNr=None, route_color='b',
               line_width=2.0, line_style='-', max_resolution=70000000):
    MapCanvas.__init__(self, title, figureNr, 'MN %d %s', map_manager)
    
    self.route_color = route_color
    self.line_width = line_width
    self.line_style = line_style
    self.basic_style = dict(color=route_color, linestyle=line_style, linewidth=line_width)
    self.route = []
    self.trajectories = []
    self.stat_mark_prop = {}
    self.stat_mark_data_idx = {}
    self.max_resolution = max_resolution

    self.Markers = {}
    self.MarkerLabels = {}
    return

  def addStyles(self, Styles):
    if not Styles:
      return
    for Type, (LegendName, Style) in Styles.iteritems():
      self.Markers[Type] = Style.copy()
      self.MarkerLabels[Type] = LegendName
    return

  def add_trajectory(self, time, trajectory):
    longitude = trajectory['longitude']
    latitude = trajectory['latitude']
    heading = trajectory.get('heading', None)
    type_ = trajectory['type']
    color = trajectory.get('color', None)
    self.trajectories.append(TrajectoryData(time, longitude, latitude, heading, type_, color))
    return

  def get_map_bbox(self):
    min_lon, min_lat, max_lon, max_lat = None, None, None, None
    for traj in self.trajectories:
      curr_min_lon = traj.coords.lon.min()
      curr_max_lon = traj.coords.lon.max()
      curr_min_lat = traj.coords.lat.min()
      curr_max_lat = traj.coords.lat.max()
      min_lon = curr_min_lon if min_lon is None or min_lon > curr_min_lon else min_lon
      max_lon = curr_max_lon if max_lon is None or max_lon > curr_max_lon else max_lon
      min_lat = curr_min_lat if min_lat is None or min_lat > curr_min_lat else min_lat
      max_lat = curr_max_lat if max_lat is None or max_lat > curr_max_lat else max_lat

    map_bbox = mbox.MapBbox(min_lon, min_lat, max_lon, max_lat)
    return map_bbox

  def set_route(self, zoom=None, check_zoom_in_db=False):
    if not self.trajectories:
      raise IOError

    map_bbox = self.get_map_bbox()
    self.nav_tools.init_map_drawing(map_bbox, check_zoom_in_db, zoom, self.max_resolution)

    for traj in self.trajectories:
      traj_style = self.Markers[traj.type] if traj.type in self.Markers else self.basic_style
      traj_pix = self._convertGpsToPixCoords(traj.coords.lon, traj.coords.lat)
      if traj.color is not None:
        # https://matplotlib.org/examples/pylab_examples/multicolored_line.html
        points = np.array([traj_pix.x, traj_pix.y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        traj.line = LineCollection(segments, linewidths=2., colors=traj.color)
        self.map_axis.add_collection(traj.line)
      else:
        traj.line, = self.map_axis.plot(traj_pix.x, traj_pix.y, zorder=15, **traj_style)

    return
  
  def draw_arrow(self):
    arrow_x = []
    arrow_y = []
    tmp = 0

    for traj in self.trajectories:
      route_x = traj.line.get_xdata()
      route_y = traj.line.get_ydata()
      for i, (x, y) in enumerate(zip(route_x, route_y)):
        if ((tmp + i) % 8000 == 0
            and x > 0 and y > 0 and x < self.nav_tools.map_image.size[0]
            and y < self.nav_tools.map_image.size[1]):
          arrow_x.append(x)
          arrow_y.append(y)
      tmp += len(route_x)
    
    if len(arrow_x) >= 2:
      tmp_dist = np.sqrt((arrow_x[-1] - arrow_x[0])**2 +
                         (arrow_y[-1] - arrow_y[0])**2)
      if tmp_dist < 40:
        self.map_axis.text(arrow_x[1], arrow_y[1] - 15,
                           'START/FINISH',
                           bbox=dict(facecolor='#D3D3D3', alpha=1.0),
                           fontsize=8, zorder=10001)
      else:
        self.map_axis.text(arrow_x[1], arrow_y[1] - 15,
                           'START',
                           bbox=dict(facecolor='#D3D3D3', alpha=1.0),
                           fontsize=8, zorder=10001)
        self.map_axis.text(arrow_x[-1], arrow_y[-1] - 15,
                           'FINISH',
                           bbox=dict(facecolor='#D3D3D3', alpha=1.0),
                           fontsize=8, zorder=10001)
    for i in xrange(0, len(arrow_x) - 1, 15):
      arrow_len = np.sqrt((arrow_x[i+1] - arrow_x[i])**2 +
                          (arrow_y[i+1] - arrow_y[i])**2)
      dx = arrow_x[i+1] - arrow_x[i]
      dy = arrow_y[i+1] - arrow_y[i]
      dirvec_x = dx/arrow_len
      dirvec_y = dy/arrow_len
      normvec_x = -dirvec_y
      normvec_y = dirvec_x
      arr = mpl.pyplot.Arrow(arrow_x[i] + (normvec_x * 15),
                             arrow_y[i] + (normvec_y * 15),
                             dirvec_x * 25, dirvec_y * 25,
                             edgecolor='black', facecolor='gray', width=8)
      self.map_axis.add_patch(arr)
    return
  
  def set_markers(self, event_interval_list, label, event_color='r',
                  event_marker_size=100.0, event_marker_style='D'):
    self.set_marker_properties(self.stat_mark_prop,label, event_color,
                               event_marker_size, event_marker_style)
    stat_mark_data_idx = self.stat_mark_data_idx.setdefault(label, [])
    for _, event_intervals in zip(self.trajectories, event_interval_list):
      stat_mark_data_idx.append([start for start, _ in event_intervals])
    return
  
  @staticmethod
  def set_marker_properties(mark_prop_dict, label, event_color,
                            event_marker_size, event_marker_style):
    prop = mark_prop_dict.setdefault(label, {})
    prop['c'] = event_color
    prop['s'] = event_marker_size
    prop['marker'] = event_marker_style
    return
  
  def start(self):
    for xtick_label in self.map_axis.get_xticklabels():
      xtick_label.set_visible(False)
    for ytick_label in self.map_axis.get_yticklabels():
      ytick_label.set_visible(False)
    
    for label, marker_indeces in self.stat_mark_data_idx.iteritems():
      for traj, markers in zip(self.trajectories, marker_indeces):
        route_xdata = traj.line.get_xdata()
        route_ydata = traj.line.get_ydata()
        self.map_axis.scatter(route_xdata[markers], route_ydata[markers],
                              zorder=5, **self.stat_mark_prop[label])
    self.map_axis.imshow(self.nav_tools.map_image, origin="lower")
    mpl._pylab_helpers.Gcf.set_active(self.figure_manager)
    self.map_axis.set_xlim((0, self.nav_tools.map_image.size[0]))
    self.map_axis.set_ylim((0, self.nav_tools.map_image.size[1]))
    return


class MapNavigator(StaticMapNavigator, iGroup):
  """
  Queries map database for tiles to be drawn for a map region. Assembles map
  tiles into one map image and draws it. Transforms route to the map and draws
  it.
  :Parameters:
    map_manager: measproc.MapManager.cMapManager
      Instantiation of cMapManager class.
    figure_num: int
      Number of the figure used for map and route plotting.
  :Exception:
    cMapNavigatorError:
      Missing map database, tiles or map drawing omitted before route plotting.
  """
  def __init__(self, map_manager, title='', figureNr=None,
               route_color='b', line_width=2.0,
               line_style='-', route_marker_size=250.0, route_marker_style='.',
               max_resolution=70000000):
    StaticMapNavigator.__init__(self, map_manager, title, figureNr, route_color,
                                line_width, line_style, max_resolution)
    iGroup.__init__(self)

    self.Menu = self.menuBar()
    self.GroupMenu = QtGui.QMenu('Groups')
    self.Menu.addMenu(self.GroupMenu)
    self.ViewMenu = QtGui.QMenu('View')
    self.Menu.addMenu(self.ViewMenu)
    self.tickFormatMenu = QtGui.QMenu('Figure Tick Format')

    self.image_visible = True
    self.show_veh_info = True

    self.show_road_map = False
    self.road_map = []

    self.int_width = self.line_width + 3
    self.route_marker_size = route_marker_size
    self.route_marker_style = route_marker_style
    self.veh_pos = VehiclePosition(0, 0)
    self.nav_tools.veh_pos = self.veh_pos

    self.current_heading = None
    self.veh_marker = None

    self.highlighted_section = HighlightedSection(self.map_axis)
    self.events = []
    self.event_legend = None

    self.alpha_selected = 1.0
    self.alpha_deselected = 0.1

    self.tick_format = 'coord'

    control_keys = {'F1':           'Show/hide this help screen',
                    'h':            'Show/hide legend',
                    'b':            'Enable/disable background image',
                    'x':            'Remove event selection',
                    't':            'Toggle axis formatter Coordinate/Meter',
                    '.':            'Enable/disable floating vehicle info function (does not work during playback)',
                    'r':            'Enable/disable roadmap',
                    'arrow keys':   'Cycle through events',
                    'delete':       'Delete selected event markers',
                    'Right click':  'Define a new interval'}
    help_font = mpl.font_manager.FontProperties('monospace', 'normal', 'normal',
                                                'normal', 'normal', 'small')
    self.help = self.fig.text(0.1, 0.5,
                              'Keyboard shortcuts:\n\n'
                              'F1                   %(F1)s\n'
                              'h                    %(h)s\n'
                              'b                    %(b)s\n'
                              'x                    %(x)s\n'
                              't                    %(t)s\n'
                              '.                    %(.)s\n'
                              'r                    %(r)s\n'
                              'up/down arrow keys   %(arrow keys)s\n'
                              'delete               %(delete)s\n'
                              'Right click          %(Right click)s*\n'
                              '\n*Works when pan/zoom mode is inactive'
                              % control_keys,
                              visible=False,
                              fontproperties=help_font,
                              bbox=dict(facecolor='LightYellow', pad=20))

    self.VehInfo = self.map_axis.annotate("", (0, 0), xycoords='data',
                                          xytext=(40, 40), textcoords='offset points', fontproperties=help_font,
                                          bbox=dict(boxstyle='square', facecolor='LightYellow'),
                                          arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
                                          visible=False, zorder=100000)

    self.create_view_menu()

    self.time_text = self.fig.text(0.025, 0.025, "")
    self.pick_text = self.fig.text(0.75, 0.025, "")
    self.canvas.mpl_connect('pick_event', self.on_pick)
    self.canvas.mpl_connect('key_press_event', self.on_figure_key_press)
    self.canvas.mpl_connect('motion_notify_event', self.on_motion)
    return

  def create_view_menu(self):
    formatActionGroup = QtGui.QActionGroup(self)
    coordState = QtGui.QAction('Coordinate', self, triggered=lambda: self.set_tick_format('coord'))
    coordState.setCheckable(True)
    coordState.setChecked(True)
    meterState = QtGui.QAction('Meter', self, triggered=lambda: self.set_tick_format('meter'))
    meterState.setCheckable(True)
    formatActionGroup.addAction(coordState)
    formatActionGroup.addAction(meterState)
    self.tickFormatMenu.addActions([coordState, meterState])
    self.ViewMenu.addMenu(self.tickFormatMenu)

    self.vehInfoAction = QtGui.QAction('Floating Vehicle Position', self, triggered=lambda: self.set_veh_info_state())
    self.vehInfoAction.setShortcut(self.tr('.'))
    self.vehInfoAction.setCheckable(True)
    self.vehInfoAction.setChecked(self.show_veh_info)
    self.ViewMenu.addAction(self.vehInfoAction)

    self.roadmapAction = QtGui.QAction('Show Roadmap', self, triggered=lambda: self.set_roadmap_state())
    self.roadmapAction.setShortcut(self.tr('r'))
    self.roadmapAction.setCheckable(True)
    self.roadmapAction.setChecked(self.show_road_map)
    self.ViewMenu.addAction(self.roadmapAction)
    return

  def get_measured_traj(self):
    for traj in self.trajectories:
      if self.MarkerLabels[traj.type] == 'Measured traj':
        return traj
    return self.trajectories[0] if self.trajectories else None

  def set_tick_format(self, tick_format):
    self.tick_format = tick_format
    if self.tick_format is 'coord':
      self.nav_tools.set_tick_formatter(LonDegreeFormatter, LatDegreeFormatter)
    else:
      self.nav_tools.set_tick_formatter(XFormatter, YFormatter)
    return

  def set_veh_info_state(self):
    self.show_veh_info = self.vehInfoAction.isChecked()
    self.VehInfo.set_visible(self.show_veh_info)
    self.canvas.draw()
    return

  def set_roadmap_state(self):
    if self.road_map is None:
      self.logger.warning("Can't draw roadmap on map")
      self.logger.info("Reason:\nNo available .osm file for roadmap visualization")
      return
    self.show_road_map = self.roadmapAction.isChecked()
    for road in self.road_map:
      road.set_visible(self.show_road_map)
    self.canvas.draw()
    return
  
  def set_markers(self, event_interval_list, label, event_color='r',
                  event_marker_size=100.0, event_marker_style='D'):
    measured_traj = self.get_measured_traj()
    x = measured_traj.line.get_xdata()
    y = measured_traj.line.get_ydata()
    self.events.append(Events(self.map_axis, event_interval_list, label, x, y,
                              c=event_color, s=event_marker_size, marker=event_marker_style))
    return

  def setGroup(self, GroupName, Visible, KeyCode):
    action = QtGui.QAction(GroupName, self)
    action.setCheckable(True)

    action.triggered.connect(lambda n=GroupName, _action=action:
                             (self._setVisible(n, _action.isChecked()),
                              self.onSelectGroup(n),))

    self.GroupMenu.addAction(action)
    action.setChecked(Visible)
    return

  def selectGroup(self, GroupName):
    iGroup.selectGroup(self, GroupName)
    [group.setChecked(not self.Toggles[GroupName]) for group in self.GroupMenu.actions() if group.text() == GroupName]
    return

  def _setVisible(self, GroupName, Visible):
    for traj in self.trajectories:
        visible = not traj.type in self.Invisibles
        traj.line.set_visible(visible)
    self.canvas.draw()
    return

  def remove_event_selection(self):
    self.highlighted_section.setSelected(True)
    self.highlighted_section.selected = False
    for traj_event in self.events:
      traj_event.setSelected(True)
      traj_event.selected = False
    return

  def set_legend(self, visible=False):
    labels = []
    artists = []
    for traj in self.trajectories:
      labels.append(self.MarkerLabels[traj.type])
      artists.append(traj.line)

    for event in self.events:
      labels.append(event.label)
      artists.append(event.start_pos)
    if self.highlighted_section.isSectionAvailable():
      labels.append(self.highlighted_section.label)
      artists.append(self.highlighted_section.start_pos)

    self.event_legend = self.map_axis.legend(artists, labels, loc='upper right',
                                             bbox_to_anchor=(0, 0, 1, 1),
                                             bbox_transform=self.fig.transFigure,
                                             scatterpoints=1)
    self.event_legend.zorder = 100
    self.event_legend.set_visible(visible)
    self.event_legend.draggable(state=True)
    return

  def select_legend_item(self, event):
    texts = self.event_legend.get_texts()
    markers = self.event_legend.legendHandles
    for text, marker in zip(texts, markers):
      if text.contains(event)[0] or marker.contains(event)[0]:
        return text, marker
    raise ValueError
  
  def resize_help(self):
    if self.help.get_visible():
      bx = self.help.get_window_extent()
      bx = bx.inverse_transformed(self.fig.transFigure)
      self.help.set_position(((1 - bx.width) / 2., (1 - bx.height) / 2.))
    return

  def setROI(self, client, start, end, color):
    cNavigator.setROI(self, client, start, end, color)

    if start == end:
      self.highlighted_section.removeArtists()
    else:
      measured_traj = self.get_measured_traj()
      start_idx = np.searchsorted(measured_traj.time, start)
      end_idx = np.searchsorted(measured_traj.time, end)
      self.highlighted_section.setStartPoint(start_idx)
      self.highlighted_section.setEndPoint(end_idx)
      route_line = measured_traj.line
      self.highlighted_section.setMarkerAndLine(route_line.get_xdata(), route_line.get_ydata())

      show_legend = self.event_legend.get_visible()
      self.set_legend(show_legend)

    self.canvas.draw()
    return

  def on_pick(self, event):
    mouse = event.mouseevent
    picked_line = event.artist
    if self.event_legend.get_visible() and self.event_legend.contains(mouse)[0]:
      try:
        selected_text, marker = self.select_legend_item(mouse)
      except ValueError:  # clicked on empty area of the legend
        pass
      else:
        text = selected_text.get_text()
        self.highlighted_section.setSelected(self.highlighted_section.label == text)
        for traj_event in self.events:
          traj_event.setSelected(traj_event.label == text)

    if picked_line != self.event_legend:
      data_indeces = event.ind
      route_xdata = picked_line.get_xdata()
      route_ydata = picked_line.get_ydata()
      route_xdata_masked = route_xdata[data_indeces]
      route_ydata_masked = route_ydata[data_indeces]
      dist = np.sqrt((mouse.xdata - route_xdata_masked)**2 +
                     (mouse.ydata - route_ydata_masked)**2)
      min_dis_ind = np.argmin(dist)
      data_index = data_indeces[min_dis_ind]

      meas_time = self.get_measured_traj().time
      if mouse.button == 1:
        time = meas_time[data_index]
        self.seekSignal.signal.emit(time)
        self.seek(time)
      elif mouse.button == 3:
        if self.highlighted_section.isStartPoint():
          self.highlighted_section.setStartPoint(data_index)
          self.highlighted_section.setMarkerAndLine(route_xdata, route_ydata)
          self.pick_text.set_text('Pick end of interval!')
        else:
          self.pick_text.set_text('')
          start = meas_time[self.highlighted_section.start_idx]
          end = meas_time[data_index]
          self.onSetROI(start, end, 'g')
        show_legend = self.event_legend.get_visible()
        self.set_legend(show_legend)
    self.canvas.draw()
    return
  
  def on_figure_key_press(self, event):
    if event.key == 'f1':
      self.help.set_visible(not self.help.get_visible())
      self.resize_help()
    elif event.key == 'h':
      show_legend = self.event_legend.get_visible()
      self.event_legend.set_visible(not show_legend)
    elif event.key == 'q':
      self.copyContentToClipboard()
      self.nav_tools.set_message('Figure copied to clipboard')
    elif event.key == 'b':
      self.image_visible = not self.image_visible
      img = self.map_axis.images[-1]
      img.set_visible(self.image_visible)
    elif event.key == 't':
      if self.tick_format == 'coord':
        tick_format = 'meter'
        self.tickFormatMenu.actions()[1].setChecked(True)
      else:
        tick_format = 'coord'
        self.tickFormatMenu.actions()[0].setChecked(True)
      self.set_tick_format(tick_format)
    elif event.key in ['up', 'down']:
      measured_traj = self.get_measured_traj()
      meas_time = measured_traj.time
      loc_idx = np.searchsorted(meas_time, self.time)
      event_start_idxs = [[self.highlighted_section.start_idx] if self.highlighted_section.isSectionAvailable() else []]
      event_start_idxs += [traj_event.start_indices for traj_event in self.events]
      event_start_idxs = [idx_item for sublist in event_start_idxs for idx_item in sublist]
      if loc_idx not in event_start_idxs:
        event_start_idxs.append(loc_idx)
      event_start_idxs.sort()
      
      index = event_start_idxs.index(loc_idx)
      prev_idx = event_start_idxs[index - 1]
      next_idx = event_start_idxs[(index + 1) % len(event_start_idxs)]
      time = meas_time[prev_idx if event.key == 'down' else next_idx]
      self.seekSignal.signal.emit(time)
      self.seek(time)

    elif event.key == 'delete':
      if self.highlighted_section.selected or not self.events:
        self.onSetROI(0.0, 0.0, 'g')
      else:
        removable = []
        for idx, traj_event in enumerate(self.events):
          if traj_event.selected or len(self.events) == 1:
            traj_event.removeArtists()
            removable.append(idx)
        self.events = [traj_event for i, traj_event in enumerate(self.events) if i not in removable]
      self.remove_event_selection()
      show_legend = self.event_legend.get_visible()
      self.set_legend(show_legend)
    elif event.key == 'x':
      self.remove_event_selection()

    self.canvas.draw()
    return

  def on_motion(self, event):
    if self.playing:
      return
    elif self.show_veh_info and event.inaxes == self.map_axis:
      dist = np.sqrt(np.square(event.xdata - self.veh_pos.x) + np.square(event.ydata - self.veh_pos.y))
      if dist < 2:
        x_formatter = self.map_axis.xaxis.get_major_formatter()
        y_formatter = self.map_axis.yaxis.get_major_formatter()
        x_pos = x_formatter(self.veh_pos.x).replace(' ', '')
        y_pos = y_formatter(self.veh_pos.y).replace(' ', '')
        self.VehInfo.xy = (event.xdata, event.ydata)
        self.VehInfo.set_text("Vehicle position\nx=%s, y=%s" % (x_pos, y_pos))
        self.VehInfo.set_visible(True)
      else:
        self.VehInfo.set_visible(False)
    self.canvas.draw()
    return

  def on_figure_resize(self, event):
    self.resize_help()
    self.canvas.draw()
    return  
  
  def resizeEvent(self, event):
    self.on_figure_resize(event)
    return
  
  def keyPressEvent(self, event):
    self.canvas.keyPressEvent(event)
    return
  
  def keyReleaseEvent(self, event):
    self.canvas.keyReleaseEvent(event)
    return

  def drawRoadMap(self, **kwargs):
    if self.nav_tools.road_map is None:
      self.logger.warning("Can't draw roadmap on map")
      self.logger.info("Reason:\nNo available .osm file for roadmap visualization")
      return
    for road_line in self.nav_tools.road_map.road_lines:
      Lon, Lat = road_line.node_coordinates
      road_pix = self._convertGpsToPixCoords(Lon, Lat)
      self.road_map += self.map_axis.plot(road_pix.x, road_pix.y, **kwargs)
    return

  def redrawMarker(self):
    vertices = get_triangle_vertices((self.veh_pos.x, self.veh_pos.y), self.current_heading,
                                     x_factor=self.nav_tools.marker_x_factor, y_factor=self.nav_tools.marker_y_factor)
    self.veh_marker.set_xy(vertices)
    return

  def seekWindow(self):
    measured_traj = self.get_measured_traj()
    route_x_data = measured_traj.line.get_xdata()
    route_y_data = measured_traj.line.get_ydata()
    data_index = np.searchsorted(measured_traj.time, self.time)
    data_index = min(data_index, route_x_data.size - 1)
    data_index = min(data_index, route_y_data.size - 1)
    self.veh_pos.set_coords(route_x_data[data_index], route_y_data[data_index])
    if measured_traj.heading is not None:
      self.current_heading = measured_traj.heading[data_index]
      self.redrawMarker()
    else:
      self.veh_marker.set_offsets((route_x_data[data_index],
                                   route_y_data[data_index]))
    self.time_text.set_text("%.3f" % self.time)
    self.canvas.draw()
    return
  
  def start(self):
    self.map_axis.xaxis.set_major_formatter(
        LonDegreeFormatter(self.nav_tools.zoom_level,
                           self.nav_tools.map_orig_tile, (0, 0), self.nav_tools.map_bbox))
    self.map_axis.yaxis.set_major_formatter(
        LatDegreeFormatter(self.nav_tools.zoom_level,
                           self.nav_tools.map_orig_tile, (0, 0), self.nav_tools.map_bbox))
    for label in self.map_axis.xaxis.get_ticklabels():
      label.set_rotation(15)

    measured_traj = self.get_measured_traj()
    measured_traj.line.set_picker(5)
    route_xdata = measured_traj.line.get_xdata()
    route_ydata = measured_traj.line.get_ydata()
    if measured_traj.heading is not None:
      self.current_heading = measured_traj.heading[0]
      vertices = get_triangle_vertices((route_xdata[0], route_ydata[0]), measured_traj.heading[0],
                                       x_factor=self.nav_tools.marker_x_factor, y_factor=self.nav_tools.marker_y_factor)
      self.veh_marker = Polygon(vertices, closed=True, fill=True, color=self.route_color, zorder=50)
      self.map_axis.add_patch(self.veh_marker)
      # add the redraw callback to the backend
      self.nav_tools.redraw_marker = self.redrawMarker
    else:
      self.veh_marker = self.map_axis.scatter(route_xdata[0], route_ydata[0],
                                           s=self.route_marker_size,
                                           c=self.route_color,
                                           marker=self.route_marker_style,
                                           zorder=50)
    # self.veh_pos = (route_xdata[0], route_ydata[0])
    self.veh_pos.set_coords(route_xdata[0], route_ydata[0])

    self.drawRoadMap(linestyle='-', marker=None, color='black', linewidth=1, visible=self.show_road_map)

    self.set_legend()
    self.map_axis.imshow(self.nav_tools.map_image, origin="lower")
    mpl._pylab_helpers.Gcf.set_active(self.figure_manager)
    self.map_axis.set_xlim((0, self.nav_tools.map_image.size[0]))
    self.map_axis.set_ylim((0, self.nav_tools.map_image.size[1]))
    return


# TODO: create a new(?) utils package for visualization helper functions!!!
def get_triangle_vertices(center, heading, x_factor=1., y_factor=1.):
    heading_rad = np.deg2rad(heading)
    x_length = 2 * x_factor
    y_length = 1 * y_factor

    transformation_matrix = np.array([[np.cos(heading_rad), -np.sin(heading_rad), center[0]],
                                      [np.sin(heading_rad),  np.cos(heading_rad), center[1]],
                                      [0,                    0,                   1]])

    A_point = np.array([-x_length, -y_length, 1])
    B_point = np.array([x_length, 0, 1])
    C_point = np.array([-x_length, y_length, 1])

    transformed_A_point = transformation_matrix.dot(A_point)
    transformed_B_point = transformation_matrix.dot(B_point)
    transformed_C_point = transformation_matrix.dot(C_point)

    return np.array([transformed_A_point[:2], transformed_B_point[:2], transformed_C_point[:2]])
