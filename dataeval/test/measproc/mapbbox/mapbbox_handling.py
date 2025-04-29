import unittest
import numpy as np
import os

import measproc.mapbbox as mbox
import measproc.MapTileCalculation as mtc
from measproc.workspace import DinWorkSpace
from measproc.GenMaperitiveScripts import OSM_API_TEMPLATES


class SetUpMapBBoxTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    lons0 = np.linspace(8.0, 8.2, 10)
    lats0 = np.linspace(49.0, 49.2, 10)
    lons1 = np.linspace(7.9, 8.3, 10)
    lats1 = np.linspace(48.9, 49.3, 10)
    lons2 = np.linspace(8.06, 8.14, 10)
    lats2 = np.linspace(49.06, 49.14, 10)
    lons3 = np.linspace(8.00008, 8.20008, 10)
    lats3 = np.linspace(49.00049, 49.20049, 10)
    lons4 = np.linspace(8.0, 8.2, 10)
    lats4 = np.linspace(49.0, 49.2, 10)
    times = np.linspace(0, 100, 10)
    ws_datas = [{'Longitude': lons0, 'Latitude': lats0, 'Time': times},
                {'Longitude': lons1, 'Latitude': lats1, 'Time': times},
                {'Longitude': lons2, 'Latitude': lats2, 'Time': times},
                {'Longitude': lons3, 'Latitude': lats3, 'Time': times},
                {'Longitude': lons4, 'Latitude': lats4, 'Time': times}]
    
    cls.workspaces = []
    cls.osm_names = []
    for idx, ws_data in enumerate(ws_datas):
      title = 'map_bbox_handling_test_%s' % idx
      workspace = DinWorkSpace(title)
      workspace.add(**ws_data)
      cls.workspaces.append(workspace)
      lon_min = np.min(ws_data['Longitude'])
      lat_min = np.min(ws_data['Latitude'])
      lon_max = np.max(ws_data['Longitude'])
      lat_max = np.max(ws_data['Latitude'])
      cls.osm_names.append(r'C:\KBData\map_bbox_handling_test_%f,%f,%f,%f.osm' %
                           (lon_min, lat_min, lon_max, lat_max))
    cls.min_zoom_level = 7
    cls.max_zoom_level = 17
    cls.max_map_resolution = 30000000
    cls.spec = 'TMS'
    return
  
  @classmethod
  def tearDownClass(cls):
    for workspace in cls.workspaces:
      os.remove(workspace.PathToSave)
    return

