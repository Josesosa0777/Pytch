from datavis import pyglet_workaround  # necessary as early as possible (#164)

import os
import sys
import os.path
import shutil
import unittest
import cStringIO

import numpy
import pyglet
from pyglet import app

from PIL import ImageGrab
from PySide import QtGui, QtCore, QtTest

from datavis.VideoNavigator import cVideoNavigator
from datavis.GroupParam import cGroupParam
from datavis.OpenGLutil import EDGE

video = 'c:/KBData/measurement/test/CVR3_B1_2011-02-10_16-53_020.avi'

if not os.path.isfile(video):
  sys.stderr.write('Test skipped,\n%s is not present\n' %(video))
  sys.exit(1)

MS         = 10      # default marker size
MEW        =  1      # default marker edge width
MEC        = 'k'     # default marker edge color
MFC        = 'None'  # default marker face color (transparent)
COL        = 'k'     # default color
LS         = ''      # default line style
LW         =  1      # default line width
ALP        =  1.0    # default alpha channel value

groups = {
            'FooGroup' : cGroupParam((1, 2), '1', False, False),
            'BarGroup' : cGroupParam((0, 3), '2', True, False),
            'BazGroup' : cGroupParam((0, 5), '3', False, True),
            'EggGroup' : cGroupParam((0, 4), '4', True, True),
          }

group_key_2_pyglet_key_code = {
                              '1' : pyglet.window.key._1,
                              '2' : pyglet.window.key._2,
                              '3' : pyglet.window.key._3,
                              '4' : pyglet.window.key._4,
                          }

marker = {'CVR3_LOC_VALID': ('CVR3_LOC - Valid',
                            ( dict( shape='YupsideDown', type=EDGE, color=COL,
                                    lw=LW, ),)),}

x = numpy.arange(50.0, 71.0, 0.05)
y = numpy.arange(0.0, 21.0, 0.05)

Time = numpy.arange(0.0, 42.0, 0.1)
time = numpy.arange(21.0, 63.0, 0.1)

obj = {
         'dx': x,
         'dy': y,
         'label': 'object',
         'type': 'CVR3_LOC_VALID',
         'color': (90, 60, 90) ,
      }

other_obj = {
         'dx': y,
         'dy': x,
         'label': 'object',
         'type': 'CVR3_LOC_VALID',
         'color': (90, 60, 90) ,
      }

lane = {
          'range' : time,
          'C0' : y,
          'C1' : x,
       }

class Build(unittest.TestCase):
  def setUp(self):
    self.navigator = cVideoNavigator(video, {})
    self.init_navigator()
    return

  def init_navigator(self):
    self.navigator.setLegend(marker)
    self.navigator.addGroups(groups)
    self.navigator.setObjects(time, [obj])
    self.navigator.setSignal('x', time, x, unit='m')
    self.navigator.setLanes(time, [lane])

    self.navigator.start()
    return

  def tearDown(self):
    self.navigator.close()
    return

class TestBaseNavigatorFunctions(Build):
  def test_play(self):
    self.navigator.play(2.0)
    self.assertTrue(self.navigator.player.playing())
    return

  def test_pause(self):
    self.navigator.play(2.0)
    self.assertTrue(self.navigator.player.playing())
    self.navigator.pause(3.0)
    self.assertFalse(self.navigator.player.playing())
    self.assertAlmostEqual(self.navigator.player.objseektime, 3.0)
    return

  def test_seek(self):
    self.navigator.seek(5.0)
    self.assertAlmostEqual(self.navigator.player.objseektime, 5.0)
    return

  def test_geometry(self):
    new_geom = '800x600+100+100'
    self.navigator.setWindowGeometry(new_geom)
    self.assertAlmostEqual(new_geom, self.navigator.getWindowGeometry())
    return

  def test_set_window_title(self):
    new_title = 'Foo'
    self.navigator.setWindowTitle(new_title)
    self.assertEqual(new_title, self.navigator.getWindowTitle())
    return

