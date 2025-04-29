# -*- dataeval: init -*-
import os
from collections import OrderedDict

from reportlab.platypus import Spacer, PageBreak, Table, FrameBreak, Image,\
                               NextPageTemplate, Frame, PageTemplate
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, cm, landscape, A4
from reportlab.pdfbase.pdfmetrics import stringWidth

from interface.Interfaces import iAnalyze
from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, grid_table_style, Paragraph, Link,\
                          get_index_link, superscript

from analyzeAEBSWarningsSimAndRoadTypes import conv_float
from docgen_bendix_warning import EventSummary, addPageTemplates, Analyze,\
                                  Client, TrackNavigator, VideoNavigator, ActiveFlag
from search_aebs_warning import init_params as search_params
from aebs.fill.calc_aebs_phases import Calc as KbCalc
from aebs.fill.calc_trw_aebs_phases import Calc as TrwCalc
from aebs.fill.calc_flr20_aebs_phases import Calc as Flr20Calc

init_params = {
  'all': dict(date=None, start_date=None, end_date=None),
}

class AebsAnalyze(Analyze):
  def init(self, date, start_date, end_date):
    Analyze.init(self)
    self.date = date
    self.start_date = start_date
    self.end_date = end_date
    return

  def fill(self):
    ###
    import matplotlib
    matplotlib.rcParams['savefig.dpi'] = 72
    ###
    batch = self.get_batch()
    self.view_name = batch.create_table_from_last_entries(
      date=self.date, start_date=self.start_date, end_date=self.end_date)

    story = intro(
      "AEBS field test evaluation report",
      """
      This is an automatically generated report, based on field tests with
      simultaneously measured forward-looking radar (FLR20) and camera (FLC20)
      sensors.<br/>
      The output signals of AEBS are analyzed and the
      relevant events are collected in this report.<br/>
      The results are summarized in the table below, followed by the detailed
      overview of the individual events.<br/>
      """
    )
    story.append(PageBreak())
    story.extend(toc())
    story.append(PageBreak())

    summaries = [
      # KbSummary(batch, self.view_name),
      # TrwSummary(batch, self.view_name),
      Flr20Summary(batch, self.view_name),
      # AutoboxSummary(batch, self.view_name),
      # SilSummary(batch, self.view_name),
    ]

    story.extend(self.active_flags('Active TRW flag summary table',
                                   'trw-active-faults'))
    story.extend(self.active_flags('Active A087 flag summary table',
                                   'a087-active-faults'))
    story.extend(self.summaries(summaries))
    story.extend(self.warnings(summaries))
    return story

  def analyze(self, story):
    doc = self.get_doc('dataeval.simple', pagesize=A4)
    addPageTemplates(doc)
    doc.multiBuild(story)
    return

  def active_flags(self, header, title):
    batch = self.get_batch()
    story = [
      IndexedParagraph(header, style='Heading1'),
      Spacer(width=1*cm, height=0.2*cm),
      ActiveFlag(batch, self.view_name, title).get_table(),
      PageBreak(),
    ]
    return story

  def summaries(self, summaries):
    story = [
      IndexedParagraph('Warning summary tables', style='Heading1'),
      NextPageTemplate('LandscapeTable'),
    ]
    for summary in summaries:
      story.append(PageBreak())
      story.append(IndexedParagraph(summary.title, style='Heading2'))
      story.append(summary.get_table(link_pattern=self.EVENT_LINK,
                                     link_heading='Heading2')),
    return story

