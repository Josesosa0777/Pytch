# -*- dataeval: init -*-

import os
import sys

import numpy as np

import datavis
import interface
from measparser.signalproc import rescale
from view_fwdvehicledet_signals import add_dots

COMMONTIME = True  # rescale all signals to AEBS time or not
DESC_SIGNALS = {
  "warning": {
    "FLR20": {
      "KB": ["(PropWarn_FD, AcousticalWarning_FD)",],
      "RAIL": ["(AEBS1, Adv_Emergency_Braking_Sys_State)",],
      "FLR20": ["(AEBS1_2A, AEBSState_2A)",],
      },
    },
  "partial braking": {
    "FLR20": {
      "KB": ["(PropWarn_FD, AcousticalWarning_FD)",
             "(XBR_FD, XBRUS_AccelDemand_FD)"],
      "RAIL": ["(AEBS1, Adv_Emergency_Braking_Sys_State)",
               "(XBR_2A, XBR_ExtAccelDem_2A)"],
      "FLR20": ["(AEBS1_2A, AEBSState_2A)",
                "(XBR_2A, XBR_ExtAccelDem_2A)"],
      },
    },
  "emergency braking": {
    "FLR20": {
      "KB": ["(PropWarn_FD, AcousticalWarning_FD)",
             "(XBR_FD, XBRUS_AccelDemand_FD)"],
      "RAIL": ["(AEBS1, Adv_Emergency_Braking_Sys_State)",
               "(XBR_2A, XBR_ExtAccelDem_2A)"],
      "FLR20": ["(AEBS1_2A, AEBSState_2A)",
                "(XBR_2A, XBR_ExtAccelDem_2A)"],
      },
    },
  "acc. demand": {
    "FLR20": {
      "KB": ["(XBR_FD, XBRUS_AccelDemand_FD)",],
      "RAIL": ["(XBR_2A, XBR_ExtAccelDem_2A)",],
      "FLR20": ["(XBR_2A, XBR_ExtAccelDem_2A)",],
      },
    },
  "acc. measured": {
    "FLR20": {
      "KB": ["(IMU_XAccel_and_YawRate, X_Accel)",],
      "RAIL": ["(VDC2_0B, VDC2_LongAccel_0B)",],
      "FLR20": ["(VDC2_0B, VDC2_LongAccel_0B)",],
      },
    },
  "distance (dx)": {
    "FLR20": {
      "KB": ["(Tracks, tr0_range)",
             "(Tracks, tr0_uncorrected_angle)"],
      "RAIL": ["(Tracks, tr0_range)",
               "(Tracks, tr0_uncorrected_angle)"],
      "FLR20": ["(Tracks, tr0_range)",
                "(Tracks, tr0_uncorrected_angle)"],
      },
    },
  "ego speed (v_ego)": {
    "FLR20": {
      "KB": ["(General_radar_status,actual_vehicle_speed)"],
      "RAIL": ["(General_radar_status, actual_vehicle_speed)"],
      "FLR20": ["(General_radar_status, actual_vehicle_speed)"],
      },
    },
  "object speed (v_obj)": {
    "FLR20": {
      "KB": ["(General_radar_status, actual_vehicle_speed)",
             "(Tracks, tr0_relative_velocity)"],
      "RAIL": ["(General_radar_status, actual_vehicle_speed)",
               "(Tracks, tr0_relative_velocity)"],
      "FLR20": ["(General_radar_status, actual_vehicle_speed)",
                "(Tracks, tr0_relative_velocity)"],
      },
    },
  "ego yaw rate (&omega;_ego)": {
    "FLR20": {
      "KB": ["(General_radar_status, cvd_yawrate)"],
      "RAIL": ["(General_radar_status, cvd_yawrate)"],
      "FLR20": ["(General_radar_status, cvd_yawrate)"],
      },
    },
  }

init_params = {}
for algoname in "KB", "FLR20", "TRW", "RAIL":
  init_params["FLR20_%s" % algoname] = \
    dict(sensor='AC100', objind=None, algo="%s" % algoname)
  for i in xrange(20):
    init_params["FLR20_%02d_%s" % (i, algoname)] = \
      dict(sensor='AC100', objind=i, algo="%s" % algoname)

