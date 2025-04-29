import unittest
import numpy
import matplotlib as mpl
import argparse
import os
import sys

from datavis.backend_map import NavigationTools, CanvasWithSpecButtonSensing
import measproc.MapTileCalculation as mtc
import measproc.mapbbox as mbox
import measproc.mapmanager as mapman


def add_mapdb_to_sys_argv():
  parser = argparse.ArgumentParser()
  parser.add_argument('--mapdb', 
                      help='location of map database')
  parser.add_argument('-v', '--verbose',
                      help='Verbose output',
                      action="store_true",
                      default=False)
  parser.add_argument('-q', '--quiet',
                      help='Minimal output',
                      action="store_true",
                      default=False)
  parser.add_argument('-f', '--failfast',
                      help='Stop on first failure',
                      action="store_true",
                      default=False)
  parser.add_argument('-c', '--catch',
                      help='Catch control-C and display results',
                      action="store_true",
                      default=False)
  parser.add_argument('-b', '--buffer',
                      help='Buffer stdout and stderr during test runs',
                      action="store_true",
                      default=False)
  parser.add_argument('unittest_args', nargs='*',
                      help=("Which part of the unittest to run."
                            "Examples:\n"
                            "  %(prog)s                         "
                            "  - run default set of tests\n"
                            "  %(prog)s MyTestSuite             "
                            "  - run suite 'MyTestSuite'\n"
                            "  %(prog)s MyTestCase.testSomething"
                            "  - run MyTestCase.testSomething"
                            "  %(prog)s MyTestCase              "
                            "  - run all 'test*' test methods in MyTestCase"))
  args = parser.parse_args()
  
  if not os.path.exists(args.mapdb):
    raise mapman.MapManagerError('%s: %s is not present\n'
                                 % (__file__, args.mapdb))
  
  flags = []
  for key, value in vars(args).iteritems():
    if type(value) == bool and value:
      flags.append("--%s" % key)
  
  argv = flags + args.unittest_args
  sys.argv[1:] = argv
  return args

args = add_mapdb_to_sys_argv()

class SetUpNavigationToolsTest(unittest.TestCase):
  def setUp(self):
    figureNr = 1
    fig = mpl.pyplot.figure(figureNr)
    map_axis = fig.add_subplot(1, 1, 1)
    canvas = CanvasWithSpecButtonSensing(fig)
    map_man = mapman.MapManager(args.mapdb)
    self.nav_tools = NavigationTools(canvas, canvas, map_man, map_axis)
    return
  
  def tearDown(self):
    return


