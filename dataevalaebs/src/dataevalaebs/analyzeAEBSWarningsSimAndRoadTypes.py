# -*- dataeval: init -*-
import os
import re
import sys
import time
import datetime
from collections import OrderedDict

import numpy
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4, cm, landscape
from reportlab.platypus import Spacer, PageBreak, Table,\
                               NextPageTemplate, Frame, PageTemplate,\
                               FrameBreak, Image
from reportlab.graphics.shapes import Drawing, Polygon, String

import measproc
from measproc.IntervalList import cIntervalList
from interface.Interfaces import iAnalyze
from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, grid_table_style, bold, underline,\
                          Paragraph, bullet, Link, LinkDst


import searchSensorCheck_CVR3
import searchSensorCheck_SCam
import searchSensorCheck_CANape
from searchAEBSWarnEval_CIPVRejectCVR3 import CVR3_FUSSignalTemplates

styles = getSampleStyleSheet()

FLOAT_FORMAT = '%.2f'

def conv_float(value):
  if isinstance(value, float):
    value = FLOAT_FORMAT % value
  return value

init_params = {
  'all': dict(sensors=['CVR3', 'CVR2', 'AC100', 'S-Cam', 'CANape'],
              sensor_aliases={'S-Cam': 'KB-Cam advanced'},
              algos=[
                ('KB ASF Avoidance', 'ASF'),
                ('Mitigation10',     'M10'),
                ('Mitigation20',     'M20'),
                ('KB AEBS',          'MKB'),
                ('Avoidance',        'AVO'),
                ('CVR3 Warning',     'CVR3'),
                ('CVR2 Warning',     'CVR2'),
                ('AC100 Warning',    'AC100'),
              ]),

  'AC100': dict(sensors=['AC100', 'S-Cam', 'CANape'],
                sensor_aliases={'S-Cam': 'KB-Cam advanced'},
                algos=[
                  ('KB ASF Avoidance', 'ASF'),
                  ('Mitigation10',     'M10'),
                  ('Mitigation20',     'M20'),
                  ('KB AEBS',          'MKB'),
                  ('Avoidance',        'AVO'),
                  ('AC100 Warning',    'AC100'),
                ]),
}


