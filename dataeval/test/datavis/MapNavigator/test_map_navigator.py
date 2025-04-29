import unittest
from PIL import ImageGrab, Image, ImageChops
import numpy
import matplotlib
from PySide import QtGui, QtCore, QtTest

from datavis.Synchronizer import cSynchronizer
from datavis.MapNavigator import MapNavigator
from datavis.PlotNavigator import cPlotNavigator
import measproc.mapmanager as mapman
import test_static_map_navigator as stat_test


class SetUpMapNavigatorTest(stat_test.SetUpStaticMapNavigatorTest):
  def setUp(self):
    map_man = mapman.MapManager(stat_test.args.mapdb)
    self.navigator = MapNavigator(map_man)
    return


class MapNavigatorSetAttribTest(SetUpMapNavigatorTest):
  def setUp(self):
    SetUpMapNavigatorTest.setUp(self)
    self.lon_GPS_data = numpy.linspace(8.464, 8.532, 100)
    self.lat_GPS_data = numpy.linspace(48.622, 48.655, 100)
    self.time = numpy.linspace(0.0, 100.0, 100)
    return
  
  def test_set_time(self):
    self.navigator.set_route(self.lon_GPS_data, self.lat_GPS_data)
    self.navigator.set_time(self.time)
    time_array_is_OK = numpy.allclose(self.time, self.navigator.time_array)
    self.assertTrue(time_array_is_OK)
    return
  
  def test_set_markers(self):
    intervals =\
        [(start, end) for start, end in zip(range(2, 25, 5), range(6, 30, 5))]
    lon_int_starts = []
    lat_int_starts = []
    for start, _ in intervals:
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
    marker_offsets = self.navigator.event_start_pos[label].get_offsets()
    x_data, y_data = zip(*marker_offsets)
    x_data = numpy.array(x_data)
    y_data = numpy.array(y_data)
    marker_coords = self.convert_pixel_to_global_coords(x_data, y_data)
    lon_data_is_OK = numpy.allclose(lon_int_starts, marker_coords.lon)
    lat_data_is_OK = numpy.allclose(lat_int_starts, marker_coords.lat)
    event_start_pos_alpha = self.navigator.event_start_pos[label].get_alpha()
    color =\
        matplotlib.colors.colorConverter.to_rgba_array(event_color,
                                                       event_start_pos_alpha)
    event_start_pos_color = self.navigator.event_start_pos[label].get_facecolor()
    color_is_OK = numpy.all(event_start_pos_color == color)
    label_is_OK = label in self.navigator.event_intervals.keys()
    event_start_pos_size = self.navigator.event_start_pos[label].get_sizes()
    size_is_OK = numpy.all(event_start_pos_size == event_marker_size)
    # marker style cannot be acquired from collections
    self.assertTrue(lon_data_is_OK and lat_data_is_OK)
    self.assertTrue(color_is_OK and label_is_OK and size_is_OK)
    for line_idx, line in enumerate(self.navigator.event_path[label]):
      event_path_xdata = line.get_xdata()
      event_path_ydata = line.get_ydata()
      route_xdata = self.navigator.route[0].get_xdata()
      route_ydata = self.navigator.route[0].get_ydata()
      event_start, event_end = self.navigator.event_intervals[label][line_idx]
      xdata_is_OK = numpy.allclose(event_path_xdata,
                                   route_xdata[event_start:event_end])
      ydata_is_OK = numpy.allclose(event_path_ydata,
                                   route_ydata[event_start:event_end])
      self.assertTrue(xdata_is_OK)
      self.assertTrue(ydata_is_OK)
    return


class MapNavigatorNavFuncTest(SetUpMapNavigatorTest):
  def setUp(self):
    SetUpMapNavigatorTest.setUp(self)
    lon_GPS_data = numpy.linspace(8.464, 8.532, 100)
    lat_GPS_data = numpy.linspace(48.622, 48.655, 100)
    time = numpy.arange(0.0, 100.0, 1.0)
    self.navigator.set_route(lon_GPS_data, lat_GPS_data)
    self.navigator.set_time(time)
    self.navigator.start()
    return
  
  def test_close(self):
    self.navigator.show()
    self.assertFalse(self.navigator.isHidden())
    self.navigator.close()
    self.assertTrue(self.navigator.isHidden())
    return

  def test_play(self):
    self.navigator.play(2.0)
    self.assertTrue(self.navigator.playing)
    return

  def test_on_play(self):
    self.navigator.onPlay(2.0)
    self.assertTrue(self.navigator.playing)
    return

  def test_pause(self):
    self.navigator.play(5.0)
    self.navigator.pause(2.0)
    self.assertFalse(self.navigator.playing)
    self.assertAlmostEqual(self.navigator.time, 2.0)
    return

  def test_on_pause(self):
    self.navigator.play(5.0)
    self.navigator.onPause(2.0)
    self.assertFalse(self.navigator.playing)
    self.assertAlmostEqual(self.navigator.time, 2.0)
    return

  def test_seek(self):
    self.navigator.seek(2.0)
    self.assertAlmostEqual(self.navigator.time, 2.0)
    return

  def test_on_seek(self):
    self.navigator.onSeek(2.0)
    self.assertAlmostEqual(self.navigator.time, 2.0)
    return


