# -*- dataeval: init -*-

import os
import sys
from collections import OrderedDict
import numpy

from reportlab.platypus import Image, Table, TableStyle, Spacer, PageBreak
from reportlab.lib.pagesizes import cm
from reportlab.lib.styles import getSampleStyleSheet

import interface
from measparser.signalgroup import SignalGroupError
from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, Paragraph, List, \
                          grid_table_style, decorate, ListItem

INCLUDE_OBJDET = True
INCLUDE_AEBS = True
INCLUDE_DRIVER_OVERRIDE = True
VISIBLEDURATION_PRE_OBJDET  = 20.0
VISIBLEDURATION_POST_OBJDET = 20.0
VISIBLEDURATION_PRE_AEBS    =  1.0
VISIBLEDURATION_POST_AEBS   =  2.0
VISIBLEDURATION_PRE_DRIVER_OVERRIDE  = 3.0
VISIBLEDURATION_POST_DRIVER_OVERRIDE = 10.0
IMAGEDIR = os.path.join(os.path.dirname(__file__), "images")  # TODO: remove

init_params = {
  "FLR20_KB": dict(sensor='AC100', algo='KB'),
  "FLR20_FLR20": dict(sensor='AC100', algo='FLR20'),
  "FLR20_TRW": dict(sensor='AC100', algo='TRW'),
  "FLR20_RAIL": dict(sensor='AC100', algo='RAIL'),
}

class AC100(object):
  """
  AC100-specific parameters.
  """
  permaname = 'AC100'
  productname = "FLR20"
  objind_labelgroup = 'AC100 track'
  ego_fill = 'calc_flr20_egomotion@aebs.fill'
  aebobj_fill = 'fill_flr20_aeb_track@aebs.fill'

class KB(object):
  """
  KB AEBS algorithm specific parameters - old version.
  """
  name = 'KB'
  algo_fill = 'calc_aebs_phases@aebs.fill'

class FLR20(object):
  """
  KB AEBS algorithm specific parameters.
  """
  name = 'FLR20'
  algo_fill = 'calc_flr20_aebs_phases-radar@aebs.fill'

class TRW(object):
  """
  TRW AEBS algorithm specific parameters.
  """
  name = 'TRW'
  algo_fill = 'calc_trw_aebs_phases@aebs.fill'

class RAIL(object):
  """
  AEBS algorithm parameters that can be used with RAIL measurements.
  """
  name = 'RAIL'
  algo_fill = 'calc_flr20_aebs_phases-rail@aebs.fill'


def gen_figures(manager, sessionprops, viewprops):
  figs = []
  build_session(manager, sessionprops, viewprops)
  for module_id, props in viewprops.iteritems():
    sync = manager.get_sync()
    try:
      client = sync.getClient(module_id, props['windowid'])
    except ValueError:
      fig = None
    else:
      client.setWindowGeometry(props['windowgeom'])
      fp = client.copyContentToBuffer()
      fig = Image(fp, width=props['width'], height=props['height'])
    figs.append(fig)
  manager.close()
  return figs

def build_session(manager, sessionprops, viewprops):
  if 'measpath' in sessionprops:
    manager.set_measurement(sessionprops['measpath'])
  manager.build(viewprops, show_navigators=False)

  seektime = sessionprops.get('seektime')
  xmin = sessionprops.get('xmin')
  xmax = sessionprops.get('xmax')

  sync = manager.get_sync()
  if seektime is not None:
    sync.seek(seektime)
  if xmin is not None or xmax is not None:
    sync.setAxesLimits([xmin, xmax])
  return

def begin(manager, sensor, algo):
  querystr = """
  SELECT en.comment
    FROM entryintervals ei
    JOIN interval2label i2l ON i2l.entry_intervalid = ei.id
    JOIN labels la ON la.id = i2l.labelid
    JOIN entries en ON en.id = ei.entryid
    JOIN measurements me ON me.id = en.measurementid
    JOIN modules mo ON mo.id = en.moduleid
    LEFT JOIN intervalcomments ic ON ic.entry_intervalid = i2l.entry_intervalid
    WHERE mo.class = "dataevalaebs.search_aebs_test_summary.Search" AND
          mo.param = "algo='" || :algo || "',sensor='" || :sensor || "'"
  """
  queryparams = {
    'algo': algo.name,
    'sensor': sensor.permaname,
  }
  batch = manager.get_batch()
  test_sum_en_comments = batch.query(querystr, **queryparams)
  if test_sum_en_comments:
    radar_sw_ver = test_sum_en_comments[0][0]
    radar_sw_ver_txt = " (radar software version: %s)" % radar_sw_ver
  else:
    radar_sw_ver_txt = ""

  if algo.name == 'RAIL':
    title = "Legislation test of %s by RaIL simulation%s" % (sensor.productname,
                                                             radar_sw_ver_txt)
    add_rail_txt1 = " done in RaIL"
    add_rail_txt2 = " RaIL (Radar In the Loop) is a hardware in the loop simulation."
  else:
    title = "Evaluation of forward vehicle detection of %s%s" % (sensor.productname,
                                                                 radar_sw_ver_txt)
    add_rail_txt1 = ""
    add_rail_txt2 = ""

  story = intro(
    "%s" % title,

    """
    This document shows the results of the AEBS use case tests with %s%s, where
    the target object was approached with constant velocity.%s<br/>
    The document illustrates the results with statistics, as well as details
    each approach individually. Short explanation of the algorithms is
    also given.
    """ % (sensor.productname, add_rail_txt1, add_rail_txt2)
  )
  return story

