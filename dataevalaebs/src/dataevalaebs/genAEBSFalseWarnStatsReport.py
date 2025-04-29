'''
genAEBSFalseWarnStatsReport.py
Concluding documentation generation for the statistics of AEBS false warning evaluation

This script is not part of the tool chain. It generates a concluding documentation
of the AEBS false warning evaluation. The script has two command line parameters:
    1. The first one is the location of the folder containing the batch files of measurement
       reports.
    2. The second one is the location of the text file containing the measurement
       dates for document creation. This text file shall contain all the measurement 
       dates for which conclusion report generation is intended. Every measurement
       date shall be written in a new line.
Both of these parameters shall be given otherwise the script exits and the report
won't generate! If the reports have not been labeled properly before running this
script then no concluding documentation will be generated!
'''

from datavis import pyglet_workaround  # necessary as early as possible (#164)

import csv
import sys
import os
import fnmatch
import numpy
import subprocess
import datetime
import hashlib

import reportlab.lib
import reportlab.platypus as plat
import reportlab.platypus.tableofcontents
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
import reportlab.graphics.charts.barcharts as barchart
import reportlab.graphics.charts.piecharts as piechart
import reportlab.graphics.charts.linecharts as linechart
import reportlab.graphics.charts.legends as chartlegend

import measproc
from analyzeAddLabels import VOTES_EXPLAINED

# constants for report generation ----------------------------------------------
PYTHONEXE = sys.executable if sys.executable else 'python'
CSV_FOLDER_NAME = 'CSV_Files'
REP_FOLDER_NAME = 'Report_Docs'
BATCH_NAME = 'batchAEBSWarningsSimAndRoadTypes'
BACKUP = r'C:\KBData\WorkData\BackUp4DataEval'
IMAGEDIR = os.path.join(os.path.dirname(__file__), "images")
CONFIGFILEDIR = os.path.join(os.path.dirname(__file__), "cfg")
TMPCONFIGFILE = os.path.join(CONFIGFILEDIR, "AEBSFalseWarnStatsReport_ConfigBackup.cfg")

DEFAULT_TABLE_STYLE = [('BACKGROUND', (0,0), (-1,-1), reportlab.lib.colors.white),
                       ('TEXTCOLOR',  (0,0), (-1,-1), reportlab.lib.colors.black),
                       ('GRID',       (0,0), (-1,-1), 1, reportlab.lib.colors.black),
                       ('VALIGN',     (0,0), (-1,-1), "MIDDLE")]

CalcPercent = lambda value, total: (sum(value) / sum(total)) * 100 if sum(total) != 0 else 0

# function for drawing pie charts ----------------------------------------------
def drawPieChart(frameWidth, indent, pieSize, colors2Plot, data, dataKeys, **kwargs):
  dataDivisor = kwargs['dataDivisor'] if 'dataDivisor' in kwargs else None
  header2label = kwargs['header2label'] if 'header2label' in kwargs else False
  
  d = Drawing(frameWidth, pieSize)
  pc = piechart.Pie3d()
  pc.checkLabelOverlap = 1
  pc.x = indent
  pc.y = 0
  pc.width = pieSize
  pc.height = pieSize
  pc.slices.strokeColor = colors.white
  pc.slices.strokeWidth = 1
  fwCausesPercent = {}
  
  # sort data keys and colors for legend according to occurrence/number/relevance
  list4Sorting = []
  for dataKey, sliceColor in zip(dataKeys, colors2Plot):
    list4Sorting.append((CalcPercent(data[dataKey], pc.data), dataKey, sliceColor))
  list4Sorting = sorted(list4Sorting, key=lambda listData: listData[0], reverse=True)
  dataKeys = list(zip(*list4Sorting)[1])
  colors2Plot = list(zip(*list4Sorting)[2])
  
  pc.data = [sum(data[dataKey]) for dataKey in dataKeys]
  for dataKey in dataKeys:
    fwCausesPercent[dataKey] = CalcPercent(data[dataKey], pc.data)
  
  for index, sliceColor in enumerate(colors2Plot):
    pc.slices[index].fillColor = sliceColor
  
  centimeter = 72.0 / 2.54
  
  l = chartlegend.Legend()
  l.x = pc.x + pc.width + 2 * centimeter
  l.y = pc.height * 0.5
  l.dx = 8
  l.dy = 8
  l.alignment = 'right'
  l.boxAnchor = 'w'
  l.deltay = 10
  l.columnMaximum = 13
  l.dxTextSpace = 5
  l.dividerLines = 1|1|0 if header2label else 1|2|4
  l.dividerOffsY = 7
  l.subCols.rpad = 10
  
  if header2label:
    if dataDivisor:
      legendElements = [(None, ('\nCause', '\nRelative', 'Abs. per\n4000 km', 'Abs.\ntotal'))]
    else:
      legendElements = [(None, ('Cause', 'Relative'))]
  else:
    legendElements = []
  
  percentTotal = 0.0
  kmSegmentTotal = 0.0
  dataTotal = 0.0
  for i, label in enumerate(dataKeys):
    if dataDivisor:
      kmSegment = sum(data[label]) / dataDivisor
      legendElements.append((pc.slices[i].fillColor,
                             (label.split(' (')[0], 
                              "%.2f %%" % fwCausesPercent[label], 
                              "%.2f" % kmSegment,
                              "%d" % sum(data[label]))))
      percentTotal += fwCausesPercent[label]
      kmSegmentTotal += kmSegment
      dataTotal += sum(data[label])
    else:
      legendElements.append((pc.slices[i].fillColor,
                             (label.split(' (')[0], 
                              "%.2f %%" % fwCausesPercent[label])))
  if dataDivisor and header2label:
    legendElements.append((None,
                           (None, 
                            "%.2f %%" % percentTotal,
                            "%.2f" % kmSegmentTotal,
                            "%d" % dataTotal)))
  l.colorNamePairs = legendElements
  
  d.add(pc)
  d.add(l)
  return d

# function for drawing horizontal bar charts -----------------------------------
def drawHorizontalBarChart(frameWidth, chartWidth, chartHeight, indent, colors2Plot, data, dataKeys, **kwargs):
  split = kwargs['split'] if 'split' in kwargs else True
  percent = kwargs['percent'] if 'percent' in kwargs else False
  sortDataKeys = kwargs['sortDataKeys'] if 'sortDataKeys' in kwargs else False
  incSum = kwargs['incSum'] if 'incSum' in kwargs else True
  
  d = Drawing(frameWidth, chartHeight)
  bc = barchart.HorizontalBarChart()
  bc.x = indent
  bc.y = 0
  bc.width = chartWidth
  bc.height = chartHeight
  bc.valueAxis.forceZero = 1
  bc.groupSpacing = 0
  bc.categoryAxis.style = 'stacked'
  bc.categoryAxis.visibleTicks = 0
  
  centimeter = 72.0 / 2.54
  
  l = chartlegend.Legend()
  l.x = bc.x + bc.width + 1 * centimeter
  l.y = bc.height * 0.5
  l.dx = 8
  l.dy = 8
  l.alignment = 'right'
  l.boxAnchor = 'w'
  l.deltay = 10
  l.columnMaximum = 13
  l.dxTextSpace = 5
  l.dividerLines = 1|1|4 if incSum and percent else 1|2|4
  l.dividerOffsY = 7
  l.subCols.rpad = 10
  
  # sort bars according to occurrence/number/relevance only if they would not be stacked and requested
  if not isinstance(dataKeys[0], tuple):
    if sortDataKeys:
      list4Sorting = []
      for dataKey, barColor in zip(dataKeys, colors2Plot):
        list4Sorting.append((sum(data[dataKey]), dataKey, barColor))
      list4Sorting = sorted(list4Sorting, key=lambda listData: listData[0], reverse=True)
      dataKeys = list(zip(*list4Sorting)[1])
      colors2Plot = list(zip(*list4Sorting)[2])
  
  for index, barColor in enumerate(colors2Plot):
    bc.bars[index].fillColor = barColor
  
  if not isinstance(dataKeys[0], tuple):
    legendElements = []
    barData = [barDataList[:] for barDataList in [[0] * len(dataKeys)] * len(dataKeys)]
    totalValue = [sum(data[label]) for label in dataKeys]
    for index, label in enumerate(dataKeys):
      barData[index][index] = sum(data[label])
      if split:
        if percent and incSum:
          nameValuePair = (label.split(' (')[0],
                           "%d" % sum(data[label]),
                           "%.2f %%" % CalcPercent(data[label], totalValue))
        elif percent and not incSum:
          nameValuePair = (label.split(' (')[0],
                           "%.2f %%" % CalcPercent(data[label], totalValue))
        else:
          sumValue = sum(data[label])
          if sumValue % 1 != 0:
            nameValuePair = (label.split(' (')[0],
                             "%.2f" % sumValue)
          else:
            nameValuePair = (label.split(' (')[0],
                             "%d" % sumValue)
      else:
        if percent and incSum:
          nameValuePair = (label,
                           "%d" % sum(data[label]),
                           "%.2f %%" % CalcPercent(data[label], totalValue))
        elif percent and not incSum:
          nameValuePair = (label,
                           "%.2f %%" % CalcPercent(data[label], totalValue))
        else:
          sumValue = sum(data[label])
          if sumValue % 1 != 0:
            nameValuePair = (label,
                             "%.2f" % sumValue)
          else:
            nameValuePair = (label,
                             "%d" % sumValue)
      legendElements.append((bc.bars[index].fillColor, nameValuePair))
    if incSum and percent:
      legendElements.append((None, (" ", "Number", "Ratio")))
    legendElements.reverse() # start filling of legend from the bottom as the case is with the chart itself
    
  else:
    legendElements = []
    barData = [barDataList[:] for barDataList in [[0] * len(dataKeys)] * len(dataKeys[0])]
    if incSum and percent:
      legendElements.append((None, (" ", "Number", "Ratio")))
    for rowIndex, dataKeyTuple in enumerate(dataKeys):
      totalValue = [sum(data[label]) for label in dataKeyTuple]
      for colIndex, dataKey in enumerate(dataKeyTuple):
        barData[colIndex][rowIndex] = sum(data[dataKey])
        if split:
          if percent and incSum:
            nameValuePair = (dataKey.split(' (')[0],
                             "%d" % sum(data[dataKey]),
                             "%.2f %%" % CalcPercent(data[dataKey], totalValue))
          elif percent and not incSum:
            nameValuePair = (dataKey.split(' (')[0],
                             "%.2f %%" % CalcPercent(data[dataKey], totalValue))
          else:
            nameValuePair = (dataKey.split(' (')[0],
                             "%d" % sum(data[dataKey]))
        else:
          if percent and incSum:
            nameValuePair = (dataKey,
                             "%d" % sum(data[dataKey]),
                             "%.2f %%" % CalcPercent(data[dataKey], totalValue))
          elif percent and not incSum:
            nameValuePair = (dataKey,
                             "%.2f %%" % CalcPercent(data[dataKey], totalValue))
          else:
            nameValuePair = (dataKey,
                             "%d" % sum(data[dataKey]))
        legendElements.append((bc.bars[colIndex].fillColor, nameValuePair))
  
  bc.data = barData
  l.colorNamePairs = legendElements
  
  d.add(bc)
  d.add(l)
  return d

