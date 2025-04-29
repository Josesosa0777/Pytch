import numpy
import os
import scipy.optimize as optim

import MapTileCalculation as mtc
from .relations import greater_equal, less_equal

class MapBbox(object):
  def __init__(self, min_lon, min_lat, max_lon, max_lat):
    self.ll_corner = mtc.Coord(min_lon, min_lat)
    self.ur_corner = mtc.Coord(max_lon, max_lat)
    return
  
  def __iter__(self):
    yield self.ll_corner
    yield self.ur_corner
  
  def __eq__(self, other):
    min_eq = self.ll_corner == other.ll_corner
    max_eq = self.ur_corner == other.ur_corner
    return min_eq and max_eq
  
  def to_mbtiles_mrc_line(self):
    bound = "%f,%f,%f,%f" % (self.ll_corner.lon, self.ll_corner.lat,
                             self.ur_corner.lon, self.ur_corner.lat)
    return bound
  
  def to_osm_mrc_line(self, osm_api_url, pixel_res=4.0):
    # zoom level for a resolution of 4.0 m/pixel
    zoom_level_4_data = mtc.zoom_for_pixel_resolution(pixel_res)
    tile_locs = self.get_tile_locs(zoom_level_4_data)
    x_tiles, y_tiles = zip(*tile_locs)
    ll_corner = mtc.Tile(min(x_tiles), min(y_tiles))
    # upper right corner tends to draw towards lower left corner in the map
    # tile calculation algorithm
    ur_corner = mtc.Tile(max(x_tiles) + 1, max(y_tiles) + 1)
    ll_corner_coord, _ = ll_corner.to_coord_corners(zoom_level_4_data)
    _, ur_corner_coord = ur_corner.to_coord_corners(zoom_level_4_data)
    bound = {'min_lon': ll_corner_coord.lon, 'min_lat': ll_corner_coord.lat,
             'max_lon': ur_corner_coord.lon, 'max_lat': ur_corner_coord.lat}
    mrc_line = osm_api_url % bound
    return mrc_line
  
  def to_file_name(self,  prefix='', suffix=''):
    bound = "%f,%f,%f,%f" % (self.ll_corner.lon, self.ll_corner.lat,
                             self.ur_corner.lon, self.ur_corner.lat)
    file_name = prefix + '_' + bound + suffix
    return file_name
  
  @classmethod
  def from_workspace(cls, workspace):
    Longitude = workspace.workspace['Longitude']
    Latitude = workspace.workspace['Latitude']
    Longitude = Longitude.flatten()
    Latitude = Latitude.flatten()
    mask = numpy.logical_and(Latitude != 0.0, Longitude != 0.0)
    Longitude = Longitude[mask]
    Latitude = Latitude[mask]
    if not (len(Longitude) and len(Latitude)): return
    min_lon = numpy.min(Longitude)
    min_lat = numpy.min(Latitude)
    max_lon = numpy.max(Longitude)
    max_lat = numpy.max(Latitude)
    self = cls(min_lon, min_lat, max_lon, max_lat)
    return self
  
  @classmethod
  def from_mapbboxes(cls, map_bboxes):
    ll_corners, ur_corners = zip(*map_bboxes)
    min_lons, min_lats = zip(*ll_corners)
    max_lons, max_lats = zip(*ur_corners)
    min_lon = min(min_lons)
    min_lat = min(min_lats)
    max_lon = max(max_lons)
    max_lat = max(max_lats)
    self = cls(min_lon, min_lat, max_lon, max_lat)
    return self
  
  @classmethod
  def from_osm_name(cls, osm_file):
    file_name = os.path.splitext(osm_file)[0]
    bounding_box = file_name.split('_')[-1]
    min_lon, min_lat, max_lon, max_lat =\
        [float(coord) for coord in bounding_box.split(',')]
    self = cls(min_lon, min_lat, max_lon, max_lat)
    return self
  
  def __contains__(self, other):
    if isinstance(other, MapBbox):
      osm_bound_min = numpy.array([other.ll_corner.lon, other.ll_corner.lat])
      osm_bound_max = numpy.array([other.ur_corner.lon, other.ur_corner.lat])
      map_bbox_min = numpy.array([self.ll_corner.lon, self.ll_corner.lat])
      map_bbox_max = numpy.array([self.ur_corner.lon, self.ur_corner.lat])
      osm_leq_bbox = less_equal(map_bbox_min, osm_bound_min)
      osm_geq_bbox = greater_equal(map_bbox_max, osm_bound_max)
      bbox_contains = numpy.logical_and(osm_leq_bbox, osm_geq_bbox)
      return numpy.all(bbox_contains)
    else:
      return False
  
  def limit_max_zoom_level(self, min_zoom_level, max_zoom_level,
                           max_map_resolution=30000000):
    """
    If called this method limits the value of maximum zoom level if needed so
    that the resolution of the map will not be greater than `max_map_resolution`
    on that particular zoom level. The default value of `max_map_resolution` is
    30 MPixels.
    """
    max_tile_cnt = max_map_resolution / (mtc.TILE_SIZE**2)
    for zoom_level in xrange(max_zoom_level, min_zoom_level, -1):
      x_tile_count, y_tile_count = self.count_tiles(zoom_level)
      if max_tile_cnt > x_tile_count * y_tile_count:
        break
    return zoom_level
  
  def get_tile_locs(self, zoom, spec='TMS'):
    """
    Determine the tiles that can occur in a map bounding box.
    """
    ll_tile = self.ll_corner.to_tile(zoom, spec=spec)
    ur_tile = self.ur_corner.to_tile(zoom, spec=spec)
    tile_locs = []
    for tile_y in range(ll_tile.y, ur_tile.y + 1, 1):
      for tile_x in range(ll_tile.x, ur_tile.x + 1, 1):
        tile_locs.append((tile_x, tile_y))
    return tile_locs
  
  def count_tiles(self, zoom, spec='TMS'):
    """
    Count the number of tiles (horizontal and vertical) that cover the map
    bounding box.
    """
    ll_tile = self.ll_corner.to_tile(zoom, spec=spec)
    ur_tile = self.ur_corner.to_tile(zoom, spec=spec)
    x_tile_count = numpy.abs(ur_tile.x - ll_tile.x) + 1
    y_tile_count = numpy.abs(ur_tile.y - ll_tile.y) + 1
    return x_tile_count, y_tile_count
  
  def get_optimal_zoom(self, min_zoom, max_zoom, spec='TMS'):
    """
    Determine the optimal zoom level for a map bounding box at which
    useful map region is maximal and tile count (actual map resolution) is
    minimal.
    """
    def objective_func(zoom, map_bbox, spec):
      zoom = round(zoom)
      ll_tile = map_bbox.ll_corner.to_tile(zoom, spec=spec)
      ur_tile = map_bbox.ur_corner.to_tile(zoom, spec=spec)
      ll_coord = ll_tile.to_coord_corners(zoom)[0]
      ur_coord = ur_tile.to_coord_corners(zoom)[1]
      coord_lon_diff = numpy.abs(map_bbox.ur_corner.lon -
                                 map_bbox.ll_corner.lon)
      coord_lat_diff = numpy.abs(map_bbox.ur_corner.lat -
                                 map_bbox.ll_corner.lat)
      tile_lon_diff = numpy.abs(ur_coord.lon - ll_coord.lon)
      tile_lat_diff = numpy.abs(ur_coord.lat - ll_coord.lat)
      ratio = ((tile_lon_diff * tile_lat_diff) /
               (coord_lon_diff * coord_lat_diff))
      x_tile_cnt, y_tile_cnt = map_bbox.count_tiles(zoom, spec=spec)
      tile_cnt = x_tile_cnt * y_tile_cnt
      obj_func_val = ratio + tile_cnt
      return obj_func_val
    optim_zoom = optim.fminbound(objective_func, min_zoom, max_zoom,
                                 args=(self, spec), xtol=1)
    optim_zoom = round(optim_zoom)
    return optim_zoom