def test_summary(batch, sensor, algo):
  story = []
  styles = getSampleStyleSheet()

  querystr = """
    SELECT IFNULL(ic.comment, ''), la.name
    FROM entryintervals ei
    JOIN interval2label i2l ON i2l.entry_intervalid = ei.id
    JOIN labels la ON la.id = i2l.labelid
    JOIN entries en ON en.id = ei.entryid
    JOIN measurements me ON me.id = en.measurementid
    JOIN modules mo ON mo.id = en.moduleid
    LEFT JOIN intervalcomments ic ON ic.entry_intervalid = i2l.entry_intervalid
    WHERE mo.class = "dataevalaebs.search_aebs_test_summary.Search" AND
          en.title = "AEBS test types" AND
          mo.param = "algo='" || :algo || "',sensor='" || :sensor || "'"
    ORDER BY ic.comment
  """
  test_type_summary = batch.query(querystr, sensor=sensor.permaname,
                                  algo=algo.name)

  if test_type_summary:
    test_type_occurs = OrderedDict([])
    for ttype, tresult in test_type_summary:
      ttype_tresults = test_type_occurs.setdefault(ttype, [])
      ttype_tresults.append(tresult)

    ptext = "Summary of results by test type"
    story.append(Paragraph(ptext, styles['Heading1']))

    ptext = """
      As of now, there are three type of tests made: homologation test, that is for
      determining if AEBS function complies with the legislation, driver override
      test, that is for testing if overrides are properly handled and additional
      test that is meant to test special cases. As of now, additional tests are
      made up of the following test cases:"""
    story.append(Paragraph(ptext))
    ptext = "alley way test"
    story.append(ListItem(ptext, styles['Normal'], level=0))
    ptext = "moving object cut-in and cut-out"
    story.append(ListItem(ptext, styles['Normal'], level=0))
    ptext = "exit from in-crash braking"
    story.append(ListItem(ptext, styles['Normal'], level=0))
    ptext = """
    Homologation and driver override tests are mandatory, additional tests are
    optional."""
    story.append(Paragraph(ptext))
    story.append(Spacer(0, 0.5*cm))

    ttext = []
    for_release_cnt = 0
    for ttype, toccurs in test_type_occurs.iteritems():
      ttext.append([ttype + " test",
                    "%d of %d passed" % (toccurs.count('passed'), len(toccurs)),
                    "OK" if toccurs.count('passed') == len(toccurs) else "not OK"])
      if (ttype in ['homologation', 'driver override']
          and toccurs.count('passed') == len(toccurs)):
        for_release_cnt += 1
    table_style = list(grid_table_style)
    table_style.remove(table_style[-1]) # don't make the topmost row bold
    table_style.append(('ALIGN', (1,0), (-1,-1), 'CENTER'))
    test_type_table = Table(ttext, style=table_style)
    story.append(test_type_table)
    story.append(Spacer(0, 0.5*cm))

    if for_release_cnt == 2:
      sw_release_res = "ready for release"
    else:
      sw_release_res = "not ready for release"
    ptext = "Recommendation: %s" % sw_release_res
    story.append(Paragraph(ptext))
  return story

def introduction(algo):
  story = []

  ptext = "Introduction"
  story.append(IndexedParagraph(ptext, 'Heading1'))

  ptext = "AEBS summary"
  story.append(IndexedParagraph(ptext, 'Heading2'))

  # TODO: restruct explanations (remove "if"...)
  if algo.name in ['KB', 'RAIL', 'FLR20']:
    ptext = """The KB-AEBS is realized as a three-phase cascade, consisting of
      a warning phase, a partial braking phase and an emergency braking
      phase.<br/>
      The following figure illustrates the operation for a stationary obstacle
      in the case of ego vehicle speed of 80 km/h, as well as the legal
      requirements for the different phases."""
    story.append(Paragraph(ptext))

    story.append(Spacer(0, 0.5*cm))

    fig = Image(os.path.join(IMAGEDIR, 'aebs_cascade_stationary.png'),
                     width=17.03*cm, height=8.87*cm)
    story.append(fig)
  else:
    ptext = "(no algo description for %s-AEBS)" % algo.name
    print >> sys.stderr, "Warning:", ptext
    story.append(Paragraph(ptext))

  ptext = "Coordinate frames"
  story.append(IndexedParagraph(ptext, 'Heading2'))

  ptext = """All values in this document are referenced to the conventional
    land vehicle frame, having its origin in the middle of the front bumper.
    The x axis is pointing forward, while the y axis is pointing to the left.
    The remaining directions fulfill the right-hand rule."""
  story.append(Paragraph(ptext))

  story.append(Spacer(0, 0.5*cm))

  fig = Image(os.path.join(IMAGEDIR, 'coordinate_frame.png'),
                   width=12.0*cm, height=3.54*cm)
  story.append(fig)
  return story

def statistics(manager, sensor):
  story = []

  ptext = "Statistics"
  story.append(IndexedParagraph(ptext, 'Heading1'))

  # generate and insert figures
  props = OrderedDict([
    (
      'view_fwdvehicledet_stabledethist-%s@dataevalaebs' %sensor.productname,
      {
        'windowid':    'Stable_detection_distance_vs_approaching_speed',
        'windowgeom':  '640x520+171+271',
        'width':       10.0*cm,
        'height':      8.13*cm,
      },
    ),
    (
      'view_fwdvehicledet_speedredhist-%s@dataevalaebs' %sensor.productname,
      {
        'windowid':    'Maximum_possible_speed_reduction_vs_relative_approaching_speed',
        'windowgeom':  '640x520+171+271',
        'width':       10.0*cm,
        'height':      8.13*cm,
      },
    ),
    (
      'view_fwdvehicledet_speedredscatter-%s@dataevalaebs' %sensor.productname,
      {
        'windowid':    'Maximum_possible_speed_reduction',
        'windowgeom':  '640x520+171+271',
        'width':       10.0*cm,
        'height':      8.13*cm,
      },
    ),
  ])
  print >> sys.stderr, "Generating figures for statistics..."
  stabledethist, speedredhist, speedredscatter = gen_figures(manager, {}, props)

  ptext = """
    The following figure shows the conditional probability density of the
    stable detection distances, given the approaching speed. In other words,
    it demonstrates the frequency of different stable detection distances
    (i.e. histogram) for every speed range of the x axis, where the density is
    represented by the color intensity.<br/>
    The exact values are also indicated on the plot.
  """
  story.append(Paragraph(ptext))
  story.append(Spacer(0, 0.5*cm))
  story.append(stabledethist)

  story.append(Spacer(0, 1.0*cm))

  ptext = """
    The following figure shows the conditional probability density of the
    theoretically possible maximum speed reduction values, given the relative
    speed between the ego vehicle and the object.<br/>
    The achievable speed reduction is calculated with the KB-cascade
    profile, assuming that the AEBS cascade starts at the previously shown
    stable detection points.<br/>
    The exact values are also indicated on the plot.
  """
  story.append(Paragraph(ptext))
  story.append(Spacer(0, 0.5*cm))
  story.append(speedredhist)

  story.append(PageBreak())

  ptext = """
    The following figure shows the previous data as a scatter plot.<br/>
    The ideal system would avoid the collision, i.e. its speed reduction equals
    the relative speed between the ego vehicle and the object.<br/>
    Note that the relative speed is an averaged value for an approach,
    which can lead to
    small differences between the sensor's and ideal system's performance.
  """
  story.append(Paragraph(ptext))
  story.append(Spacer(0, 0.5*cm))
  story.append(speedredscatter)
  return story

