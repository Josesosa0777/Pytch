# -*- dataeval: init -*-
import os
from collections import OrderedDict

from reportlab.platypus import Spacer, PageBreak, Table, FrameBreak, Image,\
                               NextPageTemplate, Frame, PageTemplate
from reportlab.lib import colors
from reportlab.lib.pagesizes import cm, landscape, A4
from reportlab.pdfbase.pdfmetrics import stringWidth

#import matplotlib
#matplotlib.rcParams['savefig.dpi'] = 72

from interface.Interfaces import iAnalyze
from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, Paragraph, Link,\
                          get_index_link, superscript

from analyzeAEBSWarningsSimAndRoadTypes import conv_float, TableDict
from search_bendix_warning import init_params as search_init_params
from aebs.fill.calc_bendix_acc_activity import Calc as AccCalc
from aebs.fill.calc_bendix_cmt_warning import Calc as AebCalc
from aebs.fill.calc_bendix_umo import Calc as UmoCalc
from aebs.fill.calc_bendix_stat_obj_alert import Calc as StatCalc
from aebs.fill.calc_bendix_ldw import Calc as LdwCalc
from aebs.fill.calc_bendix_tsr import Calc as TsrCalc

class Analyze(iAnalyze):
  def init(self):
    self.view_name = ''
    self.EVENT_LINK = '%s @ %.2f sec'
    return

  def fill(self):
    batch = self.get_batch()
    self.view_name = batch.create_table_from_last_entries(
      start_date=self.start_date, end_date=self.end_date)

    story = intro(
      "AEBS & ACC field test evaluation report",
      """
      This is an automatically generated report, based on field tests with
      simultaneously measured forward-looking radar (FLR20) and camera (FLC20)
      sensors.<br/>
      The output signals of AEBS and ACC functions are analyzed and the
      relevant events are collected in this report.<br/>
      The results are summarized in the table below, followed by the detailed
      overview of the individual events.<br/>
      """
    )
    story.append(PageBreak())
    story.extend(toc())
    story.append(PageBreak())

    summaries = [
      AebSummary(batch, self.view_name),
      AccSummary(batch, self.view_name),
      UmoSummary(batch, self.view_name),
      StatSummary(batch, self.view_name),
      LdwSummary(batch, self.view_name),
      TsrSummary(batch, self.view_name),
    ]

    story.extend(self.summaries(summaries,
      'view_bendix_warning_by_tot_dist@dataevalaebs'))
    story.extend(self.active_flags('Active TRW flag summary table',
                                   'trw-active-faults'))
    story.extend(self.active_flags('Active A087 flag summary table',
                                   'a087-active-faults'))
    story.extend(self.warnings(summaries))
    story.extend(self.ldw_intervals())
    story.extend(self.dorc_intervals())
    return story

  def analyze(self, story):
    footer = u"\N{Copyright Sign} " \
      "Bendix reserves all rights even in the event of " \
      "industrial property. We reserve all rights of disposal such as " \
      "copying and passing on to third parties."
    doc = self.get_doc('dataeval.simple', logo='Bendix_logo.png', footer=footer,
                       pagesize=A4)
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

  def summaries(self, summaries, module_name):
    story = [
      IndexedParagraph('Warning summary tables', style='Heading1'),
      self.module_plot(module_name),
      NextPageTemplate('LandscapeTable'),
      PageBreak(),
    ]
    for summary in summaries:
      story.append(IndexedParagraph(summary.title, style='Heading2'))
      story.append(summary.get_table(link_pattern=self.EVENT_LINK,
                                     link_heading='Heading2')),
      story.append(PageBreak())
    return story

  def module_plot(self, module_name, client_name='MatplotlibNavigator'):
    batch = self.get_batch()
    manager = self.clone_manager()
    manager.set_batch(batch.clone())

    manager.build([module_name], show_navigators=False)
    sync = manager.get_sync()
    client = Client('MatplotlibNavigator', '640x733+0+0', 12.8, 14.66, cm)
    image = client(sync, module_name)
    manager.close()
    return image

  def warnings(self, summaries):
    story = []
    for summary in summaries:
      story.append(IndexedParagraph('%s events'%summary.title, style='Heading1'))
      story.extend(self.events(summary))
      story.append(NextPageTemplate('LandscapeTable'))
      story.append(PageBreak())
    return story
  
  def ldw_intervals(self):
    story = [
      IndexedParagraph('LDW interval summary', style='Heading1'),
    ]
    dur = []
    line = "Right"
    VIEWRANGE_MIN = "20-0"
    for line in ("Right", "Left"):
      for view_range in ("0-0", VIEWRANGE_MIN):
        qs = """
          SELECT TOTAL(ei.end_time-ei.start_time)
          FROM entryintervals AS ei
          JOIN %(entries)s AS en ON en.id = ei.entryid
          JOIN modules AS mo ON mo.id = en.moduleid
          WHERE en.title = "%(side)s line detected > %(view_range)s m" AND
          mo.class = "dataevalaebs.search_lanes_visible_bendix.Search"
          """ % dict(entries=self.view_name, side=line, view_range=view_range)
        data = self.batch.query(qs)
        duration = data[0][0]
        dur.append(duration)
        story.append(Paragraph("%s line detected > %s m" % (line, view_range)))
        story.append(Paragraph("%f seconds" % duration))
        story.append(Paragraph("-"))
    if dur[0] > 0.0:
      story.append(Paragraph("Right lane ratio = %.1f%%" % (100*dur[1]/dur[0])))
    else:
      story.append(Paragraph("Right lane ratio = 0.0%"))
    if dur[2] > 0.0:
      story.append(Paragraph("Left lane ratio = %.1f%%" % (100*dur[3]/dur[2])))
    else:
      story.append(Paragraph("left lane ratio = 0.0%"))
    story.append(PageBreak())
    return story
  
  def dorc_intervals(self):
    story = [
      IndexedParagraph('DORC interval summary', style='Heading1'),
    ]
    qs = """
         SELECT COUNT(*)
         FROM entryintervals AS ei
         JOIN %(entries)s AS en ON en.id = ei.entryid
         JOIN modules AS mo ON mo.id = en.moduleid
         WHERE en.title = "DORC Red Button Pressed" AND
         mo.class = "dataevalaebs.search_dorc_press_bendix.Search"
         """ % dict(entries=self.view_name)
    data = self.batch.query(qs)
    presses = data[0][0]
    story.append(Paragraph("DORC button press detected"))
    story.append(Paragraph("%d presses" % presses))
    story.append(Paragraph("-"))
    story.append(PageBreak())
    return story

  def events(self, summary):
    statuses = ['fillFLR20@aebs.fill']
    statuses.extend(summary.statuses)
    groups = ['FLR20', 'moving', 'stationary']
    groups.extend(summary.groups)

    story = summary.get_tracknav_legend()

    for meas, warnings in summary.iteritems():
      manager = self.clone_manager()
      manager.set_measurement(meas)
      manager.build(summary.modules, status_names=statuses,
                    visible_group_names=groups, show_navigators=False)
      sync = manager.get_sync()
      for warning in warnings:
        title = self.EVENT_LINK % (os.path.basename(meas), warning['start'])
        story.extend([
          NextPageTemplate('Landscape'),
          PageBreak(),
          IndexedParagraph(title, style='Heading2'),
          FrameBreak(),
          Paragraph(summary.explanation % warning, style='Normal'),
        ])
        sync.seek(warning['start'])
        manager.set_roi(warning['start'], warning['end'], color='y',
                        pre_offset=8.0, post_offset=7.0)
        for module_name, client in summary.modules.iteritems():
          story.append( client(sync, module_name) )
          story.append( FrameBreak() )
        if summary.modules: story.pop(-1)  # remove last FrameBreak
      manager.close()
    return story