class AebsSummary(EventSummary):
  def init(self, batch, view_name):
    data = batch.query("""
      SELECT IFNULL(measurements.local, measurements.origin),
             entryintervals.start_time, entryintervals.end_time, phase.name,
             moving.name, asso.name, 3.6*speed.value, target_dx.value,
             pure_aeb.value, dx_aeb.value, rating.name, cause.name
        FROM %s en
        JOIN modules ON
             modules.id = en.moduleid

        JOIN measurements ON
             measurements.id = en.measurementid

        JOIN entryintervals ON
             entryintervals.entryid = en.id

        JOIN interval2label algo_i2l ON
                            algo_i2l.entry_intervalid = entryintervals.id
        JOIN labels algo ON
                    algo.id = algo_i2l.labelid
        JOIN labelgroups algo_labelgroups ON
                         algo_labelgroups.id = algo.groupid

        JOIN interval2label phase_i2l ON
                            phase_i2l.entry_intervalid = entryintervals.id
        JOIN labels phase ON
                    phase.id = phase_i2l.labelid
        JOIN labelgroups phase_labelgroups ON
                         phase_labelgroups.id = phase.groupid

        JOIN interval2label moving_i2l ON
                            moving_i2l.entry_intervalid = entryintervals.id
        JOIN labels moving ON
                    moving.id = moving_i2l.labelid
        JOIN labelgroups moving_labelgroups ON
                         moving_labelgroups.id = moving.groupid

        JOIN interval2label asso_i2l ON
                            asso_i2l.entry_intervalid = entryintervals.id
        JOIN labels asso ON
                    asso.id = asso_i2l.labelid
        JOIN labelgroups asso_labelgroups ON
                         asso_labelgroups.id = asso.groupid

        LEFT JOIN (
          SELECT interval2label.entry_intervalid, labels.name
          FROM   interval2label
          JOIN labels ON labels.id = interval2label.labelid
          JOIN labelgroups ON labelgroups.id = labels.groupid
          WHERE labelgroups.name = :rating_group
        ) AS rating ON
          rating.entry_intervalid = entryintervals.id

        LEFT JOIN (
          SELECT interval2label.entry_intervalid, labels.name
          FROM   interval2label
          JOIN labels ON labels.id = interval2label.labelid
          JOIN labelgroups ON labelgroups.id = labels.groupid
          WHERE labelgroups.name = :cause_group
        ) AS cause ON
          cause.entry_intervalid = entryintervals.id

        JOIN quantities speed ON
                        speed.entry_intervalid = entryintervals.id
        JOIN quanames speed_names ON
                      speed_names.id = speed.nameid
        JOIN quanamegroups speed_namegroups ON
                           speed_namegroups.id = speed_names.groupid

        JOIN quantities target_dx ON
                        target_dx.entry_intervalid = entryintervals.id
        JOIN quanames target_dx_names ON
                      target_dx_names.id = target_dx.nameid
        JOIN quanamegroups target_dx_namegroups ON
                           target_dx_namegroups.id = target_dx_names.groupid

        JOIN quantities pure_aeb ON
                        pure_aeb.entry_intervalid = entryintervals.id
        JOIN quanames pure_aeb_names ON
                      pure_aeb_names.id = pure_aeb.nameid
        JOIN quanamegroups pure_aeb_namegroups ON
                           pure_aeb_namegroups.id = pure_aeb_names.groupid

        JOIN quantities dx_aeb ON
                        dx_aeb.entry_intervalid = entryintervals.id
        JOIN quanames dx_aeb_names ON
                      dx_aeb_names.id = dx_aeb.nameid
        JOIN quanamegroups dx_aeb_namegroups ON
                           dx_aeb_namegroups.id = dx_aeb_names.groupid

      WHERE algo_labelgroups.name = :algo_group
        AND algo.name = :algo
        AND modules.class = :class_name
        AND phase_labelgroups.name = :phase_group
        AND moving_labelgroups.name = :moving_group
        AND asso_labelgroups.name = :asso_group
        AND speed_namegroups.name = :ego_group
        AND speed_names.name = :speed
        AND target_dx_namegroups.name = :target_group
        AND target_dx_names.name = :dx_qua
        AND pure_aeb_namegroups.name = :target_group
        AND pure_aeb_names.name = :pure_aeb
        AND dx_aeb_namegroups.name = :target_group
        AND dx_aeb_names.name = :dx_aeb

      ORDER BY measurements.basename, entryintervals.start
      """ % view_name,

      algo_group='AEBS algo',
      algo=self.title,
      class_name='dataevalaebs.search_aebs_warning.Search',
      phase_group='AEBS cascade phase',
      moving_group='moving state',
      asso_group='asso state',
      rating_group='AEBS event rating scale',
      cause_group='false warning cause',
      ego_group='ego vehicle',
      speed='speed',
      target_group='target',
      dx_qua='dx start',
      pure_aeb='pure aeb duration',
      dx_aeb='dx aeb',
    )

    ###
    # to rename labels
    RATING = {
      '1-False alarm': '1-False alarm',
      '2-Questionable false alarm': '2-Questionable false alarm',
      '3-Questionable': '3-Questionable',
      '4-Questionable mitigation': '4-Questionable justified alarm',
      '5-Mitigation': '5-Justified alarm',
      None: 'None',
    }
    ###
    for meas, start, end, phase, moving, asso, speed_kph, target_dx, pure_aeb,\
        dx_aeb, rating, cause \
     in data:
      self.setdefault(meas, []).append(dict(
        start=start, end=end, duration=end-start, phase=phase, moving=moving,
        asso=asso, speed=speed_kph, target_dx=target_dx, pure_aeb=pure_aeb,
        dx_aeb=dx_aeb, rating=RATING[rating], cause=cause,
      ))

    self.modules.update([
      ('view_videonav_lanes-NO_LANES@evaltools',  # TODO: -FLC20
       VideoNavigator('VideoNavigator', '320x180+0+0', 5.3, 3.0, cm,
                      veh='Bluey', date='131015')),
      ('view_tracknav_lanes-NO_LANES@evaltools',  # TODO: -FLC20
       TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
    ])

    self.columns.update([
      ('start', 'start\n[s]\n'),
      ('duration', 'duration\n[s]\n'),
      ('phase', 'aebs phase\n\n'),
      ('moving', 'moving\nstate\n'),
      ('asso', 'asso\nstate\n'),
      ('speed', 'ego speed\n[kmph]\n'),
      ('pure_aeb', 'aeb period\nbefore start\n[s]'),
      ('dx_aeb', 'dx at aeb\nselction\n[m]'),
    ])
    return

class KbSummary(AebsSummary):
  title = search_params['kb']['algo']
  explanation = """
  AEB %s event duration = %s sec<br/>
  Event is triggered because XBR demand was not positive (%.2f: partial,
  %.2f: emergency) and Acoustical warning was set.
  """\
  % ('%(phase)s', '%(duration).2f', KbCalc.XBR_PARTIAL, KbCalc.XBR_EMRGENCY)

  legend_pics = [
    (EventSummary.stat_im, 'stationary'),
    (EventSummary.mov_im, 'moving'),
    (EventSummary.aeb_im, 'AEB track'),
  ]
  extra_modules = [
    ('view_ego_vehicle-kb@dataevalaebs',
     Client('Ego_vehicle', '640x700+0+0', 11, 12, cm)),
    ('view_flr20_selected_track-AEB@dataevalaebs',
     Client('FLR20_AEB_track', '640x700+0+0', 11, 12, cm)),
  ]
  statuses = ['fillFLR20_AEB@aebs.fill']
  groups = ['FLR20_AEB']


class TrwSummary(AebsSummary):
  title = search_params['trw']['algo']
  explanation = """
  AEB %s event duration = %s sec<br/>
  Event is triggered because XBR demand was not positive (%.2f: partial, %.2f:
  emergency) and cm system status was set (%d: warning, %d: braking).
  """\
  % ('%(phase)s', '%(duration).2f', TrwCalc.XBR_PARTIAL, TrwCalc.XBR_EMRGENCY,
     TrwCalc.CM_WARNING, TrwCalc.CM_BRAKING)

  legend_pics = [
    (EventSummary.stat_im, 'stationary'),
    (EventSummary.mov_im, 'moving'),
    (EventSummary.aeb_im, 'AEB track'),
  ]
  extra_modules = [
    ('view_ego_vehicle-trw@dataevalaebs',
     Client('Ego_vehicle', '640x700+0+0', 11, 12, cm)),
    ('view_flr20_selected_track-AEB@dataevalaebs',
     Client('FLR20_AEB_track', '640x700+0+0', 11, 12, cm)),
  ]
  statuses = ['fillFLR20_AEB@aebs.fill']
  groups = ['FLR20_AEB']

class Flr20Summary(AebsSummary):
  title = search_params['flr20']['algo']
  explanation = """
  AEB %s - event duration: %s sec, cause: %s, rating: %s<br/>
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
    ('view_ego_vehicle-flr20@dataevalaebs',
     Client('Ego_vehicle', '640x700+0+0', 11, 12, cm)),
    ('view_flr20_selected_track-AEB@dataevalaebs',
     Client('FLR20_AEB_track', '640x700+0+0', 11, 12, cm)),
  ]
  statuses = ['fillFLR20_AEB@aebs.fill']
  groups = ['FLR20_AEB']

class AutoboxSummary(Flr20Summary):
  title = search_params['autobox']['algo']
  extra_modules = [
    ('view_ego_vehicle-autobox@dataevalaebs',
     Client('Ego_vehicle', '640x700+0+0', 11, 12, cm)),
    ('view_flr20_selected_track-AEB@dataevalaebs',
     Client('FLR20_AEB_track', '640x700+0+0', 11, 12, cm)),
  ]

class SilSummary(AebsSummary):
  title = search_params['sil']['algo']
  explanation = """
  SIL %s event duration = %s sec<br/>
  """ % ('%(phase)s', '%(duration).2f')

  extra_modules = [
    ('view_wrapper_vehicle@silkbaebs',
     Client('AEBS_wrapper_vehicle', '640x700+0+0', 11, 12, cm)),
    ('view_wrapper_selected_track@silkbaebs',
     Client('AEB_wrapper_track', '640x700+0+0', 11, 12, cm)),
  ]
  legend_pics = [
    (EventSummary.stat_im, 'stationary'),
    (EventSummary.mov_im, 'moving'),
    (EventSummary.aeb_im, 'AEB track'),
  ]

  statuses = ['fillFLR20_AEB@aebs.fill']
  groups = ['FLR20_AEB']
  pass