class MapNavigatorSyncTest(SetUpMapNavigatorTest):
  def setUp(self):
    SetUpMapNavigatorTest.setUp(self)
    self.lon_GPS_data = numpy.linspace(8.464, 8.532, 100)
    self.lat_GPS_data = numpy.linspace(48.622, 48.655, 100)
    self.time = numpy.arange(0.0, 100.0, 1.0)
    self.navigator.set_route(self.lon_GPS_data, self.lat_GPS_data)
    self.navigator.set_time(self.time)
    self.plot_navigator = cPlotNavigator()
    self.plot_navigator.addsignal('longitude', [self.time, self.lon_GPS_data])
    self.sync = cSynchronizer()
    self.sync.addClient(self.navigator)
    self.sync.addClient(self.plot_navigator)
    self.sync.start()
    self.sync.show()
    return
  
  def test_seek_with_sync(self):
    self.navigator.onSeek(20.0)
    self.assertAlmostEqual(self.plot_navigator.time, 20.0)
    return
  
  def test_seek_window(self):
    self.navigator.seek(20.0)
    seek_time = "%.3f" % self.navigator.time
    self.assertEqual(seek_time, self.navigator.time_text.get_text())
    veh_pos = self.navigator.veh_pos.get_offsets()
    veh_pos_xdata, veh_pos_ydata = zip(*veh_pos)
    veh_pos_coords =\
        self.convert_pixel_to_global_coords(veh_pos_xdata, veh_pos_ydata)
    lon_idx = numpy.argmin(numpy.abs(self.lon_GPS_data - veh_pos_coords.lon))
    lat_idx = numpy.argmin(numpy.abs(self.lat_GPS_data - veh_pos_coords.lat))
    indeces_match = lon_idx == lat_idx
    times_match = numpy.allclose(self.time[lon_idx], 20.0)
    self.assertTrue(indeces_match and times_match)
    return
  
  def tearDown(self):
    self.sync.close()
    return


class TestPlotNavigatorSignals(SetUpMapNavigatorTest):
  def setUp(self):
    SetUpMapNavigatorTest.setUp(self)
    self.lon_GPS_data = numpy.linspace(8.464, 8.532, 100)
    self.lat_GPS_data = numpy.linspace(48.622, 48.655, 100)
    self.time = numpy.arange(0.0, 100.0, 1.0)
    self.navigator.set_route(self.lon_GPS_data, self.lat_GPS_data)
    self.navigator.set_time(self.time)
    self.navigator.start()
    self.args = None
    self.navigator.closeSignal.signal.connect(self.save_args)
    self.navigator.playSignal.signal.connect(self.save_args)
    self.navigator.pauseSignal.signal.connect(self.save_args)
    self.navigator.seekSignal.signal.connect(self.save_args)
    return
  
  def save_args(self, *args):
    self.args = args
    return
  
  def test_close_signal(self):
    layout = self.navigator.getWindowGeometry()
    self.navigator.close()
    self.assertAlmostEqual(self.args, (layout, ))
    return

  def test_play_signal(self):
    self.navigator.onPlay(20.0)
    self.assertAlmostEqual(self.args, (20.0, ))
    return

  def test_pause_signal(self):
    self.navigator.onPause(20.0)
    self.assertAlmostEqual(self.args, (20.0, ))
    return

  def test_seek_signal(self):
    self.navigator.onSeek(20.0)
    self.assertAlmostEqual(self.args, (20.0, ))
    return
  
  def tearDown(self):
    SetUpMapNavigatorTest.tearDown(self)
    self.navigator.closeSignal.signal.disconnect()
    self.navigator.playSignal.signal.disconnect()
    self.navigator.pauseSignal.signal.disconnect()
    self.navigator.seekSignal.signal.disconnect()
    return