class AC100(object):
  """
  AC100-specific parameters and functions.
  """
  permaname = 'AC100'
  productname = "FLR20"
  ego_fill = 'calc_flr20_egomotion@aebs.fill'
  obj_fill = 'fill_flr20_raw_tracks@aebs.fill'
  objind_labelgroup = 'AC100 track'

class KB(object):
  """
  KB AEBS algorithm specific parameters - old version.
  """
  algo_fill = 'calc_aebs_phases@aebs.fill'
  signalgroups = [{"xbr": ("XBR_FD", "XBRUS_AccelDemand_FD"),},]

class FLR20(object):
  """
  KB AEBS algorithm specific parameters.
  """
  algo_fill = 'calc_flr20_aebs_phases-radar@aebs.fill'
  signalgroups = [{"xbr": ("XBR_FD", "XBRUS_AccelDemand_FD"),},]

class TRW(object):
  """
  TRW AEBS algorithm specific parameters.
  """
  algo_fill = 'calc_trw_aebs_phases@aebs.fill'
  signalgroups = [{"xbr": ("XBRUS_2A", "XBRUS_AccelDemand_2A"),},]


sgs = [
  {"ax": ("IMU_XAccel_and_YawRate", "X_Accel"),},
  {"ax": ("VDC2--Message--H566_All_Messages_v_04","LongitudinalAcceleration"),},
  {"ax": ("VDC2_0B", "VDC2_LongAccel_0B"),},
]

class RAIL(object):
  """
  AEBS algorithm parameters that can be used with RAIL measurements.
  """
  algo_fill = 'calc_flr20_aebs_phases-rail@aebs.fill'
  signalgroups = [{"xbr": ("XBR_2A", "XBR_ExtAccelDem_2A"),}]