def result_summary(batch, sensor, algo):
  story = []
  styles = getSampleStyleSheet()

  querystr = """
    SELECT me.basename, ei.start_time, la.name, IFNULL(ic.comment, '')
    FROM entryintervals ei
    JOIN interval2label i2l ON i2l.entry_intervalid = ei.id
    JOIN labels la ON la.id = i2l.labelid
    JOIN entries en ON en.id = ei.entryid
    JOIN measurements me ON me.id = en.measurementid
    JOIN modules mo ON mo.id = en.moduleid
    LEFT JOIN intervalcomments ic ON ic.entry_intervalid = i2l.entry_intervalid
    WHERE mo.class = "dataevalaebs.search_aebs_test_summary.Search" AND
          en.title = "AEBS overall test results" AND
          mo.param = "algo='" || :algo || "',sensor='" || :sensor || "'"
    ORDER BY me.basename
  """
  summary_contents = batch.query(querystr, sensor=sensor.permaname,
                                 algo=algo.name)

  ptext = "Summary of measurement evaluation results"
  story.append(IndexedParagraph(ptext, 'Heading1'))

  ptext = """
    This section contains the summary of the evaluation of measurements. The
    table below contains the measurement file name, the start of the corresponding
    interval evaluated, the result of the evaluation and a comment where
    applicable. The evaluation was as follows:
  """
  story.append(Paragraph(ptext))
  ptext = """
    For moving and stationary objects the evaluation results as passed if
    the individual phases of the cascade appear at and span for the correct time,
    and the speed reduction was sufficient according to the AEBS legislation.
    Speed reduction is sufficient if collision was avoided in the case of a
    moving target or was 20 km/h for a stationary target. Warning phase shall
    start at least 1.4 seconds before emergency braking phase. Partial braking
    phase shall start at least 0.8 seconds before emergency braking phase.
    Emergency braking phase shall start not later than a TTC value of 3 seconds.
  """
  story.append(ListItem(ptext, styles['Normal'], level=0))
  ptext = """
    For alley way tests, evaluation is passed if no warning (and braking) is
    given for the stationary objects at the two sides.
  """
  story.append(ListItem(ptext, styles['Normal'], level=0))
  ptext = """
    In the case of driver override tests an override has to be active and the
    value of the AEBS1.AEBSstate signal shall be 3 for a passed result.
  """
  story.append(ListItem(ptext, styles['Normal'], level=0))
  ptext = """
    In the case of in-crash braking exit test the in-crash braking phase has to be
    interrupted on a suitable driver override (at present state it is accelerator
    pedal kick-down) for a passed result.
  """
  story.append(ListItem(ptext, styles['Normal'], level=0))
  story.append(Spacer(0, 1.0*cm))

  if summary_contents:
    ttext = [["Measurement", "Interval start time", "Result", "Comment"]]
    for meas, int_start, result, comment in summary_contents:
      ttext.append([meas, "%.2f s" % int_start, result, comment])
    table_style = list(grid_table_style)
    table_style.append(('ALIGN', (1,0), (-1,-1), 'CENTER'))
    sum_table = Table(ttext, style=table_style)
    story.append(sum_table)
  else:
    ptext = "Summarization is not possible because of missing signals"
    story.append(Paragraph(ptext, align='CENTER'))
  return story

