import os

from reportlab.lib.pagesizes import cm, A4
from reportlab.platypus.doctemplate import NextPageTemplate, FrameBreak
from reportlab.platypus.flowables import Image, PageBreak, Spacer

from interface import iAnalyze
from datalab.tygra import IndexedParagraph, Paragraph
from reportgen.common.pagetemplates import addPageTemplates
from reportgen.common.clients import Client

PIC_DIR = os.path.join(os.path.dirname(__file__), 'images')

class Analyze(iAnalyze):
  warningtemplate = 'Landscape'
  def init(self):
    self.view_name = ''
    self.EVENT_LINK = '%s @ %.2f sec'
    return

  def fill(self):
    story = []
    return story

  def analyze(self, story):
    doc = self.get_doc('dataeval.simple', pagesize=A4, header="Strictly confidential")
    try:
      event_detail_pagesize = story[03].text.split(': ')[1].split('<')[0]
      if event_detail_pagesize == 'A3' or event_detail_pagesize == 'A3-TSR':
        addPageTemplates(doc, event_detail_pagesize)
    except:
      addPageTemplates(doc)
    doc.multiBuild(story)
    return

  def explanation(self):
    story = [IndexedParagraph('Data interpretation', style='Heading1')]
    
    story += [IndexedParagraph('Statistical results', style='Heading2')]
    ptext = """The statistical values are valid in the indicated
      time period.<br/>
      The ratios are representing the distribution over time, unless
      explicitly stated otherwise."""
    story += [Paragraph(ptext)]
    
    story += [IndexedParagraph('AEBS event classification', style='Heading2')]
    ptext = """Besides the automatic measurement evaluation, all AEBS events
      are reviewed and rated manually.<br/>
      The two most important aspects are the severity and root cause."""
    story += [Paragraph(ptext)]
    story += [IndexedParagraph('AEBS event severities', style='Heading3')]
    ptext = """Five pre-defined severity classes are used:<br/>
      <br/>
      <b>1 - False alarm</b><br/>
      Driver has no idea, what the warning was given for, e.g. bridge,
      ghost objects etc.<br/>
      <br/>
      <b>2 - Questionable false alarm</b><br/>
      Very unlikely to become a dangerous situation, but real obstacle is
      present, e.g. parking car, low speed situations.<br/>
      <br/>
      <b>3 - Questionable</b><br/>
      50% of the drivers would find the warning helpful, 50% would not.<br/>
      Driver keeps speed, only soft reaction, e.g. sharp turn, braking car.<br/>
      <br/>
      <b>4 - Questionable justified alarm</b><br/>
      Warning supposed to be helpful for the driver.<br/>
      Driver action was needed (pedal activation, steering), e.g. sharp turn,
      braking car.<br/>
      <br/>
      <b>5 - Justified alarm</b><br/>
      Driver has to make emergency maneuver (evasive steering or emergency
      braking) to avoid a collision; it is obvious that a crash was likely.<br/>
      """
    story += [Paragraph(ptext)]
    story += [IndexedParagraph('AEBS event causes', style='Heading3')]
    ptext = """Four main pre-defined causes are used:<br/>
      <br/>
      <b>Ghost object</b><br/>
      AEBS reacts on a non-existing object due to e.g. improper radar
      reflection.<br/>
      Collision is not possible.<br/>
      <br/>
      <b>Surroundings</b><br/>
      AEBS reacts on an existing but out-of-plane object, e.g. bridge,
      manhole.<br/>
      Collision is not possible.<br/>
      <br/>
      <b>Infrastructure</b><br/>
      AEBS reacts on a real in-plane obstacle, that is, however, not actively
      taking part in the traffic itself. Examples are traffic island, parking
      vehicle, guardrail etc.<br/>
      Collision is possible.<br/>
      <br/>
      <b>Traffic situation</b><br/>
      AEBS reacts on a real traffic situation, e.g. braking forward vehicle,
      cut-in, granny turn etc.<br/>
      Collision is possible.<br/>
      """
    story += [Paragraph(ptext)]
    
    story += [PageBreak()]
    
    story += [IndexedParagraph('Coordinate frames', style='Heading2')]
    ptext = """All values in this document are referenced to the conventional
      land vehicle frame, having its origin in the middle of the front bumper.
      The x axis is pointing forward, while the y axis is pointing to the left.
      The remaining directions fulfill the right-hand rule."""
    fig = Image(os.path.join(PIC_DIR, 'coordinate_frame.png'),
                width=12.0*cm, height=3.54*cm)
    story += [Paragraph(ptext), Spacer(0, 0.5*cm), fig, NextPageTemplate('LandscapeTable'),]
    
    story += [PageBreak()]
    return story

  def summaries(self, summaries, module_name=None):
    story = [
      IndexedParagraph('Warning summary tables', style='Heading1'),
      NextPageTemplate('LandscapeTable'),
    ]
    if module_name is not None:
      story.insert(1, self.module_plot(module_name))
      story.append(PageBreak())
    for summary in summaries:
      story.append(IndexedParagraph(summary.title, style='Heading2'))
      story.append(summary.get_table(link_pattern=self.EVENT_LINK,
                                     link_heading='Heading2')),
      story.append(PageBreak())
    return story

  def module_plot(self, module_name, client_name='MatplotlibNavigator',
                  windgeom='640x733+0+0', width=None, height=None,
                  unit=cm, kind='direct',
                  overwrite_start_end=False, start_date=None, end_date=None):
    if start_date is not None or end_date is not None:
      assert overwrite_start_end, \
        "start_date and/or end_date provided but overwrite_start_end is False"
    manager = self.clone_manager()
    manager.strong_time_check = False  # TODO: make default behavior with warning
    if overwrite_start_end:
      manager.start_date = start_date
      manager.end_date = end_date
    manager.set_batch(self.batch.clone())
    manager.build([module_name], show_navigators=False)
    client = Client(client_name, windgeom, width, height, unit, kind)
    image = client(manager.sync, module_name)
    manager.close()
    return image

  def warnings(self, summaries):
    story = []
    for summary in summaries:
      story.append(IndexedParagraph(summary.title, style='Heading1'))
      story.extend(self.events(summary))
      story.append(NextPageTemplate('LandscapeTable'))
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
      manager.strong_time_check = False  # TODO: make default behavior with warning
      manager.set_measurement(meas)
      manager.build(summary.modules, status_names=statuses,
                    visible_group_names=groups, show_navigators=False)
      sync = manager.get_sync()
      for warning in warnings:
        title = self.EVENT_LINK % (os.path.basename(meas), warning['start'])
        story.extend([
          NextPageTemplate(self.warningtemplate),
          PageBreak(),
          IndexedParagraph(title, style='Heading2'),
          FrameBreak(),
          Paragraph(summary.explanation % warning, style='Normal'),
        ])
        sync.seek(warning['start'])
        manager.set_roi(warning['start'], warning['end'], color='y',
                        pre_offset=5.0, post_offset=5.0)
        for module_name, client in summary.modules.iteritems():
          story.append( client(sync, module_name) )
          story.append( FrameBreak() )
        if summary.modules: story.pop(-1)  # remove last FrameBreak
      manager.close()
    return story
