# -*- dataeval: init -*-

import sys

import numpy
import scipy

import datavis
import measparser
import interface
import pathpred.pathpredictor

import pathpred.predictedpath

Lines = [{'CurveLane': ('RadarFC', 'evi.General_TC.kapCurvTraj'),
          'CurveEgo':  ('RadarFC', 'dcp.kapCourse')}]

ROADRMOLanePolyA0 = 1.5
ROADRSOLanePolyA0 = 0.9
AC100LanePolyA0 = ROADRMOLanePolyA0

init_params = {
  "CVR3_SCAM": dict(lanes=dict(cvr3=True, flc20=True, flr20lf=False, flr20flc20pp=False)),
  "FLR20LF_FLC20_FLR20FLC20PP": dict(lanes=dict(cvr3=False, flc20=True, flr20lf=True, flr20flc20pp=True)),
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
  ego_motion = ego_motion.rescale(flc20_lines.time)  # TODO: avoid
  line_f, debug = pp.predict(ego_motion, flc20_lines)
  # make viewrange Dataset-compatible
  viewrange_f_x = numpy.vstack((debug.viewrange_f, debug.viewrange_f)).T
  viewrange_f_y = numpy.empty_like(viewrange_f_x)
  viewrange_f_y[:, 0] = -1000.0  # arbitrary small number
  viewrange_f_y[:, 1] =  1000.0  # arbitrary large number
  return line_f.time, line_f, debug.dx_m, debug.dy_m, debug.dy_l, debug.dy_f, viewrange_f_x, viewrange_f_y

class View(interface.iView):
  def init(self, lanes):
    self.lanes = lanes
    dep = set()
    if self.lanes['flr20lf']:
      dep.add('calc_flr20_pathpred_lf@aebs.fill')
    if self.lanes['flc20']:
      dep.add('calc_flc20_lanes@aebs.fill')
    if self.lanes['flr20flc20pp']:
      dep.add('calc_flc20_lanes@aebs.fill')
      dep.add('calc_flr20_egomotion@aebs.fill')
      dep.add('calc_vbox_egomotion@aebs.fill')
      dep.add('calc_vbox_egopath@aebs.fill')
    self.dep = tuple(dep)
    return

  def view(self):
    TN = datavis.cTrackNavigator()
    TN.addGroups(interface.Groups)
    TN.setLegend(interface.Legends)

    for GroupName, (LeftAngle, RightAngle, kwargs) in interface.ViewAngles.iteritems():
      TN.setViewAngle(LeftAngle, RightAngle, GroupName, **kwargs)

    if self.lanes['cvr3']:
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

    if self.lanes['flc20']:
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

    if self.lanes['flr20lf']:
      flr20_line = self.get_modules().fill('calc_flr20_pathpred_lf@aebs.fill')
      flr20_time = flr20_line.time
      Track = TN.addTrack('FLR20 LF', flr20_time, color='b')
      FuncName = Track.addFunc(polyClothoid)
      Track.addParam(FuncName, 'A0', flr20_time, flr20_line.a0)
      Track.addParam(FuncName, 'A1', flr20_time, flr20_line.a1)
      Track.addParam(FuncName, 'A2', flr20_time, flr20_line.a2)
      Track.addParam(FuncName, 'A3', flr20_time, flr20_line.a3)
      Track.addParam(FuncName, 'Distance', flr20_time, 100.0 * numpy.ones_like(flr20_time))

    for StatusName in interface.Objects.get_selected_by_parent(interface.iFill):
      Time, Objects = interface.Objects.fill(StatusName)
      for Object in Objects:
        TN.addObject(Time, Object)

    if self.lanes['flr20flc20pp']:
      modules = self.get_modules()
      ego_motion = modules.fill('calc_flr20_egomotion@aebs.fill')

      ego_motion_imu = modules.fill('calc_vbox_egomotion@aebs.fill')
      ego_motion_imu = ego_motion_imu.rescale(ego_motion.time)

      ego_path = modules.fill('calc_vbox_egopath@aebs.fill')
      ego_path = ego_path.rescale(ego_motion.time)
      ego_path = ego_path._smooth()
      ego_path_sliced = ego_path.slice(0, 50)
      TN.addDataset(ego_path_sliced.time, ego_path_sliced.get_dxs(), ego_path_sliced.get_dys(), 'Factual ego path (VBOX)', color='k')

      predicted_path = pathpred.predictedpath.calc_predicted_path(ego_motion, 40e-3, 0.95, ego_motion_imu)
      time = ego_motion.time
      # add predicted paths as a series of positions
      TN.addDataset(time, predicted_path['IMM x predictions'], predicted_path['IMM y predictions'], 'Predicted ego path (IMM)', color='c')
      #TN.addDataset(time, predicted_path['CA x predictions'], predicted_path['CA y predictions'], 'Predicted ego path (CA Kalman)', color='y')
      #TN.addDataset(time, predicted_path['CTR x predictions'], predicted_path['CTR y predictions'], 'Predicted ego path (CTR Kalman)', color='m')

      PN = datavis.cPlotNavigator() # probabilities
      PN2 = datavis.cPlotNavigator() # states

      plot_signals = predicted_path['plot signals']
      _, norms = predicted_path['IMM filter'].reshape_measurement_residuals(predicted_path['measurement residuals'])

      axis_residuals = PN.addAxis()
      PN.addSignal2Axis(axis_residuals, "CA residual", time, norms[0, :])
      PN.addSignal2Axis(axis_residuals, "CTR residual", time, norms[1, :])
      #PN.addSignal2Axis(axis_residuals, "CTRA residual", time, norms[2, :])

      axis_likelihoods = PN.addAxis()
      PN.addSignal2Axis(axis_likelihoods, "CA likelihood", time, predicted_path['likelihood functions'][0, :])
      PN.addSignal2Axis(axis_likelihoods, "CTR likelihood", time, predicted_path['likelihood functions'][1, :])
      #PN.addSignal2Axis(axis_likelihoods, "CTRA likelihood", time, predicted_path['likelihood functions'][2, :])

      axis = PN.addAxis()
      PN.addSignal2Axis(axis, "CA probability", time, predicted_path['mode probabilities'][0, :])
      PN.addSignal2Axis(axis, "CTR probability", time, predicted_path['mode probabilities'][1, :])
      #PN.addSignal2Axis(axis, "CTRA probability", time, predicted_path['mode probabilities'][2, :])

      axis_speed = PN2.addAxis()
      PN2.addSignal2Axis(axis_speed, "measured v", time, plot_signals['v'])
      PN2.addSignal2Axis(axis_speed, "IMM v", time, predicted_path['IMM states'][0, :])
      #PN2.addSignal2Axis(axis_speed, "CA v", time, predicted_path['CA filtered states'][0, :])
      #PN2.addSignal2Axis(axis_speed, "CTR v", time, predicted_path['CTR filtered states'][0, :])
      #PN2.addSignal2Axis(axis_speed, "CTRA v", time, predicted_path['CTRA filtered states'][0, :])

      axis_tangent = PN2.addAxis()
      PN2.addSignal2Axis(axis_tangent, "measured at", time, plot_signals['at'])
      PN2.addSignal2Axis(axis_tangent, "IMM at", time, predicted_path['IMM states'][1, :])
      #PN2.addSignal2Axis(axis_tangent, "CA at", time, predicted_path['CA filtered states'][1, :])
      #PN2.addSignal2Axis(axis_tangent, "CTR at", time, predicted_path['CTR filtered states'][1, :])
      #PN2.addSignal2Axis(axis_tangent, "CTRA at", time, predicted_path['CTRA filtered states'][1, :])

      axis_yaw = PN2.addAxis()
      PN2.addSignal2Axis(axis_yaw, "measured yaw rate", time, plot_signals['yaw rate'])
      PN2.addSignal2Axis(axis_yaw, "IMM yaw rate", time, predicted_path['IMM states'][2, :])
      #PN2.addSignal2Axis(axis_yaw, "CA yaw rate", time, predicted_path['CA filtered states'][2, :])
      #PN2.addSignal2Axis(axis_yaw, "CTR yaw rate", time, predicted_path['CTR filtered states'][2, :])
      #PN2.addSignal2Axis(axis_yaw, "CTRA yaw rate", time, predicted_path['CTRA filtered states'][2, :])

       #Measurement residuals
#       reshaped, norms = predicted_path['IMM filter'].reshape_measurement_residuals(predicted_path['measurement residuals'])
#
#       axis_residuals = PN.addAxis()
#       PN.addSignal2Axis(axis_residuals, "CA residual", time, norms[0, :])
#       PN.addSignal2Axis(axis_residuals, "CTR residual", time, norms[1, :])
#       #PN.addSignal2Axis(axis_residuals, "Dumb residual", time, norms[2, :])
#
#       axis_likelihoods = PN.addAxis()
#       PN.addSignal2Axis(axis_likelihoods, "CA likelihood", time, predicted_path['likelihood functions'][0, :])
#       PN.addSignal2Axis(axis_likelihoods, "CTR likelihood", time, predicted_path['likelihood functions'][1, :])
#       #PN.addSignal2Axis(axis_likelihoods, "Dumb likelihood", time, likelihoods[2, :])
#
#       axis = PN.addAxis()
#       PN.addSignal2Axis(axis, "CA probability", time, predicted_path['mode probabilities'][0, :])
#       PN.addSignal2Axis(axis, "CTR probability", time, predicted_path['mode probabilities'][1, :])
#       #PN.addSignal2Axis(axis, "Dumb probability", time, mode_probabilities[2, :])
#
#       #model states
#       plot_signals = predicted_path['plot signals'] #pathpred.predictedpath.construct_plot_signals(ego_motion, ego_motion_imu)
#
#       axis2 = PN2.addAxis()
#       PN2.addSignal2Axis(axis2, "measured x", time, plot_signals['x'])
#       PN2.addSignal2Axis(axis2, "IMM x", time, predicted_path['IMM states'][0, :])
# #       PN2.addSignal2Axis(axis2, "CA x", time, predicted_path['CA filtered states'][0, :])
# #       PN2.addSignal2Axis(axis2, "CTR x", time, predicted_path['CTR filtered states'][0, :])
#
#       axis3 = PN2.addAxis()
#       PN2.addSignal2Axis(axis3, "measured vx", time, plot_signals['vx'])
#       PN2.addSignal2Axis(axis3, "IMM vx", time, predicted_path['IMM states'][1, :])
# #       PN2.addSignal2Axis(axis3, "CA vx", time, predicted_path['CA filtered states'][1, :])
# #       PN2.addSignal2Axis(axis3, "CTR vx", time, predicted_path['CTR filtered states'][1, :])
#
#       axis4 = PN2.addAxis()
#       PN2.addSignal2Axis(axis4, "measured ax", time, plot_signals['ax'])
#       PN2.addSignal2Axis(axis4, "IMM ax", time, predicted_path['IMM states'][2, :])
# #       PN2.addSignal2Axis(axis4, "CA ax", time, predicted_path['CA filtered states'][2, :])
# #       PN2.addSignal2Axis(axis4, "CTR ax", time, predicted_path['CTR filtered states'][2, :])
#
#       axis5 = PN2.addAxis()
#       PN2.addSignal2Axis(axis5, "measured y", time, plot_signals['y'])
#       PN2.addSignal2Axis(axis5, "IMM y", time, predicted_path['IMM states'][3, :])
# #       PN2.addSignal2Axis(axis5, "CA y", time, predicted_path['CA filtered states'][3, :])
# #       PN2.addSignal2Axis(axis5, "CTR y", time, predicted_path['CTR filtered states'][3, :])
#
#       axis6 = PN2.addAxis()
#       PN2.addSignal2Axis(axis6, "measured vy", time, plot_signals['vy'])
#       PN2.addSignal2Axis(axis6, "IMM vy", time, predicted_path['IMM states'][4, :])
# #       PN2.addSignal2Axis(axis6, "CA vy", time, predicted_path['CA filtered states'][4, :])
# #       PN2.addSignal2Axis(axis6, "CTR vy", time, predicted_path['CTR filtered states'][4, :])
#
#       axis7 = PN2.addAxis()
#       PN2.addSignal2Axis(axis7, "measured ay", time, plot_signals['ay'])
#       PN2.addSignal2Axis(axis7, "IMM ay", time, predicted_path['IMM states'][5, :])
# #       PN2.addSignal2Axis(axis7, "CA ay", time, predicted_path['CA filtered states'][5, :])
# #       PN2.addSignal2Axis(axis7, "CTR ay", time, predicted_path['CTR filtered states'][5, :])
#
#       axis8 = PN2.addAxis()
#       PN2.addSignal2Axis(axis8, "measured yaw rate", time, plot_signals['yaw rate'])
#       PN2.addSignal2Axis(axis8, "IMM yaw rate", time, predicted_path['IMM states'][6, :])
# #       PN2.addSignal2Axis(axis8, "CA yaw_rate", time, predicted_path['CA filtered states'][6, :])
# #       PN2.addSignal2Axis(axis8, "CTR yaw_rate", time, predicted_path['CTR filtered states'][6, :])


    interface.Sync.addClient(PN)
    interface.Sync.addClient(PN2)
    interface.Sync.addClient(TN)

    return
