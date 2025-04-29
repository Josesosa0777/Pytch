import os
import sqlite3
import numpy
import subprocess
import sys
import hashlib
import reportlab.lib
import reportlab.platypus as plat

import interface
import measproc

DefParam = interface.NullParam

PYTHONEXE  = sys.executable if sys.executable else "python"
CONFIGFILEDIR = os.path.join(os.path.dirname(__file__), "cfg")
CONFIGFILE = os.path.join(CONFIGFILEDIR, 'view_cvr3_videonav-acceptfilt.rc')
TMPCONFIGFILE = os.path.join(CONFIGFILEDIR, "view_backup.cfg")
IMAGEDIR = os.path.join(os.path.dirname(__file__), "images")

ADJUSTTIME = lambda num:"%.3f" % (num + .0405)
LOWERLIMSET = lambda num:"%.3f" % (num - 1.0)
UPPERLIMSET = lambda low_num, up_num: "%.3f" % ((up_num + 1.0) + (((up_num + 1.0) - (low_num - 1.0)) / 3))

DEFAULT_TABLE_STYLE = [('BACKGROUND', (0,0), (-1,-1), reportlab.lib.colors.white),
                       ('TEXTCOLOR',  (0,0), (-1,-1), reportlab.lib.colors.black),
                       ('GRID',       (0,0), (-1,-1), 1, reportlab.lib.colors.black),
                       ('VALIGN',     (0,0), (-1,-1), "MIDDLE")]

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

def addHeadingToPDF(story, text, sty):
  # generate bookmarkname
  bn = hashlib.sha1(text+sty.name).hexdigest()
  # modify paragraph text to include an anchor point with name bn
  h = plat.Paragraph(text+'<a name="%s"/>' % bn, sty)
  # store the bookmark name on the flowable so afterFlowable can see this
  h._bookmarkName = bn
  story.append(h)
  return