class Analyze(iAnalyze):
  def init(self, sensors, sensor_aliases, algos):
    self.sensors = OrderedDict([(sensor, sensor_aliases.get(sensor, sensor))
                                for sensor in sensors])

    self.algos = OrderedDict(algos)

    self.production_name = 'KB ASF Avoidance'
    self.view_name = ''
    self.DIAG_LINK = 'diag_%(sensor_alias)s_%(meas_nr)s'
    return

  def get_alias_iterator(self, sensors):
    aliases = AliasIterator(self.sensors.iteritems(), sensors)
    return aliases

  def get_algo_iterator(self, algos):
    algos = AliasIterator(self.algos.iteritems(), algos)
    return algos

  def fill(self):
    batch = self.get_batch()
    self.view_name = batch.create_view_from_last_start()

    story = intro(
     "AEBS field test evaluation report",
     """
     This is an automatically generated report. Different radar and video
     sensors are measured simultaneously.<br/>
     Based on these measurements different AEBS algorithms are calculated
     off-line in Python with the exception of LRR3Warning, CVR3Warning and
     AC100Warning which are calculated online in the sensor.<br/>
     The results are presented in this report, which contain data based on the
     measurement files that can be found in the table in the Appendix.<br/>
     """
    )
    story.append(PageBreak())

    aliases = self.get_alias_iterator({'CVR2', 'CVR3', 'AC100'})
    warning_summary = WarningSummary(aliases, batch, self.view_name)
    roadtype_summary = RoadTypeSummary(aliases, batch, self.view_name)

    roadtypes = RoadTypes(batch, self.view_name)
    story.extend(self.summary(warning_summary, roadtypes))
    story.extend(toc())
    story.append(PageBreak())

    checkers = {
      'CVR3':   SensorCheck(batch, self.view_name, 'CVR3'),
      'S-Cam':  ScamSensorCheck(batch, self.view_name, 'S-Cam', font_size=7),
      'CANape': SensorCheck(batch, self.view_name, 'CANape'),
    }

    story.extend(self.device_diagnostic(checkers))
    story.extend(self.summarizing_tables(warning_summary, roadtype_summary,
                                         roadtypes))
    story.extend(self.aebs_warning_events())
    story.extend(self.appendix(checkers))
    return story

  def analyze(self, story):
    doc = self.get_doc('dataeval.simple')
    addPageTemplates(doc)
    doc.multiBuild(story)
    return

  def summary(self, warning_summary, roadtypes):
    batch = self.get_batch()

    date_time = DateTime(batch, self.view_name)
    duration = Duration(batch, self.view_name)

    story = [
      IndexedParagraph('Summary', styles['Heading1']),

      Paragraph("Number of warnings: (%s)" % self.production_name),
      Spacer(1.0*cm, 0.5*cm),
      warning_summary.get_table(),
      Spacer(1.0*cm, 0.5*cm),

      Paragraph("""
        Summary of SDF performance with active KB-Cam Advance for %(moving)d
        warning(s)""" %warning_summary['CVR3']['KB ASF Avoidance']),
      Spacer(1.0*cm, 0.5*cm),
      SdfPerfomanceSummary(self.sensors, batch, self.view_name).get_table(),
      Spacer(1.0*cm, 0.5*cm),

      Paragraph(get_plate(batch, self.view_name)),

      Paragraph('Total mileage: %.1f km' % roadtypes.sum()),
      Paragraph('Date of measurements: %s - %s' % (duration.get_start_date(),
                                                   duration.get_end_date())),
      Paragraph('Duration of measurements: %s' %date_time.sum()),

      Paragraph('The summary of recording time of %d measurement file' %
                len(duration)),
      Spacer(10.0*cm, 0.2*cm),
      Table([('', 'min [s]', 'max [s]', 'mean [s]'),
             duration.get_summary(),
             date_time.get_summary()], style=grid_table_style),

      Spacer(10.0*cm, 0.2*cm),
      Paragraph("""
        The next page contains maps which show the direction of travel and the
        location of AEBS warnings. The following diagram explains the pictograms
        that can be found on the AEBS warnings map:
        """),
      Spacer(10.0*cm, 0.2*cm),

      get_warning_pictograms(),

      Spacer(10.0*cm, 0.2*cm),
      Paragraph("""
        The letters in the fields of pictograms denote the phase of the AEBS
        cascade (according to the length of warning interval):
        W stands for warning; P stands for partial brake and E stands for
        emergency brake phase respectively.
        If a pictogram is blacked out at one or more of its quarters then it
        means that there were no warnings for that  particular sensor at that
        location.
        """),
      PageBreak(),
    ]
    return story

  def device_diagnostic(self, checkers):
    batch = self.get_batch()

    story = [
      IndexedParagraph('Device diagnostic', styles['Heading1']),
      Paragraph("""
        This is the summary of device diagnostics. Detailed diagnostics data can
        be found in the appendix.
        The availability of sensors and the validity of the measurements is
        shown in the table below.
        Following the table, corrupt measurement files are stated categorized by
        sensor name.
        """),
      Spacer(10.0*cm, 0.2*cm),
      Paragraph("""
        These are the signals which were used to determine if a measurement is
        corrupt or not:
        """),
      Spacer(10.0*cm, 0.2*cm),
    ]

    validators = {
      'S-Cam':  ['availability'],
      'CANape': ['videoTimeDer_min', 'videoTimeDer_max', 'videoAvailability'],
      'CVR3':   ['invalidTimeCount', 'tcCycleTime_max'],
    }

    meas_sum = OrderedDict()
    aliases = self.get_alias_iterator(checkers)
    for alias, checker, validator in aliases.zip(checkers, validators):
      text = 'for %s: %s' % (alias, ' and '.join(validator))
      story.append(Paragraph(bullet()+text))
      meas_sum[alias] = checker.get_not_available_measurements(),\
                        checker.get_corrupt_measurements(validator)
    story.append(Spacer(10.0*cm, 0.2*cm))

    measurements = checkers['CVR3'].measurements
    no_meas = len(measurements)
    summary = [('sensor', 'available', 'not corrupt')]
    for alias, (not_availables, corrupts) in meas_sum.iteritems():
      no_availables = no_meas - len(not_availables)
      no_not_corrupts = no_availables - len(corrupts)

      row = alias,\
            '%d/%d' % (no_availables, no_meas),\
            '%d/%d' % (no_not_corrupts, no_availables)
      summary.append(row)
    story.append(Table(summary, style=grid_table_style))
    story.append(Spacer(10.0*cm, 0.2*cm))

    for alias, (not_availables, corrupts) in meas_sum.iteritems():
      comment = 'none found' if not corrupts else ''
      text = bold('Corrupt measurement files of %s:' % alias) + comment
      story.append(Paragraph(text))
      link_frmt = self.DIAG_LINK % dict(sensor_alias=alias, meas_nr='%d')
      for meas in corrupts:
        col = measurements.index(meas) + 1
        link = link_frmt % col
        link_text = 'column #%d' % col
        text = bullet() + meas + ' ' + Link(link, link_text)
        story.append(Paragraph(text))
      story.append(Spacer(10.0*cm, 0.2*cm))

    story.append(PageBreak())
    return story

  def summarizing_tables(self, warning_summary, roadtype_summary, roadtypes):
    algos = self.get_algo_iterator({'KB ASF Avoidance', 'Mitigation10',
                                    'Mitigation20', 'KB AEBS', 'Avoidance'})
    sensors = self.get_alias_iterator(warning_summary)

    header = ['sensor', 'test', 'event count']
    header.extend(warning_summary.columns)
    header.extend(roadtype_summary.columns)
    data = [header]

    no_sensors = len(sensors)
    no_tests = len(algos) + 1
    first_roadtype_col_nr = header.index(roadtype_summary.columns[0])
    style  = [
      ('GRID', (0, 0), (-1, -1), 0.025*cm, colors.black),
    ]
    style.extend(
      ('SPAN', (0, i+1), (0, i+no_tests))
      for i in xrange(0, no_tests*no_sensors, no_tests)
    )
    style.append(('SPAN',
                  (0, -1), (first_roadtype_col_nr-1, -1)))
    style.extend(
      ('BACKGROUND', (1, i), (-1, i), colors.lightsalmon)
      for i in xrange(1, no_sensors*no_tests, no_tests)
    )

    for sensor, alias in sensors:
      for algo, _ in algos:
        data.append(get_warning_summary(warning_summary, roadtype_summary,
                                        sensor, alias, algo))
      algo = '%s Warning' % sensor
      data.append(get_warning_summary(warning_summary, roadtype_summary, sensor,
                                      alias, algo))

    row = ['' for i in xrange(first_roadtype_col_nr)]
    row[0] = 'distance [km]'
    row.extend([FLOAT_FORMAT % roadtypes.get(roadtype, 0.0)
               for roadtype in roadtype_summary.columns])
    data.append(row)

    story = [
      IndexedParagraph('Summarizing tables', styles['Heading1']),
      Paragraph('AEBS Warnings: Overall, per Obstacle Type and per Road Type'),
      Spacer(10.0*cm, 0.2*cm),
      Table(data, style=style),
      Spacer(10.0*cm, 0.2*cm),
    ]
    if 'CVR3' in self.sensors:
      cipv_aliases = [(name, alias)
                      for alias, name in CVR3_FUSSignalTemplates.iteritems()]
      story.extend([
        Paragraph('%(CVR3)s Classifiers Causing CIPV Rejection' % self.sensors),
        CipvRejectionSummary(self.get_batch(), self.view_name).get_table(
          algos=self.algos.items(), classifs=cipv_aliases),
      ])
    story.append(PageBreak())
    return story

  def aebs_warning_events(self):
    text = bold(underline('Short explanation of the following pages:'))
    story = [
      IndexedParagraph('AEBS warning events', styles['Heading1']),
      Paragraph(text),
      Paragraph("""
        This chapter contains the evaluation of AEBS warning events per
        intervals.
        Each page is dedicated for one larger interval group defined by the
        separation of all the intervals with a gap of 2 seconds.
        The shorter intervals incorporated into the interval group represent the
        warning generated by an AEBS algorithm.
      """),
      Paragraph("""
        The pages contain 3 tables that are always there and two tables that are
        present occasionally.
        Permanent tables are: 'AEBS Warnings', 'Closest In Path Vehicle' and
        'Ego-vehicle'.
        Occasional tables are: 'CVR3 and KB-Cam Advanced Association Table' and
        the one with the classifiers responsible for the CIPV rejection.
      """),
      Spacer(10.0*cm, 0.2*cm),
      Table([
          ['W', 'Warning phase'],
          ['P', 'Partial brake phase'],
          ['E', 'Emergency brake phase'],
        ],
        style=[
          ('INNERGRID',  (0, 0), (-1, -1), 0.025*cm, colors.black),
          ('BOX',        (0, 0), (-1, -1), 0.025*cm, colors.black),
          ('BACKGROUND', (0, 0), ( 0,  0),           colors.yellow),
          ('BACKGROUND', (0, 1), ( 0,  1),           colors.orange),
          ('BACKGROUND', (0, 2), ( 0,  2),           colors.red),
        ]),
      Spacer(10.0*cm, 0.2*cm),
      Paragraph("""
        The 'Closest In Path Vehicle' and 'Ego-vehicle' tables contain data
        about the kinematic state of CIPV object and ego-vehicle respectively.
        The 'AEBS Warnings' table show information about warning interval per
        algorithm for each sensor
        The cells blacked out are the ones that make no sense for a particular
        sensor.
        The warning phases reached (the fact of driver override, object lost,
        etc. also) are represented with pictograms.
        The occurring pictograms and their meaning is shown in the next table.
      """),
      Paragraph("""
        The other two tables show percentage values in their cells (one
        exception is the FUS ID line of CIPV rejection table).
        The percentage values mean the portion of the warning intervals in which
        a particular classifier was active (CIPV rejection table)
        or KB-Cam Advanced and CVR3 (same lane near object) association was
        present (CVR3 and KB-Cam Advanced association table).
      """),
      Paragraph("""
        The occurrence of empty cell in a table means that there was no interval
        present for that cell (algorithm and sensor) according to which the
        information could be displayed.
        If a column contains values of 'n/a' then it means that there were no
        sensor signals or the appropriate search script was not run.
        There is one exception though. The value of 'n/a' in the CIPV rejection
        tables mean that the sensor has not detected an object for that interval
        (algorithm).
        In order to consume less space, abbreviations are used throughout the
        next pages that are explained in the following table.
      """),
      Spacer(10.0*cm, 0.2*cm),
      Table([
          ["algorithm name",   "abbreviation", "explanation"],
          ["KB ASF Avoidance", "ASF",
           "Offline algorithm. Speed reduction is speed dependent. Has no\n"
           "online SDF."],
          ["Mitigation10",     "M10",
           "Offline algorithm. Speed reduction is 10 km/h. Has no online SDF."],
          ["Mitigation20",     "M20",
           "Offline algorithm. Speed reduction is 20 km/h. Has no online SDF."],
          ["KBAEBS",           "MKB",
           "Offline algorithm. Speed reduction is speed dependent. Has no\n"
           "online SDF."],
          ["Avoidance",        "AVO",
           "Offline algorithm. Speed reduction is as much that would avoid\n"
           "collision. Has no online SDF."],
          ["CVR3Warning",      "CVR3",
           "Online algorithm. Speed reduction is speed dependent. Has online\n"
           "SDF."],
          ["CWR2Warning",      "CVR2",
           "Online algorithm. Speed reduction is speed dependent. Has no\n"
           "online SDF."],
          ["AC100Warning",     "AC100",
           "Online algorithm. Speed reduction is speed dependent. Has no\n"
           "online SDF."],
        ],
        style=grid_table_style,
      ),
      PageBreak(),
      Paragraph("""
        Explanation and logical relationship between the classifiers is in the
        table below:
      """),
      Spacer(10.0*cm, 0.2*cm),
      Table([
          ["Classifier Name", "Explanation", "Logical relationship", ""],
          ["wClassObst",
           "Aggregated output of the obstacle classification for far objects",

           "AND between the\nfour classifiers",
           "OR between\nthe two groups",
          ],
          ["wConstElem",
           "Classification of construction elements", "", ""],
          ["dLength",
           "Classification according to the obstacle's dimension", "", ""],
          ["dVarYvBase",
           "Classification according to the variance of the obstacle's dy\n"
           "value", "", ""],
          ["wClassObstNear",
           "Aggregated output of the obstacle classification for nearby\n"
           "objects",

           "AND between\nthe two classifiers",
           ""
          ],
          ["qClass",
           "Quality of the classification", "", ""]
        ],
        style=[
          ('GRID', (0, 0), (-1, -1), 0.025*cm, colors.black),
          ('SPAN', (2, 0), (-1,  0)),
          ('SPAN', (2, 1), ( 2,  4)),
          ('SPAN', (2, 5), ( 2, -1)),
          ('SPAN', (3, 1), ( 3, -1)),
        ],
      ),
    ]
    story.extend(self.aebs_warnings())
    return story

  def aebs_warnings(self):
    story = [
      NextPageTemplate('Landscape'),
    ]
    batch = self.get_batch()

    statuses = {
      'CVR2': 'fillLRR3_POS@aebs.fill',
      'CVR3': 'fillCVR3_POS@aebs.fill',
      'AC100': 'fillAC100_CW@aebs.fill',
    }
    groups = {
      'CVR2': 'LRR3_POS', 'CVR3': 'CVR3_POS', 'AC100': 'AC100_CW',
    }
    sensors = self.get_alias_iterator(statuses)
    statuses = [status for alias, status in sensors.zip(statuses)]
    groups = [group for alias, group in sensors.zip(groups)]

    algos = self.algos.items()
    cipv_aliases = [(name, alias)
                    for alias, name in CVR3_FUSSignalTemplates.iteritems()]


    modules = OrderedDict([
      ('viewEgoData4AEBSWarnEval-DefParam', OrderedDict([ ('PN',
        dict(windowgeom='260x200+0+0', width=7.2*cm, height=5.55*cm)),
      ])),
      ('viewVideoOverlay-DefParam', OrderedDict([ ('VideoNavigator',
        dict(windowgeom='260x200+0+0', width=7.4*cm, height=5.55*cm)),
      ])),
      ('viewTrackNavigatorRoad-DEFPARAM', OrderedDict([ ('TrackNavigator',
        dict(windowgeom='136x200+0+0', width=3.78*cm, height=5.55*cm)),
      ])),
    ])
    for meas, bounds in IntervalGroups(batch, self.view_name, 2.0).iteritems():
      manager = self.clone_manager()
      manager.set_measurement(meas)
      manager.build(modules, status_names=statuses, visible_group_names=groups,
                    show_navigators=False)
      meas = os.path.basename(meas)
      for start, end in bounds:
        story.extend([
          PageBreak(),
          IndexedParagraph('%s @ %.2f sec' %(meas, start), styles['Heading2']),
          FrameBreak(),
        ])
        if 'CVR3' in self.sensors and 'S-Cam' in self.sensors:
          story.extend([
            Paragraph('%(CVR3)s and %(S-Cam)s association table' % self.sensors,
                      align='center'),
            AssoDutyData(batch, self.view_name, meas, start, end).get_table(
              algos=algos),
          ])
        story.extend([
          FrameBreak(),

          Paragraph('AEBS warnings', align='center'),
          Warnings(batch, self.view_name, meas, start, end).get_table(sensors,
                                                                      algos),
          FrameBreak(),

          Paragraph('Closest in path vehicle',
                             align='center'),
          TargetData(batch, self.view_name, meas, start, end).get_table(
            sensors=sensors,
            values=[('dx start', 'dx [m]'), ('dy start', 'dy [m]'),
                    ('vx start', 'vr [m/s]'), ('stationary', 'stationary')]),

          Paragraph('Ego vehicle', align='center'),
          EgoData(batch, self.view_name, meas, start, end).get_table(
            values=[('speed', 'v [km/h]'), ('curvature', 'curvature [1/m]'),
                    ('acceleration', 'ax [m/s^2]'),
                    ('lateral acceleration', 'ay [m/s^2]', )],
            factors={'speed': 3.6}),
          FrameBreak(),
        ])
        sync = manager.get_sync()
        sync.seek(start)
        for module_name, navigators in modules.iteritems():
          for navigator, props in navigators.iteritems():
            try:
              client = sync.getClient(module_name, navigator)
            except ValueError:
              story.append(Paragraph('No %s' %navigator))
            else:
              client.setWindowGeometry(props['windowgeom'])
              story.append(Image(client.copyContentToBuffer(),
                                 width=props['width'],
                                 height=props['height']))
            story.append(FrameBreak())
        data = CipvRejectData(batch, self.view_name, meas, start, end)
        if data:
          story.append(data.get_table(algos=self.algos, classifs=cipv_aliases))
      manager.close()
    return story

  def appendix(self, checkers):
    story = [
      NextPageTemplate('AppendixPortrait'),
      PageBreak(),
      IndexedParagraph('Appendix', styles['Heading1']),
    ]
    story.extend(self.table_of_measurement_files())

    sCamQuas = searchSensorCheck_SCam.QUANTITIES_CORE
    for name, (u, desc) in searchSensorCheck_SCam.QUANTITIES_REPEAT.iteritems():
      name = name.replace('%02d', '##')
      desc = desc.replace('%02d', '##') + ' Where ## spans from 01 to 10'
      sCamQuas[name] = u, desc
    quantities = {
      'CVR3':   searchSensorCheck_CVR3.QUANTITIES,
      'S-Cam':  sCamQuas,
      'CANape': searchSensorCheck_CANape.QUANTITIES,
    }

    aliases = self.get_alias_iterator(checkers)
    for alias, checker, quas in aliases.zip(checkers, quantities):
      story.extend(self.diagnostic_tables(alias, quas, checker))

    return story

  def table_of_measurement_files(self):
    batch = self.get_batch()
    story = [
      IndexedParagraph('Table of measurement files', styles['Heading2']),
      Paragraph("""
        The table shows the measurement files used for the creation of this
        report.
        The last three columns of the table present information about the
        recording time of the measurements.
        If there is n/a in the 'Start time' and 'Time gap' columns then it means
        that road type evaluation
        (which contains recording date and time statistics determination too)
        has not run for that measurement because of two possible reasons:
        missing signals or warning evaluation script(s) (at least one) has not
        been run along with the road type evaluation script for that
        measurement.
        """),
      Spacer(10.0*cm, 0.2*cm),
      Measurement(batch, self.view_name).get_table(),
      PageBreak(),
    ]
    return story

  def diagnostic_tables(self, alias, quantities, sensor_check, chunk=6):
    title = '%s diagnostic tables' % alias
    story = [
      IndexedParagraph(title, styles['Heading2']),
      Paragraph("""
        This section contains diagnostic quantities for every measurements
        covered by this report.
        The quantities are explained below.
        """),

      Spacer(10.0*cm, 0.2*cm),
      SensorCheckDescription(quantities).get_table(),
      Spacer(10.0*cm, 0.2*cm),

      Paragraph("""
        The following tables show the calculated diagnostic values.
        The numbers in the header refer to the measurements listed at the first
        subsection of the appendix.
        Cells with red background indicate the values that might need to be
        checked manually."
        """),
      Spacer(10.0*cm, 0.2*cm),
      PageBreak(),
    ]
    link_frmt = self.DIAG_LINK % dict(sensor_alias=alias, meas_nr='%d')
    story.extend(sensor_check.get_tables(link_frmt, chunk))
    return story


