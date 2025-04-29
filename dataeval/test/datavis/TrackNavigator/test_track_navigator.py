import os
import os.path
import shutil
import unittest
import cStringIO

import numpy
import matplotlib
from PIL import ImageGrab
from PySide import QtGui, QtCore, QtTest

from datavis.TrackNavigator import cTrackNavigator, circle
from datavis.GroupParam import cGroupParam
from measparser import ffmpeg

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
          
group_key_2_qt_key_code = {
                              '1' : QtCore.Qt.Key_1,
                              '2' : QtCore.Qt.Key_2,
                              '3' : QtCore.Qt.Key_3,
                              '4' : QtCore.Qt.Key_4,
                          }

marker = {'CVR3_LOC_VALID': ('CVR3_LOC - Valid', dict(marker='2', ms=MS, 
                                  mew=MEW*2, mec=MEC, mfc=MFC, color=COL, ls=LS, 
                                  lw=LW, alpha=ALP)),}

x = numpy.arange(50.0, 71.0, 0.05)
y = numpy.arange(0.0, 21.0, 0.05)

Time    = numpy.arange(0.0, 42.0, 0.1)
x_data = numpy.arange(50.0, 71.0, 0.05)
y_data = numpy.arange(11.0, 32.0, 0.05)
Coeff   = numpy.ones_like(Time)
R = 150.0
O = 1.5
Radius = R * Coeff
Offset = O * Coeff

Tracks = [
          ['curve-left-letf-side',  'r',  1,  1],
          ['curve-left-right-side', 'b',  1, -1],
          ['curve-right-left-side', 'g', -1,  1],
          ['curve-right-right-side','y', -1, -1],
        ]

angle_left, angle_right = -15.0, 15.0

Obj = {
         'dx': x,
         'dy': y,
         'label': 'object',
         'type': 'CVR3_LOC_VALID',
         'color': (90, 60, 90) ,
      }

class Build(unittest.TestCase):
  def setUp(self):
    self.navigator = cTrackNavigator()
    self.init_navigator()
    return

  def init_navigator(self):
    for Name, Color, r, o in Tracks:
      Track = self.navigator.addTrack(Name, Time, color=Color)
      FuncName = Track.addFunc(circle, LengthMax=self.navigator.LengthMax)
      Track.addParam(FuncName, 'R',      Time, r*Radius)
      Track.addParam(FuncName, 'Offset', Time, o*Offset)
    self.navigator.addDataset(Time, x_data, y_data, label='dataset')
    self.navigator.setViewAngle(angle_left, angle_right)
    self.navigator.setLegend(marker)
    self.navigator.addObject(Time, Obj)
    self.navigator.addGroups(groups)
    self.navigator.start()
    return
    
  def tearDown(self):
    self.navigator.close()
    return