class Client(object):
  def __init__(self, client_name, windgeom, width, height, unit, **kwargs):
    self.client_name = client_name
    self.windgeom = windgeom
    self.size = dict(width=width*unit, height=height*unit)
    self.mod_kwargs = kwargs
    return

  def __call__(self, sync, module_name):
    try:
      client = sync.getClient(module_name, self.client_name)
    except ValueError:
      data = Paragraph('No %s' %self.client_name)
    else:
      self.mod_client(client, **self.mod_kwargs)
      client.setWindowGeometry(self.windgeom)
      data = Image(client.copyContentToBuffer(), **self.size)
    return data

  def mod_client(self, client):
    return

class TrackNavigator(Client):
  def mod_client(self, client):
    client.showPosition = True
    return

class VideoNavigator(Client):
  pass

PIC_DIR = os.path.join(os.path.dirname(__file__), 'images')

class Summary(TableDict):
  font_name = 'Helvetica'
  font_size = 7
  title = ''

  def __init__(self, batch, view_name):
    TableDict.__init__(self)
    self.columns = OrderedDict()
    self.modules = OrderedDict()
    self.init(batch, view_name)
    self.colWidths = self.get_colwidth()
    return

  def get_colwidth(self, default=12*cm):
    if self:
      colwidth = stringWidth(self.keys()[0], self.font_name, self.font_size)
    else:
      colwidth = default
    return colwidth

  def get_table(self, link_pattern, link_heading, **kwargs):
    data = self.get_data(link_pattern, link_heading, **kwargs)
    style = self.get_style()
    colWidths = [self.colWidths]
    colWidths.extend(None for e in self.columns)
    table = Table(data, style=style, colWidths=colWidths)
    return table

  def get_data(self, link_pattern, link_heading):
    raise NotImplementedError()

  def get_style(self):
    raise NotImplementedError()


