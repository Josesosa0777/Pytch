import os
import sys
import unittest
import cStringIO

import PIL
from PIL import ImageGrab
import numpy
import matplotlib
from PySide import QtGui, QtCore, QtTest

from datavis.Synchronizer import cSynchronizer
from datavis.PlotNavigator import cPlotNavigator
import measproc

class Build(unittest.TestCase):
  def setUp(self):
    self.navigator = cPlotNavigator()
    return

  def tearDown(self):
    self.navigator.close()
    return

class TestPlotNavigatorNavigatorFunctions(Build):
  def setUp(self):
    Build.setUp(self)
    self.navigator.addAxis()
    self.navigator.start()
    return

  def test_close(self):
    self.navigator.show()
    self.assertFalse(self.navigator.isHidden())
    self.assertNotEqual(len(matplotlib._pylab_helpers.Gcf.get_all_fig_managers()), 0)
    self.navigator.close()
    self.assertTrue(self.navigator.isHidden())
    self.assertEqual(len(matplotlib._pylab_helpers.Gcf.get_all_fig_managers()), 0)
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

  def test_set_ROI(self):
    self.navigator.setROI(self.navigator, 2.0, 5.0, 'b')
    self.assertAlmostEqual(self.navigator.ROIstart, 2.0)
    self.assertAlmostEqual(self.navigator.ROIend, 5.0)
    return

  def test_on_set_ROI(self):
    self.navigator.onSetROI(2.0, 5.0, 'b')
    self.assertAlmostEqual(self.navigator.ROIstart, 2.0)
    self.assertAlmostEqual(self.navigator.ROIend, 5.0)
    return

  def test_geometry(self):
    new_geom = '800x600+100+100'
    self.navigator.setWindowGeometry(new_geom)
    self.assertAlmostEqual(new_geom, self.navigator.getWindowGeometry())
    return

  def test_set_window_title(self):
    new_title = 'Foo'
    self.navigator.setWindowTitle(new_title)
    self.assertEqual(new_title, self.navigator.windowTitle())
    return

  def test_set_xlim_online(self):
    self.navigator.set_xlim_online(2.0, 5.0)
    left, right = self.navigator.fig.shared_sp.get_xlim()
    self.assertAlmostEqual(2.0, left)
    self.assertAlmostEqual(5.0, right)
    return

  def test_on_set_xlim_online(self):
    self.navigator.on_set_xlim_online(2.0, 5.0)
    left, right = self.navigator.fig.shared_sp.get_xlim()
    self.assertAlmostEqual(2.0, left)
    self.assertAlmostEqual(5.0, right)
    return

class TestSetXLimOnline(Build):
  def setUp(self):
    Build.setUp(self)
    self.second_navigator = cPlotNavigator()
    t = numpy.arange(0,400,0.01)
    self.navigator.addsignal('sine' ,  [t, numpy.sin(t)])
    self.second_navigator.addsignal('cos' ,  [t, numpy.cos(t)])
    self.sync = cSynchronizer()
    self.sync.addClient(self.navigator)
    self.sync.addClient(self.second_navigator)
    self.sync.start()
    self.sync.show()
    return

  def test_set_xlim(self):
    self.navigator.on_set_xlim_online(2.0, 5.0)
    left, right = \
            self.second_navigator.fig.shared_sp.get_xlim()
    self.assertAlmostEqual(2.0, left)
    self.assertAlmostEqual(5.0, right)
    return

  def test_a_press(self):
    self.navigator.fig.shared_sp.set_xlim(2.0, 5.0)
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_A)
    left, right = \
            self.second_navigator.fig.shared_sp.get_xlim()
    self.assertAlmostEqual(2.0, left)
    self.assertAlmostEqual(5.0, right)
    return

  def tearDown(self):
    self.sync.close()
    return
    
