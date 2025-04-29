import os

from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.pagesizes import A4, cm
from datalab.reportlab import tygra


class DocTemplate(BaseDocTemplate):
  FOOTER = u"\N{Copyright Sign} " \
    "Knorr-Bremse SfN GmbH reserves all rights even in the event of " \
    "industrial property. We reserve all rights of disposal such as " \
    "copying and passing on to third parties."
  HEADER = "Strictly confidential"
  LOGO = os.path.join(os.path.dirname(__file__), '..', 'pics', 'Knorr_logo.png')

  tygra = tygra

  @classmethod
  def set_logo(cls, name):
    cls.LOGO = os.path.join(os.path.dirname(__file__), '..', 'pics', name)
    return


class StoryBuilder(object):
  def __init__(self):
    self.story = []

  def add(self, element):
    if isinstance(element, StoryBuilder):
      element = element.story
    if not isinstance(element, (tuple, set, list)):
      element = [element]
    for e in element:
      if isinstance(e, (tuple, list, set)):
        self.add(e)
      else:
        self.story += [e]

  def __add__(self, other):
    self.add(other)
    return self


class SimpleDocTemplate(DocTemplate):
  def __init__(self, filename, **kwargs):
    """
    :Keywords:
      toclevels : int
        Number of levels to be included in the table of contents. Default is 2.
      * : *
        reportlab.platypus.doctemplate.BaseDocTemplate keywords.
    """
    self.toclevels = kwargs.pop('toclevels', 2)
    BaseDocTemplate.__init__(self, filename, **kwargs)
    # define frame and page template
    x, y, width, height = self.getGeom()
    xExt, yExt, widthExt, heightExt = self.getExtGeom()
    contentFrame = Frame(xExt, y, widthExt, height, id='Content')
    simplePageTemplate = PageTemplate(id='SimplePage', frames=contentFrame,
                                      onPage=self.onPortraitPage, pagesize=A4)
    self.addPageTemplates([simplePageTemplate])
    return

  def multiBuild(self, story, maxPasses = 10, *args, **buildKwds):
      # pop docxlab kwargs
      buildKwds.pop("f_template", None)
      BaseDocTemplate.multiBuild(self, story, maxPasses, **buildKwds)

  def getGeom(self):
    return self.leftMargin, self.bottomMargin, self.width, self.height

  def getExtGeom(self):
    offset = 58

    x = self.leftMargin - offset
    y = self.bottomMargin - offset
    width = self.width + 2*offset
    height = self.height + 2*offset
    return x, y, width, height

  def getAppGeom(self):
    x = self.leftMargin  - 58
    y = self.bottomMargin - 55
    width = self.width + 2*58
    height = self.height + 90
    return x, y, width, height

  def afterFlowable(self, flowable):
    """
    Registers TOC entries with clickable links.
    (source: http://www.reportlab.com/snippets/13/)
    """
    if flowable.__class__.__name__ == 'Paragraph':
      # exclude non-indexed paragraphs
      if not hasattr(flowable, '_bookmarkName'):
        return
      # find the toc level N of the paragraph "HeadingN"
      style = flowable.style.name
      splits = style.split('Heading')
      if len(splits) != 2 and splits[0] != '':
        return
      level = int(splits[1]) - 1
      # exclude too deep entries
      if level+1 > self.toclevels:
        return
      # add entry to the toc
      text = flowable.getPlainText()
      E = [level, text, self.page]
      # if we have a bookmark name append that to our notify data
      bn = getattr(flowable, '_bookmarkName', None)
      if bn is not None:
        E.append(bn)
      self.notify('TOCEntry', tuple(E))
    return

  @classmethod
  def onPortraitPage(cls, canvas, self):
    """Sets the page geometry, header and footer."""
    canvas.saveState()
    x, y, width, height = self.getExtGeom()
    # header
    canvas.drawImage(cls.LOGO, x, y+height, width=6*cm, height=-1.23*cm)
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(x+width, y+height, cls.HEADER)
    # footer
    canvas.setFont('Helvetica', 5)
    canvas.drawString(x, y, cls.FOOTER)
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(x+width, y, "%d" % self.page)
    ###
    #canvas.restoreState()
    return

  @classmethod
  def onLandscapePage(cls, canvas, self):
    canvas.saveState()
    x, y, width, height = self.getExtGeom()
    # header
    canvas.drawImage(cls.LOGO, x, width, width=6*cm, height=-1.23*cm)
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(x+height, y+width, cls.HEADER)
    # footer
    canvas.setFont('Helvetica', 5)
    canvas.drawString(x, y, cls.FOOTER)
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(x+height, y, '%d' % (self.page))
    return

