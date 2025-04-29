# -*- dataeval: init -*-

import os

import numpy as np

import datavis
import interface
from measparser.signalproc import rescale

COMMONTIME = True  # rescale all signals to object time or not
PLOT_CONFIDENCE = False
PLOT_POWER = False

init_params = {}
for i in xrange(20):
  init_params["FLR20_%02d" % i] = dict(sensor='AC100', objind=i)

class AC100(object):
  """
  AC100-specific parameters and functions.
  """
  permaname = 'AC100'
  productname = "FLR20"
  ego_fill = 'calc_flr20_egomotion@aebs.fill'
  obj_fill = 'fill_flr20_raw_tracks@aebs.fill'
  objind_labelgroup = 'AC100 track'


def explain(sensor_productname):
  if sensor_productname != "FLR20":
    raise NotImplementedError  # TODO: add description

  from collections import OrderedDict

  from reportlab.platypus import Paragraph, Spacer
  from reportlab.lib.styles import getSampleStyleSheet
  from reportlab.lib.pagesizes import cm

  from datalab.tygra import ListItem, bold, italic

  styles = getSampleStyleSheet()
  story = []

  ptext = """
    The object detection performance evaluation plot shows several signals
    to help to analyze the detection and classification behavior.<br/>
    The selected area indicates the stable detection period, i.e. the interval
    in which the sensor considered the object as a relevant obstacle for
    the AEBS function, and automatic braking is possible.
  """
  story.append(Paragraph(ptext, styles['Normal']))
  story.append(Spacer(0, 0.5*cm))

  story.append(Paragraph(bold("Signals:"), styles['Normal']))

  desc = OrderedDict([ (
    "ego speed (v_ego)",
    OrderedDict([
      ("Meaning", "The speed of the ego (host) vehicle in [km/h]."),
      ("Source",  "FLR20, based on the vehicle's wheel speed sensors"),
      ("Signals", "(General_radar_status, actual_vehicle_speed)"),
      ("Conversion", "The value has to be converted from [m/s] to [km/h]."),
    ])), (
    "object speed (v_obj)",
    OrderedDict([
      ("Meaning", "The absolute speed of the target vehicle in [km/h]."),
      ("Source",  "FLR20"),
      ("Signals", "(General_radar_status, actual_vehicle_speed), "
                  "(Tracks, tr0_relative_velocity)"),
      ("Calculation", "v_obj = actual_vehicle_speed + tr0_relative_velocity"),
      ("Conversion", "The value has to be converted from [m/s] to [km/h]."),
    ])), (
    "ego yaw rate (&omega;_ego)",
    OrderedDict([
      ("Meaning", "The yaw rate of the ego (host) vehicle in [&deg;/s]."),
      ("Source",  "FLR20 internal yaw rate sensor"),
      ("Signals", "(General_radar_status, cvd_yawrate)"),
      ("Conversion", "The value has to be multiplied by -1 to meet the "
                  "conventional coordinate frame."),
    ])), (
    "distance (dx)",
    OrderedDict([
      ("Meaning", "The longitudinal distance between the ego vehicle and the "
                  "obstacle in [m]."),
      ("Source",  "FLR20"),
      ("Signals", "(Tracks, tr0_range), (Tracks, tr0_uncorrected_angle)"),
      ("Calculation", "dx = tr0_range &sdot; cos(tr0_uncorrected_angle), "
                  "where the angle is in [&deg;]."),
    ])), (
    "aeb_track",
    OrderedDict([
      ("Meaning", "The obstacle is selected as the most relevant object for "
                  "the AEBS (braking might occur on this obstacle only)."),
      ("Source",  "FLR20"),
      ("Signals", "(Tracks, tr0_CW_track)"),
      ("Calculation", "The corresponding signal equals 1, and the ego vehicle "
                  "has stopped."),
    ])), (
    "fused",
    OrderedDict([
      ("Meaning", "The obstacle is detected by both the radar and the camera "
                  "in the corresponding cycle, and its attributes are fused "
                  "(improved)."),
      ("Source",  "FLR20"),
      ("Signals", "(Tracks, tr0_is_video_associated)"),
    ])),
  ])
  if PLOT_CONFIDENCE:
    desc["radar conf."] = OrderedDict([
      ("Meaning", ""),
      ("Source",  ""),
      ("Signals", ""),
    ])
    desc["video conf."] = OrderedDict([
      ("Meaning", ""),
      ("Source",  ""),
      ("Signals", ""),
    ])
    raise NotImplementedError  # TODO: add description
  if PLOT_POWER:
    desc["power"] = OrderedDict([
      ("Meaning", ""),
      ("Source",  ""),
      ("Signals", ""),
    ])
    raise NotImplementedError  # TODO: add description
  for signal, details in desc.iteritems():
    story.append(ListItem(bold(signal), styles['Normal'], level=0))
    for k, v in details.iteritems():
      story.append(ListItem("%s: %s"%(italic(k), v), styles['Normal'], level=1))
  return story