class AliasIterator(list):
  def __init__(self, aliases, selected):
    list.__init__(self)
    for name, alias in aliases:
      if name in selected:
        self.append((name, alias))
    return

  def zip(self, *data_dicts):
    for name, alias in self:
      data = [data_dict[name] for data_dict in data_dicts if name in data_dict]
      data.insert(0, alias)
      yield data
    return

class TableDict(OrderedDict):
  def __init__(self):
    OrderedDict.__init__(self)
    return

  def get_table(self, **kwargs):
    data = self.get_data(**kwargs)
    style = self.get_style()
    table = Table(data, style=style)
    return table

  def get_data(self, **kwargs):
    raise NotImplementedError()

  def get_style(self):
    return grid_table_style

class Summary(TableDict):
  header = 'sensor', 'no warnings'

  def __init__(self, aliases, batch, view_name):
    TableDict.__init__(self)
    self.aliases = aliases
    self._build(batch, view_name)
    return

  def _build(self, batch, view_name):
    raise NotImplementedError()

  def get_data(self, **kwargs):
    data = [self.header]
    for sensor, alias in self.aliases:
      warnings = self.get_summary(sensor, **kwargs)
      row = [alias, sum(warnings)]
      row.extend(warnings)
      data.append(row)
    return data

  def get_summary(self, sensor, algo='KB ASF Avoidance'):
    warnings = [self.get(sensor, {}).get(algo, {}).get(moving_state, 0)
                for moving_state in self.columns]
    return warnings

class WarningSummary(Summary):
  columns = 'stationary', 'moving'

  def _build(self, batch, view_name):
    counts = batch.query("""
      SELECT tags.name, algo_labels.name, moving_labels.name, COUNT(*)
      FROM %(view)s en
        JOIN entry2tag ON
             entry2tag.entryid = en.id
        JOIN tags ON
             tags.id = entry2tag.tagid

        JOIN entryintervals ON
             entryintervals.entryid = en.id

        JOIN interval2label AS moving_i2l ON
                               moving_i2l.entry_intervalid = entryintervals.id
        JOIN labels AS moving_labels ON
                       moving_labels.id = moving_i2l.labelid
        JOIN labelgroups AS moving_labelgroups ON
                            moving_labelgroups.id = moving_labels.groupid

        JOIN interval2label AS algo_i2l ON
                               algo_i2l.entry_intervalid = entryintervals.id
        JOIN labels AS algo_labels ON
                       algo_labels.id = algo_i2l.labelid
        JOIN labelgroups AS algo_labelgroups ON
                            algo_labelgroups.id = algo_labels.groupid

      WHERE moving_labelgroups.name = :moving_group
        AND algo_labelgroups.name = :algo_group
        AND en.title = :title

      GROUP BY tags.name, algo_labels.name, moving_labels.name
      """ %dict(view=view_name),

      moving_group='moving state',
      algo_group='AEBS algo',
      title='AEBS-warning')

    for sensor, algo, moving_state, count in counts:
      self.setdefault(sensor, {}).setdefault(algo, {})[moving_state] = count
    return

class RoadTypeSummary(Summary):
  columns = 'city', 'rural', 'highway'

  def _build(self, batch, view_name):
    warnings = batch.query("""
      SELECT algo.tag, algo.label, roadtype.label, COUNT(*) FROM (
        SELECT tags.name tag, labels.name label, en.measurementid meas_id,
               entryintervals.start_time, entryintervals.end_time
        FROM %(view)s en
          JOIN entry2tag ON
               entry2tag.entryid = en.id
          JOIN tags ON
               tags.id = entry2tag.tagid

          JOIN entryintervals ON
               entryintervals.entryid = en.id
          JOIN interval2label ON
               interval2label.entry_intervalid = entryintervals.id
          JOIN labels ON
               labels.id = interval2label.labelid
          JOIN labelgroups ON
               labelgroups.id = labels.groupid

        WHERE labelgroups.name = :algo_group
          AND en.title = :algo_title

      ) algo
      JOIN (
        SELECT labels.name label, en.measurementid meas_id,
               entryintervals.start_time, entryintervals.end_time
        FROM %(view)s en
          JOIN modules ON
               modules.id = en.moduleid

          JOIN entryintervals ON
               entryintervals.entryid = en.id
          JOIN interval2label ON
               interval2label.entry_intervalid = entryintervals.id
          JOIN labels ON
               labels.id = interval2label.labelid
          JOIN labelgroups ON
               labelgroups.id = labels.groupid

        WHERE en.title = :roadtype_title
          AND modules.class = :roadtype_class
          AND labelgroups.name = :roadtype_group
      )     roadtype ON
            roadtype.meas_id = algo.meas_id
      AND   MAX(roadtype.start_time, algo.start_time)
         <= MIN(roadtype.end_time, algo.end_time)

      GROUP BY algo.tag, algo.label, roadtype.label
      """ % dict(view=view_name),

      algo_group='AEBS algo',
      algo_title='AEBS-warning',
      roadtype_class='dataevalaebs.searchAEBSWarnEval_RoadTypes.cSearch',
      roadtype_title='AEBS-RoadType-Intervals',
      roadtype_group='road type')

    for sensor, algo, roadtype, count in warnings:
      self.setdefault(sensor, {}).setdefault(algo, {})[roadtype] = count
    return