def casc_eval_summary(batch, sensor, algo):
  story = []
  styles = getSampleStyleSheet()

  querystr = """
    SELECT DISTINCT me.basename, ei.start_time
    FROM entryintervals ei
    JOIN interval2label i2l ON i2l.entry_intervalid = ei.id
    JOIN labels la ON la.id = i2l.labelid
    JOIN entries en ON en.id = ei.entryid
    JOIN measurements me ON me.id = en.measurementid
    JOIN modules mo ON mo.id = en.moduleid
    LEFT JOIN intervalcomments ic ON ic.entry_intervalid = i2l.entry_intervalid
    WHERE mo.class = "dataevalaebs.search_aebs_test_summary.Search" AND
          en.title = "AEBS cascade phase evaluation" AND
          mo.param = "algo='" || :algo || "',sensor='" || :sensor || "'"
    ORDER BY me.basename AND ei.start_time
  """
  query_params = {'sensor': sensor.permaname,
                  'algo': algo.name}
  meas_with_start_time = batch.query(querystr, **query_params)

  ptext = "Summary of AEBS cascade evaluation results"
  story.append(IndexedParagraph(ptext, 'Heading1'))

  ptext = """
  The following table shows how the cascade meets demands of the legislation.
  The evaluation is done according to a number of requirements that can be
  seen in the columns of the table:
  """
  story.append(Paragraph(ptext))
  ptext = """
  warning start: passed if the start time of the warning phase is at least
  1.4 seconds before the start of the emergency phase
  """
  story.append(ListItem(ptext, styles['Normal'], level=0))
  ptext = """
  part brake start: passed if the start time of the partial braking phase is
  at least 0.8 seconds before the start of the emergency braking phase
  """
  story.append(ListItem(ptext, styles['Normal'], level=0))
  ptext = """
  emer brake start: passed if the emergency braking phase starts if the time
  to collision is not more than 3 seconds.
  """
  story.append(ListItem(ptext, styles['Normal'], level=0))
  ptext = """
  speed red in part: passed if the speed reduction in the partial braking
  phase does not exceed a value which is the maximum of 15 km/h and 30 % of the
  ego-vehicle's speed
  """
  story.append(ListItem(ptext, styles['Normal'], level=0))
  ptext = """
  speed red in emer: passed if the speed reduction in the emergency braking
  phase was sufficient enough which, in the case of moving target, means speed
  reduction at which collision is evaded and in the case of stationary target
  a speed reduction of at least 20 km/h
  """
  story.append(ListItem(ptext, styles['Normal'], level=0))
  story.append(Spacer(0, 1.0*cm))

  if meas_with_start_time:
    eval_keys = ['warning start', 'part brake start', 'emer brake start',
                 'speed red in part', 'speed red in emer']
    querystr = """
      SELECT ic.comment, la.name
      FROM entryintervals ei
      JOIN interval2label i2l ON i2l.entry_intervalid = ei.id
      JOIN labels la ON la.id = i2l.labelid
      JOIN entries en ON en.id = ei.entryid
      JOIN measurements me ON me.id = en.measurementid
      JOIN modules mo ON mo.id = en.moduleid
      LEFT JOIN intervalcomments ic ON ic.entry_intervalid = i2l.entry_intervalid
      WHERE mo.class = "dataevalaebs.search_aebs_test_summary.Search" AND
            en.title = "AEBS cascade phase evaluation" AND
            mo.param = "algo='" || :algo || "',sensor='" || :sensor || "'" AND
            me.basename = :meas AND
            ei.start_time = :start_time
    """
    ttext = [["Measurement", "Interval\nstart\ntime"]
             + [eval_key.replace(" ", "\n") for eval_key in eval_keys]]
    for meas, start_time in meas_with_start_time:
      query_params = {'sensor': sensor.permaname,
                      'algo': algo.name,
                      'meas': meas,
                      'start_time': start_time}
      casc_eval_contents = batch.query(querystr, **query_params)
      casc_eval_contents = dict(casc_eval_contents)
      table_row = [meas, "%.2f s" % start_time]
      for eval_key in eval_keys:
        table_row.append(casc_eval_contents[eval_key])
      ttext.append(table_row)
    table_style = list(grid_table_style)
    table_style.append(('ALIGN', (1,0), (-1,-1), 'CENTER'))
    table_style.append(('ALIGN', (0,0), (1,1), 'CENTER'))
    casc_eval_table = Table(ttext, style=table_style)
    story.append(casc_eval_table)
  else:
    ptext = "No AEBS cascade was present in all of the evaluated measurements."
    story.append(Paragraph(ptext, align='CENTER'))
  return story

def ignoredmeasurements(batch, sensor):
  story = []

  ptext = "Ignored measurements"
  story.append(IndexedParagraph(ptext, 'Heading1'))

  ptext = """
    This section lists the measurements where no approach was automatically
    detected (but probably should have been), and the measurements where one
    or more automatically detected approaches were incorrect, hence manually
    excluded.
  """
  story.append(Paragraph(ptext))
  story.append(Spacer(0, 1.0*cm))

  # measurements where no approach was detected by the search script
  querystr = """
    SELECT DISTINCT me.basename
    FROM entries en
    LEFT JOIN measurements me ON me.id = en.measurementid
    LEFT JOIN results re ON re.id = en.resultid
    LEFT JOIN modules mo ON mo.id = en.moduleid
    WHERE re.name != "passed" AND
          mo.class = "dataevalaebs.search_fwdvehicledet.Search" AND
          mo.param = "sensor='" || :sensor || "'"
  """
  ignoredmeass = batch.query(querystr, sensor=sensor.permaname)
  if ignoredmeass:
    ptext = "Approach has not been detected in the following measurements:"
    story.append(Paragraph(ptext))
    ignoredmeass = (measname for measname, in ignoredmeass)
    story.extend(List(ignoredmeass))
  else:
    ptext = "No measurement has been ignored."
    story.append(Paragraph(ptext))

  story.append(Spacer(0, 0.5*cm))

  # measurements where an automatically detected approach was excluded manually
  querystr = """
    SELECT DISTINCT me.basename
    FROM entryintervals ei
    LEFT JOIN entries en         ON en.id = ei.entryid
    LEFT JOIN measurements me    ON me.id = en.measurementid
    LEFT JOIN modules mo         ON mo.id = en.moduleid
    LEFT JOIN interval2label il  ON il.entry_intervalid = ei.id
    LEFT JOIN labels la          ON la.id = il.labelid
    LEFT JOIN labelgroups lg     ON lg.id = la.groupid
    WHERE la.name != "valid" AND
          lg.name = "standard" AND
          en.title = "AEBS use case - Forward vehicle detection (whole life)" AND
          mo.class = "dataevalaebs.search_fwdvehicledet.Search" AND
          mo.param = "sensor='" || :sensor || "'"
  """
  excludedmeass = batch.query(querystr, sensor=sensor.permaname)
  if excludedmeass:
    ptext = """One or more approaches have been excluded manually
      from the following measurements:"""
    story.append(Paragraph(ptext))
    excludedmeass = (measname for measname, in excludedmeass)
    story.extend(List(excludedmeass))
  else:
    ptext = "No approach has been excluded manually."
    story.append(Paragraph(ptext))
  return story

