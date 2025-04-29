import matplotlib

if matplotlib.rcParams['backend.qt4']!='PySide':
  matplotlib.use('Qt4Agg')
  matplotlib.rcParams['backend.qt4']='PySide'

from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT

from PySide import QtCore, QtGui

from PlotNavigator import cPylabNavigator
from Synchronizer import cNavigator

class MatplotlibNavigator(cPylabNavigator, cNavigator):
  def __init__(self, title='', figureNr=None):
    cPylabNavigator.__init__(self, title, figureNr, 'MN %d %s')
    cNavigator.__init__(self, title=title)

    self.setCentralWidget(self.canvas)
    self.addToolBar(QtCore.Qt.BottomToolBarArea, self.toolbar)

    self.canvas.mpl_connect('key_press_event', self.onFigureKeyPress)
    
    self.help_font = matplotlib.font_manager.FontProperties('monospace', 
                                                            'normal', 'normal',  
                                                            'normal', 'normal', 
                                                            'small')
    self.controlKeys = {
                        'F1'    : 'Show/hide this help screen',
                        'q'     : 'Copy current figure to the clipboard',
                        'space' : 'Start/stop playback',
                        }

    self.help = self.fig.text(0.1,0.5,
                              'Keyboard shortcuts:\n\n'
                              'F1                  %(F1)s\n'
                              'Space               %(space)s\n'
                              'q                   %(q)s\n' %self.controlKeys,
                              visible=False, fontproperties=self.help_font, 
                              bbox=dict(facecolor='LightYellow', pad=20))

    return

  def start(self):
    matplotlib._pylab_helpers.Gcf.set_active(self.figure_manager)
    return

  def keyPressEvent(self, event):
    self.canvas.keyPressEvent(event)
    return

  def onFigureResize(self, event):
    """
    Event handler for figure resize event. Figure is adjusted automatically,
    but figure's help text needs to be resized if displayed at the time of event.
    
    :Parameters:
      event : matplotlib.backend_bases.ResizeEvent
    :Return: None
    """
    self.resizeHelp()
    self.canvas.draw()
    return

  def resizeEvent(self, event):
    cNavigator.resizeEvent(self, event)
    new_size = event.size()
    canvas_width = new_size.width()
    canvas_height = new_size.height() - self.toolbar.height()
    self.canvas.resizeEvent(event)
    self.canvas.resize(canvas_width, canvas_height)
    self.onFigureResize(event)
    return

  def resizeHelp(self):
    bx = self.help.get_window_extent()
    bx = bx.inverse_transformed(self.fig.transFigure)
    self.help.set_position(((1-bx.width)/2.,(1-bx.height)/2.))
    self.canvas.draw()
    return

  def onFigureKeyPress(self, event):
    if event.key == 'q':
      self.copyContentToClipboard()
    elif event.key == ' ':
      # synchronizable interface callback
      if self.playing:
        self.onPause(self.time)
      else:
        self.onPlay(self.time)
    elif event.key == 'F1':
      self.help.set_visible(not self.help.get_visible())
      self.resizeHelp()
    elif event.key == 'k':
      for ax in self.fig.axes:
        if ax.get_xscale() == 'linear':
          ax.set_xscale('log')
        else:
          ax.set_xscale('linear')
    elif event.key == 'l':
      for ax in self.fig.axes:
        if ax.get_yscale() == 'linear':
          ax.set_yscale('log')
        else:
          ax.set_yscale('linear')
    self.canvas.draw()
    return
    
if __name__ == '__main__':
  import sys
  
  app =QtGui.QApplication([])
  
  pn = MatplotlibNavigator(title="foo")
  fig = pn.fig
  ax = fig.add_subplot(111)
  ax.plot((1,2,3), (4,5,6))
  ax.set_xlabel("time [s]")
  pn.start()
  pn.show()
  sys.exit(app.exec_())