def get_warning_summary(warning_summary, roadtype_summary, sensor, alias, test):
  row = [alias, test]
  warnings = warning_summary.get_summary(sensor, test)
  total = sum(warnings)
  row.append(total)
  row.extend(warnings)
  row.extend(roadtype_summary.get_summary(sensor, test))
  return row

class SdfPerfomanceSummary(TableDict):
  query = """
    SELECT COUNT(*) FROM %(view)s
      JOIN entryintervals ON
           entryintervals.entryid = %(view)s.id

      JOIN modules ON
           modules.id = %(view)s.moduleid

      JOIN interval2label ON
           interval2label.entry_intervalid = entryintervals.id
      JOIN labels ON
           labels.id = interval2label.labelid
      JOIN labelgroups ON
           labelgroups.id = labels.groupid

      JOIN quantities ON
           quantities.entry_intervalid = entryintervals.id
      JOIN quanames ON
           quanames.id = quantities.nameid
      JOIN quanamegroups ON
           quanamegroups.id = quanames.groupid

    WHERE modules.class = :class_name
      AND %(view)s.title = :title
      AND labelgroups.name = :labelgroup
      AND labels.name = :label
      AND quanamegroups.name = :quagroup
      AND quanames.name = :quantity
      AND quantities.value %(rel)s :limit
    """
  def __init__(self, sensors, batch, view_name):
    TableDict.__init__(self)
    self.sensors = sensors

    for duty in 'online duty', 'offline duty':
      suppresses = {}
      for suppressed,       relation, limit in [
         ('suppressed',     '<',      1e-2),
         ('not suppressed', '>',      99e-2),
      ]:
        suppresses[suppressed], = batch.query(self.query % dict(view=view_name,
                                                                rel=relation),
          title='AEBS-CVR3ImprovBySCAM',
          class_name='dataevalaebs.searchAEBSWarnEval_CVR3nSCamAsso.cSearch',
          labelgroup='AEBS algo',
          label='KB ASF Avoidance',
          quagroup='association',
          quantity=duty,
          limit=limit,

          fetchone=True)
      self[duty] = suppresses
    return

  def get_summary(self, duty):
    sups = self[duty]
    sup = sups['suppressed']
    not_sup = sups['not suppressed']
    total = sup +  not_sup
    sup_percent = FLOAT_FORMAT %(100.0 * sup / total)
    not_sup_percent = FLOAT_FORMAT %(100.0 * not_sup / total)
    return sup, sup_percent, not_sup, not_sup_percent

  def get_data(self):
    data = [
      ('suppressed', '%', 'not suppressed', '%'),
      self.get_summary('online duty'),
    ]
    return data

def get_plate(batch, view_name):
  meases = batch.query("""
    SELECT IFNULL(origin, local) FROM measurements
      JOIN %(view)s ON
           %(view)s.measurementid = measurements.id""" %dict(view=view_name))
  if not meases:
    print >> sys.stderr, 'No measurement for plate search'
    return ''

  sep_count = 0
  for m, in meases:
    count = max(m.count(os.path.sep), m.count('/'))
    if count > sep_count:
      sep_count = count
      meas = os.path.abspath(m)

  if meas.count(os.path.sep) < 3:
    print >> sys.stderr, 'Invalid directoty structure for plate search:'
    print >> sys.stderr, meas
    return ''

  PLATE_SEP = '-'
  plate = meas.split(os.path.sep)[-3].replace('_', PLATE_SEP)

  if plate.count(PLATE_SEP) != 1:
    print >> sys.stderr, 'Invalid directoty name for plate search: %s' % plate

  for part in plate.split(PLATE_SEP):
    if not all([c.isdigit() or c.isalpha() for c in part]):
      break
  else:
    return 'Vehicle: %s' % plate

  print >> sys.stderr, 'Invalid directoty name for plate search: %s' % plate
  return ''

class RoadTypes(TableDict):
  def __init__(self, batch, view_name):
    TableDict.__init__(self)
    roadtypes = batch.query("""
      SELECT labels.name, TOTAL(quantities.value) FROM %(view)s en
        JOIN entryintervals ON
             entryintervals.entryid = en.id

        JOIN modules ON
             modules.id = en.moduleid

        JOIN interval2label ON
             interval2label.entry_intervalid = entryintervals.id
        JOIN labels ON
             labels.id = interval2label.labelid
        JOIN labelgroups ON
             labelgroups.id = labels.groupid

        JOIN quantities ON
             quantities.entry_intervalid = entryintervals.id
        JOIN quanames ON
             quanames.id = quantities.nameid
        JOIN quanamegroups ON
             quanamegroups.id = quanames.groupid

      WHERE modules.class = :class_name
        AND en.title = :title
        AND labelgroups.name = :labelgroup
        AND quanamegroups.name = :quagroup
        AND quanames.name = :quantity

      GROUP BY labels.name
      """ % dict(view=view_name),

      title='AEBS-RoadType-Intervals',
      class_name='dataevalaebs.searchAEBSWarnEval_RoadTypes.cSearch',
      labelgroup='road type',
      quagroup='ego vehicle',
      quantity='driven distance',
      )

    self.update(roadtypes)
    return

  def sum(self):
    total = sum(self.values())
    return total


class DateTime(TableDict):
  def __init__(self, batch, view_name):
    TableDict.__init__(self)

    dates = batch.query("""
      SELECT measurements.basename, year.value, month.value, day.value,
             hour.value, minute.value, second.value FROM %(view)s
        JOIN modules ON
             modules.id = %(view)s.moduleid

        JOIN measurements ON
             measurements.id = %(view)s.measurementid

        JOIN entryintervals ON
             entryintervals.entryid = %(view)s.id

        JOIN quantities AS year ON
                           year.entry_intervalid = entryintervals.id
        JOIN quanames AS year_names ON
                         year_names.id = year.nameid
        JOIN quanamegroups AS year_group ON
                              year_group.id = year_names.groupid

        JOIN quantities AS month ON
                           month.entry_intervalid = entryintervals.id
        JOIN quanames AS month_names ON
                         month_names.id = month.nameid
        JOIN quanamegroups AS month_group ON
                              month_group.id = month_names.groupid

        JOIN quantities AS day ON
                           day.entry_intervalid = entryintervals.id
        JOIN quanames AS day_names ON
                         day_names.id = day.nameid
        JOIN quanamegroups AS day_group ON
                              day_group.id = day_names.groupid

        JOIN quantities AS hour ON
                           hour.entry_intervalid = entryintervals.id
        JOIN quanames AS hour_names ON
                         hour_names.id = hour.nameid
        JOIN quanamegroups AS hour_group ON
                              hour_group.id = hour_names.groupid

        JOIN quantities AS minute ON
                           minute.entry_intervalid = entryintervals.id
        JOIN quanames AS minute_names ON
                         minute_names.id = minute.nameid
        JOIN quanamegroups AS minute_group ON
                              minute_group.id = minute_names.groupid

        JOIN quantities AS second ON
                           second.entry_intervalid = entryintervals.id
        JOIN quanames AS second_names ON
                         second_names.id = second.nameid
        JOIN quanamegroups AS second_group ON
                              second_group.id = second_names.groupid

      WHERE modules.class = :class_name
        AND %(view)s.title = :title

        AND year_group.name = :qua_group
        AND year_names.name = :year_name

        AND month_group.name = :qua_group
        AND month_names.name = :month_name

        AND day_group.name = :qua_group
        AND day_names.name = :day_name

        AND hour_group.name = :qua_group
        AND hour_names.name = :hour_name

        AND minute_group.name = :qua_group
        AND minute_names.name = :minute_name

        AND second_group.name = :qua_group
        AND second_names.name = :second_name

      ORDER BY year.value, month.value, day.value, hour.value, minute.value,
               second.value
      """ % dict(view=view_name),
      class_name='dataevalaebs.searchAEBSWarnEval_DateTime.cSearch',
      title='AEBS-DateTime',
      qua_group='date',
      year_name='year',
      month_name='month',
      day_name='day',
      hour_name='hour',
      minute_name='minute',
      second_name='second')

    for meas, year, month, day, hour, minute, second in dates:
      date = datetime.datetime(int(year), int(month), int(day), int(hour),
                               int(minute), int(second))
      self.setdefault(meas, []).append(date)
    return

  def get_gaps(self):
    measurements = sorted(self)
    gaps = [self.get_gap(meas) for meas in measurements[1:]]
    gaps = numpy.array(gaps)
    return gaps

  def get_gap(self, meas):
    if meas not in self:
      return float('nan')

    measus = sorted(self)

    i = measus.index(meas)
    if i == 0:
      return 0
    else:
      _, end = self[measus[i-1]]
      start, _ = self[meas]
      gap = start - end
      gap = int(gap.total_seconds())
    return gap

  def get_start(self, meas):
    if meas in self:
      start, end = self[meas]
    else:
      start = 'n/a'
    return start

  def sum(self):
    if self:
      total = sum((end - start).total_seconds()
                  for start, end in self.itervalues())
      total = datetime.timedelta(seconds=int(total))
    else:
      total = 'n/a'
    return total

  def get_data(self):
    data = [('min [s]', 'max [s]', 'mean [s]')]
    data.append(self._get_summary())
    return data

  def get_summary(self):
    min, max, mean = self._get_summary()
    return 'gap', min, max, mean

  def _get_summary(self):
    if self:
      gaps = self.get_gaps()
      min = FLOAT_FORMAT % gaps.min()
      max = FLOAT_FORMAT % gaps.max()
      mean = FLOAT_FORMAT % gaps.mean()
    else:
      min = max = mean = 'n/a'
    return min, max, mean