def eventsdetails(manager, sensor, algo):
  story = []

  ptext = "Event details"
  story.append(IndexedParagraph(ptext, 'Heading1'))

  ptext = """
    This section shows the details for every approach separately.<br/>
    Every page contains a plot and a video image, besides some numerical
    values. All the quantities and video captures correspond to the timestamp
    of the red vertical line on the plot.
  """
  story.append(Paragraph(ptext))
  ptext = """
    The contents of the subsections are introduced next, which is followed by
    the details of the actual events. The signals from the measurement files are
    referenced as "(&lt;device name&gt;, &lt;signal name&gt;)".
  """
  story.append(Paragraph(ptext))

  if INCLUDE_AEBS:
    ptext = "AEBS braking evaluation"
    story.append(IndexedParagraph(ptext, 'Heading2'))
    import view_aebs_main
    try:
      story.extend(view_aebs_main.explain(sensor.productname, algo.name))
    except NotImplementedError:
      story.append(Paragraph("(no explanation available)"))
    story.append(Spacer(0, 0.5*cm))
    ptext = """
      The durations of the different phases are also shown, as well as the
      initial speed at the beginning of the cascade.
    """
    story.append(Paragraph(ptext))

  if INCLUDE_OBJDET:
    ptext = "Object detection evaluation"
    story.append(IndexedParagraph(ptext, 'Heading2'))
    import view_fwdvehicledet_signals
    try:
      story.extend(view_fwdvehicledet_signals.explain(sensor.productname))
    except NotImplementedError:
      story.append(Paragraph("(no explanation available)"))
    story.append(Spacer(0, 0.5*cm))
    ptext = """
      The approaching speed is indicated (which is an averaged value for the
      approaching interval), and the possible speed reduction is also calculated
      with the AEBS cascade, which is,
      in ideal case, <i>close</i> to the approaching speed (exact equality
      is not ensured because of the averaging).
    """
    story.append(Paragraph(ptext))

  if INCLUDE_DRIVER_OVERRIDE and algo.name == 'RAIL':
    ptext = "Driver override evaluation"
    story.append(IndexedParagraph(ptext, 'Heading2'))
    import view_driver_override_signals
    try:
      story.extend(view_driver_override_signals.explain(sensor.productname,
                                                        algo.name))
    except NotImplementedError:
      story.append(Paragraph("(no explanation available)"))
    story.append(Spacer(0, 0.5*cm))

  story.append(PageBreak())

  querystr = """
    SELECT DISTINCT wholelife.measname,
                    wholelife.measpath,
                    wholelife.objind,
                    stableint.starttime,
                    stableint.endtime,
                    wholelife.dxfirst,
                    stableint.dxfirst,
                    wholelife.egospeed,
                    wholelife.objspeed,
                    stableint.speedred,
                    stableint.validity
    FROM (
      SELECT me.basename measname,
             COALESCE(me.local, me.origin) measpath,
             ei.start_time starttime,
             ei.end_time endtime,
             la2.name objind,
             qu1.value dxfirst,
             qu2.value+qu3.value objspeed,
             qu3.value egospeed
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
      JOIN quantities qu1     ON qu1.entry_intervalid = ei.id
      JOIN quanames qn1       ON qn1.id = qu1.nameid
      JOIN quanamegroups qg1  ON qg1.id = qn1.groupid
      JOIN quantities qu2     ON qu2.entry_intervalid = ei.id
      JOIN quanames qn2       ON qn2.id = qu2.nameid
      JOIN quanamegroups qg2  ON qg2.id = qn2.groupid
      JOIN quantities qu3     ON qu3.entry_intervalid = ei.id
      JOIN quanames qn3       ON qn3.id = qu3.nameid
      JOIN quanamegroups qg3  ON qg3.id = qn3.groupid
      WHERE qg1.name = "target" AND
            qn1.name = "dx start" AND
            qg2.name = "target" AND
            qn2.name = "vx" AND
            qg3.name = "ego vehicle" AND
            qn3.name = "speed" AND
            la1.name = "valid" AND
            lg1.name = "standard" AND
            lg2.name = :objind_labelgroup AND
            en.title = "AEBS use case - Forward vehicle detection (whole life)" AND
            mo.class = "dataevalaebs.search_fwdvehicledet.Search" AND
            mo.param = "sensor='" || :sensor || "'"
    ) wholelife
    LEFT JOIN (
      SELECT me.basename measname,
             ei.start_time starttime,
             ei.end_time endtime,
             la2.name objind,
             qu1.value dxfirst,
             qu2.value speedred,
             la1.name validity
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
      JOIN quantities qu1     ON qu1.entry_intervalid = ei.id
      JOIN quanames qn1       ON qn1.id = qu1.nameid
      JOIN quanamegroups qg1  ON qg1.id = qn1.groupid
      JOIN quantities qu2     ON qu2.entry_intervalid = ei.id
      JOIN quanames qn2       ON qn2.id = qu2.nameid
      JOIN quanamegroups qg2  ON qg2.id = qn2.groupid
      WHERE qg1.name = "target" AND
            qn1.name = "dx start" AND
            qg2.name = "AEBS" AND
            qn2.name = "speed reduction" AND
            lg1.name = "standard" AND
            lg2.name = :objind_labelgroup AND
            en.title = "AEBS use case - Forward vehicle detection (stable period)" AND
            mo.class = "dataevalaebs.search_fwdvehicledet.Search" AND
            mo.param = "sensor='" || :sensor || "'"
    ) stableint ON stableint.measname = wholelife.measname AND
                   stableint.objind = wholelife.objind AND
                   stableint.starttime BETWEEN wholelife.starttime AND
                                               wholelife.endtime AND
                   stableint.endtime   BETWEEN wholelife.starttime AND
                                               wholelife.endtime
    ORDER BY wholelife.measname, stableint.starttime
  """
  queryparams = {
    'sensor': sensor.permaname,
    'objind_labelgroup': sensor.objind_labelgroup,
  }
  batch = manager.get_batch()
  approaches = batch.query(querystr, **queryparams)
  for approach in approaches:
    measname, measpath, objind, starttime_stable, endtime_stable, \
      dx_start, dx_stable, egospeed, objspeed, speedred, stable_valid = approach
    objind = int(objind)

    ptext = "%s @ %.1f s" % (measname, starttime_stable)
    story.append(IndexedParagraph(ptext, 'Heading2'))

    if INCLUDE_AEBS:
      _eventsdetails_aebs(manager, sensor, story, measname, measpath, objind,
        algo, starttime_stable, endtime_stable)
    if INCLUDE_AEBS and INCLUDE_OBJDET:
      # hack to add "Heading2"-sized gap at the top of the page
      invisible_dot = decorate(".", color="WHITE")
      story.append(Paragraph(invisible_dot, 'Heading2'))
    if INCLUDE_OBJDET:
      _eventsdetails_objdet(manager, sensor, story, measname, measpath, objind,
        starttime_stable, dx_start, dx_stable, egospeed, objspeed, speedred,
        stable_valid)
    if INCLUDE_OBJDET and INCLUDE_DRIVER_OVERRIDE:
      # hack to add "Heading2"-sized gap at the top of the page
      invisible_dot = decorate(".", color="WHITE")
      story.append(Paragraph(invisible_dot, 'Heading2'))
    if INCLUDE_DRIVER_OVERRIDE:
      _eventsdetails_driver_override(manager, sensor, story, algo, measname,
                                     measpath, starttime_stable, endtime_stable)
  return story