class EventSummary(Summary):
  explanation = ''
  legend_pics = []
  extra_modules = []
  extra_columns = []
  statuses = []
  groups = []

  stat_im = Image(os.path.join(PIC_DIR, 'flr20_stationary_legend.png'),
                  width=0.5*cm, height=0.5*cm)
  mov_im = Image(os.path.join(PIC_DIR, 'flr20_moving_legend.png'),
                 width=0.5*cm, height=0.5*cm)
  aeb_im = Image(os.path.join(PIC_DIR, 'flr20_aeb_legend.png'),
                 width=0.5*cm, height=0.5*cm)
  acc_im = Image(os.path.join(PIC_DIR, 'flr20_acc_legend.png'),
                 width=0.5*cm, height=0.5*cm)

  def __init__(self, batch, view_name):
    Summary.__init__(self, batch, view_name)
    self.modules.update(self.extra_modules)
    self.columns.update(self.extra_columns)
    return

  @staticmethod
  def show_position(client):
    client.showPosition = True
    return

  @staticmethod
  def conv_target_vx(target_vx, moving):
    target_vx = target_vx if moving in ('moving', 'unclassified') else moving
    return target_vx

  @staticmethod
  def conv_xbr_speed_red(xbr_speed_red, cm_status):
    return xbr_speed_red

  @staticmethod
  def conv_nan(value):
    value = 'n/a' if value is None else value
    return value

  @staticmethod
  def conv_ttc(ttc_min, accel_demand_min):
    if accel_demand_min is None:
      ttc_min = 'n/a'
    return ttc_min

  @staticmethod
  def conv_gps(latitude, longitude, fmt='%.5f'):
    if latitude is None or longitude is None:
      coord = "?, ?"
    else:
      lat_sign = 'N' if latitude >= 0 else 'S'
      long_sign = 'E' if longitude >= 0 else 'W'
      coord_fmt = ' '.join(['%s', fmt, '%s', fmt])
      coord = coord_fmt % (lat_sign, abs(latitude), long_sign, abs(longitude))
    return coord

  def get_data(self, link_pattern, link_heading):
    header = self.columns.values()
    header.insert(0, 'measurement')
    data = [header]
    for meas, warnings in self.iteritems():
      basename = os.path.basename(meas)
      for warning in warnings:
        row = [conv_float(warning[name]) for name in self.columns]
        # create sub table for link
        # http://xiix.wordpress.com/2008/03/12/a-reportlab-link-in-table-cell-workaround/
        link = get_index_link(link_pattern % (basename, warning['start']),
                              link_heading)
        row.insert(0, Table([[Paragraph(Link(link, basename),
                                        fontSize=self.font_size,
                                        fontName=self.font_name)]],
                            colWidths=self.colWidths))
        data.append(row)
    return data

  def get_style(self):
    style = [
      ('GRID',   ( 0, 0), (-1, -1), 0.025*cm, colors.black),
      ('FONT',   ( 0, 0), (-1,  0), '%s-Bold' % self.font_name, self.font_size),
      ('FONT',   ( 0, 1), (-1, -1), self.font_name, self.font_size),
      ('ALIGN',  ( 0, 1), (-1, -1), 'CENTER'),
      ('VALIGN', ( 0, 1), (-1, -1), 'MIDDLE'),
    ]
    return style

  def get_tracknav_legend(self):
    story = [
      Paragraph('Legend of the birdeye view picture', style='Heading3'),
      Paragraph('Meaning of the object shapes', style='Normal'),
      Table([pic for pic in self.legend_pics], hAlign='LEFT'),
      Spacer(width=1*cm, height=0.2*cm),
      Paragraph('Meaning of the colors', style='Normal'),
      Spacer(width=1*cm, height=0.2*cm),
      Table([['stationary or very slow'], ['ongoing'], ['oncoming']],
            style=[('TEXTCOLOR', (0, 0), ( 0,  0), colors.red),
                   ('TEXTCOLOR', (0, 1), ( 0,  1), colors.green),
                   ('TEXTCOLOR', (0, 2), ( 0,  2), colors.blue)],
            hAlign='LEFT'),
      Paragraph(r'Meaning of the object label: {track}({lat}|{long})',
                style='Normal'),
      Spacer(width=1*cm, height=0.2*cm),
      Table([
        ['track', 'Name of the track.'],
        ['lat', 'Lateral distance from the ego vehicle. Left is positive'],
        ['long', 'Longitudinal distance from the ego vehicle.'],
      ], hAlign='LEFT'),
      Spacer(width=1*cm, height=0.2*cm),
    ]
    return story