def conv_measname_to_time(measname):
  timestamp = re.sub(r'.*(\d{4}).(\d{2}).(\d{2}).(\d{2}).(\d{2}).(\d{2}).+',
                     r'\1.\2.\3-\4:\5:\6', measname)
  if timestamp != measname:
    timestamp = time.strptime(timestamp, '%Y.%m.%d-%H:%M:%S')
  return timestamp

class Duration(TableDict):
  def __init__(self, batch, view_name):
    TableDict.__init__(self)

    reports = batch.query("""
      SELECT measurements.basename, %(view)s.id FROM %(view)s
        JOIN measurements ON
             measurements.id = %(view)s.measurementid

        JOIN types ON
             types.id = %(view)s.typeid

      WHERE types.name = :type_name

      GROUP BY measurements.basename
      """ % dict(view=view_name),
      type_name='measproc.Report')

    for meas, entryid in reports:
      report = batch.wake_entry(entryid)
      time = report.intervallist.Time
      duration = time[-1] - time[0]
      self[meas] = duration
    return

  def get_start_date(self):
    meas = min(self)
    date = self.get_date(meas)
    return date

  def get_end_date(self):
    meas = max(self)
    date = self.get_date(meas)
    return date

  def get_date(self, meas):
    date = conv_measname_to_time(meas)
    date = time.strftime('%Y-%m-%d %H:%M:%S', date)
    return date

  def get_data(self):
    data = [('min [s]', 'max [s]', 'mean [s]')]
    data.append(self._get_summary())
    return data

  def get_summary(self):
    min, max, mean = self._get_summary()
    return 'duration', min, max, mean

  def _get_summary(self):
    if self:
      durations = numpy.array(self.values())
      min = FLOAT_FORMAT % durations.min()
      max = FLOAT_FORMAT % durations.max()
      mean = FLOAT_FORMAT % durations.mean()
    else:
      min = max = mean = 'n/a'
    return min, max, mean

  def get_duration(self, measurement):
    duration = self.get(measurement, float('nan'))
    return duration

class IntervalGroups(TableDict):
  def __init__(self, batch, view_name, margin):
    TableDict.__init__(self)
    intervals = batch.query("""
      SELECT DISTINCT IFNULL(measurements.local, measurements.origin),
             entryintervals.start_time, entryintervals.end_time
      FROM %s en
        JOIN measurements ON
             measurements.id = en.measurementid

        JOIN entryintervals ON
             entryintervals.entryid = en.id

      WHERE en.title = :title

      ORDER BY measurements.basename, entryintervals.start, entryintervals.end
      """ % view_name,

      title='AEBS-warning')

    half_margin = 0.5 * margin
    meas_intervals = OrderedDict()
    times = {}
    for meas, start, end in intervals:
      meas_intervals.setdefault(meas, []).append((start, end))
      time = times.setdefault(meas, set())
      for event in start, start+half_margin, end, end+half_margin:
        time.add(event)

    meas_intervallists = OrderedDict()
    for meas, intervals in meas_intervals.iteritems():
      time = list(times[meas])
      time.sort()
      intervals = [(time.index(start), time.index(end)+1)
                   for start, end in intervals]
      time = numpy.array(time)
      meas_intervallists[meas] = cIntervalList.fromList(time, intervals)


    for meas, intervallist in meas_intervallists.iteritems():
      groups = intervallist.group(margin*0.5)
      meas_bounds = []
      for bounds in groups:
        first = min(start for start, end in bounds)
        last = max(end for start, end in bounds)
        meas_bounds.append((intervallist.Time[first],
                            intervallist.Time[last-1]))
      meas_bounds.sort()
      self[meas] = meas_bounds
    return

  def __repr__(self):
    msg = []
    for meas, bounds in self.iteritems():
      msg.append(meas)
      msg.extend('\t%f\t%f' % bound for bound in bounds)
    msg = '\n'.join(msg)
    return msg

class AssoDutyData(TableDict):
  def __init__(self, batch, view_name, meas, start, end):
    TableDict.__init__(self)
    data = batch.query("""
      SELECT labels.name, quanames.name, quantities.value
      FROM %s en
        JOIN measurements ON
             measurements.id = en.measurementid

        JOIN entry2tag ON
             entry2tag.entryid = en.id
        JOIN tags ON
             tags.id = entry2tag.tagid

        JOIN entryintervals ON
             entryintervals.entryid = en.id

        JOIN quantities ON
             quantities.entry_intervalid = entryintervals.id
        JOIN quanames ON
             quanames.id = quantities.nameid
        JOIN quanamegroups ON
             quanamegroups.id = quanames.groupid

        JOIN interval2label ON
             interval2label.entry_intervalid = entryintervals.id
        JOIN labels ON
             labels.id = interval2label.labelid
        JOIN labelgroups ON
             labelgroups.id = labels.groupid

      WHERE en.title = :title
        AND measurements.basename = :meas
        AND entryintervals.start_time >= :start
        AND entryintervals.end_time <= :end
        AND quanamegroups.name = :qua_group
        AND labelgroups.name = :algo_group
      """ % view_name,

      qua_group='association',
      title='AEBS-CVR3ImprovBySCAM',
      algo_group='AEBS algo',

      meas=meas,
      start=start,
      end=end)

    for algo, name, value in data:
      self.setdefault(algo, {})[name] = value
    return

  def get_data(self, algos):
    header = ['algo', 'offline', 'online']
    data = [header]
    for algo, alias in algos:
      duties = self.get(algo, {})
      row = [alias]
      row.extend(conv_float(100*duties.get(name, ''))
                 for name in ['offline duty', 'online duty'])
      data.append(row)
    return data

  def get_style(self):
    style = [
      ('BACKGROUND', (0, 0), ( 0, -1), colors.silver),
      ('BACKGROUND', (0, 0), (-1,  0), colors.silver),
      ('GRID',       (0, 0), (-1, -1), 0.025, colors.black),
    ]
    return style

class TargetData(TableDict):
  def __init__(self, batch, view_name, meas, start, end):
    TableDict.__init__(self)
    data = batch.query("""
      SELECT tags.name, entryintervals.id, entryintervals.start_time,
             quanames.name, quantities.value
      FROM %s en
        JOIN measurements ON
             measurements.id = en.measurementid

        JOIN entry2tag ON
             entry2tag.entryid = en.id
        JOIN tags ON
             tags.id = entry2tag.tagid

        JOIN entryintervals ON
             entryintervals.entryid = en.id

        JOIN quantities ON
             quantities.entry_intervalid = entryintervals.id
        JOIN quanames ON
             quanames.id = quantities.nameid
        JOIN quanamegroups ON
             quanamegroups.id = quanames.groupid

      WHERE en.title = :title
        AND measurements.basename = :meas
        AND entryintervals.start_time >= :start
        AND entryintervals.end_time <= :end
        AND quanamegroups.name = :group
      """ % view_name,

      group='target',
      title='AEBS-warning',
      meas=meas,
      start=start,
      end=end)

    firsts = FirstsByGroup(data)

    for sensor, idx, start, name, value in firsts.iter(data):
      sensor_data = self.setdefault(sensor, {})
      sensor_data[name] = value

    for sensor, idx in firsts.iteritems():
      moving, = batch.query("""
        SELECT labels.name FROM entryintervals
          JOIN interval2label ON
               interval2label.entry_intervalid = entryintervals.id
          JOIN labels ON
               labels.id = interval2label.labelid
          JOIN labelgroups ON
               labelgroups.id = labels.groupid

          JOIN interval2label algo_i2l ON
                              algo_i2l.entry_intervalid = entryintervals.id
          JOIN labels algo_labels ON
                      algo_labels.id = algo_i2l.labelid
          JOIN labelgroups algo_labelgroups ON
                           algo_labelgroups.id = algo_labels.groupid

        WHERE entryintervals.id = :intervalid
          AND labelgroups.name = :label_group
        """,

        label_group='moving state',
        intervalid=idx,

        fetchone=True)
      self[sensor]['stationary'] = 'yes' if moving == 'stationary' else 'no'
    return

  def get_data(self, sensors, values):
    header = ['']
    header.extend(alias for sensor, alias in sensors)
    data = [header]
    for value_name, value_alias in values:
      row = [value_alias]
      row.extend(conv_float(self.get(sensor, {}).get(value_name, ''))
                 for sensor, alias in sensors)
      data.append(row)
    return data

  def get_style(self):
    style = [
      ('BACKGROUND', (0, 0), ( 0, -1), colors.silver),
      ('BACKGROUND', (0, 0), (-1,  0), colors.silver),
      ('GRID',       (0, 0), (-1, -1), 0.025, colors.black),
    ]
    return style

class FirstsByGroup(dict):
  def __init__(self, data):
    dict.__init__(self)

    starts = {}
    for row in data:
      name, idx, start = row[:3]
      starts.setdefault(name, {})[start] = idx
    self.update((name, times[min(times)]) for name, times in starts.iteritems())
    return

  def iter(self, data):
    for row in data:
      name, idx = row[:2]
      if idx == self[name]:
        yield row
    return

