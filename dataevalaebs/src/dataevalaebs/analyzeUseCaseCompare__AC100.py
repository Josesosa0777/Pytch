import os
import sys
import hashlib

import reportlab.lib
import reportlab.platypus as plat
import reportlab.platypus.tableofcontents
import numpy
import matplotlib.pyplot as plt

from measparser.signalgroup import SignalGroupError
import interface

# constants needed for document generation -------------------------------------
PYTHONEXE  = sys.executable if sys.executable else "python"
CONFIGFILEDIR = os.path.join(os.path.dirname(__file__), "cfg")
TMPCONFIGFILE = os.path.join(CONFIGFILEDIR, "view_backup.cfg")
IMAGEDIR = os.path.join(os.path.dirname(__file__), "images")

DEFAULT_TABLE_STYLE = [('BACKGROUND', (0,0), (-1,-1), reportlab.lib.colors.white),
                       ('TEXTCOLOR',  (0,0), (-1,-1), reportlab.lib.colors.black),
                       ('GRID',       (0,0), (-1,-1), 1, reportlab.lib.colors.black),
                       ('VALIGN',     (0,0), (-1,-1), "MIDDLE")]

# document template class ------------------------------------------------------
class MyDocTemplate(plat.BaseDocTemplate):
  def __init__(self, filename, **kw):
    self.allowSplitting = 0
    plat.BaseDocTemplate.__init__(self, filename, **kw)
    return

  def afterFlowable(self, flowable):
    "Registers TOC entries with clickable links."
    # Source: http://www.reportlab.com/snippets/13/
    if flowable.__class__.__name__ == 'Paragraph':
      text = flowable.getPlainText()
      if text.lower() == 'table of contents':
        return
      style = flowable.style.name
      if style == 'Heading1':
        level = 0
      elif style == 'Heading2':
        level = 1
      else:
        return
      E = [level, text, self.page]
      # if we have a bookmark name append that to our notify data
      bn = getattr(flowable, '_bookmarkName', None)
      if bn is not None:
        E.append(bn)
      self.notify('TOCEntry', tuple(E))
    return

# function for adding headers --------------------------------------------------
def addHeadingToPDF(story, text, sty):
  # generate bookmarkname
  bn = hashlib.sha1(text+sty.name).hexdigest()
  # modify paragraph text to include an anchor point with name bn
  h = plat.Paragraph(text+'<a name="%s"/>' % bn, sty)
  # store the bookmark name on the flowable so afterFlowable can see this
  h._bookmarkName = bn
  story.append(h)
  return