def _eventsdetails_objdet(manager, sensor, story, measname, measpath, objind,
    seektime, dx_start, dx_stable, egospeed, objspeed, speedred, stable_valid):
  ptext = "Object detection"
  story.append(IndexedParagraph(ptext, 'Heading3'))

  if stable_valid != "valid":
    dx_stable = 0.0
    speedred = 0.0
  xmin = seektime - VISIBLEDURATION_PRE_OBJDET
  xmax = seektime + VISIBLEDURATION_POST_OBJDET
  ptext  = "Approaching speed: %.1f km/h<br/>" % (egospeed * 3.6)
  ptext += "Object's abs. speed: %.1f km/h<br/>" % (objspeed * 3.6)
  ptext += "Possible speed red.: %.1f (of %.1f) km/h<br/>" % \
    (speedred * 3.6, (egospeed-objspeed) * 3.6)
  quapara = Paragraph(ptext, align="CENTER")
  ttext = [
    ["Phase", "Distance"],
    ["First detection", "%.1f m" % dx_start],
    ["Stable detection", "%.1f m" % dx_stable],
  ]
  quatablestyle = list(grid_table_style)
  quatablestyle.append(('ALIGN', (1,0), (-1,-1), "CENTER"))
  quatable = Table(ttext, style=quatablestyle)
  quaall = Table([[quapara], [quatable]])
  quaall.setStyle(TableStyle([
    ('ALIGN', (0,0), (-1,-1), "CENTER"),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0.5*cm),
  ]))

  # generate figures
  sessionprops = {
    'measpath':   measpath,
    'seektime':   seektime,
    'xmin':       xmin,
    'xmax':       xmax,
  }
  viewprops = OrderedDict([
    (
      'viewVideoOverlay-DefParam@dataevalaebs',
      {
        'windowid':    'VideoNavigator',
        'windowgeom':  '260x200+832+271',
        'width':       6.0*cm,
        'height':      4.62*cm,
      },
    ),
    (
      'view_fwdvehicledet_signals-%s_%02d@dataevalaebs' %(sensor.productname, objind),
      {
        'windowid':    '%s_internal_track_%d' % (sensor.productname, objind),
        'windowgeom':  '640x778+171+271',
        'width':       13.0*cm,
        'height':      15.8*cm,
      },
    ),
  ])
  print>>sys.stderr, "Generating figures for object detection in %s..."%measname
  videofig, plotfig = gen_figures(manager, sessionprops, viewprops)

  # insert formatted content
  if videofig is None:
    videofig = Paragraph("(no video)", align="CENTER")
  vid_and_qua = Table([[videofig, quaall]], colWidths=8*cm)
  vid_and_qua.setStyle(TableStyle([
    ('LEFTPADDING',  (0,0), (-1,-1), 0.5*cm),
    ('RIGHTPADDING', (0,0), (-1,-1), 0.5*cm),
    ('VALIGN',       (0,0), (-1,-1), "MIDDLE"),
  ]))
  story.append(vid_and_qua)
  story.append(Spacer(0, 0.5*cm))
  story.append(plotfig)

  story.append(PageBreak())
  return