class TestSignals(Build):
  def init_navigator(self):
    self.args = None

    self.navigator.closeSignal.signal.connect(self.saveArgs)
    self.navigator.playSignal.signal.connect(self.saveArgs)
    self.navigator.pauseSignal.signal.connect(self.saveArgs)
    self.navigator.seekSignal.signal.connect(self.saveArgs)
    self.navigator.setROISignal.signal.connect(self.saveArgs)
    self.navigator.selectGroupSignal.signal.connect(self.saveArgs)
    self.navigator.setXLimOnlineSignal.signal.connect(self.saveArgs)

    Build.init_navigator(self)
    return

  def saveArgs(self, *args):
    self.args = args
    return

  def test_close_signal(self):
    layout = self.navigator.getWindowGeometry()
    self.navigator.close()
    QtCore.QCoreApplication.processEvents()
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

  def test_selectGroup_signal(self):
    self.navigator.onSelectGroup('FooGroup')
    self.assertAlmostEqual(self.args, ('FooGroup', ))
    return

  def tearDown(self):
    self.navigator.closeSignal.signal.disconnect()
    self.navigator.playSignal.signal.disconnect()
    self.navigator.pauseSignal.signal.disconnect()
    self.navigator.seekSignal.signal.disconnect()
    self.navigator.setROISignal.signal.disconnect()
    self.navigator.selectGroupSignal.signal.disconnect()
    self.navigator.setXLimOnlineSignal.signal.disconnect()
    Build.tearDown(self)
    return

