# -*- dataeval: init -*-

import numpy

import datavis
import interface

def polyClothoid(A0, A1, A2, A3, Distance):
  # f(dx) = 1/6 * a3 * x^3 + 1/2 * a2 * x^2 + tan(a1) * x + a0
  x = numpy.linspace(0.0, Distance, num=20)
  y = numpy.empty_like(x)
  y[0] = A0  # avoid computing 0*inf at x=0
  y[1:] = (A3 / 6.0) * numpy.power(x[1:], 3) + (A2 / 2.0) * numpy.power(x[1:], 2) + numpy.tan(A1) * x[1:] + A0
  return  y, x

class View(interface.iView):
  dep = 'calc_flc20_lanes@aebs.fill',

  def view(self):
    TN = datavis.cTrackNavigator()
    TN.addGroups(interface.Groups)
    TN.setLegend(interface.Legends)

    for GroupName, (LeftAngle, RightAngle, kwargs) in interface.ViewAngles.iteritems():
      TN.setViewAngle(LeftAngle, RightAngle, GroupName, **kwargs)

    flc20_lines = self.get_modules().fill('calc_flc20_lanes@aebs.fill')
    flc20_time = flc20_lines.time
    # right
    Track = TN.addTrack('FLC20 lanes', flc20_time, color='g')
    FuncName = Track.addFunc(polyClothoid)
    Track.addParam(FuncName, 'A0', flc20_time, flc20_lines.right_line.a0)
    Track.addParam(FuncName, 'A1', flc20_time, flc20_lines.right_line.a1)
    Track.addParam(FuncName, 'A2', flc20_time, flc20_lines.right_line.a2)
    Track.addParam(FuncName, 'A3', flc20_time, flc20_lines.right_line.a3)
    Track.addParam(FuncName, 'Distance', flc20_time, flc20_lines.right_line.view_range)
    # left
    Track = TN.addTrack('FLC20 lanes', flc20_time, color='g')
    FuncName = Track.addFunc(polyClothoid)
    Track.addParam(FuncName, 'A0', flc20_time, flc20_lines.left_line.a0)
    Track.addParam(FuncName, 'A1', flc20_time, flc20_lines.left_line.a1)
    Track.addParam(FuncName, 'A2', flc20_time, flc20_lines.left_line.a2)
    Track.addParam(FuncName, 'A3', flc20_time, flc20_lines.left_line.a3)
    Track.addParam(FuncName, 'Distance', flc20_time, flc20_lines.left_line.view_range)
    # right right
    Track = TN.addTrack('FLC20 lanes', flc20_time, color='g')
    FuncName = Track.addFunc(polyClothoid)
    Track.addParam(FuncName, 'A0', flc20_time, flc20_lines.right_right_line.a0)
    Track.addParam(FuncName, 'A1', flc20_time, flc20_lines.right_right_line.a1)
    Track.addParam(FuncName, 'A2', flc20_time, flc20_lines.right_right_line.a2)
    Track.addParam(FuncName, 'A3', flc20_time, flc20_lines.right_right_line.a3)
    Track.addParam(FuncName, 'Distance', flc20_time, flc20_lines.right_right_line.view_range)
    # left left
    Track = TN.addTrack('FLC20 lanes', flc20_time, color='g')
    FuncName = Track.addFunc(polyClothoid)
    Track.addParam(FuncName, 'A0', flc20_time, flc20_lines.left_left_line.a0)
    Track.addParam(FuncName, 'A1', flc20_time, flc20_lines.left_left_line.a1)
    Track.addParam(FuncName, 'A2', flc20_time, flc20_lines.left_left_line.a2)
    Track.addParam(FuncName, 'A3', flc20_time, flc20_lines.left_left_line.a3)
    Track.addParam(FuncName, 'Distance', flc20_time, flc20_lines.left_left_line.view_range)

    for Status in interface.Objects.get_selected_by_parent(interface.iFill):
      Time, Objects = interface.Objects.fill(Status)
      for Object in Objects:
        TN.addObject(Time, Object)

    interface.Sync.addClient(TN)
    return