def explain(sensor_productname, algo_name):
  if sensor_productname != "FLR20" or algo_name not in ["KB", "RAIL", "FLR20"]:
    raise NotImplementedError  # TODO: add description

  from collections import OrderedDict

  from reportlab.platypus import Paragraph, Spacer
  from reportlab.lib.styles import getSampleStyleSheet
  from reportlab.lib.pagesizes import cm

  from datalab.tygra import ListItem, bold, italic

  styles = getSampleStyleSheet()
  story = []

  ptext = """
    The AEBS braking evaluation plot shows several signals to help to analyze
    the warning and automatic braking behavior.<br/>
    The selected area indicates the AEBS cascade, or more precisely, the
    period of the warning. The colored dots represent the beginning
    of the different phases.
  """
  story.append(Paragraph(ptext, styles['Normal']))
  story.append(Spacer(0, 0.5*cm))

  story.append(Paragraph(bold("Signals:"), styles['Normal']))

  desc = OrderedDict([ (
    "warning",
    OrderedDict([
      ("Meaning", "Indicates the warning that is provided to the driver."),
      ("Source",  "FLR20, the AEBS algorithm"),
      ("Signals", ", ".join(DESC_SIGNALS["warning"][sensor_productname][algo_name])),
    ])), (
    "partial braking",
    OrderedDict([
      ("Meaning", "Indicates the period of the second phase (partial braking) "
                  "of the AEBS cascade. Calculated by the warning and "
                  "acceleration demand signals."),
      ("Source",  "FLR20, the AEBS algorithm"),
      ("Signals", ", ".join(DESC_SIGNALS["partial braking"][sensor_productname][algo_name])),
      ("Calculation", "Acceleration demand equals -3 m/s<super>2</super> "
                      "while a warning is present."),
    ])), (
    "emergency braking",
    OrderedDict([
      ("Meaning", "Indicates the period of the third phase (emergency braking) "
                  "of the AEBS cascade. Calculated by the warning and "
                  "acceleration demand signals."),
      ("Source",  "FLR20, the AEBS algorithm"),
      ("Signals", ", ".join(DESC_SIGNALS["emergency braking"][sensor_productname][algo_name])),
      ("Calculation", "Acceleration demand is less than -3 m/s<super>2</super> "
                  "while a warning is present."),
    ])), (
    "acc. demand",
    OrderedDict([
      ("Meaning", "The continuously calculated acceleration (deceleration) "
                  "demand of the AEBS algorithm in [m/s<super>2</super>], "
                  "required for "
                  "avoiding/mitigating a collision. This has to be realized "
                  "by the brake system. The final value is held for a given "
                  "time in order to keep the vehicle stopped in case of an "
                  "accident (\"in-crash braking\")."),
      ("Source",  "FLR20, the AEBS algorithm"),
      ("Destination", "Brake system"),
      ("Signals", ", ".join(DESC_SIGNALS["acc. demand"][sensor_productname][algo_name])),
    ])), (
    "acc. measured",
    OrderedDict([
      ("Meaning", "The actual acceleration (deceleration) of the ego vehicle "
                  "in [m/s<super>2</super>]."),
      ("Source",  "Acceleration sensor (IMU)"),
      ("Signals", ", ".join(DESC_SIGNALS["acc. measured"][sensor_productname][algo_name])),
      ("Conversion", "The value has to be converted from [g] to "
                  "[m/s<super>2</super>]."),
    ])), (
    "distance (dx)",
    OrderedDict([
      ("Meaning", "The longitudinal distance between the ego vehicle and the "
                  "obstacle in [m]."),
      ("Source",  "FLR20"),
      ("Signals", ", ".join(DESC_SIGNALS["distance (dx)"][sensor_productname][algo_name])),
      ("Calculation", "dx = tr0_range &sdot; cos(tr0_uncorrected_angle), "
                  "where the angle is in [&deg;]."),
    ])), (
    "ego speed (v_ego)",
    OrderedDict([
      ("Meaning", "The speed of the ego (host) vehicle in [km/h]."),
      ("Source",  "FLR20, based on the vehicle's wheel speed sensors"),
      ("Signals", ", ".join(DESC_SIGNALS["ego speed (v_ego)"][sensor_productname][algo_name])),
      ("Conversion", "The value has to be converted from [m/s] to [km/h]."),
    ])), (
    "object speed (v_obj)",
    OrderedDict([
      ("Meaning", "The absolute speed of the target vehicle in [km/h]."),
      ("Source",  "FLR20"),
      ("Signals", ", ".join(DESC_SIGNALS["object speed (v_obj)"][sensor_productname][algo_name])),
      ("Calculation", "v_obj = actual_vehicle_speed + tr0_relative_velocity"),
      ("Conversion", "The value has to be converted from [m/s] to [km/h]."),
    ])), (
    "ego yaw rate (&omega;_ego)",
    OrderedDict([
      ("Meaning", "The yaw rate of the ego (host) vehicle in [&deg;/s]."),
      ("Source",  "FLR20 internal yaw rate sensor"),
      ("Signals", ", ".join(DESC_SIGNALS["ego yaw rate (&omega;_ego)"][sensor_productname][algo_name])),
      ("Conversion", "The value has to be multiplied by -1 to meet the "
                  "conventional coordinate frame."),
    ])),
  ])
  for signal, details in desc.iteritems():
    story.append(ListItem(bold(signal), styles['Normal'], level=0))
    for k, v in details.iteritems():
      story.append(ListItem("%s: %s"%(italic(k), v), styles['Normal'], level=1))
  return story

EXP_UNITS = {
  'xbr': ('m/s^2', 'm/s2', 'm/ss'),
  'ax':  ('g', 'm/s^2', 'm/s2', 'm/ss'),
}

def check_unit(alias, unit):
  """
  Check whether the signal's physical unit is the expected one or not.
  Raise AssertionError in the latter case.
  """
  if unit == '':
    print >> sys.stderr, "Unit check not possible for %s." % alias
    return
  if unit not in EXP_UNITS[alias]:
    raise AssertionError('unexpected unit for %s: %s' % (alias, unit))
  return