class TestKeyPress(Build):
  def setUp(self):
    Build.setUp(self)
    renderer = self.navigator.fig.canvas.get_renderer()
    self.navigator.help.draw(renderer)
    return

  def test_k_press(self):
    #to avoid to change the xscale type from linear
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_K)
    for ax in self.navigator.fig.axes:
      self.assertEqual(ax.get_xscale(), 'linear')
    return

  def test_l_press(self):
    #to avoid to change the yscale type from linear
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_L)
    for ax in self.navigator.fig.axes:
      self.assertEqual(ax.get_yscale(), 'linear')
    return

  def test_a_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_A)
    self.assertEqual(self.navigator.aspectRatio, 'auto')
    self.assertEqual(self.navigator.SP.get_aspect(), 'auto')

    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_A)
    self.assertEqual(self.navigator.aspectRatio, 'equal')
    self.assertEqual(self.navigator.SP.get_aspect(), 'equal')
    return

  def test_f1_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_F1)
    self.assertTrue(self.navigator.help.get_visible())

    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_F1)
    self.assertFalse(self.navigator.help.get_visible())
    return

  def test_q_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_Q)
    clip_board_data = ImageGrab.grabclipboard()
    clip_board_data.save('fig.png')
    pics = [ f for f in os.listdir(".") if f.endswith(".png") ]
    self.assertEqual(pics, ['fig.png'])
    file_syze = os.stat('fig.png').st_size
    self.assertGreater(file_syze, 0)
    return

  def test_h_press(self):
    for ax in self.navigator.fig.axes:
      legend = ax.get_legend()
      self.assertFalse(legend.get_visible())

    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_H)
    for ax in self.navigator.fig.axes:
      legend = ax.get_legend()
      self.assertTrue(legend.get_visible())
    return

  def test_point_press(self):
    self.navigator.ObjInfo.set_visible(True)
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_Period)
    self.assertFalse(self.navigator.showObjInfo)
    self.assertFalse(self.navigator.ObjInfo.get_visible())

    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_Period)
    self.assertTrue(self.navigator.showObjInfo)
    return
    
  def test_z_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_Z)
    self.assertTrue(self.navigator.showPosition)

    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_Z)
    self.assertFalse(self.navigator.showPosition)
    return
    
  def test_u_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_U)
    self.assertEqual(self.navigator.stateLabel, 'CUSTOM')

    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_U)
    self.assertEqual(self.navigator.stateLabel, 'NONE')

    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_U)
    self.assertEqual(self.navigator.stateLabel, 'ALL')
    return
    
  def test_i_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_I)
    self.assertEqual(self.navigator.DatasetActivity, 'CUSTOM')

    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_I)
    self.assertEqual(self.navigator.DatasetActivity, 'NONE')

    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_I)
    self.assertEqual(self.navigator.DatasetActivity, 'ALL')
    return
    
  def test_v_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_V)
    for point in self.navigator.FOVs:
      self.assertFalse(point.get_visible())

    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_V)
    for point in self.navigator.FOVs:
      self.assertTrue(point.get_visible())
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
    
  def test_groups_key_press(self):
    group_2_action = {}
    for action in self.navigator.GroupMenu.actions():
      orig_visibility = self.navigator.OrigVisibility[action.text()]
      self.assertEqual(orig_visibility, action.isChecked())

    for keycode in self.navigator.KeyCodes.keys():
      qt_key = group_key_2_qt_key_code[keycode]
      QtTest.QTest.keyPress(self.navigator, qt_key)

    for action in self.navigator.GroupMenu.actions():
      orig_visibility = self.navigator.OrigVisibility[action.text()]
      self.assertNotEqual(orig_visibility, action.isChecked())
    return

  @classmethod
  def tearDownClass(cls):
    pics = [ f for f in os.listdir(".") if f.endswith(".png") ]
    for pic in pics:
      os.remove(pic)
    return

class TestFigureSave(Build):
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

class TestMenus(Build):
  def test_track_menu(self):
    for track_menu_item in self.navigator.TrackMenu.actions():
      track_name = track_menu_item.text()

      tracks = [track for track_key, track in self.navigator.Tracks.iteritems()
                       if track_key[0] == track_name ]

      for track in tracks:
        self.assertEqual(track.Visible, track_menu_item.isChecked())

    for track_menu_item in self.navigator.TrackMenu.actions():
      track_menu_item.trigger()

      track_name = track_menu_item.text()

      tracks = [track for track_key, track in self.navigator.Tracks.iteritems()
                       if track_key[0] == track_name ]

      for track in tracks:
        self.assertEqual(track.Visible, track_menu_item.isChecked())

    return

  def test_reset_track_menu(self):
    orig_menu_state = {}
    for track_menu_item in self.navigator.TrackMenu.actions():
      orig_menu_state[track_menu_item.text()] = track_menu_item.isChecked()
      track_menu_item.trigger()

    self.navigator.resetTrackMenu()  

    for track_menu_item in self.navigator.TrackMenu.actions():
      self.assertEqual(track_menu_item.isChecked(), 
                       orig_menu_state[track_menu_item.text()])
    return

  def test_group_menu(self):
    for action in self.navigator.GroupMenu.actions():
      orig_visibility = self.navigator.OrigVisibility[action.text()]
      self.assertEqual(action.isChecked(), orig_visibility)
      action.trigger()

    for action in self.navigator.GroupMenu.actions():
      orig_visibility = self.navigator.OrigVisibility[action.text()]
      self.assertNotEqual(action.isChecked(), orig_visibility)
    return

  def test_reset_group_menu(self):
    for action in self.navigator.GroupMenu.actions():
      action.trigger()

    self.navigator.resetGroupMenu()

    for action in self.navigator.GroupMenu.actions():
      orig_visibility = self.navigator.OrigVisibility[action.text()]
      self.assertEqual(action.isChecked(), orig_visibility)
    return

  def test_dataset_menu(self):
    for action, dataset in zip(self.navigator.DatasetMenu.actions(), 
                                                      self.navigator.Datasets):
        self.assertEqual(dataset.getVisible(), action.isChecked())
        action.trigger()

    for action, dataset in zip(self.navigator.DatasetMenu.actions(), 
                                                      self.navigator.Datasets):
        self.assertEqual(dataset.getVisible(), action.isChecked())
    return

