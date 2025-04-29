# -*- dataeval: init -*-

import os
from collections import OrderedDict

from interface.Interfaces import iAnalyze
from config.Analyze import cIntervalHeader
from pyutils.math import round2


abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))
cm = 1.0

class Analyze(iAnalyze):
  optdep = dict(
    aebs_events='analyze_events_merged-last_entries@aebseval',
    smess_faults='analyze_smess_faults-last_entries@flr20eval.faults',
    a087_faults='analyze_a087_faults-last_entries@flr20eval.faults',
    dur_vs_roadtype='view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
    dist_vs_roadtype='view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
    dur_vs_engine_onoff='view_quantity_vs_onoff_stats-print_duration@egoeval.enginestate',
    dur_vs_daytime='view_quantity_vs_daytime_stats-print_duration@flc20eval.daytime',
    dur_vs_aebsstate='view_quantity_vs_systemstate_stats-print_duration@aebseval.systemstate',
    dur_vs_inlane_tr0='view_quantity_vs_inlane_flr20_tr0_stats-print_duration@trackeval.inlane',
    dur_vs_inlane_tr0_fused='view_quantity_vs_inlane_flr20_tr0_fused_stats-print_duration@trackeval.inlane',
    dist_vs_inlane_tr0='view_quantity_vs_inlane_flr20_tr0_stats-print_mileage@trackeval.inlane',
    dist_vs_inlane_tr0_fused='view_quantity_vs_inlane_flr20_tr0_fused_stats-print_mileage@trackeval.inlane',
  )
  
  def init(self):
    self.doc = self.get_doc('dataeval.simpletxt')
    return
  
  def fill(self):
    index_fill = lambda fill: fill.all
    story = []
    
    # dynamic import hack  # TODO: "from self.doc.tygra import Paragraph, Spacer"
    vars_ = globals()
    for module in ('Paragraph', 'IndexedParagraph', 'Spacer', 'NonEmptyTableWithHeader', 'bold', 'italic'):
      vars_[module] = getattr(self.doc.tygra, module)
    
    story += [IndexedParagraph('Summary', 'Heading2')]
    #-------------------------------------------------
    # driven distance and duration
    if (self.optdep['dur_vs_roadtype'] in self.passed_optdep and 
        self.optdep['dist_vs_roadtype'] in self.passed_optdep):
      roadt_dur = index_fill(self.modules.fill(self.optdep['dur_vs_roadtype']))
      roadt_dist = index_fill(self.modules.fill(self.optdep['dist_vs_roadtype']))
      
      # distance
      if roadt_dist.total > 0.0:
        calc_dist_perc = lambda d: int(round2(d/roadt_dist.total*100.0, 5.0))
        story += [Paragraph(
          'Total mileage: %s (ca. %d%% city, %d%% rural, %d%% highway)'%
          (bold('%.1f km' % roadt_dist.total),
           calc_dist_perc(roadt_dist['city']),
           calc_dist_perc(roadt_dist['rural']),
           calc_dist_perc(roadt_dist['highway']))),]
      else:
        story += [Paragraph('Total mileage: %s' % bold('%.1f km' % roadt_dist.total))]
      # duration
      if roadt_dur.total > 0.0:
        calc_dist_perc = lambda d: int(round2(d/roadt_dur.total*100.0, 5.0))
        story += [Paragraph(
          'Total duration: %s (ca. %d%% standstill, %d%% city, %d%% rural, %d%% highway)'%
          (bold('%.1f hours' % roadt_dur.total),
           calc_dist_perc(roadt_dur['ego stopped']),
           calc_dist_perc(roadt_dur['city']),
           calc_dist_perc(roadt_dur['rural']),
           calc_dist_perc(roadt_dur['highway']))),]
      else:
        story += [Paragraph('Total duration: %s' % bold('%.1f hours' % roadt_dur.total))]
    else:
      self.logger.warning('Road type statistics not available')
      story += [Paragraph('Total duration: n/a'),
                Paragraph('Total mileage: n/a'),]
    # engine running
    if self.optdep['dur_vs_engine_onoff'] in self.passed_optdep:
      engine_dur = index_fill(self.modules.fill(self.optdep['dur_vs_engine_onoff']))
      if 'roadt_dur' in locals():
        # plau check for durations of different sources
        if roadt_dur.total > 0.25 and abs(1.0 - engine_dur.total/roadt_dur.total) > 0.02:  # 2% tolerance
          self.logger.error("Different duration results: %.1f h (engine state) "
          "vs. %.1f h (road type)" % (engine_dur.total, roadt_dur.total))
      # duration
      if engine_dur.total > 0.0:
        story += [Paragraph(
          'Total duration: %.1f hours (%.1f%% engine running, %.1f%% engine off)'%
          (engine_dur.total, 100.0 * engine_dur['yes']/engine_dur.total, 100.0 * engine_dur['no']/engine_dur.total)),]
      else:
        story += [Paragraph('Total duration: %.1f hours' % engine_dur.total)]
    else:
      self.logger.warning('Engine state statistics not available')
      story += [Paragraph('Total duration: n/a'),]
    # daytime
    if self.optdep['dur_vs_daytime'] in self.passed_optdep:
      daytime_dur = index_fill(self.modules.fill(self.optdep['dur_vs_daytime']))
      if 'roadt_dur' in locals():
        # plau check for durations of different sources
        if roadt_dur.total > 0.25 and abs(1.0 - daytime_dur.total/roadt_dur.total) > 0.02:  # 2% tolerance
          self.logger.error("Different duration results: %.1f h (daytime) "
          "vs. %.1f h (road type)" % (daytime_dur.total, roadt_dur.total))
      # duration
      if daytime_dur.total > 0.0:
        calc_dist_perc = lambda d: int(round2(d/daytime_dur.total*100.0, 5.0))
        story += [Paragraph(
          'Total duration: %.1f hours (ca. %d%% day, %d%% night, %d%% dusk)'%
          (daytime_dur.total,
           calc_dist_perc(daytime_dur['day']),
           calc_dist_perc(daytime_dur['night']),
           calc_dist_perc(daytime_dur['dusk']))),]
      else:
        story += [Paragraph('Total duration: %.1f hours' % daytime_dur.total)]
    else:
      self.logger.warning('Daytime statistics not available')
      story += [Paragraph('Total duration: n/a'),]
    # common remark
    story += [Paragraph(italic('Remark: Percentage values with "ca." are '
                               'rounded to nearest 5.'), fontsize=8),
              Spacer(width=1*cm, height=0.2*cm),]
    
    # in-lane obstacle detected
    if (self.optdep['dur_vs_inlane_tr0'] in self.passed_optdep and
        self.optdep['dur_vs_inlane_tr0_fused'] in self.passed_optdep and
        self.optdep['dist_vs_inlane_tr0'] in self.passed_optdep and
        self.optdep['dist_vs_inlane_tr0_fused'] in self.passed_optdep and
        'roadt_dur' in locals() and 'roadt_dist' in locals()):
      if roadt_dur.total > 0.0 and roadt_dist.total > 0.0:
        inlane_dur = index_fill(self.modules.fill(self.optdep['dur_vs_inlane_tr0']))
        inlane_fused_dur = index_fill(self.modules.fill(self.optdep['dur_vs_inlane_tr0_fused']))
        inlane_dist = index_fill(self.modules.fill(self.optdep['dist_vs_inlane_tr0']))
        inlane_fused_dist = index_fill(self.modules.fill(self.optdep['dist_vs_inlane_tr0_fused']))
        inlane_dur_perc = inlane_dur.total / roadt_dur.total * 100.0
        inlane_fused_dur_perc = inlane_fused_dur.total / roadt_dur.total * 100.0
        inlane_dist_perc = inlane_dist.total / roadt_dist.total * 100.0
        inlane_fused_dist_perc = inlane_fused_dist.total / roadt_dist.total * 100.0
        story += [Paragraph('In-lane obstacle presence: %.0f%% / %.0f%% (duration / mileage)' % (inlane_dur_perc, inlane_dist_perc)),
                  Paragraph('Fused in-lane obstacle presence: %.0f%% / %.0f%% (duration / mileage)' % (inlane_fused_dur_perc, inlane_fused_dist_perc)),
                  Spacer(width=1*cm, height=0.2*cm),]
      else:
        story += [Paragraph('In-lane obstacle presence: n/a'),
                  Paragraph('Fused in-lane obstacle presence: n/a'),
                  Spacer(width=1*cm, height=0.2*cm),]
    else:
      self.logger.warning('In-lane obstacle presence not available')
      story += [Paragraph('In-lane obstacle presence: n/a'),
                Paragraph('Fused in-lane obstacle presence: n/a'),
                Spacer(width=1*cm, height=0.2*cm),]
    
    # system performance - AEBS state
    if self.optdep['dur_vs_aebsstate'] in self.passed_optdep:
      aebss_dur = index_fill(self.modules.fill(self.optdep['dur_vs_aebsstate']))

      if 'roadt_dur' in locals():
        # plau check for durations of different sources
        if roadt_dur.total > 0.25 and abs(1.0 - aebss_dur.total/roadt_dur.total) > 0.02:  # 2% tolerance
          self.logger.error("Different duration results: %.1f h (AEBS state) "
            "vs. %.1f h (road type)" % (aebss_dur.total, roadt_dur.total))

      if aebss_dur.total > 0.0:
        calc_aebss_perc = lambda d: d/aebss_dur.total*100.0
        tempna = calc_aebss_perc(aebss_dur['Temporary n/a'])
        ready = calc_aebss_perc(aebss_dur['Ready'])
        override = calc_aebss_perc(aebss_dur['Driver override'])
        warning = calc_aebss_perc(aebss_dur['Collision warning active'])
        partial = calc_aebss_perc(aebss_dur['Collision warning with braking'])
        emer = calc_aebss_perc(aebss_dur['Emergency brake active'])
        op = tempna + ready + override + warning + partial + emer
        error = calc_aebss_perc(aebss_dur['Error'])
        notavl = calc_aebss_perc(aebss_dur['Not available'])
        notrdy = calc_aebss_perc(aebss_dur['Not ready'])
        deact = calc_aebss_perc(aebss_dur['Deactivated by driver'])
        story += [Paragraph('AEBS state: %.1f%% operational '
          '(%.1f%% temp. n/a., %.1f%% ready, %.1f%% override, '
          '%.1f%% warning, %.1f%% partial brk., %.1f%% emer. brk.), '
          '%.1f%% deactivated, %.1f%% error, %.1f%% n/a, %.1f%% not ready' % 
          (op, tempna, ready, override, warning, partial, emer,
           deact, error, notavl, notrdy))]
      else:
        story += [Paragraph('AEBS state: n/a')]
    else:
      self.logger.warning('AEBS state not available')
      story += [Paragraph('AEBS state: n/a')]

    story += [Spacer(width=1*cm, height=0.2*cm),]

    story += [IndexedParagraph('Wabco AEBS warnings', 'Heading2')]
    #-------------------------------------------------------------
    if self.optdep['aebs_events'] in self.passed_optdep:
      header = cIntervalHeader.fromFileName(abspath('../../aebseval/events_inttable.sql'))
      ids = index_fill(self.modules.fill(self.optdep['aebs_events']))
      table = self.batch.get_table(header, ids, sortby=[('measurement', True), ('start [s]', True)])
      table_chunk = [row[1:-1] for row in table]
      story += [NonEmptyTableWithHeader(table_chunk),
                Spacer(width=1*cm, height=0.2*cm),]
      meas_events = Events(table, self.doc.tygra, self.docname)
      meas_events(self._manager, story)
    else:
      self.logger.warning('Wabco AEBS warnings not available')
      story += [Paragraph('Information not available'),
                Spacer(width=1*cm, height=0.2*cm),]

    return story

  def analyze(self, story):
    self.doc.multiBuild(story, f=self.docname)  # TODO: rm self.docname if possible
    return