class NavigationToolsTest(SetUpNavigationToolsTest):
  def set_init_map(self, min_lon, min_lat, max_lon, max_lat):
    map_bbox = mbox.MapBbox(min_lon, min_lat, max_lon, max_lat)
    zoom = 13
    max_resolution = 70000000
    check_zoom_in_db = False
    self.nav_tools.init_map_drawing(map_bbox, check_zoom_in_db, zoom,
                                    max_resolution)
    self.nav_tools.map_axis.imshow(self.nav_tools.map_image, origin="lower")
    return
  
  def convert_pixel_to_global_coords(self, x_pixel, y_pixel):
    pixel = mtc.Pixel(x_pixel, y_pixel)
    crop_unnorm_x = numpy.ones_like(pixel.x) * self.nav_tools.crop_norm_value[0]
    crop_unnorm_y = numpy.ones_like(pixel.y) * self.nav_tools.crop_norm_value[1]
    pixel.x += crop_unnorm_x
    pixel.y += crop_unnorm_y
    pixel = self.nav_tools.map_orig_tile.unnorm_pixel(pixel)
    coords = pixel.to_coord(self.nav_tools.zoom_level)
    return coords
  
  def test_check_max_resolution(self):
    mapdb_metadata = self.nav_tools.map_manager.get_meta_data()
    tile_size = mapdb_metadata['tile_size']
    min_lon = 19.015
    max_lon = 19.035
    min_lat = 47.445
    max_lat = 47.465
    map_bbox = mbox.MapBbox(min_lon, min_lat, max_lon, max_lat)
    max_resolution = 70000000
    zoom = 16
    x_tile_cnt, y_tile_cnt = map_bbox.count_tiles(zoom)
    resolution = x_tile_cnt * y_tile_cnt * tile_size**2
    ref_lower_than_max_res = resolution < max_resolution
    lower_than_max_res = self.nav_tools.check_max_resolution(map_bbox, zoom,
                                                             max_resolution)
    self.assertTrue(ref_lower_than_max_res and lower_than_max_res)
    max_resolution = 1000000
    ref_lower_than_max_res = resolution < max_resolution
    lower_than_max_res = self.nav_tools.check_max_resolution(map_bbox, zoom,
                                                             max_resolution)
    self.assertFalse(ref_lower_than_max_res or lower_than_max_res)
    return
  
  def test_get_coords_from_pixel(self):
    lon = 19.015
    lat = 47.445
    pix_x = 513.262222221
    pix_y = 730.423387773
    zoom_level = 16
    pixel = mtc.Pixel(pix_x, pix_y)
    map_orig_tile = mtc.Coord(lon, lat).to_tile(zoom_level)
    crop_norm_value = (100, 100)
    acq_coord =\
        self.nav_tools.get_coords_from_pixel(pixel, crop_norm_value,
                                             zoom_level, map_orig_tile)
    self.assertTrue(numpy.allclose(lon + 0.01, acq_coord.lon)
                    and numpy.allclose(lat + 0.01, acq_coord.lat))
    return
  
  def test_get_pixel_from_coords(self):
    lon = 19.015
    lat = 47.445
    pix_x = 513.262222221
    pix_y = 730.423387773
    coords = mtc.Coord(lon + 0.01, lat + 0.01)
    zoom_level = 16
    map_orig_tile = mtc.Coord(lon, lat).to_tile(zoom_level)
    crop_norm_value = (100, 100)
    acq_pixel = self.nav_tools.get_pixel_from_coords(coords, crop_norm_value,
                                                     zoom_level, map_orig_tile)
    self.assertTrue(numpy.allclose(pix_x, acq_pixel.x)
                    and numpy.allclose(pix_y, acq_pixel.y))
    return
  
  def test_sort_last(self):
    v_min = 100
    v_max = 200
    v = 120
    v_last = 150
    v_start, v_end = self.nav_tools.sort_last(v_min, v_max, v, v_last)
    self.assertTrue(v_start == v and v_end == v_last)
    v_min = 300
    v_max = 200
    v = 220
    v_last = 250
    v_start, v_end = self.nav_tools.sort_last(v_min, v_max, v, v_last)
    self.assertTrue(v_start == v_last and v_end == v)
    v_min = 100
    v_max = 200
    v = 20
    v_last = 230
    v_start, v_end = self.nav_tools.sort_last(v_min, v_max, v, v_last)
    self.assertTrue(v_start == v_min and v_end == v_max)
    return
  
  def test_init_map_drawing(self):
    map_bbox = mbox.MapBbox(8.48, 48.62, 8.52, 48.64)
    zoom = 15
    max_resolution = 70000000
    check_zoom_in_db = False
    self.nav_tools.init_map_drawing(map_bbox, check_zoom_in_db, zoom,
                                    max_resolution)
    map_img, map_orig_tile =\
        self.nav_tools.map_manager.draw_map_image(map_bbox, zoom)
    self.assertEqual(self.nav_tools.map_bbox, map_bbox)
    self.assertEqual(self.nav_tools.crop_bbox,
                     (0, 0, map_img.size[0], map_img.size[1]))
    self.assertEqual(self.nav_tools.crop_norm_value, (0, 0))
    self.assertTrue(self.nav_tools.map_orig_tile.x == map_orig_tile.x
                    and self.nav_tools.map_orig_tile.y == map_orig_tile.y)
    max_res_checks = self.nav_tools.check_max_resolution(map_bbox, zoom,
                                                         max_resolution)
    self.assertTrue(max_res_checks and self.nav_tools.zoom_level == zoom)
    zooms_in_db = self.nav_tools.map_manager.get_zooms_map_bbox(map_bbox)
    zoom = 20
    check_zoom_in_db = True
    zoom_in_db_before = zoom in zooms_in_db
    self.nav_tools.init_map_drawing(map_bbox, check_zoom_in_db, zoom,
                                    max_resolution)
    zoom_in_db_after = self.nav_tools.zoom_level in zooms_in_db
    self.assertTrue(not zoom_in_db_before and zoom_in_db_after)
    return
  
  def test_calc_crop_bbox(self):
    map_bbox = mbox.MapBbox(8.48, 48.62, 8.52, 48.64)
    zoom = 15
    max_resolution = 70000000
    check_zoom_in_db = False
    self.nav_tools.init_map_drawing(map_bbox, check_zoom_in_db, zoom,
                                    max_resolution)
    crop_norm_value, crop_bbox = self.nav_tools.calc_crop_bbox()
    map_bbox_ll_corner = map_bbox.ll_corner.to_pixel(zoom)
    map_bbox_ur_corner = map_bbox.ur_corner.to_pixel(zoom)
    map_bbox_crop_norm =\
        self.nav_tools.map_orig_tile.norm_pixel(map_bbox_ll_corner)
    self.assertEqual(crop_norm_value,
                     (map_bbox_crop_norm.x, map_bbox_crop_norm.y))
    crop_width = int(map_bbox_ur_corner.x - map_bbox_ll_corner.x + 0.5)
    crop_height = int(map_bbox_ur_corner.y - map_bbox_ll_corner.y + 0.5)
    self.assertEqual(crop_width, crop_bbox[2] - crop_bbox[0])
    self.assertEqual(crop_height, crop_bbox[3] - crop_bbox[1])
    return
  
  def test_readjust_lines_markers(self):
    self.set_init_map(8.48, 48.62, 8.52, 48.64)
    zoom_box = (100, 100, 300, 300)
    old_crop_norm_value = self.nav_tools.crop_norm_value
    old_zoom_level = self.nav_tools.zoom_level
    old_map_orig_tile = self.nav_tools.map_orig_tile
    self.nav_tools.calc_map_bbox_and_zoom(1, 'ZOOM', *zoom_box)
    self.nav_tools.map_image, self.nav_tools.map_orig_tile =\
        self.nav_tools.map_manager.draw_map_image(self.nav_tools.map_bbox,
                                                  self.nav_tools.zoom_level)
    self.nav_tools.crop_norm_value, self.nav_tools.crop_bbox =\
        self.nav_tools.calc_crop_bbox()
    self.nav_tools.map_image =\
        self.nav_tools.map_image.crop(self.nav_tools.crop_bbox)
    self.nav_tools.update_map_image()
    line_old_pixels = []
    line_old_coords = []
    for line in self.nav_tools.map_axis.lines:
      line_xdata = line.get_xdata(orig=False)
      line_ydata = line.get_ydata(orig=False)
      line_pixel = mtc.Pixel(line_xdata, line_ydata)
      line_old_pixels.append(line_pixel)
      line_old_coords.append(self.convert_pixel_to_global_coords(line_xdata,
                                                                 line_ydata))
    marker_old_pixels = []
    marker_old_coords = []
    for marker in self.nav_tools.map_axis.collections:
      marker_offsets = marker.get_offsets()
      marker_xdata, marker_ydata = zip(*marker_offsets)
      marker_pixel = mtc.Pixel(marker_xdata, marker_ydata)
      marker_old_pixels.append(marker_pixel)
      marker_old_coords.append(self.convert_pixel_to_global_coords(marker_xdata,
                                                                   marker_ydata))
    self.nav_tools.readjust_lines_markers(old_crop_norm_value, old_zoom_level,
                                          old_map_orig_tile,
                                          self.nav_tools.crop_norm_value,
                                          self.nav_tools.zoom_level,
                                          self.nav_tools.map_orig_tile)
    line_new_pixels = []
    line_new_coords = []
    for line in self.nav_tools.map_axis.lines:
      line_xdata = line.get_xdata(orig=False)
      line_ydata = line.get_ydata(orig=False)
      line_pixel = mtc.Pixel(line_xdata, line_ydata)
      line_new_pixels.append(line_pixel)
      line_new_coords.append(self.convert_pixel_to_global_coords(line_xdata,
                                                                 line_ydata))
    marker_new_pixels = []
    marker_new_coords = []
    for marker in self.nav_tools.map_axis.collections:
      marker_offsets = marker.get_offsets()
      marker_xdata, marker_ydata = zip(*marker_offsets)
      marker_pixel = mtc.Pixel(marker_xdata, marker_ydata)
      marker_new_pixels.append(marker_pixel)
      marker_new_coords.append(self.convert_pixel_to_global_coords(marker_xdata,
                                                                   marker_ydata))
    for test_data in zip(line_old_pixels, line_old_coords,
                         line_new_pixels, line_new_coords):
      line_old_pixel, line_old_coord, line_new_pixel, line_new_coord = test_data
      self.assertNotAlmostEqual(line_old_pixel.x, line_new_pixel.x)
      self.assertNotAlmostEqual(line_old_pixel.y, line_new_pixel.y)
      self.assertAlmostEqual(line_old_coord.x, line_new_coord.x)
      self.assertAlmostEqual(line_old_coord.y, line_new_coord.y)
    for test_data in zip(marker_old_pixels, marker_old_coords,
                         marker_new_pixels, marker_new_coords):
      marker_old_pixel, marker_old_coord, marker_new_pixel, marker_new_coord =\
          test_data
      self.assertNotAlmostEqual(marker_old_pixel.x, marker_new_pixel.x)
      self.assertNotAlmostEqual(marker_old_pixel.y, marker_new_pixel.y)
      self.assertAlmostEqual(marker_old_coord.x, marker_new_coord.x)
      self.assertAlmostEqual(marker_old_coord.y, marker_new_coord.y)
    return
  
  def test_update_map_image(self):
    self.set_init_map(8.48, 48.62, 8.52, 48.64)
    prev_xlim = self.nav_tools.map_axis.get_xlim()
    prev_ylim = self.nav_tools.map_axis.get_ylim()
    new_map_bbox = mbox.MapBbox(8.49, 48.63, 8.51, 48.64)
    self.nav_tools.map_bbox = new_map_bbox
    self.nav_tools.zoom_level = 14
    self.nav_tools.map_image, self.nav_tools.map_orig_tile =\
        self.nav_tools.map_manager.draw_map_image(self.nav_tools.map_bbox,
                                                  self.nav_tools.zoom_level)
    self.nav_tools.crop_norm_value, self.nav_tools.crop_bbox =\
        self.nav_tools.calc_crop_bbox()
    self.nav_tools.map_image =\
        self.nav_tools.map_image.crop(self.nav_tools.crop_bbox)
    self.nav_tools.update_map_image()
    next_xlim = self.nav_tools.map_axis.get_xlim()
    next_ylim = self.nav_tools.map_axis.get_ylim()
    self.assertLess(next_xlim[1], prev_xlim[1])
    self.assertLess(next_ylim[1], prev_ylim[1])
    ll_coords = self.convert_pixel_to_global_coords(next_xlim[0], next_ylim[0])
    ur_coords = self.convert_pixel_to_global_coords(next_xlim[1], next_ylim[1])
    ref_map_bbox = mbox.MapBbox(ll_coords.lon, ll_coords.lat,
                                ur_coords.lon, ur_coords.lat)
    self.assertEqual(ref_map_bbox, new_map_bbox)
    new_map_bbox
    return
  
  def check_if_zoom_pan_OK(self, bbox, button, nav_mode):
    old_map_bbox = self.nav_tools.map_bbox
    old_zoom = self.nav_tools.zoom_level
    ll_coords = self.convert_pixel_to_global_coords(*bbox[:2])
    ur_coords = self.convert_pixel_to_global_coords(*bbox[2:])
    self.nav_tools.calc_map_bbox_and_zoom(button, nav_mode, *bbox)
    ref_map_bbox = mbox.MapBbox(ll_coords.lon, ll_coords.lat,
                                ur_coords.lon, ur_coords.lat)
    new_map_bbox = self.nav_tools.map_bbox
    new_zoom = self.nav_tools.zoom_level
    if nav_mode == 'ZOOM' or (button == 3 and nav_mode == 'PAN'):
      self.assertNotEqual(old_zoom, new_zoom)
    self.assertNotEqual(old_map_bbox, new_map_bbox)
    self.assertEqual(ref_map_bbox, new_map_bbox)
    return
  
  def test_calc_map_bbox_and_zoom__zoom(self):
    self.set_init_map(8.48, 48.62, 8.52, 48.64)
    zoom_box = (100, 100, 300, 300)
    self.check_if_zoom_pan_OK(zoom_box, 1, 'ZOOM')
    return
  
  def test_calc_map_bbox_and_zoom__pan(self):
    self.set_init_map(8.48, 48.62, 8.52, 48.64)
    xlim = self.nav_tools.map_axis.get_xlim()
    ylim = self.nav_tools.map_axis.get_ylim()
    pan_box = (xlim[0] + 75, ylim[0] + 75, xlim[1] + 75, ylim[1] + 75)
    self.check_if_zoom_pan_OK(pan_box, 1, 'PAN')
    return
  
  def test_calc_map_bbox_and_zoom__zoompan(self):
    self.set_init_map(8.48, 48.62, 8.52, 48.64)
    xlim = self.nav_tools.map_axis.get_xlim()
    ylim = self.nav_tools.map_axis.get_ylim()
    pan_box = (xlim[0] + 150, ylim[0] + 150, xlim[1] - 150, ylim[1] - 150)
    self.check_if_zoom_pan_OK(pan_box, 3, 'PAN')
    return


if __name__ == "__main__":
  unittest.main()