def createPDF(fileName, CaptureDir, measNamesWithApprNum):
  doc = MyDocTemplate(fileName, defaultpagesize=reportlab.lib.pagesizes.A4, showBoundary=0)

  x = doc.leftMargin
  y = doc.bottomMargin
  w = doc.width
  h = doc.height

  x_mod = x - 58
  y_mod = y - 58
  w_mod = w + 116
  h_mod = h + 116

  frameP0 = plat.Frame(x_mod, y, w_mod, h, id='portrait0')  # original portrait frame incorporating the whole page

  cm = reportlab.lib.pagesizes.cm

  # draw header and footer -----------------------------------------------------
  def pageSetup_Porttrait(canvas, doc):
    canvas.saveState()
    # header
    canvas.drawImage(os.path.join(IMAGEDIR, "Knorr_logo.png"), x_mod, y_mod+h_mod, width=6*cm, height=-1.23*cm)
    headertext = 'Strictly confidential'
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(x_mod+w_mod, y_mod+h_mod, headertext)
    # footer
    footertext = u'\N{Copyright Sign} Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial property. We reserve all rights of disposal such as copying and passing on to third parties.'
    canvas.setFont('Helvetica', 5)
    canvas.drawString(x_mod, y_mod, footertext)
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(x_mod+w_mod, y_mod, '%d' % (doc.page))

  def pageSetup_Landscape(canvas, doc):
    canvas.saveState()
    # header
    canvas.drawImage(os.path.join(IMAGEDIR, "Knorr_logo.png"), x_mod, w_mod, width=6*cm, height=-1.23*cm)
    headertext = 'Strictly confidential'
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(x_mod+h_mod, y_mod+w_mod, headertext)
    # footer
    footertext = u'\N{Copyright Sign} Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial property. We reserve all rights of disposal such as copying and passing on to third parties.'
    canvas.setFont('Helvetica', 5)
    canvas.drawString(x_mod, y_mod, footertext)
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(x_mod+h_mod, y_mod, '%d' % (doc.page))

  doc.addPageTemplates([plat.PageTemplate(id='Portrait', frames=frameP0, onPage=pageSetup_Porttrait, pagesize=reportlab.lib.pagesizes.A4)])

  # container for the 'Flowable' objects
  elements = []

  styles=reportlab.lib.styles.getSampleStyleSheet()

  ptext="Use Case Benchmark Of AC100"
  elements.append(plat.Paragraph(ptext, styles["Title"]))

  # Add scope ------------------------------------------------------------------
  addHeadingToPDF(elements, "<seq id='section'/>. Scope", styles["Heading1"])
  ptext = ("This document shows the results of use case benchmark of AC100. "
           "These figures show the change of dx distance from the obstacle during an approach. "
           "The distances of first detection and stable detection are labeled on the plots.")
  elements.append(plat.Paragraph(ptext, styles["Normal"]))
  elements.append(plat.Spacer(w, 1*cm))

  # Add summary ----------------------------------------------------------------
  addHeadingToPDF(elements, "<seq id='section'/>. Summary", styles["Heading1"])
  ptext = ("The figure below shows the possible speed reduction for each use case run. "
           "The red dots represent AC100. "
           "The upper horizontal line stands for step 2 (speed reduction of 20 km/h) and "
           "the lower stands for step 1 (speed reduction of 10 km/h).")
  elements.append(plat.Paragraph(ptext, styles["Normal"]))
  elements.append(plat.Spacer(w, 0.2*cm))
  picPath = os.path.join(CaptureDir, 'SpeedReduc.png')
  im=plat.Image(picPath, width=15*cm, height=11.25*cm)
  im.hAlign="CENTER"
  elements.append(im)
  ptext = ("The figures below show the stable detection (when object was considered as an obstacle) "
           "distance vs. approach scatter plot and histogram respectively.")
  elements.append(plat.Paragraph(ptext, styles["Normal"]))
  elements.append(plat.Spacer(w, 0.2*cm))
  picPath = os.path.join(CaptureDir, 'StableDet.png')
  im=plat.Image(picPath, width=15*cm, height=11.25*cm)
  im.hAlign="CENTER"
  elements.append(im)
  elements.append(plat.Spacer(w, 0.2*cm))
  picPath = os.path.join(CaptureDir, 'StableDetHistogram.png')
  im=plat.Image(picPath, width=15*cm, height=11.25*cm)
  im.hAlign="CENTER"
  elements.append(im)
  elements.append(plat.PageBreak())

  # add table of contents ------------------------------------------------------
  addHeadingToPDF(elements, "Table Of Contents", styles["Heading1"])
  toc = plat.tableofcontents.TableOfContents()
  elements.append(toc)
  elements.append(plat.PageBreak())

  # Add comparison plots for each obstacle approach ----------------------------
  for measFile in sorted(measNamesWithApprNum.keys()):
    for apprNum in sorted(measNamesWithApprNum[measFile]):
      addHeadingToPDF(elements, "<seq id='section'/>. Detection distances at approach %d in %s" % (apprNum+1, measFile), styles["Heading1"])
      elements.append(plat.Spacer(w, 0.2*cm))
      picPath = os.path.join(CaptureDir, '%s=%s.png' % (measFile, apprNum))
      if os.path.exists(picPath):
        im=plat.Image(picPath, width=15*cm, height=20*cm)
        im.hAlign="CENTER"
        elements.append(im)
      else:
        elements.append(plat.Paragraph("CW object detection interval not found.", styles["Normal"]))
      elements.append(plat.PageBreak())

  doc.multiBuild(elements)
  return

DefParam = interface.NullParam

