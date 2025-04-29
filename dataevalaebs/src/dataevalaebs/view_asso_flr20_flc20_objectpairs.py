# -*- dataeval: method -*-

from collections import OrderedDict

import numpy as np

import datavis
import interface
from aebs.sdf import asso_flr20_flc20
from aebs.fill import fill_flc20_4_fusion

class cParameter(interface.iParameter):
  def __init__(self, k):
    self.k = k
    self.genKeys()
    return
# instantiation of module parameters
NEIGHBOUR_00 = cParameter(0)
NEIGHBOUR_01 = cParameter(1)
NEIGHBOUR_02 = cParameter(2)
NEIGHBOUR_03 = cParameter(3)
NEIGHBOUR_04 = cParameter(4)
NEIGHBOUR_05 = cParameter(5)
NEIGHBOUR_06 = cParameter(6)
NEIGHBOUR_07 = cParameter(7)
NEIGHBOUR_08 = cParameter(8)
NEIGHBOUR_09 = cParameter(9)
NEIGHBOUR_10 = cParameter(10)
NEIGHBOUR_11 = cParameter(11)
NEIGHBOUR_12 = cParameter(12)
NEIGHBOUR_13 = cParameter(13)
NEIGHBOUR_14 = cParameter(14)
NEIGHBOUR_15 = cParameter(15)
NEIGHBOUR_16 = cParameter(16)
NEIGHBOUR_17 = cParameter(17)
NEIGHBOUR_18 = cParameter(18)
NEIGHBOUR_19 = cParameter(19)
NEIGHBOUR_20 = cParameter(20)

class cView(interface.iView):
  dep = 'fill_flr20_4_fusion@aebs.fill', 'fill_flc20_4_fusion@aebs.fill'
  def fill(self):
    radarTime, radarTracks = interface.Objects.fill("fill_flr20_4_fusion@aebs.fill")
    videoTime, videoTracks = interface.Objects.fill("fill_flc20_4_fusion@aebs.fill")
    newVideoTracks = fill_flc20_4_fusion.rescaleToExternalTime(videoTime, videoTracks, radarTime)
    # collect tracks in a dict (will be unnecessary later..)
    radarTracks = OrderedDict( zip(xrange(len(radarTracks)),radarTracks) )
    newVideoTracks = OrderedDict( zip(xrange(len(newVideoTracks)),newVideoTracks) )
    # create asso object
    a = asso_flr20_flc20.AssoFlr20Core(radarTime, radarTracks, newVideoTracks)
    a.calc()
    return a

  def view(cls, par, a):
    Client = datavis.cListNavigator(title="LN")
    # before
    for k in xrange(par.k,0,-1):
      # shift pairs
      left = [[] for i in xrange(k)]
      right = a.objectPairs[:-k]
      left.extend(right)
      assert len(left) == len(a.objectPairs) == a.scaleTime.size
      Client.addsignal("current - %d" %k, (a.scaleTime, left))
      # shift time
      t = np.roll(a.scaleTime,k)
      t[:k] = np.NaN
      Client.addsignal("current - %d" %k, (a.scaleTime, t), groupname='time')
    # actual
    Client.addsignal("current", (a.scaleTime, a.objectPairs), bg='red')
    Client.addsignal("current", (a.scaleTime, a.scaleTime),   bg='red', groupname='time')
    # after
    for k in xrange(1,par.k+1):
      # shift pairs
      left = a.objectPairs[k:]
      right = [[] for i in xrange(k)]
      left.extend(right)
      assert len(left) == len(a.objectPairs)
      Client.addsignal("current + %d" %k, (a.scaleTime, left))
      # shift time
      t = np.roll(a.scaleTime,-k)
      t[-k:] = np.NaN
      Client.addsignal("current + %d" %k, (a.scaleTime, t), groupname='time')
    # register client
    interface.Sync.addClient(Client)
    return