class TestFigureSave(Build):
  def setUp(self):
    Build.setUp(self)
    self.navigator.addAxis()
    self.navigator.start()
    return

  def test_copy_content_to_file(self):
    self.navigator.copyContentToFile('fig')
    pics = [ f for f in os.listdir(".") if f.endswith(".png") ]
    self.assertEqual(pics, ['fig.png'])
    file_syze = os.stat('fig.png').st_size
    self.assertGreater(file_syze, 0)
    return

  def test_copy_content_to_buffer(self):
    buff = self.navigator.copyContentToBuffer()
    buffer = cStringIO.StringIO()
    self.navigator.copyContentToFile(buffer, format='png')
    buff_value = buff.getvalue()
    buffer_value = buffer.getvalue()
    self.assertNotEqual(buff_value, '')
    self.assertNotEqual(buffer_value, '')
    self.assertEqual(buff_value, buffer_value)
    return

  @classmethod  
  def tearDownClass(cls):
    pics = [ f for f in os.listdir(".") if f.endswith(".png") ]
    for pic in pics:
      os.remove(pic)
    return

class TestPlotNavigatorSignals(Build):
  def setUp(self):
    Build.setUp(self)
    self.navigator.addAxis()
    self.navigator.start()

    self.args = None

    self.navigator.closeSignal.signal.connect(self.saveArgs)
    self.navigator.playSignal.signal.connect(self.saveArgs)
    self.navigator.pauseSignal.signal.connect(self.saveArgs)
    self.navigator.seekSignal.signal.connect(self.saveArgs)
    self.navigator.setROISignal.signal.connect(self.saveArgs)
    self.navigator.selectGroupSignal.signal.connect(self.saveArgs)
    self.navigator.setXLimOnlineSignal.signal.connect(self.saveArgs)
    return

  def saveArgs(self, *args):
    self.args = args
    return

  def test_close_signal(self):
    layout = self.navigator.getWindowGeometry()
    self.navigator.close()
    self.assertAlmostEqual(self.args, (layout, ))
    return

  def test_play_signal(self):
    self.navigator.onPlay(2.0)
    self.assertAlmostEqual(self.args, (2.0, ))
    return

  def test_pause_signal(self):
    self.navigator.onPause(2.0)
    self.assertAlmostEqual(self.args, (2.0, ))
    return

  def test_seek_signal(self):
    self.navigator.onSeek(2.0)
    self.assertAlmostEqual(self.args, (2.0, ))
    return

  def test_setROI_signal(self):
    self.navigator.onSetROI(1.1, 2.2, 'r')
    self.assertAlmostEqual(self.args, 
                          (self.navigator, 1.1, 2.2, 'r'))
    return

  def test_selectGroup_signal(self):
    self.navigator.onSelectGroup('FooGroup')
    self.assertAlmostEqual(self.args, ('FooGroup', ))
    return

  def test_set_xlim_online_signal(self):
    self.navigator.on_set_xlim_online(5.0, 10.0)
    self.assertAlmostEqual(self.args, (5.0, 10.0))
    return

  def tearDown(self):
    Build.tearDown(self)
    self.navigator.closeSignal.signal.disconnect()
    self.navigator.playSignal.signal.disconnect()
    self.navigator.pauseSignal.signal.disconnect()
    self.navigator.seekSignal.signal.disconnect()
    self.navigator.setROISignal.signal.disconnect()
    self.navigator.selectGroupSignal.signal.disconnect()
    self.navigator.setXLimOnlineSignal.signal.disconnect()
    return


class TestXlimitsAtStart(Build):
  def setUp(self):
    Build.setUp(self)
    t  = numpy.arange(2, 5, 0.01)
    tt = numpy.arange(1, 4, 0.01)
    self.navigator.addsignal('sin' ,  [t,  numpy.sin(t)])
    self.navigator.addsignal('cos' ,  [tt, numpy.cos(tt)])
    self.navigator.start()
    self.t = t
    self.tt = tt
    return

  def test_x_min(self):
    self.assertEqual(self.tt.min(), self.navigator.x_min)
    return

  def test_x_max(self):
    self.assertEqual(self.t.max(), self.navigator.x_max)
    return

  def test_limits_consistency(self):
    fig_x_limits = self.navigator.fig.shared_sp.get_xlim()
    nav_x_limits = self.navigator.x_min, self.navigator.x_max
    self.assertEqual(fig_x_limits, nav_x_limits)
    return


