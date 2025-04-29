import os
import sys
import unittest
import StringIO
import argparse
import shutil
import tempfile
from PIL import ImageGrab, Image, ImageChops
import numpy
import matplotlib
from PySide import QtGui

from datavis.MapNavigator import StaticMapNavigator
import measproc.MapTileCalculation as mtc
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


class SetUpStaticMapNavigatorTest(unittest.TestCase):
  def setUp(self):
    map_man = mapman.MapManager(args.mapdb)
    self.navigator = StaticMapNavigator(map_man)
    return
  
  def img_equal(self, img1, img2):
    return ImageChops.difference(img1, img2).getbbox() is None
  
  def convert_pixel_to_global_coords(self, x_pixel, y_pixel):
    pixel = mtc.Pixel(x_pixel, y_pixel)
    crop_unnorm_x =\
        numpy.ones_like(pixel.x) * self.navigator.nav_tools.crop_norm_value[0]
    crop_unnorm_y =\
        numpy.ones_like(pixel.y) * self.navigator.nav_tools.crop_norm_value[1]
    pixel.x += crop_unnorm_x
    pixel.y += crop_unnorm_y
    pixel = self.navigator.nav_tools.map_orig_tile.unnorm_pixel(pixel)
    coords = pixel.to_coord(self.navigator.nav_tools.zoom_level)
    return coords
  
  def tearDown(self):
    self.navigator.close()
    return


class MapCanvasFuncTest(SetUpStaticMapNavigatorTest):
  @classmethod
  def setUpClass(cls):
    cls.testdir = tempfile.mkdtemp(prefix='files_for_testing_',
                                   dir=os.path.dirname(__file__))
    return
  
  def setUp(self):
    SetUpStaticMapNavigatorTest.setUp(self)
    lon_GPS_data = numpy.linspace(8.464, 8.532, 30)
    lat_GPS_data = numpy.linspace(48.622, 48.655, 30)
    self.navigator.set_route(lon_GPS_data, lat_GPS_data)
    self.navigator.start()
    return
  
  def test_set_axes_limits(self):
    self.navigator.setAxesLimits([3.0, 4.0, -0.5, 0.5])
    for ax in self.navigator.fig.axes:
      self.assertAlmostEqual(ax.get_xlim(), (3.0, 4.0))
      self.assertAlmostEqual(ax.get_ylim(), (-0.5, 0.5))
    return
  
  def test_copy_content_to_clipboard(self):
    self.navigator.copyContentToClipboard()
    clipboard_img = ImageGrab.grabclipboard()
    clipboard_img = clipboard_img.convert('RGBA')
    img_buffer = StringIO.StringIO()
    self.navigator.fig.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)
    buffer_img = Image.open(img_buffer)
    images_identical = self.img_equal(clipboard_img, buffer_img)
    self.assertTrue(images_identical)
    return
  
  def test_copy_content_to_file(self):
    self.navigator.copyContentToFile(os.path.join(self.testdir, 'fig'))
    pics = [f for f in os.listdir(self.testdir) if f.endswith(".png")]
    self.assertEqual(pics, ['fig.png'])
    file_size = os.stat(os.path.join(self.testdir, 'fig.png')).st_size
    self.assertGreater(file_size, 0)
    return
  
  def test_set_window_title(self):
    new_title = 'Foo'
    window_pattern = 'MN %d %s'
    self.navigator.setWindowTitle(new_title)
    new_title = window_pattern % (self.navigator.fig.number, new_title)
    self.assertEqual(new_title, self.navigator.windowTitle())
    return
  
  def test_geometry(self):
    new_geom = '800x600+100+100'
    self.navigator.setWindowGeometry(new_geom)
    self.assertAlmostEqual(new_geom, self.navigator.getWindowGeometry())
    return
  
  @classmethod
  def tearDownClass(cls):
    shutil.rmtree(cls.testdir)
    return


class StaticMapNavigatorTest(SetUpStaticMapNavigatorTest):
  def setUp(self):
    SetUpStaticMapNavigatorTest.setUp(self)
    self.lon_GPS_data = numpy.linspace(8.464, 8.532, 30)
    self.lat_GPS_data = numpy.linspace(48.622, 48.655, 30)
    self.many_lon_GPS_data = numpy.linspace(8.4, 8.9, 30000)
    self.many_lat_GPS_data = numpy.linspace(48.2, 48.8, 30000)
    return
  
  def test_set_route(self):
    self.navigator.set_route(self.lon_GPS_data, self.lat_GPS_data)
    self.navigator.start()
    for line in self.navigator.map_axis.lines:
      x_data = line.get_xdata(orig=False)
      y_data = line.get_ydata(orig=False)
      line_coords = self.convert_pixel_to_global_coords(x_data, y_data)
      lon_data_is_OK = numpy.allclose(self.lon_GPS_data, line_coords.lon)
      lat_data_is_OK = numpy.allclose(self.lat_GPS_data, line_coords.lat)
      self.assertTrue(lon_data_is_OK)
      self.assertTrue(lat_data_is_OK)
    return
  
  def test_set_markers(self):
    intervals =\
        [[(start, end) for start, end in zip(range(2, 25, 5), range(6, 30, 5))]]
    lon_int_starts = []
    lat_int_starts = []
    for start, _ in intervals[0]:
      lon_int_starts.append(self.lon_GPS_data[start])
      lat_int_starts.append(self.lat_GPS_data[start])
    self.navigator.set_route(self.lon_GPS_data, self.lat_GPS_data)
    label = 'test_label'
    event_color = 'r'
    event_marker_size = 100.0
    event_marker_style = 'D'
    self.navigator.set_markers(intervals, label, event_color=event_color,
                               event_marker_size=event_marker_size,
                               event_marker_style=event_marker_style)
    self.navigator.start()
    for marker in self.navigator.map_axis.collections:
      marker_offsets = marker.get_offsets()
      x_data, y_data = zip(*marker_offsets)
      x_data = numpy.array(x_data)
      y_data = numpy.array(y_data)
      marker_coords = self.convert_pixel_to_global_coords(x_data, y_data)
      lon_data_is_OK = numpy.allclose(lon_int_starts, marker_coords.lon)
      lat_data_is_OK = numpy.allclose(lat_int_starts, marker_coords.lat)
      color =\
          matplotlib.colors.colorConverter.to_rgba_array(event_color,
                                                         marker.get_alpha())
      color_is_OK = numpy.all(marker.get_facecolor() == color)
      label_is_OK = label in self.navigator.stat_mark_data_idx.keys()
      size_is_OK = numpy.all(marker.get_sizes() == event_marker_size)
      # marker style cannot be acquired from collections
      self.assertTrue(lon_data_is_OK and lat_data_is_OK)
      self.assertTrue(color_is_OK and label_is_OK and size_is_OK)
    return
  
  def test_draw_arrow(self):
    self.navigator.set_route(self.many_lon_GPS_data, self.many_lat_GPS_data)
    self.navigator.draw_arrow()
    self.navigator.start()
    possible_texts = ['START/FINISH', 'START', 'FINISH']
    arrow_cnt_is_OK = len(self.navigator.map_axis.patches) > 0
    text_is_OK = []
    for text in self.navigator.map_axis.texts:
      text_is_OK.append(text.get_text() in possible_texts)
    self.assertTrue(arrow_cnt_is_OK and numpy.all(text_is_OK))
    return


if __name__ == "__main__":
  app = QtGui.QApplication([])
  unittest.main()