class MapNavigatorKeyPressEventTest(SetUpMapNavigatorTest):
  def setUp(self):
    SetUpMapNavigatorTest.setUp(self)
    lon_GPS_data = numpy.linspace(8.464, 8.532, 100)
    lat_GPS_data = numpy.linspace(48.622, 48.655, 100)
    time = numpy.arange(0.0, 100.0, 1.0)
    intervals =\
        [(start, end) for start, end in zip(range(2, 100, 5), range(6, 100, 5))]
    intervals_label = 'testing'
    self.navigator.set_route(lon_GPS_data, lat_GPS_data)
    self.navigator.set_time(time)
    self.navigator.set_markers(intervals, intervals_label)
    self.navigator.selected_event = intervals_label
    self.navigator.start()
    renderer = self.navigator.canvas.get_renderer()
    self.navigator.help.draw(renderer)
    return
  
  def test_h_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_H)
    self.assertTrue(self.navigator.event_legend.get_visible())
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_H)
    self.assertFalse(self.navigator.event_legend.get_visible())
    return
  
  def test_f1_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_F1)
    self.assertTrue(self.navigator.help.get_visible())
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_F1)
    self.assertFalse(self.navigator.help.get_visible())
    return
  
  def test_up_press(self):
    orig_time = self.navigator.time
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_Up)
    time = self.navigator.time
    self.assertGreater(time, orig_time)
    return
  
  def test_down_press(self):
    self.navigator.time = 50.0
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_Down)
    time = self.navigator.time
    self.assertLess(time, 50.0)
    return
  
  def test_delete_press(self):
    event_start_coords =\
        self.navigator.event_start_pos[self.navigator.selected_event].get_offsets()
    event_idx = self.navigator.event_seek_idx[self.navigator.selected_event]
    self.navigator.veh_pos.set_offsets(event_start_coords[event_idx])
    orig_event_cnt =\
        len(self.navigator.event_intervals[self.navigator.selected_event])
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_Delete)
    event_cnt =\
        len(self.navigator.event_intervals[self.navigator.selected_event])
    self.assertLess(event_cnt, orig_event_cnt)
    return
  
  def test_o_press(self):
    self.navigator.map_axis.set_navigate_mode('PAN')
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_O)
    self.assertEqual(self.navigator.map_axis.get_navigate_mode(), 'ZOOM')
    return
  
  def test_p_press(self):
    self.navigator.map_axis.set_navigate_mode('ZOOM')
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_P)
    self.assertEqual(self.navigator.map_axis.get_navigate_mode(), 'PAN')
    return
  
  def test_home_press(self):
    self.set_navigator_views(68.0, 700.0, 50.0, 480.0)
    orig_left, orig_right = self.navigator.map_axis.get_xlim()
    self.set_navigator_views(200.0, 400.0, 120., 220.0)
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_Home)
    left, right = self.navigator.map_axis.get_xlim()
    left_is_OK = numpy.allclose(orig_left, left)
    right_is_OK = numpy.allclose(orig_right, right)
    self.assertTrue(left_is_OK and right_is_OK)
    return
  
  def test_left_press(self):
    self.set_navigator_views(68.0, 700.0, 50.0, 480.0)
    orig_left, orig_right = self.navigator.map_axis.get_xlim()
    self.set_navigator_views(200.0, 400.0, 120., 220.0)
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_Left)
    left, right = self.navigator.map_axis.get_xlim()
    left_is_OK = numpy.allclose(orig_left, left)
    right_is_OK = numpy.allclose(orig_right, right)
    self.assertTrue(left_is_OK and right_is_OK)
    return
  
  def test_right_press(self):
    self.set_navigator_views(68.0, 700.0, 50.0, 480.0)
    self.set_navigator_views(200.0, 400.0, 120., 220.0)
    orig_left, orig_right = self.navigator.map_axis.get_xlim()
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_Left)
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_Right)
    left, right = self.navigator.map_axis.get_xlim()
    left_is_OK = numpy.allclose(orig_left, left)
    right_is_OK = numpy.allclose(orig_right, right)
    self.assertTrue(left_is_OK and right_is_OK)
    return
  
  def set_navigator_views(self, x_min, x_max, y_min, y_max):
    self.navigator.nav_tools.calc_map_bbox_and_zoom(3, 'ZOOM',
                                                    x_min, y_min, x_max, y_max)
    self.navigator.nav_tools.map_image, self.navigator.nav_tools.map_orig_tile =\
        self.navigator.nav_tools.map_manager.draw_map_image(\
            self.navigator.nav_tools.map_bbox, self.navigator.nav_tools.zoom_level)
    self.navigator.nav_tools.crop_norm_value, self.navigator.nav_tools.crop_bbox =\
        self.navigator.nav_tools.calc_crop_bbox()
    self.navigator.nav_tools.map_image =\
        self.navigator.nav_tools.map_image.crop(self.navigator.nav_tools.crop_bbox)
    self.navigator.nav_tools.update_map_image()
    self.navigator.nav_tools.push_current()
    return


if __name__ == "__main__":
  app = QtGui.QApplication([])
  unittest.main()
