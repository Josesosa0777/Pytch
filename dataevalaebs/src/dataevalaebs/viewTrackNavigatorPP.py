# -*- dataeval: init -*-

import sys

import numpy

import datavis
import measparser
import interface
import pathpred.pathpredictor

Lines = [{'CurveLane': ('RadarFC', 'evi.General_TC.kapCurvTraj'),
          'CurveEgo':  ('RadarFC', 'dcp.kapCourse')}]

ROADRMOLanePolyA0 = 1.5
ROADRSOLanePolyA0 = 0.9
AC100LanePolyA0 = ROADRMOLanePolyA0

RMS_MAX = 10.0

init_params = {
  "SCAM_CVR3_VBOX": dict(lanes=dict(cvr3=True, flc20=True, vbox=True)),
  "FLC20_FLR20LF_FLR20FLC20PP_VBOX":
    dict(lanes=dict(flc20=True, flr20lf=True, flr20flc20pp=True, vbox=True)),
  "FLC20_FLR20LF_VBOX": dict(lanes=dict(flc20=True, flr20lf=True, vbox=True)),
  "FLC20_FLR20LF_FLR20RO_VBOX":
    dict(lanes=dict(flc20=True, flr20lf=True, flr20ro=True, vbox=True)),
  "FLC20_FLR20LF": dict(lanes=dict(flc20=True, flr20lf=True)),
  "FLC20_FLR20LF_FLR20RO":
    dict(lanes=dict(flc20=True, flr20lf=True, flr20ro=True)),
}

def polyClothoid(A0, A1, A2, A3, Distance):
  # f(dx) = 1/6 * a3 * x^3 + 1/2 * a2 * x^2 + tan(a1) * x + a0
  x = numpy.linspace(0.0, Distance, num=20)
  y = numpy.empty_like(x)
  y[0] = A0  # avoid computing 0*inf at x=0
  y[1:] = (A3 / 6.0) * numpy.power(x[1:], 3) + (A2 / 2.0) * numpy.power(x[1:], 2) + numpy.tan(A1) * x[1:] + A0
  return  y, x

def calcPredPath(ego_motion, flc20_lines):
  # calculation
  pp = pathpred.pathpredictor.PathPredictor(debug_active=True)
  flc20_lines = flc20_lines.rescale(ego_motion.time)  # TODO: avoid
  line_f, debug = pp.predict(ego_motion, flc20_lines)
  # make viewrange Dataset-compatible
  viewrange_f_x = numpy.vstack((debug.viewrange_f, debug.viewrange_f)).T
  viewrange_f_y = numpy.empty_like(viewrange_f_x)
  viewrange_f_y[:, 0] = -1000.0  # arbitrary small number
  viewrange_f_y[:, 1] =  1000.0  # arbitrary large number
  return line_f.time, line_f, debug.dx_m, debug.dy_m, debug.dy_l, debug.dy_f, viewrange_f_x, viewrange_f_y, debug.sliced_fused_path