querystr_base = """
  SELECT ei.start_time,
         ei.end_time
  FROM entryintervals ei
  JOIN entries en         ON en.id = ei.entryid
  JOIN measurements me    ON me.id = en.measurementid
  JOIN modules mo         ON mo.id = en.moduleid
  JOIN interval2label il1 ON il1.entry_intervalid = ei.id
  JOIN labels la1         ON la1.id = il1.labelid
  JOIN labelgroups lg1    ON lg1.id = la1.groupid
  JOIN interval2label il2 ON il2.entry_intervalid = ei.id
  JOIN labels la2         ON la2.id = il2.labelid
  JOIN labelgroups lg2    ON lg2.id = la2.groupid
  WHERE la1.name = "valid" AND
        lg1.name = "standard" AND
        la2.name = :objind AND
        lg2.name = :objind_labelgroup AND
        en.title = "%s" AND
        mo.class = "dataevalaebs.search_fwdvehicledet.Search" AND
        mo.param = "sensor='" || :sensor || "'" AND
        me.basename = :measname
"""

querystr = """
  SELECT wholelife.start_time,
         wholelife.end_time,
         stableint.start_time,
         stableint.end_time
  FROM (%s) wholelife
  LEFT JOIN (%s) stableint ON
    stableint.start_time BETWEEN wholelife.start_time AND
                                 wholelife.end_time AND
    stableint.end_time   BETWEEN wholelife.start_time AND
                                 wholelife.end_time
""" % (
  querystr_base % "AEBS use case - Forward vehicle detection (whole life)",
  querystr_base % "AEBS use case - Forward vehicle detection (stable period)",
)

def _add_dots(ax, time, value, life_limits, stable_limits, annotate=False):
  textoffset = None
  life_starts = [start for start, _ in life_limits]
  if annotate:
    textoffset = (-10, 5)
  add_dots(ax, time, value, life_starts, 'b.', textoffset)
  stable_starts = [start for start, _ in stable_limits]
  if annotate:
    textoffset = (5, 5)
  add_dots(ax, time, value, stable_starts, 'r.', textoffset)
  return

def add_dots(ax, time, value, timestamps, style, textoffset):
  if time.size < 1:
    return
  for timestamp in timestamps:
    if timestamp is None:
      continue
    if timestamp < time[0] or timestamp > time[-1]:
      continue
    ind = time.searchsorted(timestamp)
    if np.allclose(time[ind], timestamp):  # exact value
      val = value[ind]
    else:  # 'zoh' behavior
      prev_ind = max(ind-1, 0)
      val = value[prev_ind]
      timestamp = time[prev_ind]
    if val is np.ma.masked:
      continue
    ax.plot(timestamp, val, style)
    if textoffset is not None:
      if isinstance(val, int):
        text = "%d" % val
      elif isinstance(val, float):
        text = "%.1f" % val
      else:
        text = str(val)
      ax.annotate(text, xy=(timestamp,val),
        xytext=textoffset, textcoords='offset points')
  return

