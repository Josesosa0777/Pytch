"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright:
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial
  property. We reserve all rights of disposal such as copying and passing on to
  third parties.
"""
__docformat__ = "restructuredtext en"

from PIL import Image
from PySide import QtCore
import matplotlib as mpl
if mpl.rcParams['backend.qt4']!='PySide':
  mpl.use('Qt4Agg')
  mpl.rcParams['backend.qt4']='PySide'
import matplotlib.ticker as tkr
import numpy as np
import os
import logging
from matplotlib.collections import LineCollection

import measproc.MapTileCalculation as mtc
import measproc.mapbbox as mbox
from measparser.OsmParser import RoadMap

class MapNavigatorError(BaseException):
  pass

keyvald = {QtCore.Qt.Key_Control: 'control',
             QtCore.Qt.Key_Shift: 'shift',
             QtCore.Qt.Key_Alt: 'alt',
             QtCore.Qt.Key_Meta: 'super',
             QtCore.Qt.Key_Return: 'enter',
             QtCore.Qt.Key_Left: 'left',
             QtCore.Qt.Key_Up: 'up',
             QtCore.Qt.Key_Right: 'right',
             QtCore.Qt.Key_Down: 'down',
             QtCore.Qt.Key_Escape: 'escape',
             QtCore.Qt.Key_F1: 'f1',
             QtCore.Qt.Key_F2: 'f2',
             QtCore.Qt.Key_F3: 'f3',
             QtCore.Qt.Key_F4: 'f4',
             QtCore.Qt.Key_F5: 'f5',
             QtCore.Qt.Key_F6: 'f6',
             QtCore.Qt.Key_F7: 'f7',
             QtCore.Qt.Key_F8: 'f8',
             QtCore.Qt.Key_F9: 'f9',
             QtCore.Qt.Key_F10: 'f10',
             QtCore.Qt.Key_F11: 'f11',
             QtCore.Qt.Key_F12: 'f12',
             QtCore.Qt.Key_Home: 'home',
             QtCore.Qt.Key_End: 'end',
             QtCore.Qt.Key_PageUp: 'pageup',
             QtCore.Qt.Key_PageDown: 'pagedown',
             }  # keyvald definition is needed because matplotlib update!

# update the registerable keys with the delete key
key_dict = dict(keyvald)
key_dict.update({QtCore.Qt.Key_Delete : 'delete'})


class CanvasWithSpecButtonSensing(mpl.backends.backend_qt4agg.FigureCanvasQTAgg):
  keyvald = key_dict


class TickFormatter(tkr.Formatter):
  def __init__(self, zoom, map_orig_tile, crop_norm_value, map_bbox):
    self._zoom = zoom
    self._map_orig_tile = map_orig_tile
    self._map_bbox = map_bbox
    self._crop_norm_value_x, self._crop_norm_value_y = crop_norm_value
    return

  def get_conv_value(self, x):
    raise NotImplementedError()

  def __call__(self, x, pos=None):
    raise NotImplementedError()


class DegreeFormatter(TickFormatter):
  def __call__(self, x, pos=None):
    conv_value = self.get_conv_value(x)
    conv_value = round(conv_value, 10)
    conv_value = conv_value * 3600
    minutes = np.divide(conv_value, 60)
    seconds = np.fmod(conv_value, 60)
    degrees = np.divide(minutes, 60)
    minutes = np.fmod(minutes, 60)
    degrees = int(degrees)
    minutes = int(minutes)
    return u"%d\xb0 %d\' %.2f\'\'" % (degrees, minutes, seconds)


class LonDegreeFormatter(DegreeFormatter):
  def get_conv_value(self, x):
    pixel_input = mtc.Pixel(x + self._crop_norm_value_x, 0)
    x = self._map_orig_tile.unnorm_x_pixel(pixel_input)
    conv_value = mtc.Pixel.to_lon(x, self._zoom)
    return conv_value


class LatDegreeFormatter(DegreeFormatter):
  def get_conv_value(self, y):
    pixel_input = mtc.Pixel(0, y + self._crop_norm_value_y)
    y = self._map_orig_tile.unnorm_y_pixel(pixel_input)
    conv_value = mtc.Pixel.to_lat(y, self._zoom)
    return conv_value


class MeterFormatter(TickFormatter):
  def __call__(self, x, pos=None):
    return u"%.2f" % round(self.get_conv_value(x), 2)


class XFormatter(MeterFormatter):
  def get_conv_value(self, x):
    pixel_input = mtc.Pixel(x + self._crop_norm_value_x, 0)
    x = self._map_orig_tile.unnorm_x_pixel(pixel_input)
    conv_value_lon = mtc.Pixel.to_lon(x, self._zoom)
    # TODO: remove the low_left_coord2
    low_left_coord2, _ = self._map_orig_tile.to_coord_corners(self._zoom)
    low_left_coord = self._map_bbox.ll_corner
    x_coord = mtc.Coord(conv_value_lon, low_left_coord.lat)
    distance = mtc.get_distance_from_lat_lon(low_left_coord, x_coord)
    if conv_value_lon < low_left_coord.lon:
      distance *= -1
    return distance


class YFormatter(MeterFormatter):
  def get_conv_value(self, y):
    pixel_input = mtc.Pixel(0, y + self._crop_norm_value_y)
    y = self._map_orig_tile.unnorm_y_pixel(pixel_input)
    conv_value_lat = mtc.Pixel.to_lat(y, self._zoom)
    # TODO: remove the low_left_coord2
    low_left_coord2, _ = self._map_orig_tile.to_coord_corners(self._zoom)
    low_left_coord = self._map_bbox.ll_corner
    y_coord = mtc.Coord(low_left_coord.lon, conv_value_lat)
    distance = mtc.get_distance_from_lat_lon(low_left_coord, y_coord)
    if conv_value_lat < low_left_coord.lat:
      distance *= -1
    return distance


class NavigationTools(mpl.backends.backend_qt4agg.NavigationToolbar2QT):
  def __init__(self, canvas, parent, map_manager, map_axis, coord=True):
    mpl.backends.backend_qt4agg.NavigationToolbar2QT.__init__(\
        self, canvas, parent, coordinates=coord)
    if not os.path.exists(map_manager.map_db_loc):
      raise MapNavigatorError("Map database file (%s) does not exist!"
                              % map_manager.map_db_loc)
    if map_manager.osm_file and os.path.exists(map_manager.osm_file):
      self.road_map = RoadMap(map_manager.osm_file)
    else:
      self.road_map = None

    self.map_manager = map_manager
    self.zoom_level = None
    self.map_orig_tile = None
    self.crop_norm_value = None
    self.crop_bbox = None
    self.map_bbox = None
    self.map_axis = map_axis
    self.max_avail_zoom = 0
    self.min_avail_zoom = 0
    self.map_image = None
    self.prev_map_image = None
    self.route_time = None
    self.route_coords = None
    self.time = 0
    self.event_start_idx = 0
    self.event_interval = 0

    self.pan_started = False

    self.marker_x_factor = 2.
    self.marker_y_factor = 2.
    self.veh_pos = None
    self.redraw_marker = None

    self.x_tick_formatter = LonDegreeFormatter
    self.y_tick_formatter = LatDegreeFormatter
    return

  def set_tick_formatter(self, x_formatter, y_formatter):
    self.x_tick_formatter, self.y_tick_formatter = x_formatter, y_formatter
    self.draw()
    return

  def back(self, *args):
    """move back up the view lim stack"""
    self._views.back()
    self._positions.back()
    self.set_history_buttons()
    self.update_map_view()
    return

  def forward(self, *args):
    """Move forward in the view lim stack"""
    self._views.forward()
    self._positions.forward()
    self.set_history_buttons()
    self.update_map_view()
    return

  def home(self, *args):
    """Restore the original view"""
    self._views.home()
    self._positions.home()
    self.set_history_buttons()
    self.update_map_view()
    return

  def check_max_resolution(self, map_bbox, zoom, max_resolution):
    mapdb_metadata = self.map_manager.get_meta_data()
    tile_size = mapdb_metadata['tile_size']
    x_tile_count, y_tile_count = map_bbox.count_tiles(zoom)
    lower_than_max_res =\
        (x_tile_count * y_tile_count * tile_size**2) < max_resolution
    return lower_than_max_res

  def adjust_zoom_level(self, map_bbox, zoom, max_resolution=2073600):  # max_resolution = 1920*1080 by default
    if self.check_max_resolution(map_bbox, zoom, max_resolution):
      self.zoom_level = zoom
    else:
      logger = logging.getLogger()
      for new_zoom in xrange(int(zoom), 0, -1):
        if self.check_max_resolution(map_bbox, new_zoom, max_resolution):
          break
      self.zoom_level = new_zoom
      logger.info("Requested zoom level of %d would have produced a "
                  "map too large to handle and because of this it "
                  "was readjusted to be %d." % (zoom, new_zoom))
    return

  def init_map_drawing(self, map_bbox, check_zoom_in_db, zoom, max_resolution):
    # TODO: check why the db returns different values on zoom...
    # NOTE: because the mapbbox contains different zoom levels as the other parts of the world
    # TODO: update dynamically the max and min zoom in the area...
    zooms_in_db = self.map_manager.get_zooms_map_bbox(map_bbox)
    self.max_avail_zoom = zooms_in_db[-1]
    self.min_avail_zoom = zooms_in_db[0]

    if zoom is None:
      zoom = map_bbox.get_optimal_zoom(self.min_avail_zoom, self.max_avail_zoom)

    if check_zoom_in_db:
      zoom_idx = min(len(zooms_in_db) - 1, np.searchsorted(zooms_in_db, zoom))
      zoom = zooms_in_db[zoom_idx]

    self.adjust_zoom_level(map_bbox, zoom)

    # draw map image
    self.prev_map_image = self.map_image
    self.map_image, self.map_orig_tile =\
        self.map_manager.draw_map_image(map_bbox, self.zoom_level)

    self.crop_norm_value = (0, 0)
    self.crop_bbox = (0, 0, self.map_image.size[0], self.map_image.size[1])
    self.map_bbox = map_bbox

    self.map_image = self.map_image.transpose(Image.FLIP_TOP_BOTTOM)
    return

  def calc_crop_bbox(self):
    map_bbox_ll_pix = self.map_bbox.ll_corner.to_pixel(self.zoom_level)
    map_bbox_ur_pix = self.map_bbox.ur_corner.to_pixel(self.zoom_level)
    bbox_ll_pix = self.map_orig_tile.norm_pixel(map_bbox_ll_pix)
    bbox_ur_pix = self.map_orig_tile.norm_pixel(map_bbox_ur_pix)
    bbox_ll_x = int(bbox_ll_pix.x + 0.5)
    bbox_ll_y = int(bbox_ll_pix.y + 0.5)
    bbox_ur_x = int(bbox_ur_pix.x + 0.5)
    bbox_ur_y = int(bbox_ur_pix.y + 0.5)
    width = abs(bbox_ur_x - bbox_ll_x)
    height = abs(bbox_ur_y - bbox_ll_y)
    top = self.map_image.size[1] - bbox_ur_y
    left = bbox_ll_x
    crop_norm_value = (bbox_ll_pix.x, bbox_ll_pix.y)
    crop_bbox = (left, top, left + width, top + height)
    return crop_norm_value, crop_bbox

  @staticmethod
  def get_coords_from_pixel(pixel, crop_norm_value, zoom_level, map_orig_tile):
    crop_unnorm_x = np.ones_like(pixel.x) * crop_norm_value[0]
    crop_unnorm_y = np.ones_like(pixel.y) * crop_norm_value[1]
    pixel.x += crop_unnorm_x
    pixel.y += crop_unnorm_y
    pixel = map_orig_tile.unnorm_pixel(pixel)
    coords = pixel.to_coord(zoom_level)
    return coords

  @staticmethod
  def get_pixel_from_coords(coords, crop_norm_value, zoom_level, map_orig_tile):
    pixel = coords.to_pixel(zoom_level)
    pixel = map_orig_tile.norm_pixel(pixel)
    crop_norm_x = np.ones_like(pixel.x) * crop_norm_value[0]
    crop_norm_y = np.ones_like(pixel.y) * crop_norm_value[1]
    pixel.x -= crop_norm_x
    pixel.y -= crop_norm_y
    return pixel

  @staticmethod
  def readjust_pixels(x_data, y_data, old_crop_norm_value, old_zoom_level,
                      old_map_orig_tile, new_crop_norm_value,
                      new_zoom_level, new_map_orig_tile):
    old_pixel = mtc.Pixel(x_data, y_data)
    coords = NavigationTools.get_coords_from_pixel(old_pixel, old_crop_norm_value,
                                                   old_zoom_level, old_map_orig_tile)
    new_pixel = NavigationTools.get_pixel_from_coords(coords, new_crop_norm_value,
                                                      new_zoom_level, new_map_orig_tile)
    return new_pixel

  def readjust_lines_markers(self, old_crop_norm_value, old_zoom_level,
                             old_map_orig_tile, new_crop_norm_value,
                             new_zoom_level, new_map_orig_tile):
    # readjust lines
    for line in self.map_axis.lines:
      old_line_xdata = line.get_xdata(orig=False)
      old_line_ydata = line.get_ydata(orig=False)
      new_line_pixel = self.readjust_pixels(old_line_xdata, old_line_ydata,
                                            old_crop_norm_value, old_zoom_level,
                                            old_map_orig_tile, new_crop_norm_value,
                                            new_zoom_level, new_map_orig_tile)
      line.set_xdata(new_line_pixel.x)
      line.set_ydata(new_line_pixel.y)
    # readjust collections
    for marker in self.map_axis.collections:
      marker_offsets = marker.get_offsets()
      if not marker_offsets.size: continue

      # readjust linecollections
      if isinstance(marker, LineCollection):
        # https://matplotlib.org/examples/pylab_examples/multicolored_line.html
        segments = marker.get_segments()
        points = np.array(segments)
        pix_points = points[:, 0, :]
        # pix_points = np.append(pix_points, points[-1, 1, :])
        pix_points = np.vstack((pix_points, points[-1, 1, :]))
        segment_pix = self.readjust_pixels(pix_points[:, 0], pix_points[:, 1],
                                           old_crop_norm_value, old_zoom_level,
                                           old_map_orig_tile, new_crop_norm_value,
                                           new_zoom_level, new_map_orig_tile)

        points = np.array([segment_pix.x, segment_pix.y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        marker.set_segments(segments)
        continue


      old_marker_xdata, old_marker_ydata = zip(*marker_offsets)
      old_marker_xdata = np.array(old_marker_xdata)
      old_marker_ydata = np.array(old_marker_ydata)
      new_marker_pixel = self.readjust_pixels(old_marker_xdata, old_marker_ydata,
                                              old_crop_norm_value, old_zoom_level,
                                              old_map_orig_tile, new_crop_norm_value,
                                              new_zoom_level, new_map_orig_tile)

      new_marker_offset = (new_marker_pixel.x, new_marker_pixel.y)
      new_marker_offset = zip(*new_marker_offset)
      marker.set_offsets(new_marker_offset)

    # readjust the triangle marker
    if self.redraw_marker:
      prev_size = self.prev_map_image.size
      curr_size = self.map_image.size
      # calculate the new factor
      self.marker_x_factor *= (float(curr_size[0]) / float(prev_size[0]))
      self.marker_y_factor *= (float(curr_size[1]) / float(prev_size[1]))
      # readjust the vehicle position
      new_veh_pos_pix = self.readjust_pixels(self.veh_pos.x, self.veh_pos.y,
                                             old_crop_norm_value, old_zoom_level,
                                             old_map_orig_tile, new_crop_norm_value,
                                             new_zoom_level, new_map_orig_tile)
      self.veh_pos.set_coords(new_veh_pos_pix.x, new_veh_pos_pix.y)
      # redraw the triangle
      self.redraw_marker()
    return

  def update_map_image(self):
    im = self.map_axis.images[-1]
    is_visible = im.get_visible()
    self.map_axis.images.remove(im)
    self.map_image = self.map_image.transpose(Image.FLIP_TOP_BOTTOM)
    img = self.map_axis.imshow(self.map_image, origin="lower")
    img.autoscale()
    img.set_visible(is_visible)
    self.map_axis.set_xlim((0, self.map_image.size[0]))
    self.map_axis.set_ylim((0, self.map_image.size[1]))
    return

  def zoom(self, *args):
    """Activate zoom to rect mode"""
    if self._active == 'ZOOM':
      self._active = None
    else:
      self._active = 'ZOOM'

    if self._idPress is not None:
      self._idPress=self.canvas.mpl_disconnect(self._idPress)
      self.mode = ''

    if self._idRelease is not None:
      self._idRelease=self.canvas.mpl_disconnect(self._idRelease)
      self.mode = ''

    if  self._active:
      self._idPress = self.canvas.mpl_connect('button_press_event',
                                              self.press_zoom)
      self._idRelease = self.canvas.mpl_connect('button_release_event',
                                                self.release_zoom)
      self.mode = 'zoom rect'
      self.canvas.widgetlock(self)
    else:
      self.canvas.widgetlock.release(self)

    self.map_axis.set_navigate_mode(self._active)

    self.set_message(self.mode)
    self._update_buttons_checked()
    return

  def press_zoom(self, event):
    """the press mouse button in zoom to rect mode callback"""
    if event.button == 1:
      self._button_pressed = 1
    elif  event.button == 3:
      self._button_pressed = 3
    else:
      self._button_pressed=None
      return

    x, y = event.x, event.y

    # push the current view to define home if stack is empty
    if self._views.empty(): self.push_current()

    if (x is not None and y is not None and self.map_axis.in_axes(event)
        and self.map_axis.get_navigate() and self.map_axis.can_zoom()):
      self._xypress = (x, y, self.map_axis.viewLim.frozen(),
                       self.map_axis.transData.frozen())

    id1 = self.canvas.mpl_connect('motion_notify_event', self.drag_zoom)
    id2 = self.canvas.mpl_connect('key_press_event',
                                  self._switch_on_zoom_mode)
    id3 = self.canvas.mpl_connect('key_release_event',
                                  self._switch_off_zoom_mode)

    self._ids_zoom = [id1, id2, id3]
    self._zoom_mode = event.key

    self.press(event)
    return

  def drag_zoom(self, event):
    """the drag callback in zoom mode"""

    if not self._xypress: return

    x, y = event.x, event.y
    lastx, lasty, _, _ = self._xypress

    # adjust x, last, y, last
    x1, y1, x2, y2 = self.map_axis.bbox.extents
    x, lastx = max(min(x, lastx), x1), min(max(x, lastx), x2)
    y, lasty = max(min(y, lasty), y1), min(max(y, lasty), y2)

    if self._zoom_mode == "x":
      x1, y1, x2, y2 = self.map_axis.bbox.extents
      y, lasty = y1, y2
    elif self._zoom_mode == "y":
      x1, y1, x2, y2 = self.map_axis.bbox.extents
      x, lastx = x1, x2

    self.draw_rubberband(event, x, y, lastx, lasty)
    return

  def calc_map_bbox_and_zoom(self, button, nav_mode,
                             ll_pix_x, ll_pix_y, ur_pix_x, ur_pix_y):
    crop_norm_x, crop_norm_y = self.crop_norm_value
    ll_pixel = mtc.Pixel(ll_pix_x + crop_norm_x, ll_pix_y + crop_norm_y)
    ur_pixel = mtc.Pixel(ur_pix_x + crop_norm_x, ur_pix_y + crop_norm_y)
    ll_pixel = self.map_orig_tile.unnorm_pixel(ll_pixel)
    ur_pixel = self.map_orig_tile.unnorm_pixel(ur_pixel)
    ll_coord = ll_pixel.to_coord(self.zoom_level)
    ur_coord = ur_pixel.to_coord(self.zoom_level)
    self.map_bbox = mbox.MapBbox(ll_coord.lon, ll_coord.lat,
                                 ur_coord.lon, ur_coord.lat)

    x_pix_ratio = float(ur_pixel.x - ll_pixel.x) / self.map_image.size[0]
    y_pix_ratio = float(ur_pixel.y - ll_pixel.y) / self.map_image.size[1]
    pix_area_ratio = x_pix_ratio * y_pix_ratio
    zoom_x_modif = np.abs(np.log(1 / x_pix_ratio) / np.log(2))
    zoom_y_modif = np.abs(np.log(1 / y_pix_ratio) / np.log(2))
    zoom_modif = int((max(zoom_x_modif, zoom_y_modif)) + 0.5)

    # readjust max and min available zoom according to the current tile
    # because the tiles may contain different zoom levels
    zooms_in_db = self.map_manager.get_zooms_map_bbox(self.map_bbox)
    self.min_avail_zoom = zooms_in_db[0]
    self.max_avail_zoom = zooms_in_db[-1]

    if nav_mode == 'ZOOM' or (nav_mode == 'PAN' and button == 3):
      if pix_area_ratio < 0.75:
        self.zoom_level = min(self.zoom_level + zoom_modif, self.max_avail_zoom)
      elif pix_area_ratio > 1.25:
        self.zoom_level = max(self.zoom_level - zoom_modif, self.min_avail_zoom)

    self.adjust_zoom_level(self.map_bbox, self.zoom_level)

    if ll_coord.lat <= -90.0 or ur_coord.lat >= 90.0:
      raise MapNavigatorError
    return

  @staticmethod
  def sort_last(v_min, v_max, v, v_last):
    vs = [v, v_last]
    reverse = v_min > v_max
    vs.sort(reverse=reverse)
    v_start, v_end = vs
    if reverse:
      v_start = min(v_min, v_start)
      v_end = max(v_max, v_end)
    else:
      v_start = max(v_min, v_start)
      v_end  = min(v_max, v_end)
    return v_start, v_end

  def release_zoom(self, event):
    """the release mouse button callback in zoom to rect mode"""
    while self._ids_zoom:
      self.canvas.mpl_disconnect(self._ids_zoom.pop())

    if not self._xypress: return

    x, y = event.x, event.y
    lastx, lasty, _, _ = self._xypress
    # ignore singular clicks - 5 pixels is a threshold
    if abs(x - lastx) < 5 or abs(y - lasty) < 5:
      self._xypress = None
      self.release(event)
      self.draw()
      return

    # zoom to rect
    inverse = self.map_axis.transData.inverted()
    lastx, lasty = inverse.transform_point( (lastx, lasty) )
    x, y = inverse.transform_point( (x, y) )
    Xmin, Xmax = self.map_axis.get_xlim()
    Ymin, Ymax = self.map_axis.get_ylim()

    x0, x1 = self.sort_last(Xmin, Xmax, x, lastx)
    y0, y1 = self.sort_last(Ymin, Ymax, y, lasty)

    if self._button_pressed == 1:
      if self._zoom_mode == 'x':
        y0 = Ymin
        y1 = Ymax
      elif self._zoom_mode == 'y':
        x0 = Xmin
        x1 = Xmax
    elif self._button_pressed == 3:
      alpha = (Xmax - Xmin) / (x1 - x0)
      rx1 = alpha * (Xmin - x0) + Xmin
      rx2 = alpha * (Xmax - x0) + Xmin
      alpha = (Ymax - Ymin) / (y1 - y0)
      ry1 = alpha * (Ymin - y0) + Ymin
      ry2 = alpha * (Ymax - y0) + Ymin
      if self._zoom_mode == 'x':
        x0 = rx1
        x1 = rx2
        y0 = Ymin
        y1 = Ymax
      elif self._zoom_mode == 'y':
        x0 = Xmin
        x1 = Xmax
        y0 = ry1
        y1 = ry2
      else:
        x0 = rx1
        x1 = rx2
        y0 = ry1
        y1 = ry2

    old_crop_norm_value = self.crop_norm_value
    old_zoom_level = self.zoom_level
    old_map_orig_tile = self.map_orig_tile
    old_map_bbox = self.map_bbox

    try:
      self.calc_map_bbox_and_zoom(event.button, 'ZOOM', x0, y0, x1, y1)
    except MapNavigatorError:
      logger = logging.getLogger()
      logger.warning("There are not available tiles at the requested zoom level of %d "
                     "therefore the zoom request failed!" % self.zoom_level)
      self.zoom_level = old_zoom_level
      self.map_bbox = old_map_bbox
      self.draw()
    else:
      self.prev_map_image = self.map_image
      self.map_image, self.map_orig_tile =\
          self.map_manager.draw_map_image(self.map_bbox, self.zoom_level)
      self.crop_norm_value, self.crop_bbox = self.calc_crop_bbox()
      self.map_image = self.map_image.crop(self.crop_bbox)
      self.update_map_image()
      self.readjust_lines_markers(old_crop_norm_value, old_zoom_level,
                                  old_map_orig_tile, self.crop_norm_value,
                                  self.zoom_level, self.map_orig_tile)
      self.draw()
      self.push_current()

    self._xypress = None
    self._button_pressed = None
    self._zoom_mode = None

    self.release(event)

  def pan(self, *args):
    """Activate the pan/zoom tool. pan with left button, zoom with right"""
    # set the pointer icon and button press funcs to the
    # appropriate callbacks

    if self._active == 'PAN':
      self._active = None
    else:
      self._active = 'PAN'
    if self._idPress is not None:
      self._idPress = self.canvas.mpl_disconnect(self._idPress)
      self.mode = ''

    if self._idRelease is not None:
      self._idRelease = self.canvas.mpl_disconnect(self._idRelease)
      self.mode = ''

    if self._active:
      self._idPress = self.canvas.mpl_connect('button_press_event',
                                              self.press_pan)
      self._idRelease = self.canvas.mpl_connect('button_release_event',
                                                self.release_pan)
      self.mode = 'pan/zoom'
      self.canvas.widgetlock(self)
    else:
      self.canvas.widgetlock.release(self)

    self.map_axis.set_navigate_mode(self._active)

    self.set_message(self.mode)
    self._update_buttons_checked()
    return

  def press_pan(self, event):
    """the press mouse button in pan/zoom mode callback"""

    if event.button == 1:
      self._button_pressed = 1
    elif  event.button == 3:
      self._button_pressed = 3
    else:
      self._button_pressed = None
      return

    x, y = event.x, event.y

    # push the current view to define home if stack is empty
    if self._views.empty(): self.push_current()

    if (x is not None and y is not None and self.map_axis.in_axes(event)
        and self.map_axis.get_navigate() and self.map_axis.can_pan()):
      self.map_axis.start_pan(x, y, event.button)
      self.canvas.mpl_disconnect(self._idDrag)
      self._idDrag=self.canvas.mpl_connect('motion_notify_event',
                                           self.drag_pan)
      self.pan_started = True

    self.press(event)
    return

  def drag_pan(self, event):
    """the drag callback in pan/zoom mode"""
    #safer to use the recorded button at the press than current button:
    #multiple button can get pressed during motion...
    self.map_axis.drag_pan(self._button_pressed, event.key, event.x, event.y)
    self.dynamic_update()
    return

  def release_pan(self, event):
    """the release mouse button callback in pan/zoom mode"""
    if self._button_pressed is None or not self.pan_started: return
    old_crop_norm_value = self.crop_norm_value
    old_zoom_level = self.zoom_level
    old_map_orig_tile = self.map_orig_tile

    self.canvas.mpl_disconnect(self._idDrag)
    self._idDrag = self.canvas.mpl_connect('motion_notify_event',
                                           self.mouse_move)
    self.map_axis.end_pan()
    x0, y0, width, height = self.map_axis.viewLim.bounds
    x1 = x0 + width
    y1 = y0 + height
    self.calc_map_bbox_and_zoom(self._button_pressed, 'PAN', x0, y0, x1, y1)
    self.prev_map_image = self.map_image
    self.map_image, self.map_orig_tile =\
        self.map_manager.draw_map_image(self.map_bbox, self.zoom_level)
    self.crop_norm_value, self.crop_bbox = self.calc_crop_bbox()
    self.map_image = self.map_image.crop(self.crop_bbox)
    self.update_map_image()
    self.readjust_lines_markers(old_crop_norm_value, old_zoom_level,
                                old_map_orig_tile, self.crop_norm_value,
                                self.zoom_level, self.map_orig_tile)
    self._button_pressed = None
    self.pan_started = False
    self.push_current()
    self.release(event)
    self.draw()

  def draw(self):
    """Redraw the canvases, update the locators, set formaters"""
    for a in self.canvas.figure.get_axes():
      xaxis = getattr(a, 'xaxis', None)
      yaxis = getattr(a, 'yaxis', None)
      locators = []
      if xaxis is not None:
        locators.append(xaxis.get_major_locator())
        locators.append(xaxis.get_minor_locator())
        xaxis.set_major_formatter(
            self.x_tick_formatter(self.zoom_level, self.map_orig_tile,
                                  self.crop_norm_value, self.map_bbox))
      if yaxis is not None:
        locators.append(yaxis.get_major_locator())
        locators.append(yaxis.get_minor_locator())
        yaxis.set_major_formatter(
            self.y_tick_formatter(self.zoom_level, self.map_orig_tile,
                                  self.crop_norm_value, self.map_bbox))

      for loc in locators:
        loc.refresh()
    self.canvas.draw()
    return

  def update_map_view(self):
    """Update the viewlim and position from the view and position stack for
    each axes
    """
    map_data = self._views()
    if map_data is None:  return
    pos = self._positions()
    if pos is None: return

    old_crop_norm_value = self.crop_norm_value
    old_zoom_level = self.zoom_level
    old_map_orig_tile = self.map_orig_tile
    self.map_bbox, self.crop_bbox, self.crop_norm_value, self.zoom_level = map_data
    self.prev_map_image = self.map_image
    self.map_image, self.map_orig_tile =\
        self.map_manager.draw_map_image(self.map_bbox, self.zoom_level)
    self.map_image = self.map_image.crop(self.crop_bbox)
    self.update_map_image()
    self.readjust_lines_markers(old_crop_norm_value, old_zoom_level,
                                old_map_orig_tile, self.crop_norm_value,
                                self.zoom_level, self.map_orig_tile)

    self.map_axis.set_position(pos[0], 'original')
    self.map_axis.set_position(pos[1], 'active')
    self.draw()
    return

  def push_current(self):
    """push the current view limits and position onto the stack"""
    map_data = (self.map_bbox, self.crop_bbox,
                self.crop_norm_value, self.zoom_level)
    self._views.push(map_data)
    pos = (self.map_axis.get_position(True).frozen(),
           self.map_axis.get_position().frozen())
    self._positions.push(pos)
    self.set_history_buttons()
    return
