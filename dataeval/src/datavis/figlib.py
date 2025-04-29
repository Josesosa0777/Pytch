import re
import sys
import numpy
import logging
import StringIO
import matplotlib as mpl

import PIL
from PySide import QtCore, QtGui

from measproc.IntervalList import argsort

def det_figure_nr(title, figureNr):
  original = figureNr
  fignums = []
  logger = logging.getLogger()
  if figureNr is None:
    fignums = [x.num for x in mpl._pylab_helpers.Gcf.get_all_fig_managers()]
    try:
      figureNr = fignums[-1]
      if figureNr == 0:
        figureNr = 1
    except IndexError:
      figureNr = 1
  while True:
    if mpl.pyplot.figure(figureNr).number in fignums:
      figureNr += 1
    else:
      if original is not None and figureNr != original:
        logger.info('%s figure number is changed from %d to %d!\n' %(title, original, figureNr))
      break
  return figureNr

def copyContentToClipboard(fig):
  """
  Copy figure to the clipboard as a bitmap image.
  The reason for separating this function is that cTrackNavigator and
  cAxesNavigator have no common parent class, although both use the same type
  of figure for plotting.

  :Parameters:
    fig : matplotlib.figure.Figure
  """
  # Save as png
  imageFileAsPng = StringIO.StringIO()
  fig.savefig(imageFileAsPng, format='png', bbox_inches='tight')
  # Convert to bitmap
  imageFileAsPng.seek(0)
  image = PIL.Image.open(imageFileAsPng)

  width, height = image.size
  data = image.tostring('raw','RGBA')
  #from http://stackoverflow.com/questions/13302908/better-way-of-going-from-pil-to-pyside-qimage
  #if i don't use this data mixing, the colors won't be the same
  #Hint: PIL uses RGBA format, but PySide uses ARGB format
  data = ''.join([''.join(i) for i in zip(data[2::4],data[1::4],data[0::4],data[3::4])])
  qt_image = QtGui.QImage(data, width, height, QtGui.QImage.Format_ARGB32)

  clipboard = QtGui.QApplication.clipboard()
  clipboard.clear()
  clipboard.setPixmap(QtGui.QPixmap.fromImage(qt_image))

  imageFileAsPng.close()
  return

def copyContentToFile(fig, file, format=None):
  """
  Copy figure to the specified file in the specified format.
  No other parameters are allowed in order to ensure compatibility with other navigators.

  :Parameters:
    fig : matplotlib.figure.Figure
    file : str or file
    format : str
  """
  fig.savefig(file, format=format, bbox_inches='tight')
  return

def parseGeometryString(geometry):
  """
  Parse the conventional geometry string used for Tk windows.
  The format is:
    "%dx%d%+d%+d" % (width, height, xoffset, yoffset)
  e.g., "640x480+10+20"

  :Parameters:
    geometry: str
  :ReturnType: tuple
    (x, y, w, h)
  """
  sizePattern = re.compile('(\d+)x(\d+).*')
  size = sizePattern.match(geometry)
  w, h = map(int, size.groups()) if size else (None, None)
  locPattern = re.compile('.*\+(-?\d+)\+(-?\d+)')
  loc = locPattern.match(geometry)
  x, y = map(int, loc.groups()) if loc else (None, None)
  return x, y, w, h

def buildGeometryString(x, y, w, h):
  """
  Build the conventional geometry string used for Tk windows.
  The format is:
    "%dx%d%+d%+d" % (width, height, xoffset, yoffset)
  e.g., "640x480+10+20" or "640x480+-10+-20"

  :Parameters:
    x: int
    y: int
    w: int
    h: int
  :ReturnType: str
  """
  geometry = ''
  if w is not None and h is not None:
    geometry = '%dx%d' % (w, h)
  if x is not None and y is not None:
    geometry += '+%d+%d' % (x, y)
  return geometry

def makeStringFromQtGeometry(geometry):
  x = geometry.x()
  y = geometry.y()
  w = geometry.width()
  h = geometry.height()
  return '%dx%d+%d+%d' % (w, h, x, y)

