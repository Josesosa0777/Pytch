# -*- dataeval:method -*-

import os
import numpy as np
from PySide import QtGui
import sys

import interface

import datavis.VideoNavigator as VideoNavigator
import datavis.PlotNavigator as PlotNavigator
import datavis.TrackNavigator as TrackNavigator
from measparser.signalgroup import SignalGroupError

DefParam = interface.NullParam

class cView(interface.iView):
  def check(self):
    AviFile, Ext = os.path.splitext(interface.Source.FileName)
    AviFile += '.avi'
    if not os.path.exists(AviFile):
      raise SignalGroupError('Warning: video file does not exist: %s' % AviFile)
    return AviFile

  def fill(self, AviFile):
    return AviFile

  def view(self, param, AviFile):
    t = np.arange(0,400,0.01)

    pn1 = PlotNavigator.cPlotNavigator("First plot window")
    pn1.addsignal('sine' ,  [t, np.sin(t)])
    pn1.addsignal('cosine', [t, np.cos(t)])

    pn2 = PlotNavigator.cPlotNavigator("Second plot window")
    pn2.addsignal('sine' ,  [t, np.sin(t)])
    pn2.addsignal('cosine', [t, np.cos(t)])

    pn3 = PlotNavigator.cPlotNavigator("Third delayed plot window")
    pn3.addsignal('sine' ,  [t, np.sin(t)])
    pn3.addsignal('cosine', [t, np.cos(t)])

    Coeff   = np.ones_like(t)
    R       = 150.0 * Coeff
    Offset  =   1.5 * Coeff

    TN = TrackNavigator.cTrackNavigator()
    for Name, Color, r, o in [['curve-left-letf-side',  'r',  1,  1],
                              ['curve-left-right-side', 'b',  1, -1],
                              ['curve-right-left-side', 'g', -1,  1],
                              ['curve-right-right-side','y', -1, -1]]:

      Track = TN.addTrack(Name, t, color=Color)
      FuncName = Track.addFunc(TrackNavigator.circle, LengthMax=TN.LengthMax)
      Track.addParam(FuncName, 'R',      t, r*R)
      Track.addParam(FuncName, 'Offset', t, o*Offset)
    TN.setViewAngle(-15.0, 15.0)
    object = {}
    object['dx'] = np.arange(40.0, 80.0, 0.001)
    object['dy'] = np.arange(0.0, 20.0, 0.0005)
    object['type'] = 1
    object['label'] = 'Label'
    object['color'] = [102, 205, 170]
    TN.addObject(t, object)
    sync = self.get_sync()
    sync.addClient(pn1)
    sync.addClient(pn2)
    sync.addClient(pn3, [t, t+5])
    sync.addClient(TN)
    return