class TestConfiguringNavigator(Build):
  def init_navigator(self):
    return

  def test_set_axes_limits(self):
    self.navigator.start()
    self.navigator.setAxesLimits([5.0, -5.0])
    left, right = self.navigator.SP.get_xlim()
    self.assertAlmostEqual(left, 5.0)
    self.assertAlmostEqual(right, -5.0)
    return

  def test_add_groups(self):
    self.navigator.addGroups(groups)
    self.navigator.start()
    group_visible_in_menu = {}

    for action in self.navigator.GroupMenu.actions():
      group_visible_in_menu[action.text()] = action.isChecked()

    for group_name, group_param in groups.iteritems():
      self.assertIn(group_name, self.navigator.Groups)
      self.assertIn(group_name, group_visible_in_menu)
      self.assertEqual(self.navigator.Groups[group_name], group_param.Types)

      self.assertIn(group_param.KeyCode, self.navigator.KeyCodes)
      self.assertEqual(group_name, self.navigator.KeyCodes[group_param.KeyCode])

      self.assertIn(group_name, self.navigator.OrigVisibility)
      self.assertEqual(self.navigator.OrigVisibility[group_name], 
                       group_param.Visible)
      self.assertEqual(group_visible_in_menu[group_name], group_param.Visible)
    return

  def test_set_legend(self):
    self.navigator.setLegend(marker)
    self.navigator.start()

    for type, (legendname, style) in marker.iteritems():
      self.assertEqual(self.navigator.Markers[type], style)

    for ax in self.navigator.fig.axes:
      legend = ax.get_legend()
      self.assertFalse(legend.get_visible())
      for text_legend, marker_legend in zip(legend.get_texts(), 
                                            marker.values()):
        self.assertEqual(text_legend.get_text(), marker_legend[0])
    return

  def test_set_view_angle(self):
    self.navigator.setViewAngle( angle_left, angle_right, GroupName='FooGroup')
    self.navigator.start()
    bindzones = [child for child in self.navigator.SP.get_children() 
                       if type(child) == matplotlib.patches.PathPatch]

    #from tracknavigator.setViewAngle
    MAXDIST = 5000  # arbitrary large number
    tan_phiLeft   = numpy.tan(angle_left  / 180.0 * numpy.pi)
    tan_phiRight  = numpy.tan(angle_right / 180.0 * numpy.pi)
    vertices  = numpy.array([[0,0],
                            [-MAXDIST*tan_phiLeft,  MAXDIST],
                            [-MAXDIST*tan_phiLeft, -MAXDIST],
                            [-MAXDIST*tan_phiRight,-MAXDIST],
                            [-MAXDIST*tan_phiRight, MAXDIST],
                            [0,0]])

    for bindzone in bindzones: 
      self.assertEqual(self.navigator.BindZones['FooGroup'], bindzone)
      path_vertices = bindzone.get_path().vertices
      self.assertTrue(numpy.array_equal(path_vertices, vertices))
    return

  def test_add_object(self):
    self.navigator.setLegend(marker)
    self.navigator.addObject(Time, Obj)
    self.navigator.start()
    for t, dX, dY, Color, Type, Point, Label, LabelBox, ShowLabel in \
        self.navigator.Objects:

      self.assertFalse(ShowLabel)
      self.assertEqual(Label, Obj['label'])

      self.assertTrue(numpy.array_equal(t, Time))
      self.assertTrue(numpy.array_equal(dX, Obj['dy']))
      self.assertTrue(numpy.array_equal(dY, Obj['dx']))

      annotations = [child for child in self.navigator.SP.get_children() 
                           if type(child) == matplotlib.text.Annotation]

      for annotation in annotations[1:]:
         self.assertEqual(annotation.get_text(), Obj['label'])

      ndx =  max(0, t.searchsorted(0.0, side='right') -1) 
      x = Obj['dy'][ndx]
      y = Obj['dx'][ndx]

      point_x, point_y = Point.get_data()

      self.assertAlmostEqual(x, point_x)
      self.assertAlmostEqual(y, point_y)
    return

  def test_add_dataset(self):
    self.navigator.setLegend(marker)
    self.navigator.addDataset(Time, x, y_data, label='dataset')
    self.navigator.start()
    for dataset in self.navigator.Datasets:
      self.assertTrue(dataset.getVisible())
      self.assertTrue(numpy.array_equal(dataset.Time, Time))
      self.assertTrue(numpy.array_equal(dataset.Xdata, 
                      y_data.reshape(y_data.size, 1, 1).tolist()))
      self.assertTrue(numpy.array_equal(dataset.Ydata, 
                      x_data.reshape(x_data.size, 1, 1).tolist()))

      ndx =  max(0, Time.searchsorted(0.0, side='right') -1)
      for line in dataset.LineObjects:
        line_x, line_y = line.get_data()
        self.assertAlmostEqual(line_x[ndx], y_data[ndx])
        self.assertAlmostEqual(line_y[ndx], x_data[ndx])
    return

  def test_add_track(self):
    for Name, Color, r, o in Tracks:
      Track = self.navigator.addTrack(Name, Time, color=Color)
      FuncName = Track.addFunc(circle, LengthMax=self.navigator.LengthMax)
      Track.addParam(FuncName, 'R',      Time, r*Radius)
      Track.addParam(FuncName, 'Offset', Time, o*Offset)
    self.navigator.start()
    for Name, Color, r, o in Tracks:
      self.assertIn((Name, Color), self.navigator.Tracks)
      self.assertTrue(self.navigator.Tracks[(Name, Color)].Visible)
      track = self.navigator.Tracks[(Name, Color)].Tracks[0]
      visible = track.Line.get_visible()
      line_x, line_y = track.Line.get_data()
      x, y = circle(R*r, O*o, LengthMax=self.navigator.LengthMax)
      self.assertTrue(numpy.array_equal(line_x, x))
      self.assertTrue(numpy.array_equal(line_y, y))
    return

