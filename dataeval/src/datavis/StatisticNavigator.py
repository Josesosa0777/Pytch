#!/usr/bin/python

import sys

import matplotlib
if matplotlib.rcParams['backend.qt4']!='PySide':
  matplotlib.use('Qt4Agg')
  matplotlib.rcParams['backend.qt4']='PySide'

from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D  # required to fix matplotlib's bug and avoid crash
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
import numpy
from PySide import QtGui, QtCore

from Synchronizer import cNavigator

class cStatisticNavigator(cNavigator):
  def __init__(self):
    cNavigator.__init__(self)

    self.fig = Figure()
    frame = QtGui.QFrame()
    canvas = FigureCanvasQTAgg(self.fig)
    canvas.setParent(self)
    self.setCentralWidget(canvas)
    pass

  def addStatistic(self, statistic):
    no_axes = len(statistic.Axes)
    if no_axes == 2:
      self.addStatistic3D(statistic)
    elif no_axes == 1:
      self.addStatistic2D(statistic)
    else:
      self.logger.info("Don't be silly!\n")
    pass

  def addStatistic2D(self, statistic):
    ax_pos = len(self.fig.axes) + 1
    ax = self.fig.add_subplot(ax_pos, 1, 1)
    x, = statistic.Axes
    x_ticks = numpy.arange(len(statistic.TickLabels[x]), dtype=float) + 0.1
    ax.bar(x_ticks, statistic.Array, 0.8)
    ax.set_xticks(x_ticks+0.4)
    ax.set_xticklabels(statistic.TickLabels[x])
    ax.set_xlabel(x)

    title = statistic.getTitle()
    ax.set_title(title)
    pass

  def addStatistic3D(self, statistic):
    ax_pos = len(self.fig.axes) + 1
    ax = self.fig.add_subplot(ax_pos, 1, 1, projection='3d')
    x, y = statistic.Axes

    x_ticks = numpy.arange(len(statistic.TickLabels[x]), dtype=float) + 0.1
    y_ticks = numpy.arange(len(statistic.TickLabels[y]), dtype=float) + 0.1

    for i, x_tick in enumerate(x_ticks):
      x_values  = x_tick * numpy.ones_like(y_ticks)
      z_values  = numpy.zeros_like(y_ticks)
      dz_values = statistic.Array[:][i]
      ax.bar3d(x_values, y_ticks, z_values, 0.8, 0.8, dz_values)

    ax.w_xaxis.set_ticklabels(statistic.TickLabels[x])
    ax.w_xaxis.set_ticks(x_ticks+0.4)
    ax.set_xlabel(x)

    ax.w_yaxis.set_ticklabels(statistic.TickLabels[y])
    ax.w_yaxis.set_ticks(y_ticks+0.4)
    ax.set_ylabel(y)

    ax.autoscale()
    title = statistic.getTitle()
    ax.set_title(title)
    pass

  def start(self):
    #filter the multiple instances of the axes
    axes = []
    for ax in self.fig.axes:
      if ax not in axes:
        axes.append(ax)
    fig_nr = len(axes)
    for i, ax in enumerate(axes):
      ax.change_geometry(fig_nr, 1, i+1)
    self.fig.canvas.draw()
    pass

if __name__ == '__main__':
  import os
  import sys
  import optparse

  import measproc.Statistic

  app = QtGui.QApplication([])
  save_path = r'C:\KBData\dataeval_test'
  xml_name =r'C:\KBData\sqlite\2012_11_14\2012_11_14\AEBS-RoadType-Milages.w_eqmr.xml'
  Statistic2D = measproc.Statistic.iStatistic(save_path)
  Statistic2D.Axes.append('bar')
  Statistic2D.TickLabels['bar'] = ['foo', 'baz']
  Statistic2D.Array = (2.0, 3.0)

  Statistic3D = measproc.Statistic.iStatistic(save_path)
  Statistic3D.Axes.append('foo')
  Statistic3D.Axes.append('bar')
  Statistic3D.TickLabels['foo'] = ['baz', 'test']
  Statistic3D.TickLabels['bar'] = ['egg', 'spam']
  Statistic3D.Array = ((4.0, 5.5),(3.0, 2.1), )
  # create navigator for the statistic
  StatNav = cStatisticNavigator()
  StatNav.addStatistic(Statistic2D)
  StatNav.addStatistic(Statistic3D)
  StatNav.start()
  StatNav.show()
  sys.exit(app.exec_())

  Statistic.save()
  Source.save()
