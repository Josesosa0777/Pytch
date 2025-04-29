# -*- dataeval: method -*-

import interface
import datavis

class cParameter(interface.iParameter):
  def __init__(self, i):
    self.i = i
    self.genKeys()
# instantiation of module parameters
TRACK_00 = cParameter(0)
TRACK_01 = cParameter(1)
TRACK_02 = cParameter(2)
TRACK_03 = cParameter(3)
TRACK_04 = cParameter(4)
TRACK_05 = cParameter(5)
TRACK_06 = cParameter(6)
TRACK_07 = cParameter(7)
TRACK_08 = cParameter(8)
TRACK_09 = cParameter(9)
TRACK_10 = cParameter(10)
TRACK_11 = cParameter(11)
TRACK_12 = cParameter(12)
TRACK_13 = cParameter(13)
TRACK_14 = cParameter(14)
TRACK_15 = cParameter(15)
TRACK_16 = cParameter(16)
TRACK_17 = cParameter(17)
TRACK_18 = cParameter(18)
TRACK_19 = cParameter(19)

class cMyView(interface.iView):
  dep = 'fill_flr20_4_fusion@aebs.fill',

  def fill(self):
    t, tracks  = interface.Objects.fill("fill_flr20_4_fusion@aebs.fill")
    return t, tracks

  def view(self, param, t, tracks):
    track = tracks[param.i]
    if not track:
      print 'Warning: track %d is empty' %param.i
      return
    pn = datavis.cPlotNavigator(title='FLR20 internal track #%d' %param.i)
    # dx, dy, angle
    ax = pn.addAxis(ylabel='dx, dy')
    pn.addSignal2Axis(ax, 'dx', t, track['dx'], unit='m')
    pn.addSignal2Axis(ax, 'dy', t, track['dy'], unit='m')
    twinax = pn.addTwinAxis(ax, ylabel='angle', color='m')
    pn.addSignal2Axis(twinax, 'angle', t, track['angle'], unit='rad')
    # vx, invttc
    ax = pn.addAxis(ylabel='vx')
    pn.addSignal2Axis(ax, 'vx', t, track['vx'], unit='m/s')
    twinax = pn.addTwinAxis(ax, ylabel='invttc')
    pn.addSignal2Axis(twinax, 'invttc', t, track['invttc'], unit='1/s')
    # tracking status
    ax = pn.addAxis(ylabel='tracking st')
    pn.addSignal2Axis(ax, 'valid_b', t, track['valid_b'])
    pn.addSignal2Axis(ax, 'measured_b', t, track['measured_b'])
    pn.addSignal2Axis(ax, 'historical_b', t, track['historical_b'])
    # exist and obstacle prob
    ax = pn.addAxis(ylabel='prob')
    pn.addSignal2Axis(ax, 'existProb', t, track['existProb'])
    pn.addSignal2Axis(ax, 'obstacleProb', t, track['obstacleProb'])
    # moving state
    ax = pn.addAxis(ylabel='moving st')
    pn.addSignal2Axis(ax, 'stationary_b', t, track['stationary_b'])
    pn.addSignal2Axis(ax, 'stopped_b', t, track['stopped_b'])
    pn.addSignal2Axis(ax, 'notClassified_b', t, track['notClassified_b'])
    # register client
    interface.Sync.addClient(pn)
    return