# function for drawing line charts ---------------------------------------------
def drawLineChart(frameWidth, chartWidth, chartHeight, indent, colors2Plot, data, dataKeys, split=True):
  centimeter = 72.0 / 2.54
  d = Drawing(frameWidth, chartHeight)
  lc = linechart.HorizontalLineChart() # later it might change as reportlab evolves
  lc.x = indent
  lc.y = 0
  lc.width = chartWidth
  lc.height = chartHeight
  lc.joinedLines = 1
  lc.lines.symbol = linechart.makeMarker('Circle')
  lc.valueAxis.visibleGrid = 1
  
  for index, lineColor in enumerate(colors2Plot):
    lc.lines[index].strokeColor = lineColor
  
  dataKeysTmp = []
  if 'Date' in dataKeys:
    dataKeys.remove('Date')
  dataKeysTmp.append('Date')
  for dataKey in dataKeys:
    dataKeysTmp.append(dataKey)
  
  tempData = []
  for dataKey in dataKeysTmp:
    tempData.append(data[dataKey])
  
  data4Chart = {}
  for dataKey in dataKeys:
    if dataKey != 'Date':
      data4Chart.setdefault(dataKey, [])
  lc.categoryAxis.categoryNames = []
  for tmpDt in sorted(zip(*tempData), key=lambda elem: elem[0]):
    for index, dataKey in enumerate(dataKeysTmp):
      if dataKey == 'Date':
        lc.categoryAxis.categoryNames.append(tmpDt[index])
      else:
        data4Chart[dataKey].append(tmpDt[index])
  lc.data = [data4Chart[dataKey] for dataKey in dataKeys]
  
  for index in xrange(len(lc.categoryAxis.categoryNames)):
    lc.categoryAxis.labels[index].angle = 30
    lc.categoryAxis.labels[index].dy = -0.4*centimeter
    lc.categoryAxis.labels[index].dx = -0.6*centimeter
  
  l = chartlegend.Legend()
  l.x = lc.x + lc.width + 0.5 * centimeter
  l.y = lc.height * 0.5
  l.dx = 8
  l.dy = 8
  l.alignment = 'right'
  l.boxAnchor = 'w'
  l.deltay = 10
  l.columnMaximum = 13
  l.dxTextSpace = 5
  l.dividerLines = 1|2|4
  l.dividerOffsY = 7
  l.subCols.rpad = 10
  if split:
    l.colorNamePairs = [(lc.lines[lineIndex].strokeColor, dataKey.split(' (')[0]) for lineIndex, dataKey in enumerate(dataKeys)]
  else:
    l.colorNamePairs = [(lc.lines[lineIndex].strokeColor, dataKey) for lineIndex, dataKey in enumerate(dataKeys)]
  
  d.add(lc)
  d.add(l)
  return d

# define document template class (with ability to add table of contents) -------
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

# define function for adding headers with links --------------------------------
def addHeadingToPDF(story, text, sty):
  # generate bookmarkname
  bn = hashlib.sha1(text+sty.name).hexdigest()
  # modify paragraph text to include an anchor point with name bn
  h = plat.Paragraph(text+'<a name="%s"/>' % bn, sty)
  # store the bookmark name on the flowable so afterFlowable can see this
  h._bookmarkName = bn
  story.append(h)
  return

