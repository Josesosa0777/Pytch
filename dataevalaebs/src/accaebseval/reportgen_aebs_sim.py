# -*- dataeval: init -*-

import os

import matplotlib
# matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError

from reportlab.platypus import Spacer, PageBreak, Table
from reportlab.lib.pagesizes import cm

from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, Paragraph, italic
from pyutils.math import round2
from config.interval_header import cIntervalHeader

from aebs.par import aebs_classif
from reportgen.common.analyze import Analyze
from reportgen.common.summaries import EventSummary
from reportgen.common.clients import Client, TrackNavigator, VideoNavigator
from reportgen.common.utils import vector2scalar
from aebs.fill.calc_flr20_aebs_phases import Calc as Flr20Calc

abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))

AEBS_TABLE = None

class AebsAnalyze(Analyze):
  dep = {
    'aebs_events': 'analyze_events_sim_merged-last_entries@accaebseval',
  }
  
  query_files = {
    'aebs_events': abspath('../aebseval/events_inttable.sql'),
  }
  
  def fill(self):
    self.view_name = self.batch.create_table_from_last_entries(
      start_date=self.start_date, end_date=self.end_date)

    # AEBS events - TODO: restruct
    index_fill = lambda fill: fill.all
    aebs_ei_ids = index_fill( self.modules.fill(self.dep['aebs_events']) )
    header = cIntervalHeader.fromFileName(self.query_files['aebs_events'])
    global AEBS_TABLE
    AEBS_TABLE = self.batch.get_table_dict(header, aebs_ei_ids, sortby=[('measurement', True), ('start [s]', True)])

    story = intro(
      "AEBS field test evaluation report",
      """
      This is an automatically generated report, based on field tests with
      simultaneously measured forward-looking radar (FLR21) and camera (FLC20)
      sensors.<br/>
      <br/>
      The output signals of AEBS are analyzed and the
      relevant events are collected in this report.<br/>
      Statistical results are presented first, followed by the detailed
      overview of the individual events.<br/>
      """
    )
    story.append(PageBreak())
    story.extend(toc())
    story.append(PageBreak())

    summaries = [Flr20Summary(self.batch, self.view_name)]
    #story.extend(self.summaries(summaries))
    story.extend(self.warnings(summaries))
    return story


class AebsSummary(EventSummary):
  def init(self, batch, view_name):
    data = AEBS_TABLE
    
    for row in data:
      # TODO: exclude intervals within 2 sec
      self.setdefault(row['fullmeas'], []).append(dict(
        start=row['start [s]'],
        end=row['start [s]']+row['duration [s]'],
        duration=row['duration [s]'],
        phase=vector2scalar(row['cascade phase']),
        moving=vector2scalar(row['moving state']),
        asso=vector2scalar(row['asso state']),
        speed=row['ego speed [km/h]'],
        target_dx=row['dx [m]'],
        rating=vector2scalar(row['warning rating scale']),
        cause=aebs_classif.label2maingroup.get(vector2scalar(row['warning cause'])),
      ))

    self.modules.update([
      ('view_videonav_lanes-FLC20@evaltools',
       VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
      ('view_tracknav_lanes-FLC20@evaltools',
       TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
    ])

    self.columns.update([
      ('start', 'start\n[s]\n'),
      ('duration', 'duration\n[s]\n'),
      ('phase', 'aebs phase\n\n'),
      ('moving', 'moving\nstate\n'),
      ('asso', 'asso\nstate\n'),
      ('speed', 'ego speed\n[kmph]\n'),
    ])
    return


class Flr20Summary(AebsSummary):
  title = "AEBS event details"
  explanation = """
  AEBS %s - event duration: %s sec, cause: %s, rating: %s<br/>
  Event is triggered because AEBS state was active: warning (%d), partial (%d)
  or emergency (%d) braking.
  """\
  % ('%(phase)s', '%(duration).2f', '%(cause)s', '%(rating)s',
     Flr20Calc.WARNING, Flr20Calc.PARTIAL, Flr20Calc.EMERGENCY)

  legend_pics = [
    (EventSummary.stat_im, 'stationary'),
    (EventSummary.mov_im, 'moving'),
    (EventSummary.aeb_im, 'AEB track'),
  ]
  extra_modules = [
    ('view_driveract_aebsout_sim-FORD_vs_DAF_80kph@aebseval.sim',
     Client('DriverAct_AebsOut_Plot', '640x700+0+0', 11, 12, cm)),
    ('view_kinematics@aebseval',
     Client('Kinematics_Plot', '640x700+0+0', 11, 12, cm)),
  ]
  statuses = ['fillFLR20_AEB@aebs.fill']
  groups = ['FLR20_AEB']