def _eventsdetails_aebs(manager, sensor, story,
    measname, measpath, objind, algo, starttime_stable, endtime_stable):
  ptext = "AEBS braking"
  story.append(IndexedParagraph(ptext, 'Heading3'))

  max_casc_duration = _get_longest_cascade_time(manager, sensor, algo)

  querystr_base = """
    SELECT ei.start_time, ei.end_time,
           qu1.value speed_start, qu2.value speed_end,
           qu1.value+qu3.value objspeed_start,
           qu2.value+qu4.value objspeed_end
    FROM entryintervals ei
    JOIN entries en         ON en.id = ei.entryid
    JOIN measurements me    ON me.id = en.measurementid
    JOIN modules mo         ON mo.id = en.moduleid
    JOIN interval2label il  ON il.entry_intervalid = ei.id
    JOIN labels la          ON la.id = il.labelid
    JOIN labelgroups lg     ON lg.id = la.groupid
    JOIN quantities qu1     ON qu1.entry_intervalid = ei.id
    JOIN quanames qn1       ON qn1.id = qu1.nameid
    JOIN quanamegroups qg1  ON qg1.id = qn1.groupid
    JOIN quantities qu2     ON qu2.entry_intervalid = ei.id
    JOIN quanames qn2       ON qn2.id = qu2.nameid
    JOIN quanamegroups qg2  ON qg2.id = qn2.groupid
    JOIN quantities qu3     ON qu3.entry_intervalid = ei.id
    JOIN quanames qn3       ON qn3.id = qu3.nameid
    JOIN quanamegroups qg3  ON qg3.id = qn3.groupid
    JOIN quantities qu4     ON qu4.entry_intervalid = ei.id
    JOIN quanames qn4       ON qn4.id = qu4.nameid
    JOIN quanamegroups qg4  ON qg4.id = qn4.groupid
    WHERE la.name = "%s" AND
          lg.name = "AEBS cascade phase" AND
          qn1.name = "speed start" AND
          qg1.name = "ego vehicle" AND
          qn2.name = "speed end" AND
          qg2.name = "ego vehicle" AND
          qn3.name = "vx start" AND
          qg3.name = "target" AND
          qn4.name = "vx end" AND
          qg4.name = "target" AND
          mo.class = "dataevalaebs.search_aebs_cascade.Search" AND
          mo.param = "algo='" || :algo || "',sensor='" || :sensor || "'" AND
          me.basename = :measname
  """

  querystr = """
    SELECT casc.start_time,
           casc.speed_start,
           casc.objspeed_start,
           casc.objspeed_end,
           warn.end_time-warn.start_time,
           COALESCE(part.end_time-part.start_time, 0.0),
           COALESCE(emer.end_time-emer.start_time, 0.0),
           warn.speed_start-warn.speed_end,
           COALESCE(part.speed_start-part.speed_end, 0.0),
           COALESCE(emer.speed_start-emer.speed_end, 0.0)
    FROM (%s) casc
    JOIN (%s) warn      ON warn.start_time BETWEEN casc.start_time AND
                                                   casc.end_time AND
                           warn.end_time   BETWEEN casc.start_time AND
                                                   casc.end_time
    LEFT JOIN (%s) part ON part.start_time BETWEEN casc.start_time AND
                                                   casc.end_time AND
                           part.end_time   BETWEEN casc.start_time AND
                                                   casc.end_time
    LEFT JOIN (%s) emer ON emer.start_time BETWEEN casc.start_time AND
                                                   casc.end_time AND
                           emer.end_time   BETWEEN casc.start_time AND
                                                   casc.end_time
    WHERE MAX(casc.start_time, :stable_start) <= MIN(casc.end_time, :stable_end)
    ORDER BY casc.start_time
  """ % (
    querystr_base % "pre-crash intervention",
    querystr_base % "warning",
    querystr_base % "partial braking",
    querystr_base % "emergency braking",
  )
  batch = manager.get_batch()
  queryparams = {
    'measname': measname,
    'stable_start': starttime_stable,
    'stable_end': endtime_stable,
    'algo': algo.name,
    'sensor': sensor.permaname,
  }
  aebs_data = batch.query(querystr, **queryparams)
  if aebs_data:
    if len(aebs_data) > 1:
      print >> sys.stderr, \
        "Warning: multiple AEBS interventions found in %s" % measname
    seektime, speed_start, objspeed_start, objspeed_end, warn_dur, part_dur, \
      emer_dur, warn_speedred, part_speedred, emer_speedred = aebs_data[-1]
    xmin = seektime - VISIBLEDURATION_PRE_AEBS
    xmax = seektime + max_casc_duration + VISIBLEDURATION_POST_AEBS
    total_speedred = warn_speedred + part_speedred + emer_speedred
    ptext  = "Initial ego speed: %.1f km/h<br/>" % (speed_start * 3.6)
    ptext += "Initial object speed: %.1f km/h<br/>" % (objspeed_start * 3.6)
    if objspeed_end is not None:
      ptext += "Total speed reduction: %.1f (of %.1f) km/h<br/>" % \
        (total_speedred * 3.6, (speed_start-objspeed_end) * 3.6)
    else:
      # handling object loss during braking
      ptext += "Total speed reduction: %.1f (of ??) km/h<br/>" % \
        (total_speedred * 3.6)
    quapara = Paragraph(ptext, align="CENTER")
    ttext = [
      ["Phase", "Duration", "Speed reduction"],
      ["Warning", "%.2f s" % warn_dur,
        "%.1f km/h" % max((warn_speedred * 3.6), 0.0)],
      ["Partial b.", "%.2f s" % part_dur,
        "%.1f km/h" % max((part_speedred * 3.6), 0.0)],
      ["Emergency b.", "%.2f s" % emer_dur,
        "%.1f km/h" % max((emer_speedred * 3.6), 0.0)],
    ]
    quatablestyle = list(grid_table_style)
    quatablestyle.append(('ALIGN', (1,0), (-1,-1), "CENTER"))
    quatable = Table(ttext, style=quatablestyle)
    quaall = Table([[quapara], [quatable]])
    quaall.setStyle(TableStyle([
      ('ALIGN', (0,0), (-1,-1), "CENTER"),
      ('BOTTOMPADDING', (0,0), (-1,-1), 0.5*cm),
    ]))

    # generate figures
    sessionprops = {
      'measpath':   measpath,
      'seektime':   seektime,
      'xmin':       xmin,
      'xmax':       xmax,
    }
    viewprops = OrderedDict([
      (
        'viewVideoOverlay-DefParam@dataevalaebs',
        {
          'windowid':    'VideoNavigator',
          'windowgeom':  '260x200+832+271',
          'width':       6.0*cm,
          'height':      4.62*cm,
        },
      ),
      (
        'view_aebs_main-%s_%02d_%s@dataevalaebs' % (sensor.productname, objind, algo.name),
        {
          'windowid':    '%s_internal_track_%d' % (sensor.productname, objind),
          'windowgeom':  '640x778+171+271',
          'width':       13.0*cm,
          'height':      15.8*cm,
        },
      ),
    ])
    print >> sys.stderr, "Generating figures for AEBS perf. in %s..." % measname
    videofig, plotfig = gen_figures(manager, sessionprops, viewprops)

    # insert formatted content
    if videofig is None:
      videofig = Paragraph("(no video)", align="CENTER")
    vid_and_qua = Table([[videofig, quaall]], colWidths=8*cm)
    vid_and_qua.setStyle(TableStyle([
      ('LEFTPADDING',  (0,0), (-1,-1), 0.5*cm),
      ('RIGHTPADDING', (0,0), (-1,-1), 0.5*cm),
      ('VALIGN',       (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(vid_and_qua)
    story.append(Spacer(0, 0.5*cm))
    story.append(plotfig)
  else:
    ptext = "No AEBS intervention found."
    para = Paragraph(ptext)
    story.append(para)

  story.append(PageBreak())
  return

def _eventsdetails_driver_override(manager, sensor, story, algo, measname,
                                   measpath, starttime_stable, endtime_stable):
  ptext = "Driver override"
  story.append(IndexedParagraph(ptext, 'Heading3'))
  xmin = starttime_stable - VISIBLEDURATION_PRE_DRIVER_OVERRIDE
  xmax = endtime_stable + VISIBLEDURATION_POST_DRIVER_OVERRIDE
  # generate figures
  sessionprops = {
    'measpath':   measpath,
    'seektime':   starttime_stable,
    'xmin':       xmin,
    'xmax':       xmax,
  }
  viewprops = OrderedDict([
    (
      'view_driver_override_signals-%s_%s@dataevalaebs' % (sensor.productname, algo.name),
      {
        'windowid':    '%s_driver_override_signals' % sensor.productname,
        'windowgeom':  '640x778+171+271',
        'width':       13.0*cm,
        'height':      15.8*cm,
      },
    ),
  ])
  print >> sys.stderr, "Generating figures for driver override in %s..." % measname
  plotfig, = gen_figures(manager, sessionprops, viewprops)
  if plotfig is None:
      plotfig = Paragraph("Missing driver override signal(s)", align="CENTER")
  story.append(plotfig)
  story.append(PageBreak())
  return

def _get_longest_cascade_time(manager, sensor, algo):
  querystr = """
  SELECT ei.start_time, ei.end_time
    FROM entryintervals ei
    JOIN entries en         ON en.id = ei.entryid
    JOIN measurements me    ON me.id = en.measurementid
    JOIN modules mo         ON mo.id = en.moduleid
    JOIN interval2label il  ON il.entry_intervalid = ei.id
    JOIN labels la          ON la.id = il.labelid
    JOIN labelgroups lg     ON lg.id = la.groupid
    JOIN quantities qu1     ON qu1.entry_intervalid = ei.id
    JOIN quanames qn1       ON qn1.id = qu1.nameid
    JOIN quanamegroups qg1  ON qg1.id = qn1.groupid
    JOIN quantities qu2     ON qu2.entry_intervalid = ei.id
    JOIN quanames qn2       ON qn2.id = qu2.nameid
    JOIN quanamegroups qg2  ON qg2.id = qn2.groupid
    JOIN quantities qu3     ON qu3.entry_intervalid = ei.id
    JOIN quanames qn3       ON qn3.id = qu3.nameid
    JOIN quanamegroups qg3  ON qg3.id = qn3.groupid
    JOIN quantities qu4     ON qu4.entry_intervalid = ei.id
    JOIN quanames qn4       ON qn4.id = qu4.nameid
    JOIN quanamegroups qg4  ON qg4.id = qn4.groupid
    WHERE la.name = "pre-crash intervention" AND
          lg.name = "AEBS cascade phase" AND
          qn1.name = "speed start" AND
          qg1.name = "ego vehicle" AND
          qn2.name = "speed end" AND
          qg2.name = "ego vehicle" AND
          qn3.name = "vx start" AND
          qg3.name = "target" AND
          qn4.name = "vx end" AND
          qg4.name = "target" AND
          mo.class = "dataevalaebs.search_aebs_cascade.Search" AND
          mo.param = "algo='" || :algo || "',sensor='" || :sensor || "'"
  """
  batch = manager.get_batch()
  queryparams = {
    'algo': algo.name,
    'sensor': sensor.permaname,
  }
  casc_times = batch.query(querystr, **queryparams)
  start_times, end_times = zip(*casc_times)
  start_times = numpy.array(start_times)
  end_times = numpy.array(end_times)
  max_duration = numpy.max(end_times - start_times)
  return max_duration


class Analyze(interface.iAnalyze):
  def init(self, sensor, algo):
    assert sensor in globals(), "parameter class for %s not defined" % sensor
    assert algo in globals(), "parameter class for %s not defined" % algo
    self.sensor = globals()[sensor]
    self.algo = globals()[algo]
    return

  def check(self):
    # check database
    querystr = """
      SELECT COUNT(*)
      FROM entries en
      JOIN results re ON re.id = en.resultid
      JOIN modules mo ON mo.id = en.moduleid
      WHERE re.name = "passed" AND
            mo.class = "dataevalaebs.search_fwdvehicledet.Search" AND
            mo.param = "sensor='" || :sensor || "'"
    """
    batch = self.get_batch()
    n, = batch.query(querystr, sensor=self.sensor.permaname, fetchone=True)
    if n < 1:
      raise SignalGroupError("no passed entries in database for %s-%s" %
                             ("dataevalaebs.search_fwdvehicledet",
                              self.sensor.productname))
    # check desired details
    assert INCLUDE_OBJDET or INCLUDE_AEBS, \
      "either object detection details or AEBS evaluation shall be selected"
    return

  def fill(self):
    batch = self.get_batch()
    manager = self.clone_manager()
    ###
    import matplotlib
    matplotlib.rcParams['savefig.dpi'] = 72
    ###
    story = []
    story.extend(begin(manager, self.sensor, self.algo) + [Spacer(0, 1.0*cm)])
    test_summ = test_summary(batch, self.sensor, self.algo)
    if test_summ:
      story.extend(test_summ + [PageBreak()])
    story.extend(toc()                                   + [PageBreak()])
    story.extend(introduction(self.algo)                 + [PageBreak()])
    story.extend(result_summary(batch, self.sensor, self.algo) + [PageBreak()])
    story.extend(casc_eval_summary(batch, self.sensor, self.algo) + [PageBreak()])
    story.extend(statistics(manager, self.sensor)        + [PageBreak()])
    story.extend(eventsdetails(manager, self.sensor, self.algo))
    story.extend(ignoredmeasurements(batch, self.sensor))
    self.reload_interface()
    return story

  def analyze(self, story):
    doc = self.get_doc('dataeval.simple')
    doc.multiBuild(story)
    return