def buildQtGeometryFromString(geomString):
  x, y, w, h = parseGeometryString(geomString)
  qtGeometry = QtCore.QRect(x, y, w, h)
  return qtGeometry

def generateWindowId(idBase=''):
  """
  Generate a window identification string based on the given parameter. The
  resulting ID will contain only numbers, letters, '-' and '_'.

  :Parameters:
    idBase : str
      Basis for ID generation.
  :ReturnType: str
  """
  windowId  = idBase.replace(' ', '_')
  idPattern = re.compile('[^\w-]')
  windowId  = idPattern.sub('', windowId)
  if not windowId:
    windowId = 'unidentified_window'
  return windowId

def setAxesLimits(fig, limits, yAutoZoom=False):
  """
  Set the limits of all axes on the given figure.

  :Parameters:
    fig : `matplotlib.figure.Figure`
    limits : list or tuple
      Float or None can be given for every limit.
      [x_min<float>, x_max<float>, y_min<float>, y_max<float>]
    yAutoZoom : bool
      Flag to indicate automatic limit calculation for non-provided values in
      y direction.
  """
  limits.extend( [None] * (4-len(limits)) )
  if yAutoZoom and (limits[2] is None or limits[3] is None):
    for ax in fig.axes:
      x_min, x_max, y_min, y_max = limits[0:4]
      ax.set_xlim(x_min, x_max)
      if x_min is None or x_max is None:
        x_min, x_max = ax.get_xlim()
      y_minList = []
      y_maxList = []
      for dataLine in ax.lines:
        if not dataLine.get_visible() or dataLine.get_linewidth() <= 0.0:
          # exclude invisible lines from limit calculation
          continue
        try:
          # up to mpl 1.1.1
          x_isdata = dataLine.x_isdata
          y_isdata = dataLine.y_isdata
        except AttributeError:
          # since mpl 1.2.0
          transf = dataLine.get_transform()
          x_isdata, y_isdata = transf.contains_branch_seperately(ax.transData)
        if not y_isdata:
          # exclude vertical lines from limit calculation
          continue
        if not x_isdata:
          # special handling for horizontal lines
          y = dataLine.get_ydata()[0]
          y_minList.append(y)
          y_maxList.append(y)
          continue
        time, value = dataLine.get_data()
        visibleValues = value[numpy.where((~numpy.isnan(value)) & (time >= x_min) & (time <= x_max))]
        if visibleValues.size > 0:
          y_minList.append(numpy.min(visibleValues))
          y_maxList.append(numpy.max(visibleValues))
      y_min = min(y_minList) if y_min is None and len(y_minList) != 0 else y_min
      y_max = max(y_maxList) if y_max is None and len(y_maxList) != 0 else y_max
      if (y_min is not None and y_max is not None) and numpy.allclose(y_min, y_max):
        ax.set_ylim(y_min-0.01, y_max+0.01)
      else:
        ax.set_ylim(y_min, y_max)
  else:
    for ax in fig.axes:
      ax.set_xlim(limits[0:2])
      ax.set_ylim(limits[2:4])
  fig.canvas.draw()
  return

def adjustYLimits(fig):
  """
  Adjust the y limits of all axes on the given figure to the corresponding codomains.

  :Parameters:
    fig : `matplotlib.figure.Figure`
  """
  setAxesLimits(fig, [], yAutoZoom=True)
  return

def argbalance(data):
  """
  Create balanced index representation of data (suitable for pie charts).
  Returns the indices of the data elements in the following order:
    smallest, largest, 2nd smallest, 2nd largest, 3rd smallest, ...

  :Parameters:
    data : sequence
  :ReturnType: list<int>
  """
  indices = argsort(data)
  if len(data) % 2 == 1:
    # extend indices with dummy data if number of inputs is odd
    indices.append(None)
  balanced = []
  for small,large in zip(indices[::2], indices[::-2]):
    if large is not None:
      balanced.append(large)
    balanced.append(small)
  return balanced