def createPDF(fileName, captureDirectory, evalData, summaryDataTable):
  doc = MyDocTemplate(fileName, defaultpagesize=reportlab.lib.pagesizes.A4, showBoundary=0)

  x = doc.leftMargin
  y = doc.bottomMargin
  w = doc.width
  h = doc.height

  frameP  = plat.Frame(x              ,   y                ,   w          ,   h           ,   id='Portrait')     # document title and introduction frame
  frameL1 = plat.Frame(y              ,   x + 14. * w / 15.,   h          ,   1. * w / 15.,   id='landscape1')   # page title frame
  frameL2 = plat.Frame(y              ,   x + 13. * w / 15.,   h          ,   1. * w / 15.,   id='landscape2')   # situation description frame
  frameL3 = plat.Frame(y              ,   x                ,   2. * h / 3.,   13. * w / 15.,  id='landscape3')   # plot capture frame
  frameL4 = plat.Frame(y + 2. * h / 3.,   x                ,   1. * h / 3.,   13. * w / 15.,  id='landscape4')   # VideoNavigator capture frame

  cm = reportlab.lib.pagesizes.cm

  # draw header and footer
  def pageSetup_Portrait(canvas, doc):
    canvas.saveState()
    # header
    canvas.drawImage(os.path.join(IMAGEDIR, 'Knorr_logo.png'), x, y+h, width=6*cm, height=1.23*cm)
    headertext = "Strictly confidential"
    headerFontSize = 9
    canvas.setFont('Helvetica', headerFontSize)
    canvas.drawRightString(x+w, y+h+headerFontSize, headertext)
    # footer
    footertext = u"\N{Copyright Sign} Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial property. We reserve all rights of disposal such as copying and passing on to third parties."
    footerFontSize = 5
    canvas.setFont('Helvetica', footerFontSize)
    canvas.drawString(x, y-footerFontSize, footertext)
    pageNoFontSize = 9
    canvas.setFont('Helvetica', pageNoFontSize)
    canvas.drawRightString(x+w, y-pageNoFontSize, "%d" % (doc.page))

  def pageSetup_Landscape(canvas, doc):
    canvas.saveState()
    # header
    canvas.drawImage(os.path.join(IMAGEDIR, 'Knorr_logo.png'), x, y+w, width=6*cm, height=1.23*cm)
    headertext = "Strictly confidential"
    headerFontSize = 9
    canvas.setFont('Helvetica', headerFontSize)
    canvas.drawRightString(x+h, y+w+headerFontSize, headertext)
    # footer
    footertext = u"\N{Copyright Sign} Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial property. We reserve all rights of disposal such as copying and passing on to third parties."
    footerFontSize = 5
    canvas.setFont('Helvetica', footerFontSize)
    canvas.drawString(x, y-footerFontSize, footertext)
    pageNoFontSize = 9
    canvas.setFont('Helvetica', pageNoFontSize)
    canvas.drawRightString(x+h, y-pageNoFontSize, "%d" % (doc.page))

  doc.addPageTemplates([plat.PageTemplate(id='Portrait', frames=frameP, onPage=pageSetup_Portrait, pagesize=reportlab.lib.pagesizes.A4),
                        plat.PageTemplate(id='Landscape', frames=[frameL1, frameL2, frameL3, frameL4], onPage=pageSetup_Landscape, pagesize=reportlab.lib.pagesizes.landscape(reportlab.lib.pagesizes.A4)),
                        ])

  styles=reportlab.lib.styles.getSampleStyleSheet()

  # container for the 'Flowable' objects
  elements = []

  elements.append(plat.NextPageTemplate('Portrait'))
  ptext = "Use case evaluation with R7: rejection of S1 by CVR3"
  elements.append(plat.Paragraph(ptext, styles['Title']))
  elements.append(plat.Spacer(w, 1*cm))

  addHeadingToPDF(elements, "Table of contents", styles['Heading1'])
  toc = plat.tableofcontents.TableOfContents()
  elements.append(toc)

  elements.append(plat.PageBreak())

  measurements = sorted(evalData.keys())
  addHeadingToPDF(elements, "<seq id='section'/>. Introduction", styles['Heading1'])
  ptext = "The analysis of the use case measurements from %s has been done with a search script that looks \
           for intervals where the object (VW passenger car) has not got into Same Lane Near element of the position \
           matrix. These intervals are then categorized: did the object miss Same Lane Near because of the object classifier \
           or the lane classifier (has it got into some other POS element)." % measurements[0].split('_')[3]
  elements.append(plat.Paragraph(ptext, styles['Normal']))
  ptext = "The plots were created by viewSITacceptfilter.py with a modification that allows the viewing of POS element \
           the object has entered (uppermost axis). The green segments represent the intervals found."
  elements.append(plat.Paragraph(ptext, styles['Normal']))

  addHeadingToPDF(elements, "<seq id='section'/>. Summary", styles['Heading1'])
  ptext = "The following table shows the summary of this report:"
  elements.append(plat.Paragraph(ptext, styles['Normal']))
  summaryTable = summaryDataTable.getPrintable()
  t=plat.Table(summaryTable, repeatRows=summaryTable[0])
  t.setStyle(plat.TableStyle(DEFAULT_TABLE_STYLE))
  elements.append(t)

  elements.append(plat.Spacer(w, 2*cm))
  addHeadingToPDF(elements, "<seq id='section'/>. Evaluation of intervals", styles['Heading1'])
  for meas in measurements:
    for Start, End, Classifier, PosName, FUS_ID in evalData[meas]:
      elements.append(plat.NextPageTemplate('Landscape'))
      elements.append(plat.PageBreak())
      AdjStartTime = ADJUSTTIME(Start)

      ptext = "%s @ %s sec" % (meas, AdjStartTime)
      addHeadingToPDF(elements, "<seq template='%(section)s.%(subsection+)s'/>. " + ptext, styles["Heading2"])
      elements.append(plat.FrameBreak())

      if Classifier == 'laneclassif':
        ptext = "CVR3 FUS ID: %02d  -  S1 rejection because of lane classifier (object classified as %s)" % (FUS_ID, PosName)
      elif Classifier == 'objectclassif':
        ptext = "CVR3 FUS ID: %02d  -  S1 rejection because of object classifier" % (FUS_ID)
      elements.append(plat.Paragraph(ptext, styles['Normal']))
      elements.append(plat.FrameBreak())

      picPath = os.path.join(captureDirectory, AdjStartTime + 'lim' + LOWERLIMSET(Start) + ',' + UPPERLIMSET(Start, End), 'viewSITacceptFilter-FUS_INDEX_%02d-FUS_object_%d-%s.png' %(FUS_ID, FUS_ID, m))
      im=plat.Image(picPath, width=17.03*cm, height=12.12*cm)
      im.hAlign='CENTER'
      elements.append(im)
      elements.append(plat.FrameBreak())

      picPath = os.path.join(captureDirectory, AdjStartTime, 'viewVideoOverlay-DefParam-VideoNavigator-' + m + '.png')
      im=plat.Image(picPath, width=6*cm, height=4.5*cm)
      im.hAlign = 'CENTER'
      im.vAlign = 'TOP'
      elements.append(im)
      picPath = os.path.join(captureDirectory, AdjStartTime, 'viewTrackNavigator-DEFPARAM-TrackNavigator-' + m + '.png')
      im=plat.Image(picPath, width=4.8*cm, height=7*cm)
      im.hAlign = 'CENTER'
      im.vAlign = 'BOTTOM'
      elements.append(im)

  # write the document to disk
  doc.multiBuild(elements)
  return