querystr_base = """
  SELECT ei.start_time,
         ei.end_time
  FROM entryintervals ei
  JOIN entries en         ON en.id = ei.entryid
  JOIN measurements me    ON me.id = en.measurementid
  JOIN modules mo         ON mo.id = en.moduleid
  JOIN interval2label il  ON il.entry_intervalid = ei.id
  JOIN labels la          ON la.id = il.labelid
  JOIN labelgroups lg     ON lg.id = la.groupid
  WHERE la.name = "%s" AND
        lg.name = "AEBS cascade phase" AND
        mo.class = "dataevalaebs.search_aebs_cascade.Search" AND
        me.basename = :measname
"""

querystr = """
  SELECT cascade.start_time,
         cascade.end_time,
         warning.start_time,
         partbrk.start_time,
         emerbrk.start_time
  FROM (%s) cascade
  JOIN (%s) warning ON
    warning.start_time BETWEEN cascade.start_time AND cascade.end_time AND
    warning.end_time   BETWEEN cascade.start_time AND cascade.end_time
  LEFT JOIN (%s) partbrk ON
    partbrk.start_time BETWEEN cascade.start_time AND cascade.end_time AND
    partbrk.end_time   BETWEEN cascade.start_time AND cascade.end_time
  LEFT JOIN (%s) emerbrk ON
    emerbrk.start_time BETWEEN cascade.start_time AND cascade.end_time AND
    emerbrk.end_time   BETWEEN cascade.start_time AND cascade.end_time
""" % (
  querystr_base % "pre-crash intervention",
  querystr_base % "warning",
  querystr_base % "partial braking",
  querystr_base % "emergency braking",
)

def _add_dots(ax, time, value,
              warning_starts, partbrk_starts, emerbrk_starts, annotate=False):
  textoffset = None
  if annotate:
    textoffset = (-10, 5)
  add_dots(ax, time, value, warning_starts, 'b.', textoffset)
  if annotate:
    textoffset = (0, 5)
  add_dots(ax, time, value, partbrk_starts, 'r.', textoffset)
  if annotate:
    textoffset = (5, 5)
  add_dots(ax, time, value, emerbrk_starts, 'r.', textoffset)
  return

