#!/usr/bin/env python

import matplotlib as mpl
if mpl.rcParams['backend.qt4']!='PySide':
  mpl.use('Qt4Agg')
  mpl.rcParams['backend.qt4']='PySide'

from PySide import QtCore, QtGui
  
from Synchronizer import cNavigator
from PlotNavigator import cAxesNavigator


class cConcurrence(cNavigator):
  def __init__(self, ax):
    """
    :Parameters:
      name : str
    """
    cNavigator.__init__(self)
    self.ax = ax
    pass
    
  def seekWindow(self, draw=True):
    self.ax.timemarker.set_xdata(self.time)
    if draw:
      self.ax.figure.centralize(self.time)
      self.ax.figure.canvas.draw()
    return
  
  def closeEvent(self, event):
    self.ax.figure.delaxes(self.ax)
    cNavigator.closeEvent(self, event)
    pass
  
  def start(self):
    pass
  
class cConcurrenceNavigator(cAxesNavigator, QtGui.QMainWindow):
  """Display intervals of reports in batch groups which have the same title"""
  def __init__(self, title='', fgnr=None):
    """
    :Parameters:
      title : str
      fgnr : int
        Default is None.
    """
    QtGui.QMainWindow.__init__(self)
    cAxesNavigator.__init__(self, title, fgnr, 'CN')
    
    self.setWindowTitle('')
    
    self.help_font=mpl.font_manager.FontProperties('monospace', 'normal', 'normal', 'normal', 'normal', 'small')
    """:type: FontProperties
    Font for the help"""
    self.help = self.fig.text(0.1,0.5,
    "Rectangle show the interval of the report's event.\n"
    "Elipse show the interval of the report's event in case of zero length interval.\n\n"
    'Keyboard shortcuts:\n\n'
    'F1  Show/hide this help screen\n'
    , visible=False, fontproperties=self.help_font, bbox=dict(facecolor='LightYellow', pad=20))
    """:type: Text
    Online help text"""
    
    self.time = 0
    self.ax2con = {}
    self.fig.centralize = self.centralize
    self.canvas.mpl_connect('button_press_event', self.onFigureClickPress)
    self.canvas.mpl_connect('key_press_event', self.onFigureKeyPress)
    self.setCentralWidget(self.canvas)
    self.addToolBar(QtCore.Qt.BottomToolBarArea, self.toolbar)
    pass
  
  def regConcurrence(self, ax, sync, title):
    ax.set_title(title)
    con = cConcurrence(ax)
    self.ax2con[ax] = con    
    sync.addClient(con)
    return ax
  
  def addConcurrence(self, Sync, Title):
    Ax = self.regAxis(False, False, 0, 0, 1.)
    Con = self.regConcurrence(Ax, Sync, Title)
    return Con
 
  def setAllXlim(self, Xmin, Xmax):
    for ax in self.fig.axes:
      self.setXlim(ax, Xmin, Xmax)
    pass
    
  def onFigureClickPress(self, event):
    """
    Event handler for mouse click press event.
    Single mouse click: call `seekCallback` and repositioning `timemarker` of 
    the `fig.axes`.
    Area selection: call `setROI` and `setROICallback`.
    """
    ax = event.inaxes
    if ax in self.fig.axes:
      try:
        leg = self.findLegend(ax, event)
      except ValueError:
        if self.toolbar.mode not in ['zoom rect', 'pan/zoom']:
          try:
            bar = self.findBar(ax, event)
          except ValueError:
            if event.button == 1:
              self.time = event.xdata
              for ax in self.fig.axes:                
                con = self.ax2con[ax]
                con.seekSignal.signal.emit(event.xdata)
                con.time = event.xdata
                con.seekWindow(draw=False)
                pass
              self.centralize(event.xdata)
              self.canvas.draw()
          else:
            if event.button == 1:
              text = ax.bar2text[bar]
              vis = text.get_visible()
              vis = not vis
              text.set_visible(vis)
              self.canvas.draw()
    pass    
  
  def keyPressEvent(self, event):
    self.canvas.keyPressEvent(event)
    return
  
  def onFigureKeyPress(self, event):
    if event.key == 'F1':
      self.help.set_visible(not self.help.get_visible())
      bx = self.help.get_window_extent()
      bx = bx.inverse_transformed(self.fig.transFigure)
      self.help.set_position(((1-bx.width)/2.,(1-bx.height)/2.))
    elif event.key == ' ':
      for ax in self.fig.axes:
        con = self.ax2con[ax]
        if con.playing:
          con.onPause(con.time)
        else:
          con.onPlay(con.time)
        con.seekWindow(draw=False)
    self.canvas.draw()
    pass
  
  def setValueForLegend(self, ax, x):
    if ax not in self.ax2con:
      return
    con = self.ax2con[ax]
    con.time = x
    con.seekWindow(draw=False)
    self.canvas.draw()
    if not self.isHidden():
      self.centralize(x)
    return
    
  
if __name__ == '__main__':
  import sys

  import numpy

  from Synchronizer import cSynchronizer
  from PlotNavigator import cPlotNavigator

  app = QtGui.QApplication([])

  navigator = cConcurrenceNavigator()
  syncs = []
  sync2plot = {}
  for i in range(2):
    sync = cSynchronizer()
    syncs.append(sync)
    plots = set()
    sync2plot[sync] = plots
    for i in range(2):
      plot = cPlotNavigator()
      plots.add(plot)

  for sync, plots in sync2plot.iteritems():
    for plot in plots:
      t = numpy.arange(0,400,0.01)
      plot.addsignal('sine' ,  [t, numpy.sin(t)])
      sync.addClient(plot)
    navigator.addConcurrence(sync, str(sync))
    sync.start()
    sync.show()
  navigator.start()
  navigator.show()

  sys.exit(app.exec_())