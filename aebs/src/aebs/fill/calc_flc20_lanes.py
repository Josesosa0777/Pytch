# -*- dataeval: init -*-

import copy
import numpy as np
from collections import OrderedDict

import interface
from measparser.signalgroup import SignalGroup
from primitives.lane import PolyClothoid, VideoLineProp, LaneData

def convert_sensor_offset(refpoint_x, refpoint_y):
  dx0 = -refpoint_x
  dy0 =  refpoint_y
  return dx0, dy0

def convert_coeffs(offset, heading, curvature, curvature_rate):
  c0 = -offset
  c1 = -heading
  c2 = -curvature
  c3 = -curvature_rate
  return c0, c1, c2, c3

def convert_view_range(view_range):
  return view_range

def create_line(time, c0, c1, c2, c3, view_range, dx0, dy0, winner):
  if winner == 'trajectory_generator_flx20_autobox':
    line = Flc20Line(time, c0, c1, c2, c3, view_range)
  else:
    c0, c1, c2, c3 = convert_coeffs(c0, c1, c2, c3)
    view_range = convert_view_range(view_range)
    line = Flc20Line.from_physical_coeffs(time, c0, c1, c2, c3, view_range)
  return line

class Flc20Line(PolyClothoid, VideoLineProp):
  def __init__(self, time, c0, c1, c2, c3, view_range):
    PolyClothoid.__init__(self, time, c0, c1, c2, c3)
    VideoLineProp.__init__(self, time, view_range, None, None)
    return

  def translate(self, dx, dy):
    newobj = copy.copy(self)
    newobj = PolyClothoid.translate(newobj, dx, dy)
    newobj = VideoLineProp.translate(newobj, dx, dy)
    return newobj