class Events(dict):
  modules = OrderedDict([
    ('view_videonav_lanes-NO_LANES@evaltools', ['VideoNavigator']),
  ])
  statuses = ['fillFLC20@aebs.fill',
              'fillFLR20@aebs.fill', 'fillFLR20_AEB@aebs.fill',
              'fillFLR20_AEBS_Warning-flr20@aebs.fill',]
  visibles = ['FLR20_ACC', 'FLR20_AEB', 'FLR20_FUS', 'FLR20', 'FLR20_FUSED',
              'FLC20', 'FLR20_RADAR_ONLY', 'FLR20_AEBS_Warning-FLR20',
              'moving', 'stationary']
  show_nav = False
  def __init__(self, table, tygra, docname=None):
    dict.__init__(self)
    self.init(table, tygra, docname)
    return

  def init(self, table, tygra, docname=None):
    head = table[0]
    for row in table[1:]:
      event = Event(zip(head, row))
      event['start'] = event['start [s]']  # hack for later access of 'start'
      event['ego speed'] = event.get('ego speed [km/h]', event.get('ego speed start [kph]'))  # hack for later access of 'ego speed'
      meas = event['fullmeas']
      start = event['start']
      self.setdefault(meas, {})[start] = event
    self.tygra = tygra
    self.docname = docname
    return

  def __call__(self, master_manager, story):
    # dynamic import
    Paragraph = self.tygra.Paragraph
    Image = self.tygra.Image
    
    for meas in sorted(self):
      events = self[meas]
      manager = master_manager.clone()
      manager.set_measurement(meas)
      manager.build(self.modules, self.statuses, self.visibles, self.show_nav)
      sync = manager.get_sync()
      prev_start = float("-inf")
      for start in sorted(events):
        manager.set_roi(start, start+events[start]['duration [s]'],
          color='y', pre_offset=5.0, post_offset=5.0)
        event = events[start]
        see_prev_event = start - prev_start < 10.0
        standstill = event['ego speed'] < 1.0
        story += [Paragraph(event.get_title(), 'Heading3')]
        if standstill:
          story += [Paragraph("Event occurred during standstill")]
        elif see_prev_event:
          story += [Paragraph("See previous event")]
        else:
          # create snapshots
          sync.seek(start)
          for module, clients in self.modules.iteritems():
            for client_name in clients:
              try:
                client = sync.getClient(module, client_name)
              except ValueError:
                story += [Paragraph("Image not available")]
              else:
                filename = self.get_picname(event.get_picname(module, client_name))
                client.copyContentToFile(filename)
                story += [Image(os.path.basename(filename))]
        prev_start = start
      manager.close()
    return

  def get_picname(self, picname_base):
    if self.docname is not None:
      filename = "%s_%s" % (os.path.splitext(self.docname)[0], picname_base)
    else:
      filename = picname_base
    return filename


class Event(dict):
  PIC = '%(module)s_%(client)s_%(measurement)s_%(start).2f.png'
  def get_picname(self, module, client):
    self['module'] = module
    self['client'] = client
    return self.PIC % self

  TITLE = '%(measurement)s @ %(start).2f sec'
  def get_title(self):
    return self.TITLE % self