class EgoData(TableDict):
  def __init__(self, batch, view_name, meas, start, end):
    TableDict.__init__(self)
    data = batch.query("""
      SELECT entryintervals.id, entryintervals.start_time,
             quanames.name, quantities.value
      FROM %s en
        JOIN measurements ON
             measurements.id = en.measurementid

        JOIN entry2tag ON
             entry2tag.entryid = en.id
        JOIN tags ON
             tags.id = entry2tag.tagid

        JOIN entryintervals ON
             entryintervals.entryid = en.id

        JOIN quantities ON
             quantities.entry_intervalid = entryintervals.id
        JOIN quanames ON
             quanames.id = quantities.nameid
        JOIN quanamegroups ON
             quanamegroups.id = quanames.groupid

      WHERE en.title = :title
        AND measurements.basename = :meas
        AND entryintervals.start_time >= :start
        AND entryintervals.end_time <= :end
        AND quanamegroups.name = :group
      """ % view_name,

      group='ego vehicle',
      title='AEBS-warning',
      meas=meas,
      start=start,
      end=end)

    starts = dict((start, idx) for idx, start, name, value in data)
    first = starts[min(starts)]
    self.update((name, value)
                for idx, start, name, value in data if idx == first)
    self['curvature']  = self['yaw rate'] / self['speed']
    return

  def get_data(self, values, factors):
    data = []
    for name, alias in values:
      if name in self:
        value = FLOAT_FORMAT % (self[name] * factors.get(name, 1.0))
      else:
        value = 'n/a'
      data.append((alias, value))
    return data

  def get_style(self):
    style = [
      ('BACKGROUND', (0, 0), ( 0, -1), colors.silver),
      ('GRID',       (0, 0), (-1, -1), 0.025, colors.black),
    ]
    return style

class Warnings(TableDict):
  def __init__(self, batch, view_name, meas, start, end):
    TableDict.__init__(self)

    self.partial = 0.6
    self.emergency = 1.4
    self.no_warnings = 3

    data = batch.query("""
      SELECT tags.name, labels.name,
             entryintervals.end_time - entryintervals.start_time
      FROM %s en
        JOIN measurements ON
             measurements.id = en.measurementid

        JOIN entry2tag ON
             entry2tag.entryid = en.id
        JOIN tags ON
             tags.id = entry2tag.tagid

        JOIN entryintervals ON
             entryintervals.entryid = en.id

        JOIN interval2label ON
             interval2label.entry_intervalid = entryintervals.id
        JOIN labels ON
             labels.id = interval2label.labelid
        JOIN labelgroups ON
             labelgroups.id = labels.groupid

      WHERE en.title = :title
        AND measurements.basename = :meas
        AND entryintervals.start_time >= :start
        AND entryintervals.end_time <= :end
        AND labelgroups.name = :label_group
      """ % (view_name,),

      label_group='AEBS algo',
      title='AEBS-warning',
      meas=meas,
      start=start,
      end=end)

    for sensor, algo, warning_time in data:
      self.setdefault(sensor, {})[algo] = warning_time
    return

  def get_table(self, sensors, algos):
    data = self.get_data(sensors, algos)
    style = self.get_style(sensors, algos)
    col_widths = [None]
    warning_col_width = 0.5 * cm
    for e in sensors:
      col_widths.extend(warning_col_width for e in xrange(self.no_warnings))
    table = Table(data, style=style, colWidths=col_widths)
    return table

  def get_data(self, sensors, algos):
    header = ['AEBS algo']
    for sensor, alias in sensors:
      header.extend([alias, '', ''])
    data = [header]
    for algo, algo_alias in algos:
      row = [algo_alias]
      for sensor, sensor_alias in sensors:
        warnings, wcolors = self.get_warning(sensor, algo)
        row.extend(warnings)
      data.append(row)
    return data

  def get_style(self, sensors, algos):
    style = [('SPAN', (1+i*self.no_warnings, 0), ((i+1)*self.no_warnings, 0))
             for i in xrange(len(sensors))]
    style.extend([
      ('BOX',        (0, 0), (-1, -1), 0.025*cm, colors.black),
      ('ALIGN',      (1, 1), (-1, -1), 'CENTER'),
      ('FONT',       (1, 1), (-1, -1), 'Helvetica', 6),
      ('BACKGROUND', (0, 0), ( 0, -1), colors.silver),
      ('BACKGROUND', (0, 0), (-1,  0), colors.silver),
    ])
    row = 1
    for algo, algo_alias in algos:
      col = 1
      line = 'LINEABOVE', (0, row), (-1, row), 0.025*cm, colors.black
      style.append(line)
      for sensor, sensor_alias in sensors:
        line = 'LINEBEFORE', (col, 0), (col, -1), 0.025*cm, colors.black
        style.append(line)
        warnings, wcolors = self.get_warning(sensor, algo)
        for color in wcolors:
          style.append(('BACKGROUND', (col, row), (col, row), color))
          col += 1
      row += 1
    return style

  def get_warning(self, sensor, algo):
    if sensor in self and algo in self[sensor]:
      warnings = ['W']
      wcolors = [colors.yellow]

      duration = self[sensor][algo]
      if duration > self.partial:
        warnings.append('P')
        wcolors.append(colors.orange)
        if duration > self.emergency:
          warnings.append('E')
          wcolors.append(colors.red)
        else:
          warnings.append('')
          wcolors.append(colors.white)
      else:
        warnings.extend(['',''])
        wcolors.extend([colors.white, colors.white])
    else:
      warnings = ['', '', '']
      wcolors = [colors.white, colors.white, colors.white]
    return warnings, wcolors

class CipvRejectData(TableDict):
  def __init__(self, batch, view_name, meas, start, end):
    TableDict.__init__(self)

    data = batch.query("""
      SELECT algo_labels.name, entryintervals.id, entryintervals.start_time,
             fus_labels.name, quanames.name, quantities.value
      FROM %s en
        JOIN measurements ON
             measurements.id = en.measurementid

        JOIN entryintervals ON
             entryintervals.entryid = en.id

        JOIN quantities ON
             quantities.entry_intervalid = entryintervals.id
        JOIN quanames ON
             quanames.id = quantities.nameid
        JOIN quanamegroups ON
             quanamegroups.id = quanames.groupid

        JOIN interval2label fus_i2l ON
                            fus_i2l.entry_intervalid = entryintervals.id
        JOIN labels fus_labels ON
                    fus_labels.id = fus_i2l.labelid
        JOIN labelgroups fus_labelgroups ON
                         fus_labelgroups.id = fus_labels.groupid

        JOIN interval2label algo_i2l ON
                            algo_i2l.entry_intervalid = entryintervals.id
        JOIN labels algo_labels ON
                    algo_labels.id = algo_i2l.labelid
        JOIN labelgroups algo_labelgroups ON
                         algo_labelgroups.id = algo_labels.groupid

      WHERE en.title = :title
        AND measurements.basename = :meas
        AND entryintervals.start_time >= :start
        AND entryintervals.end_time <= :end
        AND fus_labelgroups.name = :fus_group
        AND algo_labelgroups.name = :algo_group
        AND quanamegroups.name = :qua_group

      ORDER BY algo_labels.name, fus_labels.name
      """ % (view_name,),

      algo_group='AEBS algo',
      fus_group='FUS object',
      qua_group='target',
      title='AEBS-NoCVR3Warnings',
      meas=meas,
      start=start,
      end=end)

    firsts = FirstsByGroup(data)

    for algo, idx, start, fus_id, name, value in firsts.iter(data):
      key = algo, fus_id
      reject_data = self.setdefault(key, {})
      reject_data[name] = value
    return

  def get_data(self, algos, classifs):
    header = ['']
    fus_ids = ['FUS ID']
    for algo, fus_id in self:
      header.append(algos[algo])
      fus_ids.append(fus_id)
    data = [header, fus_ids]

    for name, alias in classifs:
      row = [alias]
      row.extend(FLOAT_FORMAT % (100 * values[name])
                 for values in self.itervalues())
      data.append(row)
    return data

  def get_style(self):
    style = [
      ('BACKGROUND', (0, 1), ( 0, -1), colors.silver),
      ('BACKGROUND', (1, 0), (-1,  0), colors.silver),
      ('GRID',       (0, 0), (-1, -1), 0.025, colors.black),
    ]
    return style


class Measurement(TableDict):
  def __init__(self, batch, view_name):
    TableDict.__init__(self)

    self.duration = Duration(batch, view_name)
    self.date_time = DateTime(batch, view_name)
    return

  def get_data(self):
    data = [
      ('No.', 'Measurement file', 'Start time', 'Duration [s]', 'Time gap [s]'),
    ]
    for i, meas in enumerate(sorted(self.duration)):
      start = self.date_time.get_start(meas)
      duration = self.duration.get_duration(meas)
      gap = self.date_time.get_gap(meas)
      data.append(('%d.' %(i+1), meas, start, FLOAT_FORMAT %duration, gap))
    return data

class DeviceDiagnosticSummary(TableDict):
  def __init__(self, batch, view_name, class_name, sensor, quagroup):
    TableDict.__init__(self)
    e = batch.query("""
      SELECT measurements.basename, quanames.name, quantities.value, labels.name
      FROM %(view)s
        JOIN measurements ON
             measurements.id = %(view)s.measurementid

        JOIN modules ON
             modules.id = %(view)s.moduleid

        JOIN entry2tag ON
             entry2tag.entryid = %(view)s.id
        JOIN tags ON
             tags.id = entry2tag.tagid

        JOIN entryintervals ON
             entryintervals.entryid = %(view)s.id
        JOIN interval2label ON
             interval2label.entry_intervalid = entryintervals.id
        JOIN labels ON
             labels.id = interval2label.labelid
        JOIN labelgroups ON
             labelgroups.id = labels.groupid

        JOIN quantities ON
             quantities.entry_intervalid = entryintervals.id
        JOIN quanames ON
             quanames.id = quantities.nameid
        JOIN quanamegroups ON
             quanamegroups.id = quanames.groupid

      WHERE %(view)s.title = :title
        AND modules.class = :class_name
        AND tags.name = :tag
        AND labelgroups.name = :labelgroup
        AND labels.name = :label
        AND quanamegroups.name = :quagroup

      ORDER BY measurements.basename, quanames.name
      """ % dict(view=view_name),

      title='SensorCheck',
      class_name='dataevalaebs.searchSensorCheck_CVR3.cSearch',
      tag='CVR3',
      labelgroup='sensor check',
      label='invalid',
      quagroup=quagroup)
    return