class TestKeyPress(Build):
  def test_space_press(self):
    self.navigator.player.on_key_press(pyglet.window.key.SPACE,
                                       pyglet.window.key.SPACE)
    self.assertTrue(self.navigator.player.playing())
    self.navigator.player.on_key_press(pyglet.window.key.SPACE,
                                       pyglet.window.key.SPACE)
    self.assertFalse(self.navigator.player.playing())
    return

  def test_page_up_press(self):
    speed = self.navigator.player.speed
    if speed < 16.0:
      speed *= 2.0
      if speed == 1.0:
        speed *= 2.0
    self.navigator.player.on_key_press(pyglet.window.key.PAGEUP,
                                       pyglet.window.key.PAGEUP)
    self.assertAlmostEqual(speed, self.navigator.player.speed)
    return

  def test_page_down_press(self):
    speed = self.navigator.player.speed
    if speed > 1/16.0:
      speed /= 2.0
      if speed == 1.0:
        speed /= 2.0
    self.navigator.player.on_key_press(pyglet.window.key.PAGEDOWN,
                                       pyglet.window.key.PAGEDOWN)
    self.assertAlmostEqual(speed, self.navigator.player.speed)
    return

  def test_f1_press(self):
    self.navigator.player.on_key_press(pyglet.window.key.F1,
                                       pyglet.window.key.F1)
    self.assertTrue(self.navigator.player.showhelplabel)
    self.navigator.player.on_key_press(pyglet.window.key.F1,
                                       pyglet.window.key.F1)
    self.assertFalse(self.navigator.player.showhelplabel)
    return

  def test_f2_press(self):
    self.navigator.player.on_key_press(pyglet.window.key.F2,
                                       pyglet.window.key.F2)
    self.assertTrue(self.navigator.player.showstatuslabel)
    self.navigator.player.on_key_press(pyglet.window.key.F2,
                                       pyglet.window.key.F2)
    self.assertFalse(self.navigator.player.showstatuslabel)
    return

  def test_f3_press(self):
    self.navigator.player.on_key_press(pyglet.window.key.F3,
                                       pyglet.window.key.F3)
    self.assertTrue(self.navigator.player.showLegend)
    self.navigator.player.on_key_press(pyglet.window.key.F3,
                                       pyglet.window.key.F3)
    self.assertFalse(self.navigator.player.showLegend)
    return

  def test_f4_press(self):
    self.navigator.player.on_key_press(pyglet.window.key.F4,
                                       pyglet.window.key.F4)
    self.assertTrue(self.navigator.player.showSignals)

    t = self.navigator.player.objseektime
    ndx = max(0, time.searchsorted(t, side='right') -1)

    value = x[ndx]
    label = "\n%s: % .1f %s" %('x', value, 'm')

    self.assertEqual(label, self.navigator.player.signallabel.text)

    self.navigator.player.on_key_press(pyglet.window.key.F4,
                                       pyglet.window.key.F4)
    self.assertFalse(self.navigator.player.showSignals)
    return

  def test_motion_left(self):
    self.navigator.seek(5.0)
    time = self.navigator.player.gettime()
    self.navigator.player.on_key_press(pyglet.window.key.MOTION_LEFT,
                                       pyglet.window.key.T)
    self.navigator.player.on_key_release(pyglet.window.key.MOTION_LEFT,
                                        pyglet.window.key.T)
    self.assertGreater(time, self.navigator.player.gettime())
    return

  def test_motion_right(self):
    self.navigator.seek(5.0)
    time = self.navigator.player.gettime()
    self.navigator.player.on_key_press(pyglet.window.key.MOTION_RIGHT,
                                       pyglet.window.key.T)
    self.navigator.player.on_key_release(pyglet.window.key.MOTION_RIGHT,
                                        pyglet.window.key.T)
    self.assertLess(time, self.navigator.player.gettime())
    return

  def test_t_press(self):
    self.navigator.player.on_key_press(pyglet.window.key.T,
                                       pyglet.window.key.T)
    self.assertFalse(self.navigator.player.showtimelabel)
    self.navigator.player.on_key_press(pyglet.window.key.T,
                                       pyglet.window.key.T)
    self.assertTrue(self.navigator.player.showtimelabel)
    return

  def test_q_press(self):
    self.navigator.player.on_key_press(pyglet.window.key.Q,
                                       pyglet.window.key.T)
    QtCore.QCoreApplication.processEvents()
    clip_board_data = ImageGrab.grabclipboard()
    clip_board_data.save('fig.png')

    pics = [ f for f in os.listdir(".") if f.endswith(".png") ]
    self.assertEqual(pics, ['fig.png'])
    file_syze = os.stat('fig.png').st_size
    self.assertGreater(file_syze, 0)
    return

  def test_n_press(self):
    self.navigator.player.on_key_press(pyglet.window.key.N,
                                       pyglet.window.key.T)
    self.assertTrue(self.navigator.player.lanesenabled)

    while self.navigator.player.lanetodisplay < \
          len(self.navigator.player.lanes) -1:
      self.navigator.player.on_key_press(pyglet.window.key.N,
                                       pyglet.window.key.T)

    self.navigator.player.on_key_press(pyglet.window.key.N,
                                       pyglet.window.key.T)
    self.assertFalse(self.navigator.player.lanesenabled)
    return

  def test_s_press(self):
    self.navigator.player.on_key_press(pyglet.window.key.S,
                                       pyglet.window.key.T)
    self.assertTrue(self.navigator.player.customspeed)

    self.navigator.player.on_key_press(pyglet.window.key.S,
                                       pyglet.window.key.T)
    self.assertFalse(self.navigator.player.customspeed)
    return

  def test_h_press(self):
    self.navigator.player.on_key_press(pyglet.window.key.H,
                                       pyglet.window.key.T)
    self.assertTrue(self.navigator.player.showLegend)
    self.navigator.player.on_key_press(pyglet.window.key.H,
                                       pyglet.window.key.T)
    self.assertFalse(self.navigator.player.showLegend)
    return

  def test_l_press(self):
    label_level = self.navigator.player.labellevel
    self.navigator.player.on_key_press(pyglet.window.key.L,
                                         pyglet.window.key.T)

    self.assertGreater(self.navigator.player.labellevel, label_level)

    while self.navigator.player.labellevel < 2:
      self.navigator.player.on_key_press(pyglet.window.key.L,
                                         pyglet.window.key.T)
    self.navigator.player.on_key_press(pyglet.window.key.L,
                                         pyglet.window.key.T)
    self.assertAlmostEqual(self.navigator.player.labellevel, 0)
    return

  def test_r_press(self):
    self.navigator.player.on_key_press(pyglet.window.key.R,
                                         pyglet.window.key.T)
    self.assertTrue(self.navigator.player.seekbackduringplayback)

    self.navigator.player.on_key_press(pyglet.window.key.R,
                                         pyglet.window.key.T)
    self.assertFalse(self.navigator.player.seekbackduringplayback)
    return

  def test_b_press(self):
    self.navigator.player.on_key_press(pyglet.window.key.B,
                                         pyglet.window.key.T)
    self.assertFalse(self.navigator.player.showVideoImage)

    self.navigator.player.on_key_press(pyglet.window.key.B,
                                         pyglet.window.key.T)
    self.assertTrue(self.navigator.player.showVideoImage)
    return

  def test_v_press(self):
    self.navigator.player.on_key_press(pyglet.window.key.V,
                                         pyglet.window.key.T)
    self.assertTrue(self.navigator.player.showFOV)

    self.navigator.player.on_key_press(pyglet.window.key.V,
                                         pyglet.window.key.T)
    self.assertFalse(self.navigator.player.showFOV)
    return

  def test_c_press(self):
    calib_index = self.navigator.player.calibrationindex
    self.navigator.player.on_key_press(pyglet.window.key.C,
                                         pyglet.window.key.T)

    self.assertGreater(self.navigator.player.calibrationindex, calib_index)

    while self.navigator.player.calibrationindex < \
          len(self.navigator.player.calibrations) - 1:
      self.navigator.player.on_key_press(pyglet.window.key.C,
                                         pyglet.window.key.T)
    self.navigator.player.on_key_press(pyglet.window.key.C,
                                         pyglet.window.key.T)
    self.assertAlmostEqual(self.navigator.player.calibrationindex, 0)
    return

  def test_m_press(self):
    self.navigator.player.on_key_press(pyglet.window.key.M,
                                         pyglet.window.key.T)

    self.assertTrue(self.navigator.player.calibration)
    return

  def test_calib_keys(self):
    self.navigator.player.on_key_press(pyglet.window.key.M,
                                         pyglet.window.key.T)

    fov = self.navigator.player.fov
    self.navigator.player.on_key_press(pyglet.window.key.A,
                                         pyglet.window.key.T)
    self.assertAlmostEqual(fov - 0.1, self.navigator.player.fov)

    self.navigator.player.on_key_press(pyglet.window.key.Q,
                                         pyglet.window.key.T)
    self.assertAlmostEqual(fov , self.navigator.player.fov)

    looktoy = self.navigator.player.looktoy
    self.navigator.player.on_key_press(pyglet.window.key.S,
                                         pyglet.window.key.T)
    self.assertAlmostEqual(looktoy - 0.001, self.navigator.player.looktoy)

    self.navigator.player.on_key_press(pyglet.window.key.W,
                                         pyglet.window.key.T)
    self.assertAlmostEqual(looktoy , self.navigator.player.looktoy)

    looktox = self.navigator.player.looktox
    self.navigator.player.on_key_press(pyglet.window.key.D,
                                         pyglet.window.key.T)
    self.assertAlmostEqual(looktox - 0.001, self.navigator.player.looktox)

    self.navigator.player.on_key_press(pyglet.window.key.E,
                                         pyglet.window.key.T)
    self.assertAlmostEqual(looktox , self.navigator.player.looktox)

    cameraz = self.navigator.player.cameraz
    self.navigator.player.on_key_press(pyglet.window.key.F,
                                         pyglet.window.key.T)
    self.assertAlmostEqual(cameraz - 0.001, self.navigator.player.cameraz)

    self.navigator.player.on_key_press(pyglet.window.key.R,
                                         pyglet.window.key.T)
    self.assertAlmostEqual(cameraz , self.navigator.player.cameraz)

    upx = self.navigator.player.upx
    self.navigator.player.on_key_press(pyglet.window.key.G,
                                         pyglet.window.key.T)
    self.assertAlmostEqual(upx - 0.001, self.navigator.player.upx)

    self.navigator.player.on_key_press(pyglet.window.key.T,
                                         pyglet.window.key.T)
    self.assertAlmostEqual(upx , self.navigator.player.upx)
    return

  def test_group_keys(self):
    for label in self.navigator.player.Labels:
      keycode, gn, visible = label.split(' ')
      gn = gn.replace(':', '')
      visible_2_text = 'On' if self.navigator.OrigVisibility[gn] else 'Off'
      self.assertEqual(visible_2_text, visible)

    for keycode in self.navigator.KeyCodes.keys():
      self.navigator.player.on_key_press(keycode, pyglet.window.key.T)

    for label in self.navigator.player.Labels:
      keycode, gn, visible = label.split(' ')
      gn = gn.replace(':', '')
      visible_2_text = 'On' if self.navigator.OrigVisibility[gn] else 'Off'
      self.assertNotEqual(visible_2_text, visible)
    return

  @classmethod
  def tearDownClass(cls):
    pics = [ f for f in os.listdir(".") if f.endswith(".png") ]
    for pic in pics:
      os.remove(pic)
    return

