# -*- dataeval: init -*-


"""
:Name:
	view_kinematics_FLR25.py

:Type:
	View script

:Visualization Type:
	Plot

:Full Path:
	dataevalaebs/src/aebseval/resim/view_kinematics_FLR25.py

:Sensors:
	FLR25

:Short Description:
	Plot basic attributes of ego vehicle and primary track, including speed,
	distance etc.

:Large Description:
	Usage:
		- Plot AEBS-relevant kinematic information.

:Dependencies:
	- fill_flr25_aeb_track@aebs.fill
	- calc_radar_egomotion-flr25@aebs.fill
	- calc_aebs_resim_output@aebs.fill

:Output Data Image/s:
	.. image:: ../images/view_kinematics_FLR25_1.png

.. note::
	For source code click on [source] tag beside functions
"""

from numpy import rad2deg

import datavis
from interface import iView
import numpy as np
from measparser.signalproc import rescale
from measparser.filenameparser import FileNameParser

DETAIL_LEVEL = 1

mps2kph = lambda v: v*3.6

class View(iView):

  dep = 'fill_flr25_aeb_track@aebs.fill', 'calc_radar_egomotion-flr25@aebs.fill', 'calc_aebs_resim_output@aebs.fill'
  def view(self):
    # process signals
    track = self.modules.fill(self.dep[0])
    counter_for_loop_iteration = 0
    t = track.time
    ego = self.modules.fill(self.dep[1])
    aebs_resim_data, time, total_mileage = self.modules.fill(self.dep[2])

    try:
      file_name = FileNameParser(self.source.BaseName).date_underscore
    except:
      file_name = self.source.BaseName.replace('.', '-').replace('_at_', '_').rsplit('_', 2)[0]
    valid_aebs_resim_data = self.get_data_from_csv(file_name, aebs_resim_data)
    # t = ego.time
    delta_data_array = np.zeros(t.shape, dtype=float)
    masked_aray = np.ones(t.shape, dtype=bool)
    
    # create plot
    pn = datavis.cPlotNavigator(title='Ego vehicle and obstacle kinematics')

    for item in valid_aebs_resim_data:
      counter_for_loop_iteration = counter_for_loop_iteration + 1
      if counter_for_loop_iteration >=2:
        interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), t)
        if 'obj_relative_velocity_x' in item:
          delta_data_array[(interval[0] + 10):((interval[0] + 40))] = mps2kph(float(item["obj_relative_velocity_x"]))
        elif 'obj_relative_velocity_x_start' in item:
          delta_data_array[(interval[0] + 10):((interval[0] + 40))] = mps2kph(float(item["obj_relative_velocity_x_start"]))
        masked_aray[(interval[0] + 10):((interval[0] + 40))] = False
      else:
        interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), t)
        if 'obj_relative_velocity_x' in item:
          delta_data_array[(interval[0]-10):((interval[0]+40))] = mps2kph(float(item["obj_relative_velocity_x"]))
        elif 'obj_relative_velocity_x_start' in item:
          delta_data_array[(interval[0] - 10):((interval[0] + 40))] = mps2kph(float(item["obj_relative_velocity_x_start"]))
        masked_aray[(interval[0]-10):((interval[0]+40))] = False

    # speed
    ax = pn.addAxis(ylabel='speed', ylim=(-5.0, 100.0))
    pn.addSignal2Axis(ax, 'ego speed', t, mps2kph(ego.vx), unit='km/h')
    track_vx_abs = rescale(ego.time, ego.vx, t)[1] + track.vx   # v_ego + v_track #rescale(ego.time, ego.vx, t)[1]
    pn.addSignal2Axis(ax, 'obst. speed', t,  mps2kph(track.vx), unit='km/h')
    pn.addSignal2Axis(ax, 'obst. speed resim', t, np.ma.array(delta_data_array, mask=masked_aray), unit='km/h')
    self.extend_speed_axis(pn, ax)

    # acceleration
    ax = pn.addAxis(ylabel = 'accel.conti', ylim = (-10.0, 10.0))
    pn.addSignal2Axis(ax, 'ego acceleration', t, ego.ax, unit = 'm/s^2')
    pn.addSignal2Axis(ax, 'obst. acceleration', t, track.ax, unit='m/s^2') # ax_abs
    self.extend_accel_axis(pn, ax)

    # yaw rate
    if DETAIL_LEVEL > 0:
      ax = pn.addAxis(ylabel = "yaw rate", ylim = (-12.0, 12.0))
      pn.addSignal2Axis(ax, "yaw rate", t, rad2deg(ego.yaw_rate), unit = "deg/s")
    # if DETAIL_LEVEL > 0:
    #   ax = pn.addAxis(ylabel = "yaw rate", ylim = (-12.0, 12.0))
    #   pn.addSignal2Axis(ax, "yaw rate", t, rad2deg(ego.yaw_rate), unit = "deg/s")

    delta_dx_array = np.zeros(t.shape, dtype=float)
    # masked_dx_array = np.ones(t.shape, dtype=bool)
    delta_dy_array = np.zeros(t.shape, dtype=float)
    # masked_dy_array = np.ones(t.shape, dtype=bool)

    # valid_aebs_resim_dx_data = self.get_data_from_csv(file_name.date_underscore, aebs_resim_data)
    # valid_aebs_resim_dy_data = self.get_data_from_csv(file_name.date_underscore, aebs_resim_data)

    # Create dx signal from csv data
    counter_for_loop_iteration = 0
    for item in valid_aebs_resim_data:
      counter_for_loop_iteration = counter_for_loop_iteration + 1
      if counter_for_loop_iteration >=2:
        interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), t)
        if 'obj_distance_x' in item:
          delta_dx_array[(interval[0] + 10):((interval[0] + 40))] = float(item["obj_distance_x"])
        elif 'obj_distance_x_start' in item:
          delta_dx_array[(interval[0] + 10):((interval[0] + 40))] = float(item["obj_distance_x_start"])
        masked_aray[(interval[0] + 10):((interval[0] + 40))] = False
      else:
        interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), t)
        if 'obj_distance_x' in item:
          delta_dx_array[(interval[0] - 10):((interval[0] + 40))] = float(item["obj_distance_x"])
        elif 'obj_distance_x_start' in item:
          delta_dx_array[(interval[0] - 10):((interval[0] + 40))] = float(item["obj_distance_x_start"])
        masked_aray[(interval[0] - 10):((interval[0] + 40))] = False

    counter_for_loop_iteration = 0
    # Create dy signal from csv data
    for item in valid_aebs_resim_data:
      counter_for_loop_iteration = counter_for_loop_iteration + 1
      if counter_for_loop_iteration>=2:
        interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), t)
        if 'obj_distance_y' in item:
          delta_dy_array[(interval[0] + 10):((interval[0] + 40))] = float(item["obj_distance_y"])
        elif 'obj_distance_y_start' in item:
          delta_dy_array[(interval[0] + 10):((interval[0] + 40))] = float(item["obj_distance_y_start"])
        masked_aray[(interval[0] + 10):((interval[0] + 40))] = False
      else:
        interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), t)
        if 'obj_distance_y' in item:
          delta_dy_array[(interval[0] - 10):((interval[0] + 40))] = float(item["obj_distance_y"])
        elif 'obj_distance_y_start' in item:
          delta_dy_array[(interval[0] - 10):((interval[0] + 40))] = float(item["obj_distance_y_start"])
        masked_aray[(interval[0] - 10):((interval[0] + 40))] = False

    # dx
    ax = pn.addAxis(ylabel = 'long. dist.', ylim = (0.0, 150.0))
    pn.addSignal2Axis(ax, 'dx', t, track.dx, unit = 'm')
    pn.addSignal2Axis(ax, 'dx resim', t, np.ma.array(delta_dx_array, mask=masked_aray), unit='m')
    ax = pn.addTwinAxis(ax, ylabel = 'lat. dist.', ylim = (-15, 15), color = 'g')
    pn.addSignal2Axis(ax, 'dy', t, track.dy, unit = 'm', color = 'g')
    pn.addSignal2Axis(ax, 'dy resim', t, np.ma.array(delta_dy_array, mask=masked_aray), unit='m')
    # mov_state
    mapping = track.mov_state.mapping
    ax = pn.addAxis(ylabel='moving state', yticks=mapping, ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
    pn.addSignal2Axis(ax, 'obst. mov_st', t, track.mov_state.join(), color='g')
    # mov_dir
    if DETAIL_LEVEL > 0:
      mapping = track.mov_dir.mapping
      ax = pn.addAxis(ylabel='moving direction', yticks=mapping,
                      ylim=(min(mapping)-0.5, max(mapping)+0.5))
      pn.addSignal2Axis(ax, 'obst. mov_dir', t, track.mov_dir.join(), color='g')
    # # confidence
    # if DETAIL_LEVEL > 0:
    #   ax = pn.addAxis(ylabel='confidence', yticks={0:0, 1:1, 2:'no', 3:'yes'},
    #                   ylim=(-0.1, 3.1))
    #   pn.addSignal2Axis(ax, 'radar conf', t, track.radar_conf)
    #   pn.addSignal2Axis(ax, 'video conf', t, track.video_conf)
    #   pn.addSignal2Axis(ax, 'video associated', t, track.fused, offset=2,
    #                     displayscaled=True)
    
    # register client
    self.sync.addClient(pn)
    return

  def extend_speed_axis(self, pn, ax):
    return

  def get_data_from_csv(self, file_name, aebs_resim_data):
    valid_data = []

    for files in aebs_resim_data:
      name = ""
      if 'camera' in files['Measurement File']:
        name = files['Measurement File'].replace('.', '-').split('_camera')[0].replace('_at_', '_')
      elif 'radar' in files['Measurement File']:
        name = files['Measurement File'].replace('.', '-').split('_radar')[0].replace('_at_', '_')
      if name == file_name:
        valid_data.append(files)
    return valid_data

  def get_index(self, interval, time):
    st_time, ed_time = interval
    st_time = st_time / 1000000.0
    ed_time = ed_time / 1000000.0
    start_index = (np.abs(time - st_time)).argmin()
    end_index = (np.abs(time - ed_time)).argmin()
    if start_index == end_index:
      end_index += 1
    return (start_index, end_index)

  def extend_accel_axis(self, pn, ax):
    return
