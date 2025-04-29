import os
import sys

import numpy
import pylab
from matplotlib.lines   import Line2D
from matplotlib.patches import Polygon

import interface
import measproc
from aebs.par import grouptypes

param = interface.NullParam

class cSearch(interface.iSearch):
  dep = 'fillAC100_Target@aebs.fill',
  title = 'AC100 FoV based on targets'
  ZERO_EPS = 1e-3
  R_MAX = 400

  def init(self):
    self.NONE_TYPE = self.get_grouptype('NONE_TYPE', prj='aebs.fill')
    return

  def fill(self):
    modules = self.get_modules()
    dep, = self.dep
    time, objects = modules.fill(dep)
    x = []
    y = []
    for o in objects:
      mask = (  (~(     (o['dx'] <= self.ZERO_EPS)
                 | (  (o['dx'] <= self.ZERO_EPS)
                    & (o['dy'] <= self.ZERO_EPS))))
             &         (o['dx'] <= self.R_MAX))
      x.append(o['dx'][mask])
      y.append(o['dy'][mask])
    x = numpy.concatenate(x)
    y = numpy.concatenate(y)
    return x, y

  R_SPLIT = 60
  ANGLE_STD_FILTER = 4
  FIG_X_LIM = -150, 150
  FIG_Y_LIM = 0, R_MAX
  def search(self, param, x, y):
    batch = self.get_batch()
    # calc view angles
    p = x.argsort()
    x = x[p]
    y = y[p]
    a = numpy.arctan2(-y, x)
    r = numpy.sqrt(x**2 + y**2)
    i = max(r.searchsorted(self.R_SPLIT, side='right')-1, 0)

    stat = measproc.cDinStatistic(self.title, [['viewangle', ['close', 'far']]])

    # calc close view angle
    ta = numpy.abs(a[:i]).max()
    stat.set([['viewangle', 'close']], numpy.degrees(ta))

    # calc far view angle
    ra  = a[i:]
    ra = numpy.abs(ra)
    ra = ra[ra < ra.std()*self.ANGLE_STD_FILTER].max()
    stat.set([['viewangle', 'far']], numpy.degrees(ra))

    batch.add_entry(stat, self.NONE)

    # create figure
    fig = pylab.figure()
    ax = fig.add_subplot(1,1,1)
    ax.set_xlim(self.FIG_X_LIM)
    ax.set_ylim(self.FIG_Y_LIM)
    ax.plot(y, x, '.', alpha=0.1)

    # draw close view angle field
    tx = x[i-1]
    ty = numpy.tan(ta) * tx
    p = numpy.array([[0, 0], [ty, tx], [-ty, tx]])
    p = Polygon(p, closed=True, color='r')
    ax.add_patch(p)

    # draw far view angle field
    rx = x[-1]
    ty = numpy.tan(ra) * tx
    ry = numpy.tan(ra) * rx
    p  = numpy.array([[ty, tx], [ry, rx], [-ry, rx], [-ty, tx]])
    p  = Polygon(p, closed=True, color='m')
    ax.add_patch(p)

    # write information to the figure
    ax.set_title('%s: %s' %(self.title, os.path.basename(interface.Source.FileName)))
    ax.legend((Line2D([], [], color='r'),
               Line2D([], [], color='m')),
              ('viewangle close: %f' %numpy.degrees(ta),
               'viewangle far: %f'   %numpy.degrees(ra)))
    figentry = measproc.DinFigEntry(self.title, fig)
    batch.add_entry(figentry, self.NONE)

    # save view angle and range
    workspace = measproc.DinWorkSpace(self.title)
    workspace.add(viewangle=a, range=r, x=x, y=y)
    batch.add_entry(workspace, self.NONE)
    return

