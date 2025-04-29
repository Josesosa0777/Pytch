# -*- dataeval: init -*-

import numpy as np

import datavis
import interface

from viewVideoOverlay import getVideoName

# TODO: remove inferface.*

init_params = {
  "FLC20":         dict(sensors=dict(flc20=True)),
  "FLC20LDW":      dict(sensors=dict(flc20=True, ldw=True)),
  "FLC20_FLR20LF": dict(sensors=dict(flc20=True, flr20lf=True)),
  "FLC20_FLR20LF_FLR20RO":
    dict(sensors=dict(flc20=True, flr20lf=True, flr20ro=True)),
}


class cView(interface.iView):
  def init(self, sensors):
    self.sensors = sensors
    dep = []
    if self.sensors.get("flc20"):
      dep.append('calc_flc20_lanes@aebs.fill')
    if self.sensors.get("flr20lf"):
      dep.append('calc_flr20_pathpred_lf@aebs.fill')
    if self.sensors.get("flr20ro"):
      dep.append('calc_flr20_pathpred_ro@aebs.fill')
    self.dep = tuple(dep)
    return

  def check(self):
    # video file
    avi_filename = getVideoName(self.source.FileName)
    # multimedia signal
    sgs = [
      {'VidTime': ('Multimedia', 'Multimedia_1')},
      {'VidTime': ('Multimedia', 'Multimedia')},
      {'VidTime': ('Multimedia', 'Pro9000')},
      {'VidTime': ('Multimedia', 'LifeCam')},
    ]
    vidtime_group = self.source.selectSignalGroup(sgs,
      StrictTime=interface.StrictlyGrowingTimeCheck, TimeMonGapIdx=5)
    # ldw signals
    if self.sensors.get("ldw"):
      ldw_sgs  = [{
        "FLI1_LDI_Right": ("FLI1_E8", "FLI1_LaneDepartImminentRight_E8"),
        "FLI1_LDI_Left":  ("FLI1_E8", "FLI1_LaneDepartImminentLeft_E8"),
      }]
      ldw_group = self.source.selectSignalGroup(ldw_sgs)
    else:
      ldw_group = None
    return avi_filename, vidtime_group, ldw_group

  def view(self, avi_filename, vidtime_group, ldw_group):
    vn = datavis.cVideoNavigator(avi_filename, self.vidcalibs)
    vidtime_time, vidtime = vidtime_group.get_signal('VidTime')
    vn.setDisplayTime(vidtime_time, vidtime)

    vn.setLegend(interface.ShapeLegends)
    vn.addGroups(interface.Groups)

    for Status in interface.Objects.get_selected_by_parent(interface.iFill):
      ScaleTime_, Objects = interface.Objects.fill(Status)
      vn.setObjects(ScaleTime_, Objects)

    time_scale = None
    lines = []
    if self.sensors.get("flr20lf"):
      flr20_line = self.get_modules().fill('calc_flr20_pathpred_lf@aebs.fill')
      time_scale = flr20_line.time if time_scale is None else time_scale
      flr20_line = flr20_line.rescale(time_scale)
      line = {}
      line["range"] = 100.0 * np.ones_like(flr20_line.time)
      line["C0"] = flr20_line.c0
      line["C1"] = flr20_line.c1
      line["C2"] = flr20_line.c2
      line["C3"] = flr20_line.c3
      line["color"] = [0, 0, 255]
      lines.append(line)
      lines.append(line)  # dirty but necessary
    if self.sensors.get("flr20ro"):
      flr20_line = self.get_modules().fill('calc_flr20_pathpred_ro@aebs.fill')
      time_scale = flr20_line.time if time_scale is None else time_scale
      flr20_line = flr20_line.rescale(time_scale)
      line = {}
      line["range"] = 100.0 * np.ones_like(flr20_line.time)
      line["C0"] = flr20_line.c0
      line["C1"] = flr20_line.c1
      line["C2"] = flr20_line.c2
      line["C3"] = flr20_line.c3
      line["color"] = [255,0,0]#[0, 0, 100]
      lines.append(line)
      lines.append(line)  # dirty but necessary
    if self.sensors.get("flc20"):
      flc20_lines = self.get_modules().fill('calc_flc20_lanes@aebs.fill')
      time_scale = flc20_lines.time if time_scale is None else time_scale
      flc20_lines = flc20_lines.rescale(time_scale)
      left_line = {}
      left_line["range"] = flc20_lines.left_line.view_range
      left_line["C0"] = flc20_lines.left_line.c0
      left_line["C1"] = flc20_lines.left_line.c1
      left_line["C2"] = flc20_lines.left_line.c2
      left_line["C3"] = flc20_lines.left_line.c3
      left_line["color"] = [0, 255, 0]
      lines.append(left_line)
      right_line = {}
      right_line["range"] = flc20_lines.right_line.view_range
      right_line["C0"] = flc20_lines.right_line.c0
      right_line["C1"] = flc20_lines.right_line.c1
      right_line["C2"] = flc20_lines.right_line.c2
      right_line["C3"] = flc20_lines.right_line.c3
      right_line["color"] = [0, 255, 0]
      lines.append(right_line)
      left_left_line = {}
      left_left_line["range"] = flc20_lines.left_left_line.view_range
      left_left_line["C0"] = flc20_lines.left_left_line.c0
      left_left_line["C1"] = flc20_lines.left_left_line.c1
      left_left_line["C2"] = flc20_lines.left_left_line.c2
      left_left_line["C3"] = flc20_lines.left_left_line.c3
      left_left_line["color"] = [0, 255, 0]
      lines.append(left_left_line)
      right_right_line = {}
      right_right_line["range"] = flc20_lines.right_right_line.view_range
      right_right_line["C0"] = flc20_lines.right_right_line.c0
      right_right_line["C1"] = flc20_lines.right_right_line.c1
      right_right_line["C2"] = flc20_lines.right_right_line.c2
      right_right_line["C3"] = flc20_lines.right_right_line.c3
      right_right_line["color"] = [0, 255, 0]
      lines.append(right_right_line)
    if self.sensors.get("flc20") and self.sensors.get("ldw"):
      flc20_lines = self.get_modules().fill('calc_flc20_lanes@aebs.fill')
      time_scale = flc20_lines.time if time_scale is None else time_scale
      
      ldw_left = ldw_group.get_value("FLI1_LDI_Left", ScaleTime=time_scale)
      ldw_right = ldw_group.get_value("FLI1_LDI_Right", ScaleTime=time_scale)
      
      flc20_lines = flc20_lines.rescale(time_scale)
      left_line = {}
      left_line["range"] = np.where(ldw_left,
        flc20_lines.left_line.view_range, 0.0)
      left_line["C0"] = flc20_lines.left_line.c0
      left_line["C1"] = flc20_lines.left_line.c1
      left_line["C2"] = flc20_lines.left_line.c2
      left_line["C3"] = flc20_lines.left_line.c3
      left_line["color"] = [255, 0, 0]
      lines.append(left_line)
      right_line = {}
      right_line["range"] = np.where(ldw_right,
        flc20_lines.right_line.view_range, 0.0)
      right_line["C0"] = flc20_lines.right_line.c0
      right_line["C1"] = flc20_lines.right_line.c1
      right_line["C2"] = flc20_lines.right_line.c2
      right_line["C3"] = flc20_lines.right_line.c3
      right_line["color"] = [255, 0, 0]
      lines.append(right_line)

    if lines:
      vn.setLanes(time_scale, lines)

    self.sync.addClient(vn, (vidtime_time, vidtime))
    return