class cAnalyze(interface.iAnalyze):
  def check(self):
    batch = self.get_batch()
    start = batch.get_last_entry_start()
    workspaceGroups = \
    batch.filter(start=start, type='measproc.FileWorkSpace',
                 class_name='dataevalaebs.searchUseCaseCompare__AC100.cSearch')
    if not workspaceGroups:
      SignalGroupError("No usable data work space group found! Document cannot be created!")
    return workspaceGroups

  def fill(self, workspaceGroups):
    return workspaceGroups

  def analyze(self, param, workspaceGroups):
    batch = self.get_batch()
    CaptureDir = os.path.join(batch.dirname, 'pics4doc')

    # process workspace groups -------------------------------------------------
    useCaseEvalData = {}
    for entry in workspaceGroups:
      measName = batch.get_entry_attr(entry, "measurement")
      repTitle = batch.get_entry_attr(entry, "title")
      apprNum = repTitle.split('-')[-1]
      measDict = useCaseEvalData.setdefault(measName, {})
      apprDict = measDict.setdefault(int(apprNum), {})
      workspace = batch.wake_entry(entry)
      useCaseEvalDataWS = workspace.workspace
      for key in useCaseEvalDataWS.keys():
        if key in ('__header__', '__globals__', '__version__'):
          continue
        data, sensor = key.split('_')
        sensorDict = apprDict.setdefault(sensor, {})
        sensorDict[data] = useCaseEvalDataWS[key].flatten()

    # create plots -------------------------------------------------------------
    if not os.path.exists(CaptureDir): # check if a save directory exists
      os.makedirs(CaptureDir) # if it doesn't create one

    measNamesWithApprNum = {}
    speedReducData = {'runNo': [], 'speedReduc': {'AC100': []}}
    stableDetData = {'runNo': [], 'dxStableDet': {'AC100': []}}
    apprCnt = 0
    for meas in sorted(useCaseEvalData.keys()):
      apprNum4Meas = measNamesWithApprNum.setdefault(meas, [])
      for apprNum in useCaseEvalData[meas].keys():
        # save approach ID number ----------------------------------------------
        apprNum4Meas.append(apprNum)

        timeAC100 = list(useCaseEvalData[meas][apprNum]['AC100']['timeFull'])
        dxAC100 = list(useCaseEvalData[meas][apprNum]['AC100']['dxFull'])
        if len(timeAC100) != 0 and len(dxAC100) != 0:
          # create approach plots for each approach ------------------------------
          plotFigure1 = plt.figure(figsize=(13, 19), dpi=80)
          plotFigure1.subplots_adjust(hspace=0.8, top=0.98, bottom=0.02, left=0.07, right=0.7) # all parameters are fraction of the figure width or height

          subplt1 = plotFigure1.add_subplot(4, 1, 1)
          subplt1.set_title('Ego-vehicle speed', position=(0.5,1.0))
          subplt1.set_ylabel('v [kph]')

          subplt2 = plotFigure1.add_subplot(4, 1, 2, sharex=subplt1)
          subplt2.set_title('Detection distance', position=(0.5,1.0))
          subplt2.set_ylabel('dx [m]')

          subplt3 = plotFigure1.add_subplot(4, 1, 3, sharex=subplt1)
          subplt3.set_title('Object classified as obstacle (AC100)', position=(0.5,1.0))
          subplt3.set_ylim(ymax=1.1)
          subplt3.set_ylabel('flag')

          subplt4 = plotFigure1.add_subplot(4, 1, 4, sharex=subplt1)
          subplt4.set_title('Reflected power (AC100)', position=(0.5,1.0))
          subplt4.set_ylabel('power [dB]')

          vEgo = list(useCaseEvalData[meas][apprNum]['AC100']['egoVel'])
          subplt1.plot(timeAC100, vEgo)

          power = list(useCaseEvalData[meas][apprNum]['AC100']['powerFull'])
          subplt4.plot(timeAC100, power)

          d1AC100 = useCaseEvalData[meas][apprNum]['AC100']['dxFirstDet'][0] if len(useCaseEvalData[meas][apprNum]['AC100']['dxFirstDet']) != 0 else 0
          d2AC100 = useCaseEvalData[meas][apprNum]['AC100']['dxObsDet'][0] if len(useCaseEvalData[meas][apprNum]['AC100']['dxObsDet']) != 0 else 0

          cwAC100 = list(useCaseEvalData[meas][apprNum]['AC100']['objIsCW'])

          subplt3.plot(timeAC100, cwAC100, 'r')

          try:
            t1IndexAC100 = dxAC100.index(d1AC100)
            t2IndexAC100 = dxAC100.index(d2AC100)
          except ValueError:  # TODO: avoid the possibility of having ValueError
            print 'Ooops... The script could not find the event properly for %s, approach nr. %d' % (meas, apprNum)
          else:
            subplt2.plot(timeAC100, dxAC100, 'r', label='AC100')
            subplt2.plot(timeAC100[t1IndexAC100], d1AC100, 'ro', label='First detection (AC100): %.2f [m]' % d1AC100)
            subplt2.plot(timeAC100[t2IndexAC100], d2AC100, 'rd', label='Stable detection (AC100): %.2f [m]' % d2AC100)
            handles, labels = subplt2.get_legend_handles_labels()
            subplt3.plot(timeAC100[t2IndexAC100], cwAC100[t2IndexAC100], 'rd')
            plt.figlegend(handles, labels, loc='upper right', ncol=1, numpoints=1, borderaxespad=0.1, prop={'size': 11})

          plt.savefig(os.path.join(CaptureDir, '%s=%d.png' %(meas, apprNum)))

        apprCnt += 1
        # determine data for speed reduction plot ------------------------------
        speedReducData['runNo'].append(apprCnt)
        speedReducData['speedReduc']['AC100'].append(useCaseEvalData[meas][apprNum]['AC100']['speedReduc'][0] if len(useCaseEvalData[meas][apprNum]['AC100']['speedReduc']) != 0 else 0)

        # determine data for stable detection plots ----------------------------
        stableDetData['runNo'].append(apprCnt)
        stableDetData['dxStableDet']['AC100'].append(useCaseEvalData[meas][apprNum]['AC100']['dxObsDet'][0] if len(useCaseEvalData[meas][apprNum]['AC100']['dxObsDet']) != 0 else 0)

    # create speed reduction plot ----------------------------------------------
    plotFigure2 = plt.figure()
    plotFigure2.suptitle('Possible speed reduction during approaches')
    subplt = plotFigure2.add_subplot(1, 1, 1)
    subplt.set_xlabel('No. of use case runs [-]')
    subplt.set_ylabel('Possible speed reduction [km/h]')
    speedReducDataAC100 = numpy.array(speedReducData['speedReduc']['AC100']) * 3.6
    subplt.scatter(speedReducData['runNo'], speedReducDataAC100, c='r', marker='^', s=40, label='AC100')
    subplt.axhline(10)
    subplt.axhline(20)
    plt.xlim(xmin=0, xmax=max(speedReducData['runNo'])+1)
    plt.ylim(ymin=-0.5)
    subplt.legend(scatterpoints=1, bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0., prop={'size':12})
    plotFigure2.subplots_adjust(top=0.88)
    plt.savefig(os.path.join(CaptureDir, 'SpeedReduc.png'))

    # create stable dx vs. approach plot ---------------------------------------
    plotFigure3 = plt.figure()
    plotFigure3.suptitle('Stable detection during approaches')
    subplt = plotFigure3.add_subplot(1, 1, 1)
    subplt.set_xlabel('No. of use case runs [-]')
    subplt.set_ylabel('Stable detection distance [m]')
    subplt.scatter(stableDetData['runNo'], stableDetData['dxStableDet']['AC100'], c='r', marker='^', s=40, label='AC100')
    plt.xlim(xmin=0, xmax=max(speedReducData['runNo'])+1)
    plt.ylim(ymin=-0.5)
    subplt.legend(scatterpoints=1, bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0., prop={'size':12})
    plotFigure3.subplots_adjust(top=0.88)
    plt.savefig(os.path.join(CaptureDir, 'StableDet.png'))

    # create stable dx histogram -----------------------------------------------
    plotFigure4 = plt.figure()
    plotFigure4.suptitle('Histogram of stable detections')
    subplt = plotFigure4.add_subplot(1, 1, 1)
    subplt.set_xlabel('Stable detection distance [m]')
    subplt.set_ylabel('No. of occurrence [-]')
    hist, bin_edges, patches = subplt.hist([stableDetData['dxStableDet']['AC100']],
                                           bins=10, histtype='bar', align='mid', color=['red'], label=['AC100'])
    subplt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0., prop={'size':12})
    plotFigure4.subplots_adjust(top=0.88)
    plt.savefig(os.path.join(CaptureDir, 'StableDetHistogram.png'))

    # create pdf document ------------------------------------------------------
    baseName = os.path.splitext(batch.dbname)[0]
    pdfFileName = os.path.extsep.join((baseName, "pdf"))

    createPDF(pdfFileName, CaptureDir, measNamesWithApprNum)
    return