class TestStartWithoutAxes(Build):
  def test_assert_raised(self):
    with self.assertRaises(AssertionError):
      self.navigator.start()
    return


class TestKeyPressEvent(Build):
  def setUp(self):
    Build.setUp(self)
    t = numpy.arange(0,400,0.01)
    self.navigator.addsignal('sine' ,  [t, numpy.sin(t)])
    self.navigator.start()
    renderer = self.navigator.canvas.get_renderer()
    self.navigator.help.draw(renderer)
    return

  def test_f1_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_F1)
    self.assertTrue(self.navigator.help.get_visible())
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_F1)
    self.assertFalse(self.navigator.help.get_visible())
    return

  def test_space_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_Space)
    self.assertTrue(self.navigator.playing)
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_Space)
    self.assertFalse(self.navigator.playing)
    return

  def test_h_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_H)
    self.assertFalse(self.navigator.show_legend)
    for ax in self.navigator.fig.axes:
      legend = ax.get_legend()
      self.assertFalse(legend.get_visible())
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_H)

    self.assertTrue(self.navigator.show_legend)
    for ax in self.navigator.fig.axes:
      legend = ax.get_legend()
      self.assertTrue(legend.get_visible())
    return
    
  def test_q_press(self):
    fig = self.navigator.fig
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_Q)
    clip_board_data = ImageGrab.grabclipboard()
    clip_board_data.save('fig.png')
    pics = [ f for f in os.listdir(".") if f.endswith(".png") ]
    self.assertEqual(pics, ['fig.png'])
    file_syze = os.stat('fig.png').st_size
    self.assertGreater(file_syze, 0)
    return

  def test_greater_lesser_key(self):
    initial_font_size = self.navigator.font.get_size()
    initial_font_size_idx = self.navigator.FONT_SIZES.index( initial_font_size )
    max_idx = len(self.navigator.FONT_SIZES)
    new_idx = initial_font_size_idx+1 %max_idx
    new_size_check = self.navigator.FONT_SIZES[new_idx]
    # simulate '>' keypress
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_Greater)
    new_font_size = self.navigator.font.get_size()
    self.assertEqual(new_font_size, new_size_check)
    # simulate '<' keypress
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_Less)
    new_font_size = self.navigator.font.get_size()
    new_size_check = self.navigator.FONT_SIZES[initial_font_size_idx]
    self.assertEqual(new_font_size, new_size_check)
    return

  def test_k_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_K)
    for ax in self.navigator.fig.axes:
      self.assertEqual(ax.get_xscale(), 'log')

    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_K)
    for ax in self.navigator.fig.axes:
      self.assertEqual(ax.get_xscale(), 'linear')
    return

  def test_l_press(self):
    for ax in self.navigator.fig.axes:
      self.navigator.selected_axes = ax
      QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_L)
      self.assertEqual(ax.get_yscale(), 'log')
      for axis in self.navigator.fig.axes:
        if axis == ax: continue
        self.assertEqual(ax.get_yscale(), 'linear')
      QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_L)
      for axis in self.navigator.fig.axes:
        self.assertEqual(ax.get_yscale(), 'linear')
    return

  def test_i_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_I)
    self.assertTrue(self.navigator.interpolate)

    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_I)
    self.assertFalse(self.navigator.interpolate)
    return

  def test_c_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_C)
    for ax in self.navigator.fig.axes:
      for axvspan in ax.axvspans.itervalues():
        self.assertFalse(axvspan.get_visible())

    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_C)
    for ax in self.navigator.fig.axes:
      for axvspan in ax.axvspans.itervalues():
        self.assertTrue(axvspan.get_visible())
    return

  def test_r_press(self):
    self.navigator.time = 5.0
    correct_value = numpy.sin(self.navigator.time)
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_R)
    for ax in self.navigator.fig.axes:
      legend = ax.get_legend()
      texts = legend.get_texts()
      for text in texts:
        text = text.get_text()
        name, value = text.split('=')
        value = float(value)
        self.assertAlmostEqual(value, correct_value, delta=.001)
    return

  def test_m_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_M)
    self.assertTrue(self.navigator.label_multi_col)

    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_M)
    self.assertFalse(self.navigator.label_multi_col)
    return

  def test_p_press(self):
    for ax in self.navigator.fig.axes:
      ax.set_navigate_mode('ZOOM')
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_P)
    for ax in self.navigator.fig.axes:
      self.assertEqual(ax.get_navigate_mode(), 'PAN')
    return

  def test_o_press(self):
    for ax in self.navigator.fig.axes:
      ax.set_navigate_mode('PAN')
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_O)
    for ax in self.navigator.fig.axes:
      self.assertEqual(ax.get_navigate_mode(), 'ZOOM')
    return
    
  def test_home_press(self):
    self.navigator.set_xlim_online(4.5, 5.0)
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_Home)
    left, right = self.navigator.fig.shared_sp.get_xlim()
    self.assertAlmostEqual(0.0, left)
    self.assertAlmostEqual(400.0, right, delta=.01)
    return
    
  def test_left_press(self):
    self.navigator.set_xlim_online(4.5, 5.0)
    left, right = self.navigator.fig.shared_sp.get_xlim()
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_Left)
    left, right = self.navigator.fig.shared_sp.get_xlim()
    self.assertAlmostEqual(0.0, left)
    self.assertAlmostEqual(400.0, right, delta=.01)
    return

  @classmethod
  def tearDownClass(cls):
    pics = [ f for f in os.listdir(".") if f.endswith(".png") ]
    for pic in pics:
      os.remove(pic)
    return
    