# define document (PDF) creating function --------------------------------------
def createPDF(fileLoc, totalStatisticsData, commercialWeeks, appendixTable,
              totalStatsDataWithFWExBrTu, totalStatsDataWithFWSDF_OfflineAlgo,
              totalStatsDataWithFWSDF_OnlineAlgo, contingencyTablesFW,
              contingencyTablesFW_KBinfl, commWeeksWithDates):
  doc = MyDocTemplate(fileLoc, defaultpagesize=reportlab.lib.pagesizes.A4, showBoundary=0)
  
  x = doc.leftMargin
  y = doc.bottomMargin
  w = doc.width
  h = doc.height
  
  wA = reportlab.lib.pagesizes.A1[0] - doc.rightMargin - doc.leftMargin
  hA = reportlab.lib.pagesizes.A1[1] - doc.topMargin - doc.bottomMargin
  
  frameP  = plat.Frame(x, y, w , h , id='Portrait')
  frameL  = plat.Frame(y, x, hA, wA, id='Landscape')
  
  cm = reportlab.lib.pagesizes.cm
  
  # draw header and footer -----------------------------------------------------
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
  
  def pageSetup_LandscapeA0(canvas, doc):
    w = wA
    h = hA
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
                        plat.PageTemplate(id='Landscape', frames=frameL, onPage=pageSetup_LandscapeA0, pagesize=reportlab.lib.pagesizes.landscape(reportlab.lib.pagesizes.A1))])
  
  styles=reportlab.lib.styles.getSampleStyleSheet()
  
  elements = [] # container for the 'Flowable' objects
  
  # create mapping for headings ------------------------------------------------
  # needed so that the section numbers of the headings restart from 1 in the
  # second call of this function
  pdfName = os.path.split(fileLoc)[-1]
  headingTextMap = {'sectionNoSub': 'section_' + pdfName,
                    'section': '%(section_' + pdfName + ')s',
                    'subsection1+': '%(subsection1_' + pdfName + '+)s',
                    'subsection2+': '%(subsection2_' + pdfName + '+)s',
                    'subsection3+': '%(subsection3_' + pdfName + '+)s'}
  
  # add title, introduction and summary to document ----------------------------
  elements.append(plat.NextPageTemplate('Portrait'))
  dayNum = "%d" % len(totalStatisticsData['Date']) + " days" if len(totalStatisticsData['Date']) > 1 else " day"
  weekNum = commercialWeeks[0] if len(commercialWeeks) == 1 else', '.join(commercialWeeks[:-1]) + ' and %s' % commercialWeeks[-1]
  ptext = "Conclusion of %s of endurance runs on %s" % (dayNum, weekNum)
  elements.append(plat.Paragraph(ptext, styles['Title']))
  elements.append(plat.Spacer(w, 1*cm))
  
  headingText = "<seq id='%(sectionNoSub)s'/>. Introduction" % headingTextMap
  addHeadingToPDF(elements, headingText, styles['Heading1'])
  ptext = "This document summarizes the analysis of measurement data collected on %s:" % ("these days" if len(totalStatisticsData['Date']) > 1 else "this day")
  elements.append(plat.Paragraph(ptext, styles['Normal']))
  ptext = totalStatisticsData['Date'][0] if len(totalStatisticsData['Date']) == 1 else', '.join(totalStatisticsData['Date'][:-1]) + ' and %s' % totalStatisticsData['Date'][-1]
  elements.append(plat.Paragraph(ptext, styles['Normal']))
  ptext = ("The document's main theme is the evaluation of AEBS false warnings in the case of CVR2 and CVR3. "
           "Possible causes (for both sensors) and solutions (only for CVR3) are presented. "
           "The solutions include object and lane classification and SDF. "
           "Knorr Bremse's influence on CVR3 performance improvement is limited to these situations:")
  elements.append(plat.Paragraph(ptext, styles['Normal']))
  
  for key in VOTES_EXPLAINED.keys():
    if key not in ('fw-red-with-sdf', 'scam-unavailable', 'bridge', 'tunnel'):
      ptext = ("<para><bullet bulletIndent='20'>&bull;</bullet>%s: %s</para>" % VOTES_EXPLAINED[key])
      elements.append(plat.Paragraph(ptext, styles['Normal']))
  
  ptext = ("Therefore this documentation also has separate sub-chapters for false warnings in the Knorr Bremse influence area.")
  elements.append(plat.Paragraph(ptext, styles['Normal']))
  elements.append(plat.Spacer(w, 1.0*cm))
  
  headingText = "<seq id='%(sectionNoSub)s'/>. Summary" % headingTextMap
  addHeadingToPDF(elements, headingText, styles['Heading1'])
  ptext = "Distribution by road type:"
  elements.append(plat.Paragraph(ptext, styles['Heading4']))
  elements.append(plat.Spacer(w, 0.2*cm))
  
  kmValues = ["Rural km", "City km", "Highway km"]
  colors2PrintkmSum = [colors.blue, colors.red, colors.green]
  d = drawPieChart(w, 2*cm, 6*cm, colors2PrintkmSum, totalStatisticsData, kmValues)
  elements.append(d)
  elements.append(plat.Spacer(w, 0.2*cm))
  
  totalDist = sum([sum(totalStatisticsData[kmValue]) for kmValue in kmValues])
  ptext = "Total distance covered: %.2f km" % (totalDist)
  elements.append(plat.Paragraph(ptext, styles['Normal']))
  
  noSensorAvail = {'CVR2': [], 'CVR3': []}
  for index, date in enumerate(totalStatisticsData['Date']):
    if totalStatisticsData['CVR2 available'][index] == 'no':
      noSensorAvail['CVR2'].append(date)
    elif totalStatisticsData['CVR3 available'][index] == 'no':
      noSensorAvail['CVR3'].append(date)
  
  if noSensorAvail['CVR2'] or noSensorAvail['CVR3']:
    elements.append(plat.Spacer(w, 1.0*cm))
    ptext = ("NOTE:")
    elements.append(plat.Paragraph(ptext, styles['Normal']))
  if noSensorAvail['CVR2']:
    dateText = noSensorAvail['CVR2'][0] if len(noSensorAvail['CVR2']) == 1 else', '.join(noSensorAvail['CVR2'][:-1]) + ' and %s' % noSensorAvail['CVR2'][-1]
    ptext = ("CVR2 was not available on %s:" % ("this day" if len(noSensorAvail['CVR2']) == 1 else "these dates"))
    elements.append(plat.Paragraph(ptext, styles['Normal']))
    ptext = ("%s" % (dateText))
    elements.append(plat.Paragraph(ptext, styles['Normal']))
  if noSensorAvail['CVR3']:
    dateText = noSensorAvail['CVR3'][0] if len(noSensorAvail['CVR3']) == 1 else', '.join(noSensorAvail['CVR3'][:-1]) + ' and %s' % noSensorAvail['CVR3'][-1]
    ptext = ("CVR3 was not available on %s:" % ("this day" if len(noSensorAvail['CVR3']) == 1 else "these dates"))
    elements.append(plat.Paragraph(ptext, styles['Normal']))
    ptext = ("%s" % (dateText))
    elements.append(plat.Paragraph(ptext, styles['Normal']))
  
  elements.append(plat.PageBreak())
  
  fwNo = ['No. of CVR3 false warnings',
          'No. of CVR3 false warnings\nin KB influence area',
          'No. of CVR3 false warnings\nwith SDF enabled (KB AEBS algorithms)',
          'No. of CVR3 false warnings\nwith SDF enabled (Bosch AEBS algorithms)',
          'No. of CVR2 false warnings']
  colors2PrintFWSum = [colors.blue, colors.green, colors.aqua, colors.grey, colors.red]
  overallFW = {}
  overallFW['Date'] = totalStatisticsData['Date']
  overallFW[fwNo[0]] = totalStatisticsData['No. of false warnings (CVR3)']
  overallFW[fwNo[1]] = list(numpy.array(totalStatisticsData['No. of false warnings (CVR3)']) -
                                        numpy.array(totalStatisticsData['Bridges (CVR3)']) -
                                        numpy.array(totalStatisticsData['Tunnels (CVR3)']))
  overallFW[fwNo[2]] = list(numpy.array(totalStatsDataWithFWSDF_OfflineAlgo['No. of false warnings (CVR3)']))
  overallFW[fwNo[3]] = list(numpy.array(totalStatsDataWithFWSDF_OnlineAlgo['No. of false warnings (CVR3)']))
  overallFW[fwNo[4]] = totalStatisticsData['No. of false warnings (CVR2)']
  
  headingText = "<seq template='%(section)s.%(subsection1+)s'/>. Distribution of Number of False Warnings" % headingTextMap
  addHeadingToPDF(elements, headingText, styles["Heading2"])
  
  ptext = "Distribution of total number of false warnings by sensor type:"
  elements.append(plat.Paragraph(ptext, styles['Heading4']))
  elements.append(plat.Spacer(w, 1.0*cm))
  
  d = drawHorizontalBarChart(w, 7*cm, 2.5*cm, 1*cm, colors2PrintFWSum, overallFW, fwNo, split=False)
  elements.append(d)
  elements.append(plat.Spacer(w, 1.5*cm))
  
  ptext = "Development of the above over time (daily):" if len(commWeeksWithDates.keys()) > 1 else "Development of the above over time:"
  elements.append(plat.Paragraph(ptext, styles['Heading4']))
  elements.append(plat.Spacer(w, 0.5*cm))
  
  d = drawLineChart(w, 9.5*cm, 5*cm, 0.5*cm, colors2PrintFWSum, overallFW, fwNo, split=False)
  elements.append(d)
  elements.append(plat.Spacer(w, 1.5*cm))
  
  if len(commWeeksWithDates.keys()) > 1:
    ptext = "Development of the above over time (weekly):"
    elements.append(plat.Paragraph(ptext, styles['Heading4']))
    elements.append(plat.Spacer(w, 0.5*cm))
    
    overallFWWeekly = {}
    for weekNum in commWeeksWithDates.keys():
      weekDict = overallFWWeekly.setdefault('Date', [])
      weekDict.append('CW%d' % weekNum)
      for valueName in fwNo:
        tmpValue = overallFWWeekly.setdefault(valueName, [])
        tmp = 0
        for dayDate in commWeeksWithDates[weekNum]:
          tmp += overallFW[valueName][overallFW['Date'].index(dayDate)]
        tmpValue.append(tmp)
    
    d = drawLineChart(w, 9.5*cm, 5*cm, 0.5*cm, colors2PrintFWSum, overallFWWeekly, fwNo, split=False)
    elements.append(d)
  elements.append(plat.PageBreak())
  
  kmDivisor = totalDist / 4000
  
  if kmDivisor >= 1.0:
    headingText = "<seq template='%(section)s.%(subsection1+)s'/>. Distribution of Number of False Warnings In 4000 km segments" % headingTextMap
    addHeadingToPDF(elements, headingText, styles["Heading2"])
    
    ptext = "Distribution of number of false warnings per 4000 km by sensor type:"
    elements.append(plat.Paragraph(ptext, styles['Heading4']))
    elements.append(plat.Spacer(w, 1.0*cm))
    
    modifStatData = dict(overallFW)
    for dataKey in fwNo:
      modifStatData[dataKey] = list(numpy.array(overallFW[dataKey]) / kmDivisor)
    
    d = drawHorizontalBarChart(w, 7*cm, 2.5*cm, 1*cm, colors2PrintFWSum, modifStatData, fwNo, split=False)
    elements.append(d)
    elements.append(plat.Spacer(w, 1.5*cm))
    
    ptext = "Development of the above over time (daily):" if len(commWeeksWithDates.keys()) > 1 else "Development of the above over time:"
    elements.append(plat.Paragraph(ptext, styles['Heading4']))
    elements.append(plat.Spacer(w, 0.5*cm))
    
    d = drawLineChart(w, 9.5*cm, 5*cm, 0.5*cm, colors2PrintFWSum, modifStatData, fwNo, split=False)
    elements.append(d)
    elements.append(plat.Spacer(w, 1.5*cm))
    
    if len(commWeeksWithDates.keys()) > 1:
      modifStatData = dict(overallFWWeekly)
      for dataKey in fwNo:
        modifStatData[dataKey] = list(numpy.array(overallFWWeekly[dataKey]) / kmDivisor)
      
      ptext = "Development of the above over time (weekly):"
      elements.append(plat.Paragraph(ptext, styles['Heading4']))
      elements.append(plat.Spacer(w, 0.5*cm))
      
      d = drawLineChart(w, 9.5*cm, 5*cm, 0.5*cm, colors2PrintFWSum, modifStatData, fwNo, split=False)
      elements.append(d)
    
    elements.append(plat.PageBreak())
  
  headingText = "<seq template='%(section)s.%(subsection1+)s'/>. Overall performance of CVR3 in specific cases" % headingTextMap
  addHeadingToPDF(elements, headingText, styles["Heading2"])
  
  ptext = "In the tables below the following notation is used for the type of warnings:"
  elements.append(plat.Paragraph(ptext, styles['Normal']))
  ptext = ("<para><bullet bulletIndent='20'>&bull;</bullet>\"W\" "
           " stands for acoustic warning</para>")
  elements.append(plat.Paragraph(ptext, styles['Normal']))
  ptext = ("<para><bullet bulletIndent='20'>&bull;</bullet>\"W-P\" "
           " stands for acoustic warning and partial braking</para>")
  elements.append(plat.Paragraph(ptext, styles['Normal']))
  ptext = ("<para><bullet bulletIndent='20'>&bull;</bullet>\"W-P-E\" "
           "stands for acoustic warning, partial braking and emergency braking</para>")
  elements.append(plat.Paragraph(ptext, styles['Normal']))
  elements.append(plat.Spacer(w, 1.0*cm))
  
  tableStyle_contigTable = [('BACKGROUND', (0,0), (-1,-1), reportlab.lib.colors.white),
                            ('TEXTCOLOR',  (0,0), (-1,-1), reportlab.lib.colors.black),
                            ('GRID',       (0,0), (-1,-1), 1, reportlab.lib.colors.black),
                            ('VALIGN',     (0,0), (-1,-1), "MIDDLE"),
                            ('BACKGROUND', (0, 1), (0, -1), reportlab.lib.colors.silver),
                            ('BACKGROUND', (1, 0), (-1, 0), reportlab.lib.colors.silver)]
  
  headingText = "All of the false warnings"
  addHeadingToPDF(elements, headingText, styles["Heading3"])
  
  ptext = "Radar only:"
  elements.append(plat.Paragraph(ptext, styles['Heading4']))
  contigTable = contingencyTablesFW['radar_only'].getPrintable()
  t = plat.Table(contigTable)
  t.setStyle(plat.TableStyle(tableStyle_contigTable))
  elements.append(t)
  
  ptext = "SDF:"
  elements.append(plat.Paragraph(ptext, styles['Heading4']))
  contigTable = contingencyTablesFW['sdf'].getPrintable()
  t = plat.Table(contigTable)
  t.setStyle(plat.TableStyle(tableStyle_contigTable))
  elements.append(t)
  elements.append(plat.PageBreak())
  
  headingText = "False warnings in the Knorr-Bremse influence area"
  addHeadingToPDF(elements, headingText, styles["Heading3"])
  
  ptext = "Radar only:"
  elements.append(plat.Paragraph(ptext, styles['Heading4']))
  contigTable = contingencyTablesFW_KBinfl['radar_only'].getPrintable()
  t = plat.Table(contigTable)
  t.setStyle(plat.TableStyle(tableStyle_contigTable))
  elements.append(t)
  
  ptext = "SDF:"
  elements.append(plat.Paragraph(ptext, styles['Heading4']))
  contigTable = contingencyTablesFW_KBinfl['sdf'].getPrintable()
  t = plat.Table(contigTable)
  t.setStyle(plat.TableStyle(tableStyle_contigTable))
  elements.append(t)
  elements.append(plat.PageBreak())
  
  # add table of contents ------------------------------------------------------
  addHeadingToPDF(elements, "Table Of Contents", styles['Heading1'])
  toc = plat.tableofcontents.TableOfContents()
  elements.append(toc)
  elements.append(plat.PageBreak())
  
  # add chapter: Reasons For False Warnings ------------------------------------
  headingText = "<seq id='%(sectionNoSub)s'/>. Reasons For False Warnings" % headingTextMap
  addHeadingToPDF(elements, headingText, styles['Heading1'])
  
  headingText = "<seq template='%(section)s.%(subsection2+)s'/>. CVR3 False Warning Causes" % headingTextMap
  addHeadingToPDF(elements, headingText, styles["Heading2"])
  
  ptext = "All of the false warning causes:"
  elements.append(plat.Paragraph(ptext, styles['Heading4']))
  
  fwCausesCVR3 = ["Bridges (CVR3)", "Tunnels (CVR3)", "Infrastructure (CVR3)", "Parking car (CVR3)",
                  "Road exit (CVR3)", "High curvature turn (CVR3)", "Traffic island (CVR3)",
                  "Approaching curve (CVR3)", "Straight road (CVR3)", "Construction site (CVR3)",
                  "Braking forward vehicle (CVR3)"]
  
  colors2PrintFW_CVR3 = [colors.blue, colors.red, colors.green, colors.grey,
                         colors.brown, colors.lime, colors.orange,
                         colors.magenta, colors.darkblue, colors.aqua,
                         colors.darkkhaki]
  
  d = drawPieChart(w, 1*cm, 5.7*cm, colors2PrintFW_CVR3, totalStatisticsData, fwCausesCVR3, dataDivisor=kmDivisor, header2label=True)
  elements.append(d)
  
  ptext = "False warnings in the Knorr Bremse influence area:"
  elements.append(plat.Paragraph(ptext, styles['Heading4']))
  
  fwCausesCVR3_KBInfl = ["Infrastructure (CVR3)", "Parking car (CVR3)", "Road exit (CVR3)",
                         "High curvature turn (CVR3)", "Traffic island (CVR3)", "Approaching curve (CVR3)",
                         "Straight road (CVR3)", "Construction site (CVR3)", "Braking forward vehicle (CVR3)"]
  
  colors2PrintFW_CVR3_KBInfl = [colors.green, colors.grey, colors.brown,
                                colors.lime, colors.orange, colors.magenta,
                                colors.darkblue, colors.aqua, colors.darkkhaki]
  
  d = drawPieChart(w, 1*cm, 6*cm, colors2PrintFW_CVR3_KBInfl, totalStatisticsData, fwCausesCVR3_KBInfl, dataDivisor=kmDivisor, header2label=True)
  elements.append(d)
  
  ptext = "False warnings with SDF enabled (KB AEBS algorithms):"
  elements.append(plat.Paragraph(ptext, styles['Heading4']))
  offlineAlgoFW = []
  for cause in fwCausesCVR3:
    offlineAlgoFW.append(totalStatsDataWithFWSDF_OfflineAlgo[cause])
  
  if numpy.count_nonzero(offlineAlgoFW) != 0:
    d = drawPieChart(w, 1*cm, 6*cm, colors2PrintFW_CVR3, totalStatsDataWithFWSDF_OfflineAlgo, fwCausesCVR3, dataDivisor=kmDivisor, header2label=True)
    elements.append(d)
  else:
    ptext = "There were no false warnings produced with KB AEBS algorithms"
    elements.append(plat.Paragraph(ptext, styles['Normal']))
  elements.append(plat.PageBreak())
  
  ptext = "False warnings with SDF enabled (Bosch AEBS algorithms):"
  elements.append(plat.Paragraph(ptext, styles['Heading4']))
  
  onlineAlgoFW = []
  for cause in fwCausesCVR3:
    onlineAlgoFW.append(totalStatsDataWithFWSDF_OnlineAlgo[cause])
  
  if numpy.count_nonzero(onlineAlgoFW) != 0:
    d = drawPieChart(w, 1*cm, 6*cm, colors2PrintFW_CVR3, totalStatsDataWithFWSDF_OnlineAlgo, fwCausesCVR3, dataDivisor=kmDivisor, header2label=True)
    elements.append(d)
  else:
    ptext = "There were no false warnings produced with Bosch AEBS algorithms"
    elements.append(plat.Paragraph(ptext, styles['Normal']))
  
  headingText = "<seq template='%(section)s.%(subsection2+)s'/>. CVR2 False Warning Causes" % headingTextMap
  addHeadingToPDF(elements, headingText, styles["Heading2"])
  
  fwCausesCVR2 = ["Infrastructure (CVR2)", "Parking car (CVR2)", "Road exit (CVR2)",
                  "High curvature turn (CVR2)", "Traffic island (CVR2)", "Approaching curve (CVR2)",
                  "Straight road (CVR2)", "Construction site (CVR2)", "Braking forward vehicle (CVR2)"]
  
  colors2PrintFW_CVR2 = [colors.green, colors.grey, colors.brown,
                         colors.lime, colors.orange, colors.magenta,
                         colors.darkblue, colors.aqua, colors.darkkhaki]
  
  if sum(totalStatisticsData['No. of false warnings (CVR2)']) > 0:
    d = drawPieChart(w, 1*cm, 6*cm, colors2PrintFW_CVR2, totalStatisticsData, fwCausesCVR2, dataDivisor=kmDivisor, header2label=True)
    elements.append(d)
  elif numpy.all(numpy.array(totalStatisticsData['CVR2 available'])=='no'):
    ptext = "CVR2 was not available in the time interval of the report."
    elements.append(plat.Paragraph(ptext, styles['Normal']))
  #else: #TODO: few availability --> ???
  
  headingText = "<seq template='%(section)s.%(subsection2+)s'/>. Trend Of CVR3 False Warnings" % headingTextMap
  addHeadingToPDF(elements, headingText, styles["Heading2"])
  
  if len(commWeeksWithDates.keys()) > 1:
    ptext = "Daily trend of the false warnings:"
    elements.append(plat.Paragraph(ptext, styles['Heading4']))
    elements.append(plat.Spacer(w, 0.5*cm))
  
  d = drawLineChart(w, 10.5*cm, 5*cm, 0.5*cm, colors2PrintFW_CVR3, totalStatisticsData, fwCausesCVR3)
  elements.append(d)
  elements.append(plat.PageBreak())
  
  if len(commWeeksWithDates.keys()) > 1:
    fwWeeklyTrend = {}
    for weekNum in commWeeksWithDates.keys():
      weekDict = fwWeeklyTrend.setdefault('Date', [])
      weekDict.append('CW%d' % weekNum)
      for valueName in fwCausesCVR3:
        tmpValue = fwWeeklyTrend.setdefault(valueName, [])
        tmp = 0
        for dayDate in commWeeksWithDates[weekNum]:
          tmp += totalStatisticsData[valueName][totalStatisticsData['Date'].index(dayDate)]
        tmpValue.append(tmp)
    
    elements.append(plat.Spacer(w, 0.5*cm))
    ptext = "Weekly trend of the false warnings:"
    elements.append(plat.Paragraph(ptext, styles['Heading4']))
    elements.append(plat.Spacer(w, 0.5*cm))
    
    d = drawLineChart(w, 10.5*cm, 5*cm, 0.5*cm, colors2PrintFW_CVR3, fwWeeklyTrend, fwCausesCVR3)
    elements.append(d)
    elements.append(plat.Spacer(w, 1.0*cm))
  
  headingText = "<seq template='%(section)s.%(subsection2+)s'/>. Trend Of CVR2 False Warnings" % headingTextMap
  addHeadingToPDF(elements, headingText, styles["Heading2"])
  
  if len(commWeeksWithDates.keys()) > 1 and sum(totalStatisticsData['No. of false warnings (CVR2)']) > 0:
    ptext = "Daily trend of the false warnings:"
    elements.append(plat.Paragraph(ptext, styles['Heading4']))
    elements.append(plat.Spacer(w, 0.5*cm))
  
  if sum(totalStatisticsData['No. of false warnings (CVR2)']) > 0:
    d = drawLineChart(w, 10.5*cm, 5*cm, 0.5*cm, colors2PrintFW_CVR2, totalStatisticsData, fwCausesCVR2)
    elements.append(d)
  elif numpy.all(numpy.array(totalStatisticsData['CVR2 available'])=='no'):
    ptext = "CVR2 was not available in the time interval of the report."
    elements.append(plat.Paragraph(ptext, styles['Normal']))
  #else: #TODO: few availability --> ???
  
  if len(commWeeksWithDates.keys()) > 1 and sum(totalStatisticsData['No. of false warnings (CVR2)']) > 0:
    fwWeeklyTrend = {}
    for weekNum in commWeeksWithDates.keys():
      weekDict = fwWeeklyTrend.setdefault('Date', [])
      weekDict.append('CW%d' % weekNum)
      for valueName in fwCausesCVR2:
        tmpValue = fwWeeklyTrend.setdefault(valueName, [])
        tmp = 0
        for dayDate in commWeeksWithDates[weekNum]:
          tmp += totalStatisticsData[valueName][totalStatisticsData['Date'].index(dayDate)]
        tmpValue.append(tmp)
    
    elements.append(plat.Spacer(w, 1.5*cm))
    ptext = "Weekly trend of the false warnings:"
    elements.append(plat.Paragraph(ptext, styles['Heading4']))
    elements.append(plat.Spacer(w, 0.5*cm))
    
    d = drawLineChart(w, 10.5*cm, 5*cm, 0.5*cm, colors2PrintFW_CVR2, fwWeeklyTrend, fwCausesCVR2)
    elements.append(d)
  
  elements.append(plat.PageBreak())
  
  # add chapter: Suppression Mechanisms ----------------------------------------
  headingText = "<seq id='%(sectionNoSub)s'/>. Suppression Mechanisms" % headingTextMap
  addHeadingToPDF(elements, headingText, styles['Heading1'])
  
  headingText = "<seq template='%(section)s.%(subsection3+)s'/>. Reasons For CVR3 Suppressing The Warnings Seen With CVR2" % headingTextMap
  addHeadingToPDF(elements, headingText, styles["Heading2"])
  
  supprClass = ['wClassObstacle (CVR3)', 'dLength (CVR3)', 'dVarYvBase (CVR3)', 'wConstElem (CVR3)']
  colors2PrintClassif = [colors.blue, colors.red, colors.green, colors.grey]
  if sum(totalStatisticsData['No. of false warnings (CVR2)']) > 0:
    d = drawHorizontalBarChart(w, 7*cm, 3*cm, 1*cm, colors2PrintClassif, totalStatisticsData, supprClass, sortDataKeys=True)
    elements.append(d)
  elif numpy.all(numpy.array(totalStatisticsData['CVR2 available'])=='no'):
    ptext = "CVR2 was not available in the time interval of the report."
    elements.append(plat.Paragraph(ptext, styles['Normal']))
  #else: #TODO: few availability --> ???
  elements.append(plat.Spacer(w, 1.0*cm))
  
  headingText = "<seq template='%(section)s.%(subsection3+)s'/>. Possibility Of False Warning Reduction With Parallel SDF" % headingTextMap
  addHeadingToPDF(elements, headingText, styles["Heading2"])
  
  ptext = "In the case of all false warnings:"
  elements.append(plat.Paragraph(ptext, styles['Heading4']))
  
  fwRedWithSDF = [('FW red. with SDF (CVR3)', 'No red. possible (CVR3)', 'No camera available (CVR3)')]
  colors2PrintFWRed = [colors.blue, colors.red, colors.green]
  
  d = drawHorizontalBarChart(w, 7*cm, 1.5*cm, 1*cm, colors2PrintFWRed, totalStatisticsData, fwRedWithSDF, percent=True)
  elements.append(d)
  elements.append(plat.Spacer(w, 1.0*cm))
  
  ptext = "Only in the case of Knorr Bremse influence area:"
  elements.append(plat.Paragraph(ptext, styles['Heading4']))
  
  d = drawHorizontalBarChart(w, 7*cm, 1.5*cm, 1*cm, colors2PrintFWRed, totalStatsDataWithFWExBrTu, fwRedWithSDF, percent=True)
  elements.append(d)
  elements.append(plat.Spacer(w, 1.0*cm))
  
  ptext = "Availability of KB-Cam Advanced:"
  elements.append(plat.Paragraph(ptext, styles['Heading4']))
  if numpy.all(numpy.array(totalStatsDataWithFWSDF_OfflineAlgo['Total time']) != 0):
    scamAvail = [('KB-Cam Advanced available', 'KB-Cam Advanced not available')]
    colors2PrintSCamAvail = [colors.blue, colors.red]
    scamAvailData = {'KB-Cam Advanced available': [], 'KB-Cam Advanced not available': []}
    for totalTime, availTime in zip(totalStatsDataWithFWSDF_OfflineAlgo['Total time'], totalStatsDataWithFWSDF_OfflineAlgo['Availability time']):
      scamAvailData['KB-Cam Advanced available'].append(availTime / totalTime * 100)
      scamAvailData['KB-Cam Advanced not available'].append((totalTime - availTime) / totalTime * 100)
    d = drawHorizontalBarChart(w, 7*cm, 1.5*cm, 1*cm, colors2PrintSCamAvail, scamAvailData, scamAvail, percent=True, incSum=False)
    elements.append(d)
  else:
    ptext = "Data not available!"
    elements.append(plat.Paragraph(ptext, styles['Normal']))
  
  # add appendix ---------------------------------------------------------------
  elements.append(plat.NextPageTemplate('Landscape'))
  elements.append(plat.PageBreak())
  headingText = "<seq id='%(sectionNoSub)s'/>. Appendix" % headingTextMap
  addHeadingToPDF(elements, headingText, styles['Heading1'])
  ptext = "The table below shows the outcome of the summarization of the results of false warning evaluation on the evaluated measurements."
  elements.append(plat.Paragraph(ptext, styles['Normal']))
  
  appTableStyle = list(DEFAULT_TABLE_STYLE)
  cvr3DataTmp = []
  cvr2DataTmp = []
  commonTmp = []
  for colNum, col in enumerate(appendixTable.titleRow):
    if col.split('\n')[-1] == '(CVR3)':
      cvr3DataTmp.append(colNum)
    elif col.split('\n')[-1] == '(CVR2)':
      cvr2DataTmp.append(colNum)
    elif col.split('\n')[0] == 'Common':
      commonTmp.append(colNum)
  cvr3DataStart = cvr3DataTmp[0]
  cvr2DataStart = cvr2DataTmp[0]
  classifDataStart = cvr2DataTmp[-1] + 1
  commonStart = commonTmp[0]
  totalStart = appendixTable.titleCol.index('Total:') + 1
  appTableStyle.append(('LINEAFTER', (0, 0), (0, -1), 1.75, reportlab.lib.colors.black))
  appTableStyle.append(('LINEAFTER', (cvr3DataStart, 0), (cvr3DataStart, -1), 1.75, reportlab.lib.colors.black))
  appTableStyle.append(('LINEAFTER', (cvr2DataStart, 0), (cvr2DataStart, -1), 1.75, reportlab.lib.colors.black))
  appTableStyle.append(('LINEAFTER', (classifDataStart, 0), (classifDataStart, -1), 1.75, reportlab.lib.colors.black))
  appTableStyle.append(('LINEAFTER', (commonStart, 0), (commonStart, -1), 1.75, reportlab.lib.colors.black))
  appTableStyle.append(('LINEABOVE', (0, totalStart), (-1, totalStart), 2.25, reportlab.lib.colors.black))
  
  appTable = appendixTable.getPrintable()
  t=plat.Table(appTable, repeatRows=appTable[0])
  t.setStyle(plat.TableStyle(appTableStyle))
  elements.append(t)
  
  # write the document to disk -------------------------------------------------
  doc.multiBuild(elements)
  pass