class TestFigureSave(Build):
  def test_copy_content_to_file(self):
    self.navigator.copyContentToFile('fig.png')
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

class TestConfiguringNavigator(Build):
  def init_navigator(self):
    return

  def test_add_object(self):
    self.navigator.setLegend(marker)
    self.navigator.setObjects(time, [obj])
    self.navigator.start()

    self.assertEqual(len(self.navigator.player.objects), 1)
    object, idx = self.navigator.player.objects[0]
    self.assertEqual(obj, object)
    return

  def test_add_objects_same_time(self):
    self.navigator.setLegend(marker)
    objects = [obj, other_obj]
    self.navigator.setObjects(time, objects)
    self.navigator.start()

    self.assertEqual(len(self.navigator.player.objects), len(objects))

    for object, idx in self.navigator.player.objects:
      same_obj = False
      for _obj in objects:
        for key, item in _obj.iteritems():
          same_obj = key in object
          if not same_obj: continue
          same_obj = numpy.array_equal(item, object[key]) if type(item) \
          is numpy.ndarray else item is object[key]
        if same_obj: break
      self.assertTrue(same_obj)

    self.assertEqual(len(self.navigator.player.times), 1)
    return

  def test_add_objects_diff_time(self):
    self.navigator.setLegend(marker)

    self.navigator.setObjects(time, [obj])
    self.navigator.setObjects(Time, [other_obj])
    self.navigator.start()

    self.assertEqual(len(self.navigator.player.objects), 2)
    self.navigator.start()
    self.assertEqual(len(self.navigator.player.times), 2)
    return

  def test_add_lane(self):
    self.navigator.setLanes(time, [lane])
    self.navigator.start()

    self.assertEqual(len(self.navigator.player.lanes), 1)
    _lane, idx = self.navigator.player.lanes[0]
    self.assertEqual(_lane, lane)

    self.assertEqual(len(self.navigator.player.times), 1)
    return

  def add_same_time(self):
    Build.init_navigator(self)

    self.assertEqual(len(self.navigator.player.times), 1)
    return

  def test_add_signal(self):
    self.navigator.setSignal('x', time, x, unit='m')
    self.navigator.start()

    self.navigator.player.on_key_press(pyglet.window.key.F4,
                                       pyglet.window.key.F4)
    self.assertTrue(self.navigator.player.showSignals)

    t = self.navigator.player.objseektime
    ndx = max(0, time.searchsorted(t, side='right') -1)

    value = x[ndx]
    label = "\n%s: % .1f %s" %('x', value, 'm')
    self.assertEqual(label, self.navigator.player.signallabel.text)

    t = 5.0

    self.navigator.seek(t)

    ndx = max(0, time.searchsorted(t, side='right') -1)

    value = x[ndx]
    label = "\n%s: % .1f %s" %('x', value, 'm')
    self.assertEqual(label, self.navigator.player.signallabel.text)

    self.assertEqual(len(self.navigator.player.times), 1)
    return

  def test_add_group(self):
    self.navigator.setLegend(marker)
    self.navigator.addGroups(groups)
    self.navigator.start()

    for group_name, group_param in groups.iteritems():
      self.assertIn(group_name, self.navigator.Groups)
      self.assertIn(group_name, self.navigator.Toggles)
      self.assertEqual(self.navigator.Groups[group_name], group_param.Types)

      pyglet_key =  group_key_2_pyglet_key_code[group_param.KeyCode]

      self.assertIn(pyglet_key, self.navigator.KeyCodes)
      self.assertEqual(group_name, self.navigator.KeyCodes[pyglet_key])

      self.assertIn(group_name, self.navigator.OrigVisibility)
      self.assertEqual(self.navigator.OrigVisibility[group_name],
                       group_param.Visible)
    return

  def test_add_legend(self):
    self.navigator.setLegend(marker)
    self.navigator.start()

    self.assertEqual(len(self.navigator.player.legend.markers), len(marker))

    for label, style in marker.iteritems():
      self.assertIn(style, self.navigator.player.legend.markers)
    return

  def test_add_accelcomp(self):
    self.navigator.setAccelComp(time, x)
    self.navigator.start()

    accelcomp, idx = self.navigator.player.accelcomp
    self.assertTrue(numpy.array_equal(x, accelcomp))

    self.assertEqual(len(self.navigator.player.times), 1)
    return

  def test_set_displaytime(self):
    self.navigator.setDisplayTime(time, Time)
    self.navigator.start()

    self.assertEqual(self.navigator.player.displaytime, (time, Time))

    t = 30.0
    self.navigator.seek(t)

    disptime = numpy.interp([t], Time, time)[0]
    text = '%07.3f (NO OBJECTS)' % (disptime)
    self.assertEqual(text, self.navigator.player.timelabel.text)

    self.navigator.setDisplayTime(time, y)

    self.assertEqual(self.navigator.player.displaytime, (time, y))

    t = 30.0
    self.navigator.seek(t)

    disptime = numpy.interp([t], y, time)[0]
    text = '%07.3f (NO OBJECTS)' % (disptime)
    self.assertEqual(text, self.navigator.player.timelabel.text)
    return

if  __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()