# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"""
It shows the maneuver as the tire crosses the line, 
shows the lateral speed,
and shows some flags, such as LaneChange, AcousticalWarning, LDW warning
"""
import interface
import datavis

import numpy as np

import MetaDataIO
from measproc.vidcalibs import VidCalibs
sgs  = [
{
  "VDC2_SteerWhlAngle_0B": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
  "EBC2_MeanSpdFA_0B": ("EBC2_0B", "EBC2_MeanSpdFA_0B"),
  "estimated_road_curvature": ("General_radar_status", "estimated_road_curvature"),
  "VDC2_YawRate_0B": ("VDC2_0B", "VDC2_YawRate_0B"),
  "C0_left_wheel": ("Bendix_Info", "C0_left_wheel"),
  "LDW_LaneDeparture_Right": ("Bendix_Info", "LDW_LaneDeparture_Right"),
  "Lateral_Velocity_Left_B": ("Bendix_Info2", "Lateral_Velocity_Left_B"),
  "LDW_LaneDeparture_Left": ("Bendix_Info", "LDW_LaneDeparture_Left"),
  "ME_LDW_LaneDeparture_Left": ("Bendix_Info", "ME_LDW_LaneDeparture_Left"),
  "Me_Line_Changed_Left_B": ("Video_Lane_Left_B", "Me_Line_Changed_Left_B"),
  "Me_Line_Changed_Right_B": ("Video_Lane_Right_B", "Me_Line_Changed_Right_B"),
  "FLI1_AcousticalWarningLeft_E8": ("FLI1_E8", "FLI1_AcousticalWarningLeft_E8"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    return group

  def view(self,  group):
    client00 = datavis.cPlotNavigator(title="LDWS", figureNr=None)
    self.sync.addClient(client00)

    tokens = VidCalibs.parse_measurement(self.source.BaseName)
    vehicle = tokens[0] if tokens is not None else None
    parameters = MetaDataIO.cFLC20CalibData(vehicle)
    CalibData = parameters.GetData()

            # -----------------------------------------------------
        # hard coded parameters
        #   leftWheel              : absolute distance from camera to outer edge of left wheel  
        #   rightWheel             : absolute distance from camera to outer edge of right wheel
        #                             Remark: Both leftWheel and rightWheel are positive values
        #   corridor_outer_boundary : todo
        #   warning_line_tlc        : todo 
        #   dx_camera_to_front_axle : longitudinal distance from camera to front axle



    ### [cm] all of them ###
    ######################## 
    leftWheel               = CalibData["leftWheel"] 
    rightWheel              = CalibData["rightWheel"]              
    corridor_outer_boundary = CalibData["corridor_outer_boundary"]
    warning_line_tlc        = CalibData["warning_line_tlc"] 
    warn_margin_left        = CalibData["warn_margin_left"]
    warn_margin_right       = CalibData["warn_margin_right"] 
    
    timec0left, c0left = group.get_signal("C0_left_wheel")
    timeMEl, lanechange_L = group.get_signal("Me_Line_Changed_Left_B")
    timeMEr, lanechange_R = group.get_signal("Me_Line_Changed_Right_B")
    timeME, ME = group.get_signal("ME_LDW_LaneDeparture_Left")
    timeacwarning, acwarning = group.get_signal("FLI1_AcousticalWarningLeft_E8")
    timeLDW, LDW = group.get_signal("LDW_LaneDeparture_Left")

    ###AXIS1###
    ###########
    axis00 = client00.addAxis()
    ###C0left
    client00.addSignal2Axis(axis00, "C0 left wheel", timec0left, c0left, unit="m?")
    axis00.set_ylabel('inside lane <--> outside lane')
    axis00.set_xlabel('time [s]')
    warningline= np.ones_like(c0left)*warn_margin_left/100
    axis00.plot(timec0left,warningline, 'm_')
    ###edges of the red zone
    inner=np.zeros_like(c0left)
    outer=np.ones_like(c0left)*corridor_outer_boundary / 100
    axis00.fill_between(timec0left, inner,outer,color='r',alpha=.2)
    axis00.set_ylim((-1.5,1.5))
    
    ###AXIS2###
    ###########
    axis02 = client00.addAxis()
    t_latspeed, latspeed = group.get_signal("Lateral_Velocity_Left_B")
    client00.addSignal2Axis(axis02, "lateral speed", t_latspeed, latspeed, unit="m/s")
    axis02.set_ylim(-1,3)
    
    ###AXIS3###
    ###########
    ### tracking ?? lnvu ???
    axis01 = client00.addAxis()
    client00.addSignal2Axis(axis01, "LD", timeLDW, LDW, unit='', offset=4, displayscaled=False)
    client00.addSignal2Axis(axis01, "ME LD", timeME, ME, unit='', offset=6, displayscaled=False)
    client00.addSignal2Axis(axis01, "Acoustical warning",timeacwarning , acwarning, unit='', offset=6, displayscaled=False)
    client00.addSignal2Axis(axis01, "Lanechange left", timeMEl, lanechange_L, unit='')
    client00.addSignal2Axis(axis01, "Lanechange right", timeMEr, lanechange_R, unit='')

    axis01.set_ylabel('flags')
    axis01.set_yticklabels(['','Off','Crossing - On','Off','Acoust. Warn. - On2','Off','LD - On','Off','ME LD - On'])
    ### first tick does not show

    return