class View(interface.iView):
  def init(self, sensor, objind):
    assert sensor in globals(), "parameter class for %s not defined" % sensor
    self.sensor = globals()[sensor]
    self.objind = objind
    self.dep = (self.sensor.ego_fill, self.sensor.obj_fill)
    return

  def fill(self):
    modules = self.get_modules()
    ego = modules.fill(self.sensor.ego_fill)
    objects = modules.fill(self.sensor.obj_fill)
    obj = objects[self.objind]
    # rescale on demand
    if COMMONTIME:
      ego = ego.rescale(obj.time)
    # load data from database (if any)
    queryparams = {
      'objind':            self.objind,
      'objind_labelgroup': self.sensor.objind_labelgroup,
      'sensor':            self.sensor.permaname,
      'measname':          os.path.basename(self.get_source().FileName),
    }
    int_limits = self.get_batch().query(querystr, **queryparams)
    life_limits   = [lims[0:2] for lims in int_limits]
    stable_limits = [lims[2:4] for lims in int_limits]
    return ego, obj, life_limits, stable_limits

  def view(self, ego, obj, life_limits, stable_limits):
    title = "%s internal track %d" % (self.sensor.productname, self.objind)
    pn = datavis.cPlotNavigator(title=title)
    # speed
    ax = pn.addAxis(ylabel="speed", ylim=(-1.0, 100.0))
    ax.set_yticks(np.arange(0.0, 100.1, 30.0))
    egospeed_kph = 3.6 * ego.vx
    pn.addSignal2Axis(ax, "v_ego", ego.time, egospeed_kph, unit="km/h")
    _add_dots(ax, ego.time, egospeed_kph, life_limits, stable_limits, True)
    ego_vx_rescaled = rescale(ego.time, ego.vx, obj.time, Order='foh')[1]
    objspeed_kph = 3.6 * (obj.vx + ego_vx_rescaled)  # absolute speed
    pn.addSignal2Axis(ax, "v_obj", obj.time, objspeed_kph, unit="km/h")
    _add_dots(ax, obj.time, objspeed_kph, life_limits, stable_limits, True)
    # yaw rate
    ax = pn.addAxis(ylabel="yaw rate", ylim=(-12.0, 12.0))
    ax.set_yticks(np.arange(-10.0, 10.01, 5.0))
    egoyawrate_dps = np.rad2deg(ego.yaw_rate)
    pn.addSignal2Axis(ax, "$\omega$_ego", ego.time,egoyawrate_dps, unit=u"\u00B0/s")
    _add_dots(ax, ego.time, egoyawrate_dps, life_limits, stable_limits)
    # dx
    ax = pn.addAxis(ylabel="distance", ylim=(0.0, 150.0))
    ax.set_yticks(np.arange(0.0, 150.1, 30.0))
    pn.addSignal2Axis(ax, "dx", obj.time, obj.dx, unit="m")
    _add_dots(ax, obj.time, obj.dx, life_limits, stable_limits, True)
    # aeb_track & fused
    ax = pn.addAxis(ylabel="relevance", ylim=(-0.5, 3.5))
    ax.set_yticks([0, 1, 2, 3])
    ax.set_yticklabels(map(str, [0, 1, 0, 1]))
    pn.addSignal2Axis(ax, "aeb_track", obj.time, obj.aeb_track, unit="-",
      offset=2, displayscaled=False)
    _add_dots(ax, obj.time, obj.aeb_track+2, life_limits, stable_limits)
    pn.addSignal2Axis(ax, "fused", obj.time, obj.fused, unit="-",
      offset=0, displayscaled=False)
    _add_dots(ax, obj.time, obj.fused+0, life_limits, stable_limits)
    # confidence
    if PLOT_CONFIDENCE:
      ax = pn.addAxis(ylabel="confidence", ylim=(-0.2, 1.2))
      ax.set_yticks([0.0, 0.5, 1.0])
      pn.addSignal2Axis(ax, "radar conf.", obj.time, obj.radar_conf, unit="-")
      pn.addSignal2Axis(ax, "video conf.", obj.time, obj.video_conf, unit="-")
      _add_dots(ax, obj.time, obj.radar_conf, life_limits, stable_limits)
      _add_dots(ax, obj.time, obj.video_conf, life_limits, stable_limits)
    # power
    if PLOT_POWER:
      ax = pn.addAxis(ylabel="power", ylim=(0.0, 100.0))
      ax.set_yticks(np.arange(0.0, 140.1, 30.0))
      pn.addSignal2Axis(ax, "power", obj.time, obj.power, unit="dB")
      _add_dots(ax, obj.time, obj.power, life_limits, stable_limits)
    # xlabel
    ax.set_xlabel("time [s]")
    # customize and register plotnavigator
    pn.setUserWindowTitle(title)
    for start, end in stable_limits:
      # set ROI to the stable interval, reduced to the moving ego part
      standstill_mask = (start <= ego.time) & (ego.time < end) & (ego.vx <= 0.0)
      try:
        standstill_time = ego.time[np.where(standstill_mask)][0]  # first
      except IndexError:
        pass  # no standstill, keep original ROI
      else:
        end = min(end, standstill_time)  # reduce ROI end to standstill
      for ax in pn.fig.axes:
        ax.axvspan(start, end, facecolor='g', alpha=0.2)
    self.get_sync().addClient(pn)
    return