class View(interface.iView):
  def init(self, lanes):
    self.lanes = lanes
    dep = set()
    if self.lanes.get('flr20lf'):
      dep.add('calc_flr20_pathpred_lf@aebs.fill')
    if self.lanes.get('flr20ro'):
      dep.add('calc_flr20_pathpred_ro@aebs.fill')
    if self.lanes.get('flc20'):
      dep.add('calc_flc20_lanes@aebs.fill')
    if self.lanes.get('flr20flc20pp'):
      dep.add('calc_flc20_lanes@aebs.fill')
      dep.add('calc_flr20_egomotion@aebs.fill')
    if self.lanes.get('vbox'):
      dep.add('calc_vbox_egopath@aebs.fill')
      dep.add('calc_flr20_common_time@aebs.fill')
    self.dep = tuple(dep)
    return

  def view(self):
    TN = datavis.cTrackNavigator()
    TN.addGroups(interface.Groups)
    TN.setLegend(interface.Legends)

    for GroupName, (LeftAngle, RightAngle, kwargs) in interface.ViewAngles.iteritems():
      TN.setViewAngle(LeftAngle, RightAngle, GroupName, **kwargs)

    if self.lanes.get('cvr3'):
      Tracks = []
      try:
        Params = interface.Source.selectSignalGroup(Lines)
      except measparser.signalgroup.SignalGroupError, Error:
        print >> sys.stderr, 'CVR3 lanes are not added to the TrackNavigator.\n%s' % Error.message
      else:
        Tracks.append(('CVR3_SIT_MO', 'CurveLane', (
          ('y', (-ROADRMOLanePolyA0, ROADRMOLanePolyA0), 200.0),
          ('y', (-(ROADRMOLanePolyA0 + 2 * ROADRMOLanePolyA0), (ROADRMOLanePolyA0 + 2 * ROADRMOLanePolyA0)), 200.0),
          ('y', (-(ROADRMOLanePolyA0 + 4 * ROADRMOLanePolyA0), (ROADRMOLanePolyA0 + 4 * ROADRMOLanePolyA0)), 200.0))))

      for TrackName, CurveAlias, Lanes in Tracks:
        if isinstance(CurveAlias, str):
          TrackTime, Curve = interface.Source.getSignalFromSignalGroup(Params, CurveAlias)
        else:
          TrackTime, Curve = CurveAlias
        for Color, Aliases, Dist in Lanes:
          for Alias in Aliases:
            Track = TN.addTrack(TrackName, TrackTime, color=Color)
            if isinstance(Alias, str):
              Time, Value = interface.Source.getSignalFromSignalGroup(Params, Alias)
            else:
              Time = TrackTime
              Value = Alias * numpy.ones_like(TrackTime)
            FuncName = Track.addFunc(polyClothoid)
            Track.addParam(FuncName, 'A0', Time, Value)
            Track.addParam(FuncName, 'A1', TrackTime, numpy.zeros_like(TrackTime))
            Track.addParam(FuncName, 'A2', TrackTime, Curve)
            Track.addParam(FuncName, 'A3', TrackTime, numpy.zeros_like(TrackTime))
            Track.addParam(FuncName, 'Distance', TrackTime, Dist * numpy.ones_like(TrackTime))

    if self.lanes.get('flc20'):
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

    if self.lanes.get('flr20lf'):
      flr20_line = self.get_modules().fill('calc_flr20_pathpred_lf@aebs.fill')
      flr20_time = flr20_line.time
      # add as a curve
      Track = TN.addTrack('FLR20 LF', flr20_time, color='b')
      FuncName = Track.addFunc(polyClothoid)
      Track.addParam(FuncName, 'A0', flr20_time, flr20_line.a0)
      Track.addParam(FuncName, 'A1', flr20_time, flr20_line.a1)
      Track.addParam(FuncName, 'A2', flr20_time, flr20_line.a2)
      Track.addParam(FuncName, 'A3', flr20_time, flr20_line.a3)
      Track.addParam(FuncName, 'Distance', flr20_time, 100.0 * numpy.ones_like(flr20_time))

    if self.lanes.get('flr20ro'):
      flr20_line = self.get_modules().fill('calc_flr20_pathpred_ro@aebs.fill')
      flr20_time = flr20_line.time
      # add as a curve
      Track = TN.addTrack('FLR20 RO', flr20_time, color=(0,0,100./255.))
      FuncName = Track.addFunc(polyClothoid)
      Track.addParam(FuncName, 'A0', flr20_time, flr20_line.a0)
      Track.addParam(FuncName, 'A1', flr20_time, flr20_line.a1)
      Track.addParam(FuncName, 'A2', flr20_time, flr20_line.a2)
      Track.addParam(FuncName, 'A3', flr20_time, flr20_line.a3)
      Track.addParam(FuncName, 'Distance', flr20_time, 100.0 * numpy.ones_like(flr20_time))

    if self.lanes.get('vbox'):
      modules = self.get_modules()
      ego_path = modules.fill('calc_vbox_egopath@aebs.fill')
      ego_path = ego_path.rescale(modules.fill('calc_flr20_common_time@aebs.fill'))
      ego_path = ego_path._smooth()
      ego_path_sliced = ego_path.slice(0, 100)#.rescale_slices(0.1)
      TN.addDataset(ego_path_sliced.time, ego_path_sliced.get_dxs(), ego_path_sliced.get_dys(), 'Factual ego path (VBOX)', color='k')

    if self.lanes.get('flr20lf') and self.lanes.get('vbox'):
      flr20lf_slpath = flr20_line.rescale(ego_path.time).get_slicedpath(ego_path_sliced.get_dxs())
      #TN.addDataset(flr20lf_slpath.time, flr20lf_slpath.get_dxs(), flr20lf_slpath.get_dys(), 'FLR20 LF', color='b')

      errors = ego_path_sliced.calc_rms_pos_errors(flr20lf_slpath)
      errors[errors > RMS_MAX] = RMS_MAX  # TODO: remove hack
      PN = datavis.cPlotNavigator("flr20lf and vbox")
      ax = PN.addAxis()
      PN.addSignal2Axis(ax, "rms", ego_path.time, errors)
      interface.Sync.addClient(PN)

    for StatusName in interface.Objects.get_selected_by_parent(interface.iFill):
      Time, Objects = interface.Objects.fill(StatusName)
      for Object in Objects:
        TN.addObject(Time, Object)

    if self.lanes.get('flr20flc20pp'):
      modules = self.get_modules()
      ego_motion = modules.fill('calc_flr20_egomotion@aebs.fill')
      flc20_lines = modules.fill('calc_flc20_lanes@aebs.fill')
      PathTimePred, clotho, xEgoPred, yEgoPredDyn, yEgoPredRoad, yEgoPredFinal, viewrangeFinal_x, viewrangeFinal_y, fused_pp_sliced = calcPredPath(ego_motion, flc20_lines)
      # add predicted paths as a series of positions
      TN.addDataset(PathTimePred, xEgoPred, yEgoPredDyn,   'Predicted ego path (dyn)',   color='b')
      TN.addDataset(PathTimePred, xEgoPred, yEgoPredRoad,  'Predicted ego path (road)',  color='g')
      TN.addDataset(PathTimePred, xEgoPred, yEgoPredFinal, 'Predicted ego path (final)', color='r')
      # add view range info of the final predicted path
      TN.addDataset(PathTimePred, viewrangeFinal_x, viewrangeFinal_y, 'View range of predicted ego path (final)', color='r')
      # add final predicted path as a curve
      Track = TN.addTrack('Predicted ego path', PathTimePred, color='r')
      FuncName = Track.addFunc(polyClothoid)
      Track.addParam(FuncName, 'A0', PathTimePred, clotho.a0)
      Track.addParam(FuncName, 'A1', PathTimePred, clotho.a1)
      Track.addParam(FuncName, 'A2', PathTimePred, clotho.a2)
      Track.addParam(FuncName, 'A3', PathTimePred, clotho.a3)
      Track.addParam(FuncName, 'Distance', PathTimePred, 100.0 * numpy.ones_like(PathTimePred))

    if self.lanes.get('flr20flc20pp') and self.lanes.get('vbox'):
      errors = ego_path_sliced.calc_rms_errors(fused_pp_sliced)
      errors[errors > RMS_MAX] = RMS_MAX  # TODO: remove hack
      PN = datavis.cPlotNavigator("flr20flc20pp and vbox")
      ax = PN.addAxis()
      PN.addSignal2Axis(ax, "rms", ego_path.time, errors)
      interface.Sync.addClient(PN)

    interface.Sync.addClient(TN)
    return