class BendixSummary(EventSummary):
  def init(self, batch, view_name):
    data = batch.query("""
      SELECT IFNULL(measurements.local, measurements.origin),
             entryintervals.start_time, entryintervals.end_time,
             speed.value*3.6, (speed_end.value-speed.value)*3.6,
             speed_red.value, target_dx.value, target_vx.value*3.6,
             moving_labels.name, cm_status_labels.name, accel_demand_min.value,
             asso_state_labels.name, ttc_min.value,
             gps_lat.value, gps_long.value,  
             lane_left.value, lane_right.value
        FROM %s en
        JOIN modules ON
             modules.id = en.moduleid

        JOIN measurements ON
             measurements.id = en.measurementid

        JOIN entryintervals ON
             entryintervals.entryid = en.id

        JOIN (
          SELECT interval2label.entry_intervalid, labels.name
          FROM   interval2label
          JOIN labels ON labels.id = interval2label.labelid
          JOIN labelgroups ON labelgroups.id = labels.groupid
          WHERE labelgroups.name = :algo_group
            AND labels.name = :algo
        ) AS algo_labels ON
          algo_labels.entry_intervalid = entryintervals.id

        LEFT JOIN (
          SELECT interval2label.entry_intervalid, labels.name
          FROM   interval2label
          JOIN labels ON labels.id = interval2label.labelid
          JOIN labelgroups ON labelgroups.id = labels.groupid
          WHERE labelgroups.name = :moving_group
        ) AS moving_labels ON
          moving_labels.entry_intervalid = entryintervals.id

        LEFT JOIN (
          SELECT interval2label.entry_intervalid, labels.name
          FROM   interval2label
          JOIN labels ON labels.id = interval2label.labelid
          JOIN labelgroups ON labelgroups.id = labels.groupid
          WHERE labelgroups.name = :cm_status_group
        ) AS cm_status_labels ON
          cm_status_labels.entry_intervalid = entryintervals.id

        LEFT JOIN (
          SELECT interval2label.entry_intervalid, labels.name
          FROM   interval2label
          JOIN labels ON labels.id = interval2label.labelid
          JOIN labelgroups ON labelgroups.id = labels.groupid
          WHERE labelgroups.name = :asso_state_group
        ) AS asso_state_labels ON
          asso_state_labels.entry_intervalid = entryintervals.id

        LEFT JOIN (
          SELECT quantities.entry_intervalid, quantities.value
          FROM   quantities
          JOIN quanames ON quanames.id = quantities.nameid
          JOIN quanamegroups ON quanamegroups.id = quanames.groupid
          WHERE quanamegroups.name = :ego_group
            AND quanames.name = :speed_qua
        ) AS speed ON
          speed.entry_intervalid = entryintervals.id

        LEFT JOIN (
          SELECT quantities.entry_intervalid, quantities.value
          FROM   quantities
          JOIN quanames ON quanames.id = quantities.nameid
          JOIN quanamegroups ON quanamegroups.id = quanames.groupid
          WHERE quanamegroups.name = :ego_group
            AND quanames.name = :speed_end_qua
        ) AS speed_end ON
          speed_end.entry_intervalid = entryintervals.id

        LEFT JOIN (
          SELECT quantities.entry_intervalid, quantities.value
          FROM   quantities
          JOIN quanames ON quanames.id = quantities.nameid
          JOIN quanamegroups ON quanamegroups.id = quanames.groupid
          WHERE quanamegroups.name = :intervention_group
            AND quanames.name = :speed_red_qua
        ) AS speed_red ON
          speed_red.entry_intervalid = entryintervals.id

        LEFT JOIN (
          SELECT quantities.entry_intervalid, quantities.value
          FROM   quantities
          JOIN quanames ON quanames.id = quantities.nameid
          JOIN quanamegroups ON quanamegroups.id = quanames.groupid
          WHERE quanamegroups.name = :target_group
            AND quanames.name = :dx_qua
        ) AS target_dx ON
          target_dx.entry_intervalid = entryintervals.id

        LEFT JOIN (
          SELECT quantities.entry_intervalid, quantities.value
          FROM   quantities
          JOIN quanames ON quanames.id = quantities.nameid
          JOIN quanamegroups ON quanamegroups.id = quanames.groupid
          WHERE quanamegroups.name = :target_group
            AND quanames.name = :vx_qua
        ) AS target_vx ON
          target_vx.entry_intervalid = entryintervals.id

        LEFT JOIN (
          SELECT quantities.entry_intervalid, quantities.value
          FROM   quantities
          JOIN quanames ON quanames.id = quantities.nameid
          JOIN quanamegroups ON quanamegroups.id = quanames.groupid
          WHERE quanamegroups.name = :intervention_group
            AND quanames.name = :accel_demand_min
        ) AS accel_demand_min ON
          accel_demand_min.entry_intervalid = entryintervals.id

        LEFT JOIN (
          SELECT quantities.entry_intervalid, quantities.value
          FROM   quantities
          JOIN quanames ON quanames.id = quantities.nameid
          JOIN quanamegroups ON quanamegroups.id = quanames.groupid
          WHERE quanamegroups.name = :target_group
            AND quanames.name = :ttc_min
        ) AS ttc_min ON
          ttc_min.entry_intervalid = entryintervals.id

        LEFT JOIN (
          SELECT quantities.entry_intervalid, quantities.value
          FROM   quantities
          JOIN quanames ON quanames.id = quantities.nameid
          JOIN quanamegroups ON quanamegroups.id = quanames.groupid
          WHERE quanamegroups.name = :ego_group
            AND quanames.name = :gps_lat_qua
        ) AS gps_lat ON
          gps_lat.entry_intervalid = entryintervals.id

        LEFT JOIN (
          SELECT quantities.entry_intervalid, quantities.value
          FROM   quantities
          JOIN quanames ON quanames.id = quantities.nameid
          JOIN quanamegroups ON quanamegroups.id = quanames.groupid
          WHERE quanamegroups.name = :ego_group
            AND quanames.name = :gps_long_qua
        ) AS gps_long ON
          gps_long.entry_intervalid = entryintervals.id
          
        LEFT JOIN (
          SELECT quantities.entry_intervalid, quantities.value
          FROM   quantities
          JOIN quanames ON quanames.id = quantities.nameid
          JOIN quanamegroups ON quanamegroups.id = quanames.groupid
          WHERE quanamegroups.name = 'lane'
            AND quanames.name = 'left line view range start'
        ) AS lane_left ON
          lane_left.entry_intervalid = entryintervals.id       

        LEFT JOIN (
          SELECT quantities.entry_intervalid, quantities.value
          FROM   quantities
          JOIN quanames ON quanames.id = quantities.nameid
          JOIN quanamegroups ON quanamegroups.id = quanames.groupid
          WHERE quanamegroups.name = 'lane'
            AND quanames.name = 'right line view range start'
        ) AS lane_right ON
          lane_right.entry_intervalid = entryintervals.id       

      WHERE modules.class = :class_name

      ORDER BY measurements.basename, entryintervals.start
      """ % view_name,

      algo_group='Bendix event',
      algo=self.title,
      moving_group='moving state',
      cm_status_group='cm system status',
      asso_state_group='asso state',
      class_name='dataevalaebs.search_bendix_warning.Search',
      ego_group='ego vehicle',
      speed_qua='speed start',
      speed_end_qua='speed end',
      gps_lat_qua='gps lat start',
      gps_long_qua='gps long start',
      target_group='target',
      dx_qua='dx start',
      vx_qua='vx start',
      intervention_group='intervention',
      speed_red_qua='speed reduction',
      accel_demand_min='accel demand min',
      ttc_min='ttc min',
    )

    for meas, start, end, speed, speed_red, xbr_speed_red, target_dx,\
        target_vx, moving, cm_status, accel_demand_min, asso, ttc_min, \
        gps_lat, gps_long, \
        left_lane_view_range, right_lane_view_range \
      in data:
      target_vx = self.conv_target_vx(target_vx, moving)
      xbr_speed_red = self.conv_xbr_speed_red(xbr_speed_red, cm_status)
      accel_demand_min = self.conv_nan(accel_demand_min)
      ttc_min = self.conv_ttc(ttc_min, accel_demand_min)
      gps = self.conv_gps(gps_lat, gps_long)
      self.setdefault(meas, []).append(
        dict(start=start, end=end, duration=end-start, speed=speed,
             speed_red=speed_red, xbr_speed_red=xbr_speed_red,
             target_dx=target_dx, target_vx=target_vx, cm_status=cm_status,
             accel_demand_min=accel_demand_min, asso=asso,
             ttc_min=ttc_min, gps=gps,
             left_lane_view_range=left_lane_view_range, right_lane_view_range=right_lane_view_range)
      )

    self.modules.update([
      ('view_videonav_lanes-FLC20@evaltools',
       VideoNavigator('VideoNavigator', '320x260+0+0', 5.3, 4.3, cm)),
      ('view_tracknav_lanes-FLC20@evaltools',
       TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
    ])

    self.columns.update([
      ('start', 'start\n[s]'),
      ('duration', 'duration\n[s]'),
      ('speed', 'speed\n[kph]'),
#      ('gps', 'gps'),
    ])
    return


class AebSummary(BendixSummary):
  title = search_init_params['cmt']['algo']
  explanation = """
    AEB event duration = %s sec<br/>
    Event is triggered because AudibleFeedback was %d or AEB_state was
    %d or cm_system_status was %d"""\
    % ('%(duration).2f', AebCalc.AUDIBLE_FEEDBACK, AebCalc.AEB_STATE,
       AebCalc.CM_SYSTEM_STATUS)
  legend_pics = [
    (BendixSummary.stat_im, 'stationary'),
    (BendixSummary.mov_im, 'moving'),
    (BendixSummary.aeb_im, 'AEB track'),
  ]
  extra_modules = [
    ('view_bendix_ego_vehicle-cmt@dataevalaebs',
     Client('Ego_vehicle', '640x700+0+0', 11, 12, cm)),
    ('view_flr20_selected_track-AEB@dataevalaebs',
     Client('FLR20_AEB_track', '640x700+0+0', 11, 12, cm)),
  ]
  extra_columns = [
    ('target_vx', 'rel speed\n[kph]'),
    ('target_dx', 'target dx\n[m]'),
    ('asso', 'assoc\nstate'),
    ('accel_demand_min', 'min xbr\n[m/s^2]'),
    ('cm_status', 'cm system\nstatus'),
    ('xbr_speed_red', 'xbr speed red\n[kph]'),
    ('speed_red', 'speed red\n[kph]'),
    ('ttc_min', 'ttc\n[s]'),
  ]
  statuses = ['fillFLR20_AEB@aebs.fill']
  groups = ['FLR20_AEB']

  @staticmethod
  def conv_xbr_speed_red(xbr_speed_red, cm_status):
    xbr_speed_red = 'no xbr' if cm_status != '3-Braking' else xbr_speed_red
    return xbr_speed_red

class AccSummary(BendixSummary):
  title = search_init_params['acc']['algo']
  explanation = """
    ACC event duration = %s sec<br/>
    Event is triggered because XBR_ControlMode was %d and
    XBR_AccelDemand was lower than %.1f m/s%s and
    AudibleFeedback was not %d"""\
    % ('%(duration).2f', AccCalc.CTRL_MODE,
       AccCalc.ACCEL_DEMAND_LIMIT, superscript('2'),
       AccCalc.INVALID_AUDIBLE_FEEDBACK)
  legend_pics = [
    (EventSummary.stat_im, 'stationary'),
    (EventSummary.mov_im, 'moving'),
    (EventSummary.acc_im, 'ACC track'),
  ]
  extra_modules = [
    ('view_bendix_ego_vehicle-acc@dataevalaebs',
     Client('Ego_vehicle', '640x700+0+0', 11, 12, cm)),
    ('view_flr20_selected_track-ACC@dataevalaebs',
     Client('FLR20_ACC_track', '640x700+0+0', 11, 12, cm)),
  ]
  extra_columns = [
    ('target_vx', 'rel speed\n[kph]'),
    ('target_dx', 'target dx\n[m]'),
    ('asso', 'assoc\nstate'),
    ('accel_demand_min', 'min xbr\n[m/s^2]'),
    ('xbr_speed_red', 'xbr speed red\n[kph]'),
    ('speed_red', 'speed red\n[kph]'),
    ('ttc_min', 'ttc\n[s]'),
  ]
  statuses = ['fillFLR20_ACC@aebs.fill']
  groups = ['FLR20_ACC']

class UmoSummary(BendixSummary):
  title = search_init_params['umo']['algo']
  explanation = """
    UMO event duration = %s sec<br/>
    Event is triggered because umoCandidateQualified was %d"""\
    % ('%(duration).2f', UmoCalc.QUALIFIED)
  legend_pics = [
    (EventSummary.stat_im, 'stationary'),
    (EventSummary.mov_im, 'moving'),
  ]
  extra_modules = [
    ('view_bendix_ego_vehicle-umo@dataevalaebs',
     Client('Ego_vehicle', '640x700+0+0', 11, 12, cm)),
    ('view_flr20_selected_track-UMO@dataevalaebs',
     Client('FLR20_UMO_track', '640x700+0+0', 11, 12, cm)),
  ]
  extra_columns = [
    ('target_vx', 'rel speed\n[kph]'),
    ('target_dx', 'target dx\n[m]'),
    ('asso', 'assoc\nstate'),
    ('accel_demand_min', 'min xbr\n[m/s^2]'),
  ]

class StatSummary(BendixSummary):
  title = search_init_params['stat']['algo']
  explanation = """
    Stationary object alert duration = %s<br/>
    Event is triggered because AudibleFeedback was %d and FDALightStripControl
    was %d.
    """\
    % ('%(duration).2f',
       StatCalc.AUDIBLE_FEEDBACK, StatCalc.FDA_LIGHT_STRIP_CTRL)
  legend_pics = [
    (EventSummary.stat_im, 'stationary'),
    (EventSummary.mov_im, 'moving'),
  ]
  extra_modules = [
    ('view_bendix_ego_vehicle-stat@dataevalaebs',
     Client('Ego_vehicle', '640x700+0+0', 11, 12, cm)),
    ('view_flr20_selected_track-AEB@dataevalaebs',
     Client('FLR20_AEB_track', '640x700+0+0', 11, 12, cm)),
  ]
  extra_columns = [
    ('target_vx', 'rel speed\n[kph]'),
    ('target_dx', 'target dx\n[m]'),
    ('asso', 'assoc\nstate'),
    ('accel_demand_min', 'min xbr\n[m/s^2]'),
  ]

class LdwSummary(BendixSummary):
  title = search_init_params['ldw']['algo']
  explanation = """
  Ldw event duration = %s<br/>
  Event is triggered because LDW_LaneDeparture_Left or LDW_LaneDeparture_Right
  was %d.
  """ % ('%(duration).2f', LdwCalc.WARNING)
  legend_pics = [
    (EventSummary.stat_im, 'stationary'),
    (EventSummary.mov_im, 'moving'),
  ]
  extra_modules = [
    ('view_bendix_ego_vehicle-ldw@dataevalaebs',
     Client('Ego_vehicle', '640x700+0+0', 11, 12, cm)),
    ('view_flr20_selected_track-AEB@dataevalaebs',
     Client('FLR20_AEB_track', '640x700+0+0', 11, 12, cm)),
  ]
  extra_columns = [
    ('left_lane_view_range', 'left lane\nview range\n[m]'),
    ('right_lane_view_range', 'right lane\nview range\n[m]'),
  ]


class TsrSummary(BendixSummary):
  title = search_init_params['tsr']['algo']
  explanation = """
  TSR event duration = %s<br/>
  This event is triggered when TSR_Warning_Flag equals %d
  """ % ('%(duration).2f', TsrCalc.TSR_WARNING_TRIGGER)
  legend_pics = [
    (EventSummary.stat_im, 'stationary'),
    (EventSummary.mov_im, 'moving'),
  ]
  extra_modules = [
    ('view_bendix_DAS_TSR_Status-def_param@dataevalaebs',
     Client('TSR_Warning', '640x700+0+0', 11, 12, cm)),
    ('view_flr20_selected_track-AEB@dataevalaebs',
     Client('FLR20_AEB_track', '640x700+0+0', 11, 12, cm)),
  ]


class ActiveFlag(list):
  def __init__(self, batch, view_name, title):
    data = batch.query("""
      SELECT me.start, ei.end_is_last, ei.start, ei.start_time, ei.end_time,
             flag.name
        FROM %s en
        JOIN entryintervals ei ON ei.entryid = en.id
        JOIN measurements me ON me.id = en.measurementid
        JOIN modules mo ON mo.id = en.moduleid

        JOIN interval2label flag_il ON flag_il.entry_intervalid = ei.id
        JOIN labels flag ON flag.id = flag_il.labelid
        JOIN labelgroups flag_lg ON flag_lg.id = flag.groupid

      WHERE mo.class = :class_name
        AND en.title = :title
        AND flag_lg.name = :flag_lg
      ORDER BY me.start ASC
      """ % view_name,
      class_name='dataevalaebs.search_activefault.Search',
      title=title,
      flag_lg='TRW active fault',
    )

    row = dict(start_name='', start=0, start_time=0.0, end_name='',
               end_is_last=0, end_time=0.0, flags=set())
    for name, end_is_last, start, start_time, end_time, flag in data:
      if row['end_is_last'] and start == 0:
        row['end_name'] = name
        row['end_is_last'] = end_is_last
        row['end_time'] = end_time
        row['flags'].add(flag)
      else:
        row = dict(start_name=name, end_name=name, start=start,
                   start_time=start_time, end_is_last=end_is_last,
                   end_time=end_time, flags={flag})
        self.append(row)
    return

  def get_table(self):
    style = self.get_style()
    data = self.get_data()
    table = Table(data, style=style)
    return table

  def get_data(self):
    data = [['start meas', 'start time', 'end meas', 'end time', 'flags']]

    for cell in self:
      row = [
        cell['start_name'],
        conv_float(cell['start_time'] if cell['start'] != 0 else 'start'),
        cell['end_name'],
        conv_float('end' if cell['end_is_last'] else cell['end_time']),
        '\n'.join(cell['flags'])
      ]
      data.append(row)
    return data

  def get_style(self):
    style = [
      ('GRID',   ( 0, 0), (-1, -1), 0.025*cm, colors.black),
      ('FONT',   ( 0, 0), (-1,  0), 'Helvetica-Bold'),
    ]
    return style

  def str_table(self):
    table = '\n'.join('|%s|' % '|'.join(row) for row in self.get_data())
    return table


def addPageTemplates(doc):
  x, y, width, height = doc.getGeom()
  ext_x, ext_y, ext_width, ext_height = doc.getExtGeom()
  app_x, app_y, app_width, app_height = doc.getAppGeom()

  portrait_frames = [
    Frame(ext_x, y, ext_width, height, id='FullPage'),
  ]
  landscape_frames = [
    Frame(ext_y,                  x + 0.9*width,     ext_height, 0.1*width, id='Title'),
    Frame(ext_y,                  x + 0.8*width,     ext_height, 0.1*width, id='Duartion'),
    Frame(ext_y,                  x + 0.5*width, 0.2*ext_height, 0.3*width, id='VideoNav'),
    Frame(ext_y,                  x,             0.2*ext_height, 0.5*width, id='TrackNav'),
    Frame(ext_y + 0.2*ext_height, x,             0.4*ext_height, 0.8*width, id='EgoPlot'),
    Frame(ext_y + 0.6*ext_height, x,             0.4*ext_height, 0.8*width, id='TargetPlot'),
  ]
  landscape_table_frames = [
    Frame(y, x, height, width, id='FullPage'),
  ]

  doc.addPageTemplates([
    PageTemplate(id='Portrait', frames=portrait_frames,
                 onPage=doc.onPortraitPage, pagesize=A4),
    PageTemplate(id='Landscape', frames=landscape_frames,
                 onPage=doc.onLandscapePage, pagesize=landscape(A4)),
    PageTemplate(id='LandscapeTable', frames=landscape_table_frames,
                 onPage=doc.onLandscapePage, pagesize=landscape(A4)),
  ])
  return