class MapBBoxTest(SetUpMapBBoxTest):
  @staticmethod
  def get_corner_coords_from_workspace(workspace):
    lon_min = np.min(workspace.workspace['Longitude'])
    lat_min = np.min(workspace.workspace['Latitude'])
    lon_max = np.max(workspace.workspace['Longitude'])
    lat_max = np.max(workspace.workspace['Latitude'])
    ll_crnr_coord = mtc.Coord(lon_min, lat_min)
    ur_crnr_coord = mtc.Coord(lon_max, lat_max)
    return ll_crnr_coord, ur_crnr_coord
  
  def test_mapbbox_from_workspace(self):
    map_bbox_4_test = mbox.MapBbox.from_workspace(self.workspaces[0])
    is_map_bbox = isinstance(map_bbox_4_test, mbox.MapBbox)
    lon_min = np.min(self.workspaces[0].workspace['Longitude'])
    lat_min = np.min(self.workspaces[0].workspace['Latitude'])
    lon_max = np.max(self.workspaces[0].workspace['Longitude'])
    lat_max = np.max(self.workspaces[0].workspace['Latitude'])
    is_equal = (map_bbox_4_test.ll_corner.lon == lon_min
                and map_bbox_4_test.ll_corner.lat == lat_min
                and map_bbox_4_test.ur_corner.lon == lon_max
                and map_bbox_4_test.ur_corner.lat == lat_max)
    self.assertTrue(is_map_bbox and is_equal)
    return
  
  def test_map_bbox_from_mapbboxes(self):
    map_bboxes = []
    lons = []
    lats = []
    for workspace in self.workspaces:
      map_bboxes.append(mbox.MapBbox.from_workspace(workspace))
      lons.append(workspace.workspace['Longitude'])
      lats.append(workspace.workspace['Latitude'])
    map_bbox_4_test = mbox.MapBbox.from_mapbboxes(map_bboxes)
    is_map_bbox = isinstance(map_bbox_4_test, mbox.MapBbox)
    lon_min = np.concatenate(lons).min()
    lat_min = np.concatenate(lats).min()
    lon_max = np.concatenate(lons).max()
    lat_max = np.concatenate(lats).max()
    is_equal = (map_bbox_4_test.ll_corner.lon == lon_min
                and map_bbox_4_test.ll_corner.lat == lat_min
                and map_bbox_4_test.ur_corner.lon == lon_max
                and map_bbox_4_test.ur_corner.lat == lat_max)
    self.assertTrue(is_map_bbox and is_equal)
    return
  
  def test_map_bbox_from_osm_name(self):
    map_bbox_4_test = mbox.MapBbox.from_osm_name(self.osm_names[0])
    map_bbox_ref = mbox.MapBbox.from_workspace(self.workspaces[0])
    is_map_bbox = isinstance(map_bbox_4_test, mbox.MapBbox)
    is_equal = map_bbox_4_test == map_bbox_ref
    self.assertTrue(is_map_bbox and is_equal)
    return
  
  def test_map_bbox_iter(self):
    map_bbox_4_test = mbox.MapBbox.from_workspace(self.workspaces[0])
    try:
      iter(map_bbox_4_test)
    except TypeError:
      self.assertTrue(False)
    else:
      self.assertTrue(True)
    return
  
  def test_map_bbox_eq(self):
    map_bbox_a = mbox.MapBbox.from_workspace(self.workspaces[0])
    map_bbox_b = mbox.MapBbox.from_workspace(self.workspaces[4])
    self.assertEqual(map_bbox_a, map_bbox_b)
    return
  
  def test_map_bbox_eq_with_small_diff(self):
    map_bbox_a = mbox.MapBbox.from_workspace(self.workspaces[0])
    map_bbox_b = mbox.MapBbox.from_workspace(self.workspaces[3])
    self.assertEqual(map_bbox_a, map_bbox_b)
    return
  
  def test_map_bbox_to_osm_mrc_line(self):
    api_template = OSM_API_TEMPLATES['open.mapquestapi.com']
    map_bbox_4_test = mbox.MapBbox.from_workspace(self.workspaces[0])
    mrc_line = map_bbox_4_test.to_osm_mrc_line(api_template)
    api_mrc_line = mrc_line.split('=')[0]
    bound_mrc_line = mrc_line.split('=')[-1][:-1]
    bound_mrc_line = [float(bound) for bound in bound_mrc_line.split(',')]
    map_bbox_mrc_line = mbox.MapBbox(*bound_mrc_line)
    lon_min = np.min(self.workspaces[0].workspace['Longitude'])
    lat_min = np.min(self.workspaces[0].workspace['Latitude'])
    lon_max = np.max(self.workspaces[0].workspace['Longitude'])
    lat_max = np.max(self.workspaces[0].workspace['Latitude'])
    bound = [lon_min, lat_min, lon_max, lat_max]
    map_bbox_bound = mbox.MapBbox(*bound)
    api_mrc_line_ref = api_template.split('=')[0]
    api_is_OK = api_mrc_line == api_mrc_line_ref
    map_bbox_is_OK = map_bbox_bound in map_bbox_mrc_line
    self.assertTrue(api_is_OK and map_bbox_is_OK)
    return
  
  def test_map_bbox_to_mbtiles_mrc_line(self):
    map_bbox_4_test = mbox.MapBbox.from_workspace(self.workspaces[0])
    mrc_line = map_bbox_4_test.to_mbtiles_mrc_line()
    lon_min = np.min(self.workspaces[0].workspace['Longitude'])
    lat_min = np.min(self.workspaces[0].workspace['Latitude'])
    lon_max = np.max(self.workspaces[0].workspace['Longitude'])
    lat_max = np.max(self.workspaces[0].workspace['Latitude'])
    mrc_line_ref = "%f,%f,%f,%f" % (lon_min, lat_min, lon_max, lat_max)
    self.assertEqual(mrc_line, mrc_line_ref)
    return
  
  def test_map_bbox_to_file_name(self):
    map_bbox = mbox.MapBbox.from_workspace(self.workspaces[0])
    prefix = os.path.splitext(self.workspaces[0].PathToSave)[0]
    suffix = '.mbtiles'
    fname = map_bbox.to_file_name(prefix, suffix)
    lon_min = np.min(self.workspaces[0].workspace['Longitude'])
    lat_min = np.min(self.workspaces[0].workspace['Latitude'])
    lon_max = np.max(self.workspaces[0].workspace['Longitude'])
    lat_max = np.max(self.workspaces[0].workspace['Latitude'])
    bound = "%f,%f,%f,%f" % (lon_min, lat_min, lon_max, lat_max)
    fname_ref = prefix + '_' + bound  + suffix
    self.assertEqual(fname, fname_ref)
    return
  
  def test_map_bbox_contains(self):
    map_bbox = mbox.MapBbox.from_workspace(self.workspaces[0])
    smaller_map_bbox = mbox.MapBbox.from_workspace(self.workspaces[2])
    self.assertTrue(smaller_map_bbox in map_bbox)
    return
  
  def test_map_bbox_not_contains(self):
    map_bbox = mbox.MapBbox.from_workspace(self.workspaces[0])
    larger_map_bbox = mbox.MapBbox.from_workspace(self.workspaces[1])
    self.assertFalse(larger_map_bbox in map_bbox)
    return
  
  def test_map_bbox_limit_max_zoom_level(self):
    map_bbox = mbox.MapBbox.from_workspace(self.workspaces[0])
    limited_zoom =\
        map_bbox.limit_max_zoom_level(self.min_zoom_level, self.max_zoom_level,
                                      max_map_resolution=self.max_map_resolution)
    x_tile_count, y_tile_count = map_bbox.count_tiles(limited_zoom,
                                                      spec=self.spec)
    pixel_count_in_map_bbox = x_tile_count * y_tile_count * mtc.TILE_SIZE**2
    self.assertLessEqual(pixel_count_in_map_bbox, self.max_map_resolution)
    return
  
  def test_map_bbox_get_tile_locs(self):
    map_bbox = mbox.MapBbox.from_workspace(self.workspaces[0])
    tile_locs = map_bbox.get_tile_locs(self.max_zoom_level, spec=self.spec)
    x_tiles, y_tiles = zip(*tile_locs)
    x_tiles = list(set(x_tiles))
    x_tiles.sort()
    x_tiles = np.array(x_tiles)
    y_tiles = list(set(y_tiles))
    y_tiles.sort()
    y_tiles = np.array(y_tiles)
    ll_crnr_coord, ur_crnr_coord =\
        self.get_corner_coords_from_workspace(self.workspaces[0])
    ll_tile = ll_crnr_coord.to_tile(self.max_zoom_level, spec=self.spec)
    ur_tile = ur_crnr_coord.to_tile(self.max_zoom_level, spec=self.spec)
    x_tiles_ref = np.array(range(ll_tile.x, ur_tile.x + 1, 1))
    y_tiles_ref = np.array(range(ll_tile.y, ur_tile.y + 1, 1))
    if len(x_tiles) == len(x_tiles_ref) and len(y_tiles) == len(y_tiles_ref):
      if np.all(x_tiles == x_tiles_ref) and np.all(y_tiles == y_tiles_ref):
        self.assertTrue(True)
      else:
        self.assertTrue(False)
    else:
      self.assertTrue(False)
    return
  
  def test_map_bbox_count_tiles(self):
    map_bbox = mbox.MapBbox.from_workspace(self.workspaces[0])
    x_tile_count, y_tile_count = map_bbox.count_tiles(self.max_zoom_level,
                                                      spec=self.spec)
    ll_crnr_coord, ur_crnr_coord =\
        self.get_corner_coords_from_workspace(self.workspaces[0])
    ll_tile = ll_crnr_coord.to_tile(self.max_zoom_level, spec=self.spec)
    ur_tile = ur_crnr_coord.to_tile(self.max_zoom_level, spec=self.spec)
    x_tile_count_ref = np.abs(ur_tile.x - ll_tile.x) + 1
    y_tile_count_ref = np.abs(ur_tile.y - ll_tile.y) + 1
    x_tile_count_eq = x_tile_count == x_tile_count_ref
    y_tile_count_eq = y_tile_count == y_tile_count_ref
    self.assertTrue(x_tile_count_eq and y_tile_count_eq)
    return
  
  def test_map_bbox_get_optimal_zoom(self):
    map_bbox = mbox.MapBbox.from_workspace(self.workspaces[0])
    optimal_zoom = map_bbox.get_optimal_zoom(self.min_zoom_level,
                                             self.max_zoom_level,
                                             spec=self.spec)
    ll_corner, ur_corner =\
        self.get_corner_coords_from_workspace(self.workspaces[0])
    obj_func_val = []
    for zoom in xrange(self.min_zoom_level, self.max_zoom_level + 1, 1):
      ll_tile = ll_corner.to_tile(zoom, spec=self.spec)
      ur_tile = ur_corner.to_tile(zoom, spec=self.spec)
      ll_coord = ll_tile.to_coord_corners(zoom)[0]
      ur_coord = ur_tile.to_coord_corners(zoom)[1]
      coord_lon_diff = np.abs(ur_corner.lon - ll_corner.lon)
      coord_lat_diff = np.abs(ur_corner.lat - ll_corner.lat)
      tile_lon_diff = np.abs(ur_coord.lon - ll_coord.lon)
      tile_lat_diff = np.abs(ur_coord.lat - ll_coord.lat)
      ratio = ((tile_lon_diff * tile_lat_diff) /
               (coord_lon_diff * coord_lat_diff))
      x_tile_cnt = np.abs(ur_tile.x - ll_tile.x) + 1
      y_tile_cnt = np.abs(ur_tile.y - ll_tile.y) + 1
      tile_cnt = x_tile_cnt * y_tile_cnt
      obj_func_val.append(ratio + tile_cnt)
    obj_func_val_min = min(obj_func_val)
    optimal_zoom_ref_idx = obj_func_val.index(obj_func_val_min)
    optimal_zoom_ref = range(self.min_zoom_level, self.max_zoom_level + 1, 1)
    optimal_zoom_ref = optimal_zoom_ref[optimal_zoom_ref_idx]
    self.assertTrue(optimal_zoom == optimal_zoom_ref)
    return


if __name__ == "__main__":
  unittest.main()
