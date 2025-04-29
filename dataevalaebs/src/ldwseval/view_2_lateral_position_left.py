# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"""
It shows the maneuver as the tire crosses the line.

"""

import interface
import datavis

import numpy as np

import MetaDataIO
from measproc.vidcalibs import VidCalibs

sgs  = [
{

  "C0_left_wheel": ("Bendix_Info", "C0_left_wheel"),

},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, group):
    client00 = datavis.cPlotNavigator(title="LDWS", figureNr=None)
    self.sync.addClient(client00)

            # -----------------------------------------------------
        # hard coded parameters
        #   leftWheel              : absolute distance from camera to outer edge of left wheel  
        #   rightWheel             : absolute distance from camera to outer edge of right wheel
        #                             Remark: Both leftWheel and rightWheel are positive values
        #   corridor_outer_boundary : todo
        #   warning_line_tlc        : todo 
        #   dx_camera_to_front_axle : longitudinal distance from camera to front axle

    tokens = VidCalibs.parse_measurement(self.source.BaseName)
    vehicle = tokens[0] if tokens is not None else None
    parameters = MetaDataIO.cFLC20CalibData(vehicle)
    CalibData = parameters.GetData()

    ### [cm] all of them ###
    ######################## 
    leftWheel               = CalibData["leftWheel"] 
    rightWheel              = CalibData["rightWheel"]              
    corridor_outer_boundary = CalibData["corridor_outer_boundary"]
    warning_line_tlc        = CalibData["warning_line_tlc"] 
    warn_margin_left        = CalibData["warn_margin_left"]
    warn_margin_right       = CalibData["warn_margin_right"] 
    
    timec0left, c0left = group.get_signal("C0_left_wheel")


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
  
    return