class View(interface.iView):
  def init(self, sensor, objind, algo):
    assert sensor in globals(), "parameter class for %s not defined" % sensor
    assert algo in globals(), "parameter class for %s not defined" % algo
    self.sensor = globals()[sensor]
    self.algo = globals()[algo]
    self.objind = objind
    self.dep = (self.algo.algo_fill, self.sensor.ego_fill, self.sensor.obj_fill)
    return

  def check(self):
    source = self.get_source()
    group = source.selectSignalGroup(self.algo.signalgroups)
    group_ = source.selectSignalGroup(sgs)
    group.update(group_)
    return group

  def fill(self, group):
    modules = self.get_modules()
    phases = modules.fill(self.algo.algo_fill)
    ego = modules.fill(self.sensor.ego_fill)
    if self.objind is not None:
      objects = modules.fill(self.sensor.obj_fill)
      obj = objects[self.objind]
    else:
      obj = None
    if COMMONTIME:
      ScaleTime = phases.time
      ego = ego.rescale(ScaleTime)
      if obj is not None:
        obj = obj.rescale(ScaleTime)
    else:
      ScaleTime = None
    # load data from database (if any)
    measname = os.path.basename(self.get_source().FileName)
    int_data = self.get_batch().query(querystr, measname=measname)
    cascade_limits = [timestamps[0:2] for timestamps in int_data]
    warning_starts = [timestamps[2] for timestamps in int_data]
    partbrk_starts = [timestamps[3] for timestamps in int_data]
    emerbrk_starts = [timestamps[4] for timestamps in int_data]
    dots = (warning_starts, partbrk_starts, emerbrk_starts)
    return ScaleTime, phases, group, ego, obj, cascade_limits, dots

  def view(self, ScaleTime, phases, group, ego, obj, cascade_limits, dots):
    title = "%s" % self.sensor.productname
    if self.objind is not None:
      title += " internal track %d" % self.objind
    pn = datavis.cPlotNavigator(title=title)
    # cascade
    ax = pn.addAxis(ylabel="AEBS", ylim=(-0.5, 5.5))
    ax.set_yticks([0, 1, 2, 3, 4, 5])
    ax.set_yticklabels(map(str, [0, 1, 0, 1, 0, 1]))
    pn.addSignal2Axis(ax, "warning", phases.time, phases.warning,
      unit="-", offset=4, displayscaled=False)
    _add_dots(ax, phases.time, phases.warning+4, *dots)
    pn.addSignal2Axis(ax, "partial b.", phases.time, phases.partial_braking,
      unit="-", offset=2, displayscaled=False)
    _add_dots(ax, phases.time, phases.partial_braking+2, *dots)
    pn.addSignal2Axis(ax, "emergency b.", phases.time, phases.emergency_braking,
      unit="-", offset=0, displayscaled=False)
    _add_dots(ax, phases.time, phases.emergency_braking+0, *dots)
    # deceleration
    ax = pn.addAxis(ylabel="acceleration", ylim=(-12.0, 2.0))
    ax.set_yticks(np.arange(-10.0, 0.1, 3.0))
    xbr_time, xbr, xbr_unit = \
      group.get_signal_with_unit("xbr", ScaleTime=ScaleTime)
    #check_unit('xbr', xbr_unit)
    pn.addSignal2Axis(ax, "acc. demand", xbr_time, xbr, unit="m/s^2")
    _add_dots(ax, xbr_time, xbr, *dots)
    axx_time, axx, axx_unit = \
      group.get_signal_with_unit("ax", ScaleTime=ScaleTime)
    #check_unit('ax', axx_unit)
    if axx_unit is 'g':
      axx = axx * 9.81  # g -> m/s^2
    pn.addSignal2Axis(ax, "acc. measured", axx_time, axx, unit="m/s^2")
    _add_dots(ax, axx_time, axx, *dots)
    # dx
    if obj is not None:
      ax = pn.addAxis(ylabel="distance", ylim=(0.0, 80.0))
      ax.set_yticks(np.arange(0.0, 80.1, 30.0))
      pn.addSignal2Axis(ax, "dx", obj.time, obj.dx, unit="m")
      _add_dots(ax, obj.time, obj.dx, *dots, annotate=True)
    # speed
    ax = pn.addAxis(ylabel="speed", ylim=(-1.0, 100.0))
    ax.set_yticks(np.arange(0.0, 100.1, 30.0))
    egospeed_kph = 3.6 * ego.vx
    pn.addSignal2Axis(ax, "v_ego", ego.time, egospeed_kph, unit="km/h")
    _add_dots(ax, ego.time, egospeed_kph, *dots, annotate=True)
    if obj is not None:
      ego_vx_rescaled = rescale(ego.time, ego.vx, obj.time, Order='foh')[1]
      objspeed_kph = 3.6 * (obj.vx + ego_vx_rescaled)  # absolute speed
      pn.addSignal2Axis(ax, "v_obj", obj.time, objspeed_kph, unit="km/h")
      _add_dots(ax, obj.time, objspeed_kph, *dots, annotate=True)
    # yaw rate
    ax = pn.addAxis(ylabel="yaw rate", ylim=(-12.0, 12.0))
    ax.set_yticks(np.arange(-10.0, 10.01, 5.0))
    egoyawrate_dps = np.rad2deg(ego.yaw_rate)
    pn.addSignal2Axis(ax, "$\omega$_ego", ego.time,egoyawrate_dps, unit=u"\u00B0/s")
    _add_dots(ax, ego.time, egoyawrate_dps, *dots)
    # xlabel
    ax.set_xlabel("time [s]")
    # customize and register plotnavigator
    pn.setUserWindowTitle(title)
    for start, end in cascade_limits:
      for ax in pn.fig.axes:
        # highlight AEBS cascade
        ax.axvspan(start, end, facecolor='b', alpha=0.2)
    self.get_sync().addClient(pn)
    return