# acquire command line parameters ----------------------------------------------
try:
  batchDir = sys.argv[1] # command line parameter should be the location of the folder containing the batch files of measurement reports
  measDatesFileDir = sys.argv[2] # command line parameter should be the location of the text file containing the measurement dates for document creation
except IndexError:
  print >> sys.stderr, ("Please provide the appropriate commands: \n"
                        "    1. location of the folder containing the batch files of measurement reports\n"
                        "    2. location of the text file containing the measurement dates for document creation")
  exit()

# read in measurement dates for report generation ------------------------------
measDates = []
try:
  measDatesTxt = open(measDatesFileDir, 'rb')
  for measDate in measDatesTxt:
    measDates.append(measDate.strip())
finally:
  measDatesTxt.close()

# run analyze to generate necessary data as CSV --------------------------------
if os.path.exists(os.path.join(batchDir, CSV_FOLDER_NAME)):                     
  for root, dirs, filenames in os.walk(os.path.join(batchDir, CSV_FOLDER_NAME)):
    for filename in filenames:                                                  
      os.remove(os.path.join(root, filename))                                   

subprocess.call("%s -m view --export %s" % (PYTHONEXE, TMPCONFIGFILE))
try:
  for measDate in measDates:
    batchLoc = os.path.join(batchDir, '%s_%s.xml' % (BATCH_NAME, measDate))
    repDir = os.path.join(batchDir, measDate)
    print measDate
    subprocess.call('%s -m analyze --nonav -b %s -u %s --repdir %s -n iAnalyze \
                    -i +analyzeAEBSFalseWarnStatistic -n analyzeAEBSFalseWarnStatistic \
                    -p +analyzeAEBSFalseWarnStatistic.HIDECOMMON'
                    % (PYTHONEXE,
                       batchLoc,
                       BACKUP,
                       repDir))
    print ''