class TestPlottingFunctions(Build):
  def test_add_axis(self):
    ax = self.navigator.addAxis(grid=False, hide_legend=True, ylim=5.0, 
                                yticks={3.47 : '3.47'}, ylabel='foo', 
                                xlabel='time', legend_alpha=.2)
    self.navigator.start()
    self.assertNotIsInstance(ax, type(None))
    self.assertAlmostEqual(ax.get_xlabel(), 'time')
    self.assertAlmostEqual(ax.get_ylabel(), 'foo')
    self.assertAlmostEqual(ax.get_yticks(), [3.47])
    self.assertAlmostEqual(ax.get_yticklabels()[0].get_text(), '3.47')
    self.assertFalse(ax.grid())
    self.assertTrue(ax.hide_legend)
    self.assertEqual(ax.legend_alpha, .2)
    self.assertAlmostEqual(max(ax.get_ylim()), 5.0)
    return

  def test_add_signal(self):
    t = numpy.arange(0,400,0.01)
    self.navigator.addsignal('sine' ,  [t, numpy.sin(t)])
    self.navigator.start()

    self.navigator.seek(5.0)
    correct_value = numpy.sin(self.navigator.time)
    for ax in self.navigator.fig.axes:
      legend = ax.get_legend()
      texts = legend.get_texts()
      for text in texts:
        text = text.get_text()
        name, value = text.split('=')
        self.assertEqual(name, 'sine ')
        value = float(value)
        self.assertAlmostEqual(value, correct_value, delta=.001)
    return

  def test_signal_precision(self):

    value_control = 0.0001
    value_control_2 = 0.000001
    value_big_control = 20.001
    value_big_control_2 = 1.0
    value_zero = 0.0
    value_float_case_1 = (0.1 + 0.2) - 0.3
    value_float_case_2 = 20.0 + value_float_case_1

    self.assertEqual(cPlotNavigator._get_format(value_control), "%.6f")
    self.assertEqual(cPlotNavigator._get_format(value_control_2), "%.8f")
    self.assertEqual(cPlotNavigator._get_format(value_big_control), "%.3f")
    self.assertEqual(cPlotNavigator._get_format(value_big_control_2), "%.3f")
    self.assertEqual(cPlotNavigator._get_format(value_zero), "%.3f")
    self.assertEqual(cPlotNavigator._get_format(value_float_case_1), "%.19f")
    self.assertEqual(cPlotNavigator._get_format(value_float_case_2), "%.3f")
    return

  def test_add_signal_2_axis(self):
    t = numpy.arange(0,400,0.01)
    value = numpy.sin(t)
    offset = numpy.tile(42.0, t.shape)
    factor = numpy.tile(3.14, t.shape)
    ax = self.navigator.addAxis()
    self.navigator.addSignal2Axis(ax, 'sine', t, value, offset=offset,
                                      factor=factor, color='r', linewidth=3,
                                      unit='m/s')
    self.navigator.start()
    line = ax.label2line['sine']
    self.assertEqual(line.get_color(), 'r')
    self.assertEqual(line.get_linewidth(), 3)
    self.assertEqual(line.unit, '[m/s]')

    correct_value = factor * value + offset
    value_equality = numpy.array_equal(correct_value, line.value)
    self.assertTrue(value_equality)
    return

  def test_add_signal_2_axis_custom_line_properties(self):
    t = numpy.arange(0,400,0.01)
    value = numpy.sin(t)
    ax = self.navigator.addAxis()
    kwargs = dict(
      color='r',
      alpha=.5,
      linestyle=':',
      linewidth=3,
      marker='d',
      markersize=.5,
      markerfacecolor='k',
      markeredgewidth=2,
      picker=20,
    )
    self.navigator.addSignal2Axis(ax, 'sine', t, value, unit='m/s', **kwargs)
    self.navigator.start()
    line = ax.lines[-1]
    for k,v in kwargs.iteritems():
      obj = getattr(line, '_'+k)
      self.assertTrue( obj==v or obj is not None )
    return

  def test_add_threshold_2_axis(self):
    t = numpy.arange(0,400,0.01)
    value = numpy.sin(t)
    ax = self.navigator.addAxis()
    self.navigator.addSignal2Axis(ax, 'sine', t, value)
    self.navigator.addThreshold2Axis(ax, 'horizontal', 0.42, color='b')
    line_labels = [line.get_label() for line in ax.lines]
    self.assertIn('horizontal = 0.420', line_labels)
    self.assertIn('sine', line_labels)
    ndx = line_labels.index('horizontal = 0.420')
    x_data, y_data = ax.lines[ndx].get_data()
    self.assertEqual(y_data, [0.42, 0.42])
    self.assertAlmostEqual(ax.lines[ndx].get_color(), 'b')
    return

  def test_add_twin_axis(self):
    ax = self.navigator.addAxis(grid=False, hide_legend=True, ylim=5.0, 
                                yticks={3.47 : '3.47'}, ylabel='foo', 
                                xlabel='time')
    twinax = self.navigator.addTwinAxis(ax, color='m', ylabel='bar')
    self.navigator.start()
    self.assertNotIsInstance(twinax, type(None))
    self.assertEqual(twinax.twin_color, 'm')
    self.assertEqual(twinax.get_ylabel(), 'bar')
    return

  def test_add_x_tick(self):
    ax = self.navigator.addAxis(grid=False, hide_legend=True, ylim=5.0, 
                                yticks={3.47 : '3.47'}, ylabel='foo', 
                                xlabel='time')
    self.navigator.addXTick(ax, 'bar', 0.47, rotation=30)
    self.navigator.start()
    x_ticks = ax.get_xticks()
    self.assertIn(0.47, x_ticks)
    ndx = numpy.nonzero(x_ticks==0.47)[0][0]
    labels = matplotlib.pyplot.gca().get_xticklabels()
    label_texts = map(lambda label: label.get_text(), labels)

    self.assertEqual('bar', label_texts[ndx])
    self.assertAlmostEqual(labels[ndx].get_rotation(), 30.0)
    return

  def test_add_reports(self):
    t = numpy.arange(0.0, 20.0, 0.01)
    y = numpy.sin(t)
    z = numpy.cos(t)
    i = measproc.cEventFinder.compExtSigScal(t, y, measproc.greater, 0.5)
    j = measproc.cEventFinder.compExtSigScal(t, z, measproc.greater, 0.5)

    report1 = measproc.cIntervalListReport(i, 'TestReport1')
    report2 = measproc.cIntervalListReport(j, 'TestReport2')
    reports = report1, report2
    ax = self.navigator.addAxis(grid=False, hide_legend=True, ylim=5.0, 
                              yticks={3.47 : '3.47'}, ylabel='foo', 
                              xlabel='time')
    self.navigator.addReports(ax, reports)
    self.navigator.start()
    self.assertGreater(ax.bar_height, 0.0)
    self.assertIn('TestReport1', ax.title2bar)
    self.assertIn('TestReport2', ax.title2bar)
    bars = [child for child in ax.get_children()
                  if type(child) == matplotlib.patches.Rectangle]

    bar_intervals = [(bar.get_x(), bar.get_x() + bar.get_width() )
                                                           for bar in bars[:-1]]

    for interval in i:
      lower, upper = interval
      lower /= 100.0
      upper /= 100.0
      bar_lower = [b_lower for b_lower, b_upper in bar_intervals
                           if abs(b_lower - lower) <  .05]
      bar_lower, = bar_lower
      bar_upper = [b_upper for b_lower, b_upper in bar_intervals
                           if abs(b_upper - upper) <  .05]
      bar_upper, = bar_upper
      self.assertAlmostEqual(lower, bar_lower, delta=0.05)
      self.assertAlmostEqual(upper, bar_upper, delta=0.05)

    for interval in j:
      lower, upper = interval
      lower /= 100.0
      upper /= 100.0
      bar_lower = [b_lower for b_lower, b_upper in bar_intervals
                           if abs(b_lower - lower) <  .05]
      bar_lower, = bar_lower
      bar_upper = [b_upper for b_lower, b_upper in bar_intervals
                           if abs(b_upper - upper) <  .05]
      bar_upper, = bar_upper
      self.assertAlmostEqual(lower, bar_lower, delta=0.05)
      self.assertAlmostEqual(upper, bar_upper, delta=0.05)
    return

  def test_set_axes_limits(self):
    t = numpy.arange(0,400,0.01)
    self.navigator.addsignal('sine' ,  [t, numpy.sin(t)])
    self.navigator.start()

    fig = self.navigator.fig
    self.navigator.setAxesLimits([3.0, 4.0, -0.5, 0.5])
    for ax in fig.axes:
      self.assertAlmostEqual(ax.get_xlim(), (3.0, 4.0))
      self.assertAlmostEqual(ax.get_ylim(), (-0.5, 0.5))
    return

  def test_label_formatting(self):
    sample1 = numpy.arange(0.0, 10, 1)
    sample2 = numpy.arange(0.0, 1, 0.1)
    sample3 = numpy.arange(0.0, 0.1, 0.01)
    sample4 = numpy.arange(0.0, 0.01, 0.001)
    sample5 = numpy.arange(0.0, 0.001, 0.0001)

    self.assertEqual('%.3f',
                     cPlotNavigator._get_format(numpy.ptp(sample1)),
                     cPlotNavigator._get_format(numpy.ptp(sample1)))
    self.assertEqual('%.3f',\
                     cPlotNavigator._get_format(numpy.ptp(sample2)),
                     cPlotNavigator._get_format(numpy.ptp(sample2)))
    self.assertEqual('%.4f',
                     cPlotNavigator._get_format(numpy.ptp(sample3)),
                     cPlotNavigator._get_format(numpy.ptp(sample3)))
    self.assertEqual('%.5f',\
                     cPlotNavigator._get_format(numpy.ptp(sample4)),
                     cPlotNavigator._get_format(numpy.ptp(sample4)))
    self.assertEqual('%.6f',\
                     cPlotNavigator._get_format(numpy.ptp(sample5)),
                     cPlotNavigator._get_format(numpy.ptp(sample5)))

  @classmethod
  def tearDownClass(cls):
    #to remove dummy xml and npy files
    xmls = [ f for f in os.listdir(".") if f.endswith(".xml") ]
    for xml in xmls:
      os.remove(xml)

    npys = [ f for f in os.listdir(".") if f.endswith(".npy") ]
    for npy in npys:
      os.remove(npy)
    return


if  __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()