class Calc(interface.iCalc):
  dep = ('calc_flc20_common_time',)

  def check(self):
    sgs = OrderedDict([
      ('flc20-2014b-orig', {
        'RefPoint_X':                 ('Video_Data_General_A', 'RefPoint_X'),
        'RefPoint_Y':                 ('Video_Data_General_A', 'RefPoint_Y'),

        'Position_Right':             ('Video_Line_Right_A', 'C0'),
        'Heading_Angle_Right':        ('Video_Line_Right_A', 'C1'),
        'Curvature_Right':            ('Video_Line_Right_A', 'C2'),
        'Curvature_Derivative_Right': ('Video_Line_Right_A', 'C3'),
        'View_Range_Right':           ('Video_Line_Right_B', 'View_Range'),
        'Position_Left':              ('Video_Line_Left_A',  'C0'),
        'Heading_Angle_Left':         ('Video_Line_Left_A',  'C1'),
        'Curvature_Left':             ('Video_Line_Left_A',  'C2'),
        'Curvature_Derivative_Left':  ('Video_Line_Left_A',  'C3'),
        'View_Range_Left':            ('Video_Line_Left_B',  'View_Range'),

        'Position_Right2':            ('Video_Line_Next_Right_A', 'C0'),
        'Heading_Angle_Right2':       ('Video_Line_Next_Right_A', 'C1'),
        'Curvature_Right2':           ('Video_Line_Next_Right_A', 'C2'),
        'Curvature_Derivative_Right2':('Video_Line_Next_Right_A', 'C3'),
        'View_Range_Right2':          ('Video_Line_Next_Right_B', 'View_Range'),
        'Position_Left2':             ('Video_Line_Next_Left_A',  'C0'),
        'Heading_Angle_Left2':        ('Video_Line_Next_Left_A',  'C1'),
        'Curvature_Left2':            ('Video_Line_Next_Left_A',  'C2'),
        'Curvature_Derivative_Left2': ('Video_Line_Next_Left_A',  'C3'),
        'View_Range_Left2':           ('Video_Line_Next_Left_B',  'View_Range'),
      }),
      ('flc20-2014a', {
        'RefPoint_X':                 ('Video_Data_General_A', 'RefPoint_X'),
        'RefPoint_Y':                 ('Video_Data_General_A', 'RefPoint_Y'),

        'Position_Right':             ('Video_Lane_Right_A', 'C0_Right_A'),
        'Heading_Angle_Right':        ('Video_Lane_Right_A', 'C1_Right_A'),
        'Curvature_Right':            ('Video_Lane_Right_A', 'C2_Right_A'),
        'Curvature_Derivative_Right': ('Video_Lane_Right_A', 'C3_Right_A'),
        'View_Range_Right':           ('Video_Lane_Right_B', 'View_Range_Right_B'),
        'Position_Left':              ('Video_Lane_Left_A',  'C0_Left_A'),
        'Heading_Angle_Left':         ('Video_Lane_Left_A',  'C1_Left_A'),
        'Curvature_Left':             ('Video_Lane_Left_A',  'C2_Left_A'),
        'Curvature_Derivative_Left':  ('Video_Lane_Left_A',  'C3_Left_A'),
        'View_Range_Left':            ('Video_Lane_Left_B',  'View_Range_Left_B'),

        'Position_Right2':            ('Video_Lane_Next_Right_A', 'C0_Next_Right_A'),
        'Heading_Angle_Right2':       ('Video_Lane_Next_Right_A', 'C1_Next_Right_A'),
        'Curvature_Right2':           ('Video_Lane_Next_Right_A', 'C2_Next_Right_A'),
        'Curvature_Derivative_Right2':('Video_Lane_Next_Right_A', 'C3_Next_Right_A'),
        'View_Range_Right2':          ('Video_Lane_Next_Right_B', 'View_Range_Next_Right_B'),
        'Position_Left2':             ('Video_Lane_Next_Left_A',  'C0_Next_Left_A'),
        'Heading_Angle_Left2':        ('Video_Lane_Next_Left_A',  'C1_Next_Left_A'),
        'Curvature_Left2':            ('Video_Lane_Next_Left_A',  'C2_Next_Left_A'),
        'Curvature_Derivative_Left2': ('Video_Lane_Next_Left_A',  'C3_Next_Left_A'),
        'View_Range_Left2':           ('Video_Lane_Next_Left_B',  'View_Range_Next_Left_B'),
      }),
      ('flc20', {
        'RefPoint_X':                 ('Video_Data_General_A', 'RefPoint_X'),
        'RefPoint_Y':                 ('Video_Data_General_A', 'RefPoint_Y'),

        'Position_Right':             ('Video_Lane_Right_A', 'Position_Right_A'),
        'Heading_Angle_Right':        ('Video_Lane_Right_A', 'Heading_Right_A'),
        'Curvature_Right':            ('Video_Lane_Right_A', 'Curvature_Right_A'),
        'Curvature_Derivative_Right': ('Video_Lane_Right_A', 'Curvature_Rate_Right_A'),
        'View_Range_Right':           ('Video_Lane_Right_B', 'View_Range_Right_B'),
        'Position_Left':              ('Video_Lane_Left_A',  'Position_Left_A'),
        'Heading_Angle_Left':         ('Video_Lane_Left_A',  'Heading_Left_A'),
        'Curvature_Left':             ('Video_Lane_Left_A',  'Curvature_Left_A'),
        'Curvature_Derivative_Left':  ('Video_Lane_Left_A',  'Curvature_Rate_Left_A'),
        'View_Range_Left':            ('Video_Lane_Left_B',  'View_Range_Left_B'),

        'Position_Right2':            ('Video_Lane_Next_Right_A', 'Position_Next_Right_A'),
        'Heading_Angle_Right2':       ('Video_Lane_Next_Right_A', 'Heading_Next_Right_A'),
        'Curvature_Right2':           ('Video_Lane_Next_Right_A', 'Curvature_Next_Right_A'),
        'Curvature_Derivative_Right2':('Video_Lane_Next_Right_A', 'Curvature_Rate_Next_Right_A'),
        'View_Range_Right2':          ('Video_Lane_Next_Right_B', 'View_Range_Next_Right_B'),
        'Position_Left2':             ('Video_Lane_Next_Left_A',  'Position_Next_Left_A'),
        'Heading_Angle_Left2':        ('Video_Lane_Next_Left_A',  'Heading_Next_Left_A'),
        'Curvature_Left2':            ('Video_Lane_Next_Left_A',  'Curvature_Next_Left_A'),
        'Curvature_Derivative_Left2': ('Video_Lane_Next_Left_A',  'Curvature_Rate_Next_Left_A'),
        'View_Range_Left2':           ('Video_Lane_Next_Left_B',  'View_Range_Next_Left_B'),
      }),
      ('flc20-bendix', {
        'RefPoint_X':                 ('Video_Data_General_A', 'RefPoint_X'),
        'RefPoint_Y':                 ('Video_Data_General_A', 'RefPoint_Y'),

        'Position_Right':             ('Video_Lane_Right_A', 'Position'),
        'Heading_Angle_Right':        ('Video_Lane_Right_A', 'Heading'),
        'Curvature_Right':            ('Video_Lane_Right_A', 'Curvature'),
        'Curvature_Derivative_Right': ('Video_Lane_Right_A', 'Curvature_Rate'),
        'View_Range_Right':           ('Video_Lane_Right_B', 'View_Range'),
        'Position_Left':              ('Video_Lane_Left_A',  'Position'),
        'Heading_Angle_Left':         ('Video_Lane_Left_A',  'Heading'),
        'Curvature_Left':             ('Video_Lane_Left_A',  'Curvature'),
        'Curvature_Derivative_Left':  ('Video_Lane_Left_A',  'Curvature_Rate'),
        'View_Range_Left':            ('Video_Lane_Left_B',  'View_Range'),

        'Position_Right2':            ('Video_Lane_Next_Right_A', 'Position'),
        'Heading_Angle_Right2':       ('Video_Lane_Next_Right_A', 'Heading'),
        'Curvature_Right2':           ('Video_Lane_Next_Right_A', 'Curvature'),
        'Curvature_Derivative_Right2':('Video_Lane_Next_Right_A', 'Curvature_Rate'),
        'View_Range_Right2':          ('Video_Lane_Next_Right_B', 'View_Range'),
        'Position_Left2':             ('Video_Lane_Next_Left_A',  'Position'),
        'Heading_Angle_Left2':        ('Video_Lane_Next_Left_A',  'Heading'),
        'Curvature_Left2':            ('Video_Lane_Next_Left_A',  'Curvature'),
        'Curvature_Derivative_Left2': ('Video_Lane_Next_Left_A',  'Curvature_Rate'),
        'View_Range_Left2':           ('Video_Lane_Next_Left_B',  'View_Range'),
      }),
      ('scam', {
        'RefPoint_X':                 ('Host_Vehicle',     'Refpoint_X'),
        'RefPoint_Y':                 ('Host_Vehicle',     'Refpoint_Y'),

        'Position_Right':             ('LKA_Right_Lane_A', 'Position'),
        'Heading_Angle_Right':        ('LKA_Right_Lane_B', 'Heading_Angle'),
        'Curvature_Right':            ('LKA_Right_Lane_A', 'Curvature'),
        'Curvature_Derivative_Right': ('LKA_Right_Lane_A', 'Curvature_Derivative'),
        'View_Range_Right':           ('LKA_Right_Lane_B', 'View_Range'),
        'Position_Left':              ('LKA_Left_Lane_A',  'Position'),
        'Heading_Angle_Left':         ('LKA_Left_Lane_B',  'Heading_Angle'),
        'Curvature_Left':             ('LKA_Left_Lane_A',  'Curvature'),
        'Curvature_Derivative_Left':  ('LKA_Left_Lane_A',  'Curvature_Derivative'),
        'View_Range_Left':            ('LKA_Left_Lane_B',  'View_Range'),

        # assumption: 01, 02 <--> right, left; TODO: check
        'Position_Right2':            ('LKA_01_Next_Lane_A', 'Position'),
        'Heading_Angle_Right2':       ('LKA_01_Next_Lane_B', 'Heading_Angle'),
        'Curvature_Right2':           ('LKA_01_Next_Lane_A', 'Curvature'),
        'Curvature_Derivative_Right2':('LKA_01_Next_Lane_A', 'Curvature_Derivative'),
        'View_Range_Right2':          ('LKA_01_Next_Lane_B', 'View_Range'),
        'Position_Left2':             ('LKA_02_Next_Lane_A', 'Position'),
        'Heading_Angle_Left2':        ('LKA_02_Next_Lane_B', 'Heading_Angle'),
        'Curvature_Left2':            ('LKA_02_Next_Lane_A', 'Curvature'),
        'Curvature_Derivative_Left2': ('LKA_02_Next_Lane_A', 'Curvature_Derivative'),
        'View_Range_Left2':           ('LKA_02_Next_Lane_B', 'View_Range'),
      }),
      ('trajectory_generator_flx20_autobox', {
        'RefPoint_X':                 ('trajectory_generator_flx20_autobox', 'tg_controller_input_t_min'),  # TODO xcp workaround
        'RefPoint_Y':                 ('trajectory_generator_flx20_autobox', 'tg_controller_input_t_min'),  # TODO xcp workaround

        'Position_Right':             ('trajectory_generator_flx20_autobox', 'tg_lanes_input_right_c0'),
        'Heading_Angle_Right':        ('trajectory_generator_flx20_autobox', 'tg_lanes_input_right_c1'),
        'Curvature_Right':            ('trajectory_generator_flx20_autobox', 'tg_lanes_input_right_c2'),
        'Curvature_Derivative_Right': ('trajectory_generator_flx20_autobox', 'tg_lanes_input_right_c3'),
        'View_Range_Right':           ('trajectory_generator_flx20_autobox', 'tg_lanes_input_right_view_range'),
        'Position_Left':              ('trajectory_generator_flx20_autobox', 'tg_lanes_input_left_c0'),
        'Heading_Angle_Left':         ('trajectory_generator_flx20_autobox', 'tg_lanes_input_left_c1'),
        'Curvature_Left':             ('trajectory_generator_flx20_autobox', 'tg_lanes_input_left_c2'),
        'Curvature_Derivative_Left':  ('trajectory_generator_flx20_autobox', 'tg_lanes_input_left_c3'),
        'View_Range_Left':            ('trajectory_generator_flx20_autobox', 'tg_lanes_input_left_view_range'),

        'Position_Right2':            ('trajectory_generator_flx20_autobox', 'tg_lanes_input_right_right_c0'),
        'Heading_Angle_Right2':       ('trajectory_generator_flx20_autobox', 'tg_lanes_input_right_right_c1'),
        'Curvature_Right2':           ('trajectory_generator_flx20_autobox', 'tg_lanes_input_right_right_c2'),
        'Curvature_Derivative_Right2':('trajectory_generator_flx20_autobox', 'tg_lanes_input_right_right_c3'),
        'View_Range_Right2':          ('trajectory_generator_flx20_autobox', 'tg_lanes_input_right_right_view_range'),
        'Position_Left2':             ('trajectory_generator_flx20_autobox', 'tg_lanes_input_left_left_c0'),
        'Heading_Angle_Left2':        ('trajectory_generator_flx20_autobox', 'tg_lanes_input_left_left_c1'),
        'Curvature_Left2':            ('trajectory_generator_flx20_autobox', 'tg_lanes_input_left_left_c2'),
        'Curvature_Derivative_Left2': ('trajectory_generator_flx20_autobox', 'tg_lanes_input_left_left_c3'),
        'View_Range_Left2':           ('trajectory_generator_flx20_autobox', 'tg_lanes_input_left_left_view_range'),
      }),
      ('flc20_lausch', {

        "Quality_Left_A": ("Video_Lane_Left_A", "Quality_Left_A"),     # TODO Workaround
        "Quality_Right_A": ("Video_Lane_Right_A", "Quality_Right_A"),  # TODO Workaround

        'Position_Right': ("Video_Lane_Right_A","C0_Right_A"),
        'Heading_Angle_Right': ("Video_Lane_Right_A","C1_Right_A"),
        'Curvature_Right': ("Video_Lane_Right_A","C2_Right_A"),
        'Curvature_Derivative_Right': ("Video_Lane_Right_A","C3_Right_A"),
        'View_Range_Right': ("Video_Lane_Right_B","View_Range_Right_B"),

        'Position_Left': ("Video_Lane_Left_A","C0_Left_A"),
        'Heading_Angle_Left': ("Video_Lane_Left_A","C1_Left_A"),
        'Curvature_Left':("Video_Lane_Left_A","C2_Left_A"),
        'Curvature_Derivative_Left': ("Video_Lane_Left_A","C3_Left_A"),
        'View_Range_Left': ("Video_Lane_Left_B","View_Range_Left_B"),

        'Position_Right2': ("Video_Lane_Next_Right_A","C0_Next_Right_A"),
        'Heading_Angle_Right2': ("Video_Lane_Next_Right_A","C1_Next_Right_A"),
        'Curvature_Right2': ("Video_Lane_Next_Right_A","C2_Next_Right_A"),
        'Curvature_Derivative_Right2': ("Video_Lane_Next_Right_A","C3_Next_Right_A"),
        'View_Range_Right2': ("Video_Lane_Next_Right_B","View_Range_Next_Right_B"),

        'Position_Left2': ("Video_Lane_Next_Left_A","C0_Next_Left_A"),
        'Heading_Angle_Left2': ("Video_Lane_Next_Left_A","C1_Next_Left_A"),
        'Curvature_Left2': ("Video_Lane_Next_Left_A","C2_Next_Left_A"),
        'Curvature_Derivative_Left2': ("Video_Lane_Next_Left_A","C3_Next_Left_A"),
        'View_Range_Left2':  ("Video_Lane_Next_Left_B","View_Range_Next_Left_B"),
      }),
    ])
    group = SignalGroup.from_named_signalgroups(sgs, self.get_source())
    return group

  def fill(self, group):
    time = self.get_modules().fill('calc_flc20_common_time')
    rescale_kwargs = {'ScaleTime': time, 'Order': 'valid'}
    # camera offset
    try:
      dx0_raw = group.get_value('RefPoint_X', **rescale_kwargs)
      dy0_raw = group.get_value('RefPoint_Y', **rescale_kwargs)
    except:
      dx0_raw = np.zeros_like(group.get_value('Position_Left', **rescale_kwargs))
      dy0_raw = np.zeros_like(group.get_value('Position_Left', **rescale_kwargs))
    dx0, dy0 = convert_sensor_offset(dx0_raw, dy0_raw)
    # left line
    c0_raw = group.get_value('Position_Left', **rescale_kwargs)
    c1_raw = group.get_value('Heading_Angle_Left', **rescale_kwargs)
    c2_raw = group.get_value('Curvature_Left', **rescale_kwargs)
    c3_raw = group.get_value('Curvature_Derivative_Left', **rescale_kwargs)
    vr_raw = group.get_value('View_Range_Left', **rescale_kwargs)
    left_line = create_line(
      time, c0_raw, c1_raw, c2_raw, c3_raw, vr_raw, dx0, dy0, group.winner)
    # right line
    c0_raw = group.get_value('Position_Right', **rescale_kwargs)
    c1_raw = group.get_value('Heading_Angle_Right', **rescale_kwargs)
    c2_raw = group.get_value('Curvature_Right', **rescale_kwargs)
    c3_raw = group.get_value('Curvature_Derivative_Right', **rescale_kwargs)
    vr_raw = group.get_value('View_Range_Right', **rescale_kwargs)
    right_line = create_line(
      time, c0_raw, c1_raw, c2_raw, c3_raw, vr_raw, dx0, dy0, group.winner)
    # left left line
    c0_raw = group.get_value('Position_Left2', **rescale_kwargs)
    c1_raw = group.get_value('Heading_Angle_Left2', **rescale_kwargs)
    c2_raw = group.get_value('Curvature_Left2', **rescale_kwargs)
    c3_raw = group.get_value('Curvature_Derivative_Left2', **rescale_kwargs)
    vr_raw = group.get_value('View_Range_Left2', **rescale_kwargs)
    left_left_line = create_line(
      time, c0_raw, c1_raw, c2_raw, c3_raw, vr_raw, dx0, dy0, group.winner)
    # right right line
    c0_raw = group.get_value('Position_Right2', **rescale_kwargs)
    c1_raw = group.get_value('Heading_Angle_Right2', **rescale_kwargs)
    c2_raw = group.get_value('Curvature_Right2', **rescale_kwargs)
    c3_raw = group.get_value('Curvature_Derivative_Right2', **rescale_kwargs)
    vr_raw = group.get_value('View_Range_Right2', **rescale_kwargs)
    right_right_line = create_line(
      time, c0_raw, c1_raw, c2_raw, c3_raw, vr_raw, dx0, dy0, group.winner)
    # return value
    lines = LaneData(left_line, right_line, left_left_line, right_right_line)
    return lines