class SensorCheckDescription(TableDict):
  def __init__(self, quantities):
    TableDict.__init__(self)
    self.update(quantities)
    return

  def get_data(self):
    data = [('Name', 'Unit', 'Description')]
    for name in sorted(self):
      unit, description = self[name]
      data.append((name, unit, description))
    return data

class SensorCheck(TableDict):
  def __init__(self, batch, view_name, sensor, font_size=8):
    TableDict.__init__(self)

    self.font_size = font_size
    self.sensor = sensor

    self.measurements = get_measurements(batch, view_name)
    self._build(batch, view_name)
    return

  def _build(self, batch, view_name):
    checks = batch.query("""
      SELECT measurements.basename, quanames.name, quantities.value, labels.name
        FROM %(view)s
        JOIN measurements ON
             measurements.id = %(view)s.measurementid

        JOIN modules ON
             modules.id = %(view)s.moduleid

        JOIN entry2tag ON
             entry2tag.entryid = %(view)s.id
        JOIN tags ON
             tags.id = entry2tag.tagid

        JOIN entryintervals ON
             entryintervals.entryid = %(view)s.id
        JOIN interval2label ON
             interval2label.entry_intervalid = entryintervals.id
        JOIN labels ON
             labels.id = interval2label.labelid
        JOIN labelgroups ON
             labelgroups.id = labels.groupid

        JOIN quantities ON
             quantities.entry_intervalid = entryintervals.id
        JOIN quanames ON
             quanames.id = quantities.nameid
        JOIN quanamegroups ON
             quanamegroups.id = quanames.groupid

      WHERE %(view)s.title = :title
        AND modules.class = :class_name
        AND tags.name = :tag
        AND labelgroups.name = :labelgroup
        AND quanamegroups.name = :quagroup

      ORDER BY measurements.basename, quanames.name
      """ % dict(view=view_name),

      title='SensorCheck',
      class_name = 'dataevalaebs.searchSensorCheck_%s.cSearch' %self.sensor,
      tag=self.sensor,
      labelgroup='sensor check',
      quagroup='%s sensor check' %self.sensor,)

    for meas, name, value, valid in checks:
      qua = self.setdefault(meas, OrderedDict())
      qua[name] = value, valid
    return

  def get_data(self):
    header = ['']
    data = []
    for meas, quas in self.iteritems():
      row = [meas]
      for name, (value, valid) in quas.iteritems():
        row.append(FLOAT_FORMAT %value)
        data and header.append(name)
      data.append(row)
    data.insert(0, header)
    return data

  def get_tables(self, link_frmt, chunk):
    tbl = self.to_table()
    tables = []
    for chunk in tbl.getChunks(chunk):
      text = ''.join([LinkDst(link_frmt %col) for col in chunk.titleCol])
      tables.append(Paragraph(text))

      tr = chunk.getTransposed()

      table_style = [
         ('INNERGRID', (0, 0), (-1, -1), 0.025*cm, colors.black),
         ('BOX',       (0, 0), (-1, -1), 0.025*cm, colors.black),
         ('FONT',      (0, 0), (-1, -1), 'Helvetica', self.font_size),
      ]
      for i, j in tr.invalidIndices:
        idx = j+1, i+1
        table_style.append(('BACKGROUND', idx, idx, colors.red))

      tables.append(Table(tr.getPrintable(), style=table_style))
      tables.append(PageBreak())
    return tables

  def to_table(self):
    data = []
    col_title = [self.measurements.index(meas)+1 for meas in self]
    row_title = []
    invalids = []

    for row, quas in enumerate(self.itervalues()):
      if not row_title:
        row_title = quas.keys()
      data_row = []
      for col, (value, valid) in enumerate(quas.itervalues()):
        data_row.append(FLOAT_FORMAT %value)
        if valid == 'invalid':
          invalids.append((row, col))
      data.append(data_row)

    tbl = measproc.Table(data, titleRow=row_title, titleCol=col_title,
                         cornerCell='start of recording',
                         invalidIndices=invalids)
    return tbl

  def get_not_available_measurements(self):
    corrupts = [meas for meas in self.measurements if meas not in self]
    return corrupts

  def get_corrupt_measurements(self, qua_names):
    corrupts = []
    for meas, checks in self.iteritems():
      for name in qua_names:
        value, valid = checks[name]
        if valid == 'invalid':
          corrupts.append(meas)
          break
    return corrupts


def get_measurements(batch, view_name):
  measurements = batch.query("""
    SELECT DISTINCT measurements.basename from %(view)s
      JOIN measurements ON
           measurements.id = %(view)s.measurementid
    WHERE measurements.basename != :dummy
    ORDER BY measurements.basename
    """ % dict(view=view_name),

    dummy='dummy')
  measurements = [meas for meas, in measurements]
  return measurements


class ScamSensorCheck(SensorCheck):
  def _build(self, batch, view_name):
    checks = batch.query("""
      SELECT measurements.basename, quanames.name, object.name,
             quantities.value, labels.name
        FROM %(view)s
        JOIN measurements ON
             measurements.id = %(view)s.measurementid

        JOIN modules ON
             modules.id = %(view)s.moduleid

        JOIN entry2tag ON
             entry2tag.entryid = %(view)s.id
        JOIN tags ON
             tags.id = entry2tag.tagid

        JOIN entryintervals ON
             entryintervals.entryid = %(view)s.id

        JOIN interval2label ON
             interval2label.entry_intervalid = entryintervals.id
        JOIN labels ON
             labels.id = interval2label.labelid
        JOIN labelgroups ON
             labelgroups.id = labels.groupid

        LEFT JOIN interval2label object_i2l ON
                                 object_i2l.entry_intervalid = entryintervals.id
        LEFT JOIN labels object_labels ON
                         object_labels.id = object_i2l.labelid
        LEFT JOIN labelgroups object_labelgroups ON
                              object_labelgroups.id = object_labels.groupid

        LEFT JOIN (SELECT entryintervals.id, labels.name FROM entryintervals
                     JOIN interval2label ON
                          interval2label.entry_intervalid = entryintervals.id
                     JOIN labels ON
                          labels.id = interval2label.labelid
                     JOIN labelgroups ON
                          labelgroups.id = labels.groupid
                   WHERE  labelgroups.name = :object_labelgroup)
              object ON
              object.id  = entryintervals.id

        JOIN quantities ON
             quantities.entry_intervalid = entryintervals.id
        JOIN quanames ON
             quanames.id = quantities.nameid
        JOIN quanamegroups ON
             quanamegroups.id = quanames.groupid

      WHERE %(view)s.title = :title
        AND modules.class = :class_name
        AND tags.name = :tag
        AND labelgroups.name = :labelgroup
        AND quanamegroups.name = :quagroup

      ORDER BY measurements.basename, object.name, quanames.name
      """ % dict(view=view_name),

      title='SensorCheck',
      class_name='dataevalaebs.searchSensorCheck_SCam.cSearch',
      tag=self.sensor,
      labelgroup='sensor check',
      object_labelgroup='%s obstacle data' %self.sensor,
      quagroup='%s sensor check' %self.sensor)

    names = set()
    tbl = OrderedDict()
    for meas, name, idx, value, valid in checks:
      if idx is not None:
        name = 'ObstacleData%02d_%s' % (int(idx), name)
      names.add(name)
      qua = tbl.setdefault(meas, OrderedDict())
      qua[name] = value, valid

    # init quantities
    quas = OrderedDict([(name, (float('nan'), 'valid'))
                        for name in sorted(names)])
    for meas in tbl:
      self[meas] = quas.copy()
    # copy
    for meas, quas in tbl.iteritems():
      self[meas].update(quas)
    return

class CipvRejectionSummary(TableDict):
  def __init__(self, batch, view_name):
    TableDict.__init__(self)

    rejections = batch.query("""
      SELECT labels.name, quanames.name, measurements.id, entryintervals.start,
             entryintervals.end FROM %s en
        JOIN modules ON
             modules.id = en.moduleid

        JOIN measurements ON
             measurements.id = en.measurementid

        JOIN entry2tag ON
             entry2tag.entryid = en.id
        JOIN tags ON
             tags.id = entry2tag.tagid

        JOIN entryintervals ON
             entryintervals.entryid = en.id
        JOIN quantities ON
             quantities.entry_intervalid = entryintervals.id
        JOIN quanames ON
             quanames.id = quantities.nameid
        JOIN quanamegroups ON
             quanamegroups.id = quanames.groupid

        JOIN interval2label ON
             interval2label.entry_intervalid = entryintervals.id
        JOIN labels ON
             labels.id = interval2label.labelid
        JOIN labelgroups ON
             labelgroups.id = labels.groupid

      WHERE modules.class = :class_name
        AND en.title = :title
        AND tags.name = :tag
        AND quanamegroups.name = :quagroup
        AND quantities.value > :limit
        AND labelgroups.name = :labelgroup
      """ % view_name,

      class_name='dataevalaebs.searchAEBSWarnEval_CIPVRejectCVR3.cSearch',
      title='AEBS-NoCVR3Warnings',
      tag='CVR3',
      quagroup='target',
      limit=0.0,
      labelgroup='AEBS algo')

    data = {}
    for algo, name, meas, start, end in rejections:
      key = meas, start, end
      classif_data = data.setdefault(name, {})
      algo_data = classif_data.setdefault(algo, set())
      algo_data.add(key)

    for classif, classif_data in data.iteritems():
      classif_sum = {}
      for algo, algo_data in classif_data.iteritems():
        classif_sum[algo] = len(algo_data)
      self[classif] = classif_sum
    return

  def get_data(self, algos, classifs):
    header = ['']
    header.extend(alias for name, alias in algos)
    data = [header]
    for classif, classif_alias in classifs:
      row = [classif_alias]
      classif_data = self.get(classif, {})
      for algo, algo_alias in algos:
        row.append(classif_data.get(algo, 0))
      data.append(row)
    return data

  def get_style(self):
    style = [
      ('GRID', (0, 0), (-1, -1), 0.025, colors.black),
    ]
    return style