finally:
  subprocess.call("%s -m view --norun --push %s" % (PYTHONEXE, TMPCONFIGFILE))
  os.remove(TMPCONFIGFILE)

# create documentation ---------------------------------------------------------
if os.path.exists(os.path.join(batchDir, CSV_FOLDER_NAME)):
  # acquire generated data from CSV files --------------------------------------
  csvFilesReadInFW = {}
  csvFilesReadInFWExBrTu = {}
  csvFilesReadInFWWithSDF_offline = {}
  csvFilesReadInFWWithSDF_online = {}
  csvFilesReadInFWCateg = {}
  csvFilesReadInFWCateg_KB = {}
  csvFilesReadInOO = {}
  for root, dirs, filenames in os.walk(os.path.join(batchDir, CSV_FOLDER_NAME)):
    for filename in sorted(filenames):
      if fnmatch.fnmatch(filename, '*.csv'):
        try:
          csvFile = open(os.path.join(root, filename), 'rb')
          fileDialect = csv.Sniffer().sniff(csvFile.read())
          csvFile.seek(0)
          inputCSV = csv.DictReader(csvFile, dialect=fileDialect)
          
          dataDate, dataType = os.path.splitext(filename)[0].split('_')
          
          if dataType =='FalseWarnings':
            falseWarningsHeader = inputCSV.fieldnames
            csvData = {}
            for row in inputCSV:
              for key in row.keys():
                if key not in ('CVR2 available', 'CVR3 available'):
                  row[key] = float(row[key])
                else:
                  row[key] = row[key]
              csvData.update(**row)
            csvFilesReadInFW[dataDate] = csvData
          elif dataType =='FalseWarningsExBridgeTunnel':
            csvData = {}
            for row in inputCSV:
              for key in row.keys():
                row[key] = float(row[key])
              csvData.update(**row)
            csvFilesReadInFWExBrTu[dataDate] = csvData
          elif dataType == 'FalseWarningsWithSDF-OfflineAlgo':
            csvData = {}
            for row in inputCSV:
              for key in row.keys():
                row[key] = float(row[key])
              csvData.update(**row)
            csvFilesReadInFWWithSDF_offline[dataDate] = csvData
          elif dataType == 'FalseWarningsWithSDF-OnlineAlgo':
            csvData = {}
            for row in inputCSV:
              for key in row.keys():
                row[key] = float(row[key])
              csvData.update(**row)
            csvFilesReadInFWWithSDF_online[dataDate] = csvData
          elif dataType == 'FalseWarningsCategorized':
            categFWHeaders = inputCSV.fieldnames
            csvData = {}
            for row in inputCSV:
              for key in row.keys():
                rowDict = csvData.setdefault(key, [])
                if key not in ('Kind of warning',):
                  rowDict.append(int(row[key]))
                else:
                  rowDict.append(row[key])
            csvFilesReadInFWCateg[dataDate] = csvData
          elif dataType == 'FalseWarnCateg-KBinfl':
            #categFWHeaders = inputCSV.fieldnames
            csvData = {}
            for row in inputCSV:
              for key in row.keys():
                rowDict = csvData.setdefault(key, [])
                if key not in ('Kind of warning',):
                  rowDict.append(int(row[key]))
                else:
                  rowDict.append(row[key])
            csvFilesReadInFWCateg_KB[dataDate] = csvData
          elif dataType == 'OverheadObjects':
            overheadObjectHeader = inputCSV.fieldnames
            csvData = {}
            for row in inputCSV:
              for key in row.keys():
                rowDict = csvData.setdefault(key, [])
                if (key != 'Measurement' and key != 'Overhead object type') and row[key] != 'n/a':
                  rowDict.append(float(row[key]))
                else:
                  rowDict.append(row[key])
            csvFilesReadInOO[dataDate] = csvData
          
        finally:
          csvFile.close()
  
  # arrange acquired data to make it usable for documentation generation -------
  statsData = {}
  for key in csvFilesReadInFW[csvFilesReadInFW.keys()[0]].keys():
    statsData[key] = []
  
  statsDataWithFWExBrTu = {}
  for key in csvFilesReadInFWExBrTu[csvFilesReadInFWExBrTu.keys()[0]].keys():
      statsDataWithFWExBrTu[key] = []
  
  statsDataFWWithSDF_offline = {}
  for key in csvFilesReadInFWWithSDF_offline[csvFilesReadInFWWithSDF_offline.keys()[0]].keys():
    statsDataFWWithSDF_offline[key] = []
  
  statsDataFWWithSDF_online = {}
  for key in csvFilesReadInFWWithSDF_online[csvFilesReadInFWWithSDF_online.keys()[0]].keys():
    statsDataFWWithSDF_online[key] = []
  
  measDateFromCSV = []
  for date in sorted(csvFilesReadInFW.keys()):
    measDateFromCSV.append(date)
    for stat in csvFilesReadInFW[date].keys():
      statsData[stat].append(csvFilesReadInFW[date][stat])
  statsData.update(Date=measDateFromCSV)
  
  measDateFromCSV = []
  for date in sorted(csvFilesReadInFWExBrTu.keys()):
    measDateFromCSV.append(date)
    for stat in csvFilesReadInFWExBrTu[date].keys():
      statsDataWithFWExBrTu[stat].append(csvFilesReadInFWExBrTu[date][stat])
  statsDataWithFWExBrTu.update(Date=measDateFromCSV)
  
  measDateFromCSV = []
  for date in sorted(csvFilesReadInFWWithSDF_offline.keys()):
    measDateFromCSV.append(date)
    for stat in csvFilesReadInFWWithSDF_offline[date].keys():
      statsDataFWWithSDF_offline[stat].append(csvFilesReadInFWWithSDF_offline[date][stat])
  statsDataFWWithSDF_offline.update(Date=measDateFromCSV)
  
  measDateFromCSV = []
  for date in sorted(csvFilesReadInFWWithSDF_online.keys()):
    measDateFromCSV.append(date)
    for stat in csvFilesReadInFWWithSDF_online[date].keys():
      statsDataFWWithSDF_online[stat].append(csvFilesReadInFWWithSDF_online[date][stat])
  statsDataFWWithSDF_online.update(Date=measDateFromCSV)
  
  # determine commercial week number(s) to be used in the report title ---------
  measDatesSet = set(measDates)
  csvDateSet = set(statsData['Date'])
  datesWithStats = list(measDatesSet.intersection(csvDateSet))
  
  commWeekNumbers = {}
  for dateElem in sorted(datesWithStats):
    yearE, monthE, dayE = dateElem.split('-')
    dt = datetime.date(int(yearE), int(monthE), int(dayE))
    wk = dt.isocalendar()[1]
    wkDict = commWeekNumbers.setdefault(wk, [])
    wkDict.append(dateElem)
  
  # print the measurement dates for which no labels are available --------------
  datesWithnoLables = list(measDatesSet.difference(csvDateSet))
  if len(datesWithnoLables) != 0:
    print "No labels or votes for these days are available:"
    for date in datesWithnoLables:
      print "\t- %s" % date
  
  # define report title according to no. of weeks covered ----------------------
  if len(commWeekNumbers.keys()) == 0:
    print >> sys.stderr, "No requested file with labels found!"
    exit()
  elif len(commWeekNumbers.keys()) == 1:
    cwTitle = "CW%02d" % commWeekNumbers.keys()[0]
    cwTitleTmp = [cwTitle]
  else:
    commWeekNumbersNp = numpy.array(commWeekNumbers.keys())
    cwDiff = numpy.ones_like(commWeekNumbersNp)
    cwDiff[1:] = numpy.diff(commWeekNumbersNp)
    cwDiffMask = cwDiff != 1
    
    splitIndeces = []
    for numValue in commWeekNumbersNp[cwDiffMask]:
      splitIndeces.append(commWeekNumbers.keys().index(numValue))
    splitCWNumbers = numpy.split(commWeekNumbersNp, splitIndeces)
    
    cwTitleTmp = []
    for splitCWNumber in splitCWNumbers:
      if len(splitCWNumber) != 1:
        cwTitleTmp.append("CW%02d-CW%02d" % (splitCWNumber[0], splitCWNumber[-1]))
    cwTitleTmp.extend(["CW%02d" % cwNum for cwNum in commWeekNumbersNp[cwDiff != 1]])
    cwTitleTmp = sorted(cwTitleTmp)
    cwTitle = ",".join(cwTitleTmp)
  
  # create table for Appendix --------------------------------------------------
  appendixFWTableHeader = list(falseWarningsHeader)
  appendixFWTableHeader.remove('CVR2 available')
  appendixFWTableHeader.remove('CVR3 available')
  appendixTable_titleRow = [headerCell.replace(' ', '\n') for headerCell in appendixFWTableHeader]
  appendixTable_titleCol = []
  appendixTable_data = []
  statsDataTab = []
  statsDataTab.append(statsData['Date'])
  for key in appendixFWTableHeader:
    if key == 'Date':
      continue
    if key in ("Rural km", "City km", "Highway km"):
      statsDataTab.append(statsData[key])
    else:
      tmp = []
      for value in statsData[key]:
        tmp.append(int(value))
      statsDataTab.append(tmp)
  
  for row in sorted(zip(*statsDataTab), key=lambda elem: elem[0]):
    row = list(row)
    appendixTable_data.append(row[1:])
    appendixTable_titleCol.append(row[0])
  
  summedData=[]
  for data4Sum in zip(*appendixTable_data):
    summedData.append(sum(data4Sum))
  appendixTable_data.append(summedData)
  appendixTable_titleCol.append("Total:")
  
  appendixTable = measproc.Table(appendixTable_data, titleRow=appendixTable_titleRow, titleCol=appendixTable_titleCol, cornerCell="Date")
  
  # create contingency tables for false warnings -----------------------------------------
  warnTypes = ['acoustic_warn', 'part_brake', 'emer_brake', 'Total']
  contigTables_titleCol = ['W', 'W-P', 'W-P-E', 'Total']
  contigTables_titleRow = ['Moving', 'Stationary', 'Total']
  
  radarContigTable_totalData = []
  sdfContigTable_totalData = []
  radarContigTableKBinfl_totalData = []
  sdfContigTableKBinfl_totalData = []
  for contigdata in [[0] * len(contigTables_titleRow)] * len(contigTables_titleCol):
    radarContigTable_totalData.append(contigdata[:])
    sdfContigTable_totalData.append(contigdata[:])
    radarContigTableKBinfl_totalData.append(contigdata[:])
    sdfContigTableKBinfl_totalData.append(contigdata[:])
  
  for date in csvFilesReadInFWCateg.keys():
    for dataKey, data in csvFilesReadInFWCateg[date].iteritems():
      for warnType in warnTypes:
        tblIndex = csvFilesReadInFWCateg[date]['Kind of warning'].index(warnType)
        if 'Radar' in dataKey:
          if 'moving' in dataKey:
            radarContigTable_totalData[tblIndex][0] += data[tblIndex]
          if 'stationary' in dataKey:
            radarContigTable_totalData[tblIndex][1] += data[tblIndex]
          if 'total' in dataKey:
            radarContigTable_totalData[tblIndex][2] += data[tblIndex]
        if 'SDF' in dataKey:
          if 'moving' in dataKey:
            sdfContigTable_totalData[tblIndex][0] += data[tblIndex]
          if 'stationary' in dataKey:
            sdfContigTable_totalData[tblIndex][1] += data[tblIndex]
          if 'total' in dataKey:
            sdfContigTable_totalData[tblIndex][2] += data[tblIndex]
  
  for date in csvFilesReadInFWCateg_KB.keys():
    for dataKey, data in csvFilesReadInFWCateg_KB[date].iteritems():
      for warnType in warnTypes:
        tblIndex = csvFilesReadInFWCateg_KB[date]['Kind of warning'].index(warnType)
        if 'Radar' in dataKey:
          if 'moving' in dataKey:
            radarContigTableKBinfl_totalData[tblIndex][0] += data[tblIndex]
          if 'stationary' in dataKey:
            radarContigTableKBinfl_totalData[tblIndex][1] += data[tblIndex]
          if 'total' in dataKey:
            radarContigTableKBinfl_totalData[tblIndex][2] += data[tblIndex]
        if 'SDF' in dataKey:
          if 'moving' in dataKey:
            sdfContigTableKBinfl_totalData[tblIndex][0] += data[tblIndex]
          if 'stationary' in dataKey:
            sdfContigTableKBinfl_totalData[tblIndex][1] += data[tblIndex]
          if 'total' in dataKey:
            sdfContigTableKBinfl_totalData[tblIndex][2] += data[tblIndex]
  
  fwContigTables = {
      'radar_only': measproc.Table(radarContigTable_totalData,
                                   titleRow=contigTables_titleRow,
                                   titleCol=contigTables_titleCol),
      'sdf':  measproc.Table(sdfContigTable_totalData,
                             titleRow=contigTables_titleRow,
                             titleCol=contigTables_titleCol)}
  
  fwContigTablesKBinfl = {
      'radar_only': measproc.Table(radarContigTableKBinfl_totalData,
                                   titleRow=contigTables_titleRow,
                                   titleCol=contigTables_titleCol),
      'sdf':  measproc.Table(sdfContigTableKBinfl_totalData,
                             titleRow=contigTables_titleRow,
                             titleCol=contigTables_titleCol)}
  
  # set report folder ----------------------------------------------------------
  fileDir = os.path.join(batchDir, REP_FOLDER_NAME)
  if not os.path.exists(fileDir):
    os.makedirs(fileDir)
  
  # call createPDF function to create the report for the whole date interval ---
  fileName = 'EndurRun_FalseWarn_Conclusion_%s.pdf' % (cwTitle)
  fileLoc = os.path.join(fileDir, fileName)
  createPDF(fileLoc,
            statsData,
            cwTitleTmp,
            appendixTable,
            statsDataWithFWExBrTu,
            statsDataFWWithSDF_offline,
            statsDataFWWithSDF_online,
            fwContigTables,
            fwContigTablesKBinfl,
            commWeekNumbers)
  
  # write overhead object summary to CSV file for the whole date interval ------
  fileName = 'Overhead_Objects_on_%s.csv' % (cwTitle)
  fileLoc = os.path.join(fileDir, fileName)
  for index, date in enumerate(sorted(csvFilesReadInOO.keys())):
    if index == 0:
      data2Print = dict(csvFilesReadInOO[date])
    else:
      for key in csvFilesReadInOO[date].keys():
        data2Print[key].extend(csvFilesReadInOO[date][key])
  
  csvWrite = csv.writer(open(fileLoc, 'wb'), delimiter=':', lineterminator='\n')
  csvWrite.writerow(overheadObjectHeader)
  for index in xrange(len(data2Print['Measurement'])):
    csvWrite.writerow([data2Print[key][index] for key in overheadObjectHeader])
  
  # for the last week create separate report and overhead object summary -------
  if len(commWeekNumbers.keys()) > 1:
    lastWeek = sorted(commWeekNumbers.keys())[-1]
    startOfLastWeek = sorted(commWeekNumbers[lastWeek])[0]
    
    cwTitle = "CW%02d" % lastWeek
    cwTitleTmp = [cwTitle]
    fileName = 'EndurRun_FalseWarn_Conclusion_%s.pdf' % (cwTitle)
    fileLoc = os.path.join(fileDir, fileName)
    # acquire data for the last week -------------------------------------------
    statsDataLast = {}
    startIndex = statsDataWithFWExBrTu['Date'].index(startOfLastWeek)
    for statKey in statsData.keys():
      statsDataLast[statKey] = statsData[statKey][startIndex:]
    appendixTableLast = measproc.Table(appendixTable.data[-2:],
                                       titleRow=appendixTable.titleRow,
                                       titleCol=appendixTable.titleCol[-2:],
                                       cornerCell=appendixTable.cornerCell)
    statsDataWithFWExBrTuLast = {}
    startIndex = statsDataWithFWExBrTu['Date'].index(startOfLastWeek)
    for statKey in statsDataWithFWExBrTu.keys():
      statsDataWithFWExBrTuLast[statKey] = statsDataWithFWExBrTu[statKey][startIndex:]
    statsDataFWWithSDF_offlineLast = {}
    startIndex = statsDataFWWithSDF_offline['Date'].index(startOfLastWeek)
    for statKey in statsDataFWWithSDF_offline.keys():
      statsDataFWWithSDF_offlineLast[statKey] = statsDataFWWithSDF_offline[statKey][startIndex:]
    statsDataFWWithSDF_onlineLast = {}
    startIndex = statsDataFWWithSDF_online['Date'].index(startOfLastWeek)
    for statKey in statsDataFWWithSDF_online.keys():
      statsDataFWWithSDF_onlineLast[statKey] = statsDataFWWithSDF_online[statKey][startIndex:]
    
    radarContigTable_lastData = []
    sdfContigTable_lastData = []
    radarContigTableKBinfl_lastData = []
    sdfContigTableKBinfl_lastData = []
    for contigdata in [[0] * len(contigTables_titleRow)] * len(contigTables_titleCol):
      radarContigTable_lastData.append(contigdata[:])
      sdfContigTable_lastData.append(contigdata[:])
      radarContigTableKBinfl_lastData.append(contigdata[:])
      sdfContigTableKBinfl_lastData.append(contigdata[:])
    
    startIndex = sorted(csvFilesReadInFWCateg.keys()).index(startOfLastWeek)
    daysOfLastWeek = sorted(csvFilesReadInFWCateg.keys())[startIndex:]
    for date in daysOfLastWeek:
      for dataKey, data in csvFilesReadInFWCateg[date].iteritems():
        for warnType in warnTypes:
          tblIndex = csvFilesReadInFWCateg[date]['Kind of warning'].index(warnType)
          if 'Radar' in dataKey:
            if 'moving' in dataKey:
              radarContigTable_lastData[tblIndex][0] += data[tblIndex]
            if 'stationary' in dataKey:
              radarContigTable_lastData[tblIndex][1] += data[tblIndex]
            if 'total' in dataKey:
              radarContigTable_lastData[tblIndex][2] += data[tblIndex]
          if 'SDF' in dataKey:
            if 'moving' in dataKey:
              sdfContigTable_lastData[tblIndex][0] += data[tblIndex]
            if 'stationary' in dataKey:
              sdfContigTable_lastData[tblIndex][1] += data[tblIndex]
            if 'total' in dataKey:
              sdfContigTable_lastData[tblIndex][2] += data[tblIndex]
    
    startIndex = sorted(csvFilesReadInFWCateg_KB.keys()).index(startOfLastWeek)
    daysOfLastWeek = sorted(csvFilesReadInFWCateg_KB.keys())[startIndex:]
    for date in daysOfLastWeek:
      for dataKey, data in csvFilesReadInFWCateg_KB[date].iteritems():
        for warnType in warnTypes:
          tblIndex = csvFilesReadInFWCateg_KB[date]['Kind of warning'].index(warnType)
          if 'Radar' in dataKey:
            if 'moving' in dataKey:
              radarContigTableKBinfl_lastData[tblIndex][0] += data[tblIndex]
            if 'stationary' in dataKey:
              radarContigTableKBinfl_lastData[tblIndex][1] += data[tblIndex]
            if 'total' in dataKey:
              radarContigTableKBinfl_lastData[tblIndex][2] += data[tblIndex]
          if 'SDF' in dataKey:
            if 'moving' in dataKey:
              sdfContigTableKBinfl_lastData[tblIndex][0] += data[tblIndex]
            if 'stationary' in dataKey:
              sdfContigTableKBinfl_lastData[tblIndex][1] += data[tblIndex]
            if 'total' in dataKey:
              sdfContigTableKBinfl_lastData[tblIndex][2] += data[tblIndex]
    
    fwContigTablesLast = {
         'radar_only': measproc.Table(radarContigTable_lastData,
                                     titleRow=contigTables_titleRow,
                                     titleCol=contigTables_titleCol),
         'sdf': measproc.Table(sdfContigTable_lastData,
                               titleRow=contigTables_titleRow,
                               titleCol=contigTables_titleCol)}
    
    fwContigTablesLastKBinfl = {
         'radar_only': measproc.Table(radarContigTableKBinfl_lastData,
                                     titleRow=contigTables_titleRow,
                                     titleCol=contigTables_titleCol),
         'sdf': measproc.Table(sdfContigTableKBinfl_lastData,
                               titleRow=contigTables_titleRow,
                               titleCol=contigTables_titleCol)}
    
    commWeekNumbersLast = {lastWeek: commWeekNumbers[lastWeek]}
    
    # create PDF document ------------------------------------------------------
    createPDF(fileLoc,
              statsDataLast,
              cwTitleTmp,
              appendixTableLast,
              statsDataWithFWExBrTuLast,
              statsDataFWWithSDF_offlineLast,
              statsDataFWWithSDF_onlineLast,
              fwContigTablesLast,
              fwContigTablesLastKBinfl,
              commWeekNumbersLast)
    
    fileName = 'Overhead_Objects_on_%s.csv' % (cwTitle)
    fileLoc = os.path.join(fileDir, fileName)
    for index, date in enumerate(sorted(commWeekNumbers[lastWeek])):
      if index == 0:
        data2Print = dict(csvFilesReadInOO[date])
      else:
        for key in csvFilesReadInOO[date].keys():
          data2Print[key].extend(csvFilesReadInOO[date][key])
    
    csvWrite = csv.writer(open(fileLoc, 'wb'), delimiter=':', lineterminator='\n')
    csvWrite.writerow(overheadObjectHeader)
    for index in xrange(len(data2Print['Measurement'])):
      csvWrite.writerow([data2Print[key][index] for key in overheadObjectHeader])
  
else:
  print >> sys.stderr, "Location of CSV files not found!"
  exit()