class TestTrackRecoding(Build):
  def test_record_created(self):
    # Activate X key
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_X)

    # Try to make it run for a few rounds
    self.navigator.seekWindow()
    self.navigator.seekWindow()

    # close recorder
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_X)

    # Assert new files
    self.assertTrue(os.path.exists(os.path.join("recording", "TrackRecord_0.avi")))

    # Okay, cleanup.
    if os.path.exists("recording\\TrackRecord_0.avi"):
      os.remove("recording\\TrackRecord_0.avi")

    # Also check file cleanup
    self.assertFalse(os.path.exists(os.path.join("recording", "TrackRecord_0.avi")))
    self.assertFalse(os.path.exists("TrackRecord_output.log"))

    return

  def test_record_closed_halt(self):

    # Activate X key
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_X)

    # Try to run for a few rounds
    self.navigator.seekWindow()
    self.navigator.seekWindow()

    # Close nav
    self.navigator.close()

    # Assert new files
    self.assertTrue(os.path.exists(os.path.join("recording", "TrackRecord_0.avi")))

    # Okay, cleanup.
    if os.path.exists("recording\\TrackRecord_0.avi"):
      os.remove("recording\\TrackRecord_0.avi")

    # Also check file cleanup
    self.assertFalse(os.path.exists(os.path.join("recording", "TrackRecord_0.avi")))
    self.assertFalse(os.path.exists("TrackRecord_output.log"))
    return

  def test_recording_unavailable(self):

    # Try to record without starting
    self.navigator.seekWindow()
    self.navigator.seekWindow()

    # Assert no new files
    self.assertFalse(os.path.exists(os.path.join("recording", "TrackRecord_0.avi")))
    self.assertFalse(os.path.exists("TrackRecord_output.log"))

    return

  def test_multiple_restarts(self):

    # Do the same as record_created
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_X)
    self.navigator.seekWindow()
    self.navigator.seekWindow()
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_X)

    # Do it once more
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_X)
    self.navigator.seekWindow()
    self.navigator.seekWindow()
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_X)

    # assert check for x2 files
    self.assertTrue(os.path.exists(os.path.join("recording", "TrackRecord_0.avi")))
    self.assertTrue(os.path.exists(os.path.join("recording", "TrackRecord_1.avi")))

    # Cleanup
    if os.path.exists("recording\\TrackRecord_0.avi"):
      os.remove("recording\\TrackRecord_0.avi")
    if os.path.exists("recording\\TrackRecord_1.avi"):
      os.remove("recording\\TrackRecord_1.avi")

    self.assertFalse(os.path.exists(os.path.join("recording", "TrackRecord_0.avi")))
    self.assertFalse(os.path.exists(os.path.join("recording", "TrackRecord_1.avi")))
    self.assertFalse(os.path.exists("TrackRecord_output.log"))

    return

  def tearDown(self):
    Build.tearDown(self)
    if os.path.exists("recording"):
      os.rmdir("recording")

if  __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()