def get_warning_pictograms():
  d = Drawing(10.0*cm, 2*cm)
  xLoc = 6*cm
  yLoc = 0.5*cm
  xDist = 2*cm
  yDist = 0
  xLegendDist = 4*cm
  yLegendDist = 0
  xLegendLoc = xLoc
  yLegendLoc = 0.1*cm
  legendOffset = 0.1*cm

  cvr3StatPict = Polygon(points=[xLoc, yLoc+0.5*cm,
                                 xLoc, yLoc+1*cm,
                                 xLoc+0.5*cm, yLoc+1*cm,
                                 xLoc+0.5*cm, yLoc+0.5*cm],
                         fillColor='yellow',
                         edgeColor='dimgray')
  d.add(cvr3StatPict)
  cvr2StatPict = Polygon(points=[xLoc+0.5*cm, yLoc+0.5*cm,
                                 xLoc+0.5*cm, yLoc+1*cm,
                                 xLoc+1*cm, yLoc+1*cm,
                                 xLoc+1*cm, yLoc+0.5*cm],
                         fillColor='royalblue',
                         edgeColor='dimgray')
  d.add(cvr2StatPict)
  ac100StatPict = Polygon(points=[xLoc, yLoc,
                                  xLoc, yLoc+0.5*cm,
                                  xLoc+0.5*cm, yLoc+0.5*cm,
                                  xLoc+0.5*cm, yLoc],
                          fillColor='red',
                          edgeColor='dimgray')
  d.add(ac100StatPict)
  dummyStatPict = Polygon(points=[xLoc+0.5*cm, yLoc,
                                  xLoc+0.5*cm, yLoc+0.5*cm,
                                  xLoc+1*cm, yLoc+0.5*cm,
                                  xLoc+1*cm, yLoc],
                          fillColor='black',
                          edgeColor='dimgray')
  d.add(dummyStatPict)

  cvr3MovPict = Polygon(points=[xLoc+xDist, yLoc+yDist+0.5*cm,
                                xLoc+xDist+0.5*cm, yLoc+yDist+1*cm,
                                xLoc+xDist+0.5*cm, yLoc+yDist+0.5*cm],
                        fillColor='yellow',
                        edgeColor='dimgray')
  d.add(cvr3MovPict)
  cvr2MovPict = Polygon(points=[xLoc+xDist+0.5*cm, yLoc+yDist+0.5*cm,
                                xLoc+xDist+0.5*cm, yLoc+yDist+1*cm,
                                xLoc+xDist+1*cm, yLoc+yDist+0.5*cm],
                        fillColor='royalblue',
                        edgeColor='dimgray')
  d.add(cvr2MovPict)
  ac100MovPict = Polygon(points=[xLoc+xDist, yLoc+yDist+0.5*cm,
                                 xLoc+xDist+0.5*cm, yLoc+yDist+0.5*cm,
                                 xLoc+xDist+0.5*cm, yLoc+yDist],
                         fillColor='red',
                         edgeColor='dimgray')
  d.add(ac100MovPict)
  dummyMovPict = Polygon(points=[xLoc+xDist+0.5*cm, yLoc+yDist+0.5*cm,
                                 xLoc+xDist+1*cm, yLoc+yDist+0.5*cm,
                                 xLoc+xDist+0.5*cm, yLoc+yDist],
                         fillColor='black',
                         edgeColor='dimgray')
  d.add(dummyMovPict)

  cvr3Legend = Polygon(points=[xLegendLoc+xLegendDist, yLegendLoc+yLegendDist+2*legendOffset+1*cm,
                               xLegendLoc+xLegendDist, yLegendLoc+yLegendDist+2*legendOffset+1.5*cm,
                               xLegendLoc+xLegendDist+0.5*cm, yLegendLoc+yLegendDist+2*legendOffset+1.5*cm,
                               xLegendLoc+xLegendDist+0.5*cm, yLegendLoc+yLegendDist+2*legendOffset+1*cm],
                       fillColor='yellow',
                       edgeColor='dimgray')
  d.add(cvr3Legend)
  cvr2Legend = Polygon(points=[xLegendLoc+xLegendDist, yLegendLoc+yLegendDist+legendOffset+0.5*cm,
                               xLegendLoc+xLegendDist, yLegendLoc+yLegendDist+legendOffset+1*cm,
                               xLegendLoc+xLegendDist+0.5*cm, yLegendLoc+yLegendDist+legendOffset+1*cm,
                               xLegendLoc+xLegendDist+0.5*cm, yLegendLoc+yLegendDist+legendOffset+0.5*cm],
                       fillColor='royalblue',
                       edgeColor='dimgray')
  d.add(cvr2Legend)
  ac100Legend = Polygon(points=[xLegendLoc+xLegendDist, yLegendLoc+yLegendDist,
                                xLegendLoc+xLegendDist, yLegendLoc+yLegendDist+0.5*cm,
                                xLegendLoc+xLegendDist+0.5*cm, yLegendLoc+yLegendDist+0.5*cm,
                                xLegendLoc+xLegendDist+0.5*cm, yLegendLoc+yLegendDist],
                        fillColor='red',
                        edgeColor='dimgray')
  d.add(ac100Legend)

  textStat = String(xLoc+0.5*cm,
                    yLoc-0.4*cm,
                    "Stationary",
                    textAnchor='middle')
  d.add(textStat)
  textMov = String(xLoc+xDist+0.5*cm,
                   yLoc+yDist-0.4*cm,
                   "Moving",
                   textAnchor='middle')
  d.add(textMov)
  textLegendCVR3 = String(xLegendLoc+xLegendDist+1.1*cm,
                          yLegendLoc+yLegendDist+2*legendOffset+1.1*cm,
                          "CVR3",
                          textAnchor='middle')
  d.add(textLegendCVR3)
  textLegendCVR2 = String(xLegendLoc+xLegendDist+1.1*cm,
                          yLegendLoc+yLegendDist+legendOffset+0.6*cm,
                          "CVR2",
                          textAnchor='middle')
  d.add(textLegendCVR2)
  textLegendAC100 = String(xLegendLoc+xLegendDist+1.1*cm,
                           yLegendLoc+yLegendDist+0.1*cm,
                           "AC100",
                           textAnchor='middle')
  d.add(textLegendAC100)
  return d

def addPageTemplates(doc):
  x, y, width, height = doc.getGeom()
  ext_x, ext_y, ext_width, ext_height = doc.getExtGeom()
  app_x, app_y, app_width, app_height = doc.getAppGeom()

  portrait_frames = [
    Frame(ext_x, y,                ext_width,        height, id='FullPage'),
    Frame(ext_x, y + 19./2*height, ext_width,  1./20*height, id='Title'),
    Frame(ext_x, y +  7./2*height, ext_width, 12./20*height, id='WarningSum'),
    Frame(ext_x, y,                ext_width,  7./20*height, id='ClassifSum'),
    Frame(app_x, app_y,            app_width,    app_height, id='Appendix'),
  ]
  landscape_frames = [
    Frame(ext_y,                   x + 14./15*width, ext_height,    1./15*width,
          id='Title'),
    Frame(ext_y,                   x +  7./15*width, ext_height/4., 7./15*width,
          id='Cvr3ScamAsso'),
    Frame(ext_y + 0.25*ext_height, x +  7./15*width, ext_height/4., 7./15*width,
          id='AebsWarning'),
    Frame(ext_y + 0.50*ext_height, x +  7./15*width, ext_height/4., 7./15*width,
          id='Target'),
    Frame(ext_y + 0.75*ext_height, x +  7./15*width, ext_height/4., 7./15*width,
          id='Plot'),
    Frame(ext_y,                   x,                ext_height/4., 7./15*width,
          id='Video'),
    Frame(ext_y + 0.25*ext_height, x,                ext_height/4., 7./15*width,
          id='TrackNav'),
    Frame(ext_y + 0.50*ext_height, x,                ext_height/2., 7./15*width,
          id='Cvr3CipvReject'),
  ]

  doc.addPageTemplates([
    PageTemplate(id='Portrait', frames=portrait_frames[0],
                 onPage=doc.onPortraitPage, pagesize=A4),
    PageTemplate(id='SummaryPortrait', frames=portrait_frames[1:4],
                 onPage=doc.onPortraitPage, pagesize=A4),
    PageTemplate(id='Landscape', frames=landscape_frames,
                 onPage=doc.onLandscapePage, pagesize=landscape(A4)),
    PageTemplate(id='AppendixPortrait', frames=portrait_frames[4],
                 onPage=doc.onPortraitPage, pagesize=A4),
  ])
  return
