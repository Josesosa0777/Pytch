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
TRACK_20 = cParameter(20)
TRACK_21 = cParameter(21)
TRACK_22 = cParameter(22)
TRACK_23 = cParameter(23)
TRACK_24 = cParameter(24)
TRACK_25 = cParameter(25)
TRACK_26 = cParameter(26)
TRACK_27 = cParameter(27)
TRACK_28 = cParameter(28)
TRACK_29 = cParameter(29)
TRACK_30 = cParameter(30)
TRACK_31 = cParameter(31)
TRACK_32 = cParameter(32)
TRACK_33 = cParameter(33)
TRACK_34 = cParameter(34)
TRACK_35 = cParameter(35)
TRACK_36 = cParameter(36)
TRACK_37 = cParameter(37)
TRACK_38 = cParameter(38)
TRACK_39 = cParameter(39)
TRACK_40 = cParameter(40)
TRACK_41 = cParameter(41)
TRACK_42 = cParameter(42)
TRACK_43 = cParameter(43)
TRACK_44 = cParameter(44)
TRACK_45 = cParameter(45)
TRACK_46 = cParameter(46)
TRACK_47 = cParameter(47)
TRACK_48 = cParameter(48)
TRACK_49 = cParameter(49)
TRACK_50 = cParameter(50)
TRACK_51 = cParameter(51)
TRACK_52 = cParameter(52)
TRACK_53 = cParameter(53)
TRACK_54 = cParameter(54)
TRACK_55 = cParameter(55)
TRACK_56 = cParameter(56)
TRACK_57 = cParameter(57)
TRACK_58 = cParameter(58)
TRACK_59 = cParameter(59)
TRACK_60 = cParameter(60)
TRACK_61 = cParameter(61)
TRACK_62 = cParameter(62)
TRACK_63 = cParameter(63)

class cMyView(interface.iView):
  dep = 'fill_flc20_4_fusion@aebs.fill',

  def fill(self):
    t, tracks  = interface.Objects.fill("fill_flc20_4_fusion@aebs.fill")
    return t, tracks

  def view(self, param, t, tracks):
    track = tracks[param.i]
    if not track:
      print 'Warning: track %d is empty' %param.i
      return
    pn = datavis.cPlotNavigator(title='FLC20 internal track #%d' %param.i)
    # dx
    ax = pn.addAxis(ylabel='dx')
    pn.addSignal2Axis(ax, 'dx', t, track['dx'], unit='m')
    # angle
    ax = pn.addAxis(ylabel='angle')
    pn.addSignal2Axis(ax, 'left', t, track['alpLeftEdge'], unit='rad')
    pn.addSignal2Axis(ax, 'right', t, track['alpRightEdge'], unit='rad')
    # vx, invttc
    ax = pn.addAxis(ylabel='invttc')
    pn.addSignal2Axis(ax, 'invttc', t, track['invttc'], unit='1/s')
    # tracking status
    ax = pn.addAxis(ylabel='tracking st')
    pn.addSignal2Axis(ax, 'valid_b', t, track['valid_b'])
    pn.addSignal2Axis(ax, 'measured_b', t, track['measured_b'])
    pn.addSignal2Axis(ax, 'historical_b', t, track['historical_b'])
    # register client
    interface.Sync.addClient(pn)
    return
