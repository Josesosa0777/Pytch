import os.path

import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{
                 # lane offset (c0 param)
                 "left_offset_KBCam"  : ("Marking_type", "dist_left_road_marking"),
                 "right_offset_KBCam" : ("Marking_type", "dist_right_road_marking"),
                 "left_offset_SCam"   : ("LKA_Left_Lane_A", "Position"),
                 "right_offset_SCam"  : ("LKA_Right_Lane_A", "Position"),
                }]

class cView(interface.iView):
  def check(self):
    Group = interface.Source.selectSignalGroup(SignalGroups)
    return Group
    
  def fill(self, Group):
    return Group

  def view(cls, Param, Group):
    _, fileName = os.path.split(interface.Source.FileName)
    
    Client = datavis.cPlotNavigator(title=fileName, figureNr=None)
    interface.Sync.addClient(Client)
    
    # left lane
    Axis = Client.addAxis()
    time_KBCam, left_offset_KBCam = interface.Source.getSignalFromSignalGroup(Group, "left_offset_KBCam")
    Client.addSignal2Axis(Axis, "left_offset_KBCam", time_KBCam, left_offset_KBCam, unit="")
    time_SCam_left, left_offset_SCam = interface.Source.getSignalFromSignalGroup(Group, "left_offset_SCam")
    left_offset_SCam = -left_offset_SCam
    Client.addSignal2Axis(Axis, "left_offset_SCam", time_SCam_left, left_offset_SCam, unit="")
    
    # right lane
    Axis = Client.addAxis()
    right_offset_KBCam = interface.Source.getSignalFromSignalGroup(Group, "right_offset_KBCam")[1]
    Client.addSignal2Axis(Axis, "right_offset_KBCam", time_KBCam, right_offset_KBCam, unit="m")
    time_SCam_right, right_offset_SCam = interface.Source.getSignalFromSignalGroup(Group, "right_offset_SCam")
    Client.addSignal2Axis(Axis, "right_offset_SCam", time_SCam_right, right_offset_SCam, unit="m")
    
    # lane width
    Axis = Client.addAxis()
    lane_width_KBCam = left_offset_KBCam+right_offset_KBCam
    Client.addSignal2Axis(Axis, "lane_width_KBCam", time_KBCam, lane_width_KBCam, unit="m")
    time_SCam = time_SCam_right
    if time_SCam_left.size == time_SCam_right.size:
      lane_width_SCam = left_offset_SCam + right_offset_SCam
    else:
      # rescale left signal to right signal's time (as the latter is sent later)
      _, left_offset_SCam_rescale = interface.Source.rescale(time_SCam_left, left_offset_SCam, time_SCam)
      lane_width_SCam = left_offset_SCam_rescale + right_offset_SCam
    Client.addSignal2Axis(Axis, "lane_width_SCam", time_SCam_left, lane_width_SCam, unit="m")
    
    # lane width difference
    Axis = Client.addAxis()
    _, lane_width_SCam_rescale = interface.Source.rescale(time_SCam, lane_width_SCam, time_KBCam)
    lane_width_difference = lane_width_KBCam - lane_width_SCam_rescale
    Client.addSignal2Axis(Axis, "lane_width_difference", time_KBCam, lane_width_difference, unit="m")
    return