class cAnalyze(interface.iAnalyze):
  def check(self):
    batch = self.get_batch()
    start = batch.get_last_entry_start()
    filter_ = dict(start=start,
                   class_name='dataevalaebs.searchUseCaseEvalS1Rejection_CVR3.cSearch')
    reportGroup = batch.filter(type='measproc.cFileReport', result='passed', **filter_)
    workspaceGroup = batch.filter(type='measproc.FileWorkSpace', **filter_)
    return reportGroup, workspaceGroup

  def fill(self, reportGroup, workspaceGroup):
    return reportGroup, workspaceGroup

  def analyze(self, Param, reportGroup, workspaceGroup):
    # determine capture directory for plot and VideoNav ------------------------
    batch = self.get_batch()
    CaptureDir = os.path.join(batch.dirname, 'pics4doc')

    # initialize datatable -----------------------------------------------------
    con = sqlite3.connect(':memory:')
    cur = con.cursor()
    cur.execute("""CREATE TABLE classifIntervals (
                      MeasPath TEXT,
                      MeasName TEXT,
                      Start REAL,
                      End REAL,
                      Classifier TEXT,
                      PosName TEXT,
                      FUS_ID INTEGER,
                      PRIMARY KEY(MeasPath, MeasName, Start, End, Classifier, PosName, FUS_ID))""")

    # fill datatable with data -------------------------------------------------
    for entry in reportGroup:
      report = batch.wake_entry(entry)
      repTitle = report.getTitle().lower().split(' - ')
      time = numpy.load(report.getTimeFile())
      fusID = int(repTitle[1].split(' ')[1][-2:])
      classifType = repTitle[-1].split(' ')[0]
      if classifType == 'laneclassif':
        posObjName = repTitle[-1].split(' ')[-1].upper()
      elif classifType == 'objectclassif':
        posObjName = 'none'
      for start, end in report.IntervalList:
        measPath = batch.get_entry_attr(entry, 'fullmeas')
        measName = os.path.basename(measPath)
        try:
          cur.execute("INSERT INTO classifIntervals VALUES (?, ?, ?, ?, ?, ?, ?)", (
            measPath,
            measName,
            time[start],
            time[end],
            classifType,
            posObjName,
            fusID))
        except sqlite3.IntegrityError:
          pass  # ignore duplicates

    # acquire data from the datatable and create captures ----------------------
    subprocess.call("%s -m view --export %s" % (PYTHONEXE, TMPCONFIGFILE))
    cmd = ("%s -m view --norun" %PYTHONEXE).split()
    cmd.extend( open(CONFIGFILE).read().split() )
    subprocess.call(cmd)
    try:
      cur.execute("SELECT DISTINCT MeasName, MeasPath FROM classifIntervals ORDER BY MeasName")
      classifMeas = cur.fetchall()
      evalData = {}
      for m, mp in classifMeas:
        cur.execute("SELECT Start, End, Classifier, PosName, FUS_ID FROM classifIntervals WHERE MeasName = ? ORDER BY Start", (m,))
        plotSeekTimes = []
        navSeekTimes = []
        plotCmds = []
        evalData[m] = []
        plotCaptureExists = []
        videoNavCaptureExists = []
        trackNavCaptureExists = []
        fetchedData = list(cur.fetchall())
        for Start, End, Classifier, PosName, FUS_ID in fetchedData:
          navSeekTimes.append(ADJUSTTIME(Start))
          plotSeekTimes.append(ADJUSTTIME(Start) + 'lim' + LOWERLIMSET(Start) + ',' + UPPERLIMSET(Start, End))
          plotCmds.append("viewSITacceptFilter.FUS_INDEX_%02d" %FUS_ID)
          evalData[m].append([Start, End, Classifier, PosName, FUS_ID])
          plotCaptureExists.append(os.path.exists(os.path.join(CaptureDir, ADJUSTTIME(Start) + 'lim' + LOWERLIMSET(Start) + ',' + UPPERLIMSET(Start, End), 'viewSITacceptFilter-FUS_INDEX_%02d-FUS_object_%d-%s.png' %(FUS_ID, FUS_ID, m))))
          videoNavCaptureExists.append(os.path.exists(os.path.join(CaptureDir, ADJUSTTIME(Start), 'viewVideoOverlay-DefParam-VideoNavigator-' + m + '.png')))
          trackNavCaptureExists.append(os.path.exists(os.path.join(CaptureDir, ADJUSTTIME(Start), 'viewTrackNavigator-DEFPARAM-TrackNavigator-' + m + '.png')))
        plotCaptureExists = numpy.array(plotCaptureExists)
        videoNavCaptureExists = numpy.array(videoNavCaptureExists)
        trackNavCaptureExists = numpy.array(trackNavCaptureExists)
        navSeekCmdLine = "--seek " + " --seek ".join(navSeekTimes)
        if not (numpy.all(videoNavCaptureExists) and numpy.all(trackNavCaptureExists)):
          subprocess.call("%s -m view --norun -n StatusNames -n iView -n GroupNames --fill +fillCVR3_POS --fill +fillCVR3_FUS --group +CVR3_FUS --group +CVR3_POS -i +viewVideoOverlay -i +viewTrackNavigator" % PYTHONEXE)
          subprocess.call("%s -m view --nonav --capture %s -m %s %s" % (PYTHONEXE, CaptureDir, mp, navSeekCmdLine))
        if not numpy.all(plotCaptureExists):
          subprocess.call("%s -m view --norun -n StatusNames -n GroupNames -n iView -i +viewSITacceptFilter" % PYTHONEXE)
          for seekIndex in xrange(len(plotSeekTimes)):
            subprocess.call("%s -m view --nonav --capture %s -m %s --seek %s -p +%s" % (PYTHONEXE, CaptureDir, mp, plotSeekTimes[seekIndex], plotCmds[seekIndex]))
            subprocess.call("%s -m view --norun -p -%s" % (PYTHONEXE, plotCmds[seekIndex]))
    finally:
      subprocess.call("%s -m view --norun --push %s" % (PYTHONEXE, TMPCONFIGFILE))
      os.remove(TMPCONFIGFILE)

    # create summary table -----------------------------------------------------
    summaryData = []
    summaryData_titleRow = ["Measurement", "FUS ID", "First\ndetection [m]", "Classified as\nobstacle [m]", "Classified as valid &\nrelevant obstacle [m]"]
    for entry in workspaceGroup:
      row = []
      measName = batch.get_entry_attr(entry, 'measurement')
      row.append(measName)
      workspace = batch.wake_entry(entry)
      fusID = workspace.getTitle().split('-')[-1]
      row.append(fusID)
      wsSummary = workspace.workspace
      firstDet = sorted(wsSummary['dxFirstDet'], reverse=True)
      row.append("; ".join(["%.2f" % dx for dx in firstDet]))
      obsClass = sorted(wsSummary['dxAsObst'], reverse=True)
      row.append("; ".join(["%.2f" % dx for dx in obsClass]))
      valRelClass = sorted(wsSummary['dxValRel'], reverse=True)
      row.append("; ".join(["%.2f" % dx for dx in valRelClass]))
      summaryData.append(row)

    summaryData = sorted(summaryData, key=lambda row: row[0])
    summaryDataTable = measproc.Table(summaryData, titleRow=summaryData_titleRow)

    con.close()

    # create pdf report --------------------------------------------------------
    baseName = os.path.splitext(batch.dbname)[0]
    pdfFileName = os.path.extsep.join((baseName, "pdf"))

    createPDF(pdfFileName,
              CaptureDir,
              evalData,
              summaryDataTable)
    pass
