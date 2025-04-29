import os
import sys

import numpy

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import interface
import config
import measproc
import searchFoV_AC100_Target

FIG_X_LIM = searchFoV_AC100_Target.cSearch.FIG_X_LIM
FIG_Y_LIM = searchFoV_AC100_Target.cSearch.FIG_Y_LIM
NOTABLE_DISTS_CVR3 = [10.0 + 10.0 * i for i in range(16)]
NOTABLE_DISTS_AC100 = [10.0 + 10.0 * i for i in range(20)]
SPECIF_X_CVR3 = [0.0, 20.0, 60.0, 100.0, 160.0]
SPECIF_ANGLE_CVR3 = [0.0, 35.0, 22.5, 7.5, 7.5]
SPECIF_X_AC100 = [0.0, 20.0, 100.0, 200.0]
SPECIF_ANGLE_AC100 = [0.0, 12.0, 8.0, 8.0]

class cParameter(interface.iParameter):
  def __init__(self, searchClass, title):
    self.searchClass = searchClass
    self.title = title
    self.genKeys()
    return

AC100 = cParameter('dataevalaebs.searchFoV_AC100_Target.cSearch', 'AC100 FoV sum')
CVR3  = cParameter('dataevalaebs.searchFoV_CVR3_LOC.cSearch', 'CVR3 FoV sum')
COMPARE = cParameter(('dataevalaebs.searchFoV_AC100_Target.cSearch', 'searchFoV_CVR3_LOC.cSearch'), 'AC100 CVR3 FoV compare')

class cAnalyze(interface.iAnalyze):
  def analyze(self, param):
    batch = self.get_batch()
    start = batch.get_last_entry_start()
    if not isinstance(param.searchClass, tuple):
      filter_ = dict(class_name=param.searchClass, start=start)
      entryids = batch.filter(type='measproc.cFileStatistic', **filter_)
      pack = batch.pack(entryids, 'measurement')

      sumstat = measproc.cDinStatistic(param.title, [['measurement', pack.keys()],
                                                     ['viewangle',   ['close', 'far']]])

      for meas, stats in pack.iteritems():
        for entry in stats:
          stat = batch.wake_entry(entry)
          for angle in 'close', 'far':
            pos = ['viewangle', angle]
            value = stat.get([pos])
            sumstat.set([['measurement', meas], pos], value)

      title    = param.title.replace('sum', 'calc')
      calcstat = measproc.cDinStatistic(title, [['statistic', ['min',   'max']],
                                                ['viewangle', ['close', 'far']]])

      axis = sumstat.Axes.index('measurement')
      if sumstat.Array.shape[axis]:
        minv = sumstat.Array.min(axis=axis)
        maxv = sumstat.Array.max(axis=axis)

        for angle in 'close', 'far':
          pos = sumstat.TickLabels['viewangle'].index(angle)
          calcstat.set([['statistic', 'min'],  ['viewangle', angle]], minv[ pos])
          calcstat.set([['statistic', 'max'], ['viewangle', angle]],  maxv[pos])

      measurementid = batch.measurementid
      for meas in pack:
        batch.measurementid, = \
        batch.query('SELECT id FROM measurements WHERE basename = ?', meas,
                    fetchone=True)
        batch.add_entry(sumstat)
        batch.add_entry(calcstat)
      batch.measurementid = measurementid

      print '\nmeasurment                                close-view-angle far-view-angle'
      for meas in sorted(sumstat.TickLabels['measurement']):
        measpos = ['measurement', meas]
        print '%-42s%16.8f %14.8f' %(meas,
                                     sumstat.get([measpos, ['viewangle', 'close']]),
                                     sumstat.get([measpos, ['viewangle', 'far']]))

      print '\nstatistic close-view-angle far-view-angle'
      print 'min       %16.8f %14.8f' %(calcstat.get([['statistic', 'min'], ['viewangle', 'close']]),
                                        calcstat.get([['statistic', 'min'], ['viewangle', 'far']]))
      print 'max       %16.8f %14.8f' %(calcstat.get([['statistic', 'max'], ['viewangle', 'close']]),
                                        calcstat.get([['statistic', 'max'], ['viewangle', 'far']]))

      # calc view angle histogram
      viewangles = []
      ranges = []
      group = batch.filter(type='measproc.FileWorkSpace', **filter_)
      for entry in group:
        workspace = batch.wake_entry(entry)
        viewangles.append(workspace.workspace['viewangle'])
        ranges.append(workspace.workspace['range'])

      if viewangles:
        viewangles = numpy.concatenate(viewangles)
        viewangles = numpy.degrees(viewangles)

        f  = plt.figure()
        ax = f.add_subplot(1,1,1)
        ax.hist(viewangles, bins=min(viewangles.size, 100))
        title = sumstat.PathToSave.replace('sum', 'hist')
        title = title.replace('xml', 'png')
        ax.set_title(param.title.replace('sum', 'hist'))
        ax.set_xlabel('view angle of the objects [degree]')
        f.savefig(title, format='png')
        print >> sys.stderr, title

      if ranges:
        ranges = numpy.concatenate(ranges)
        ranges = ranges[numpy.abs(viewangles) < 1.0]
        f = plt.figure()
        ax = f.add_subplot(1,1,1)
        ax.hist(ranges, bins=min(ranges.size, 100))
        title = sumstat.PathToSave.replace('sum', 'hist around zero degree')
        title = title.replace('xml', 'png')
        ax.set_title(param.title.replace('sum', 'hist around zero degree'))
        ax.set_xlabel('range of the objects [m]')
        f.savefig(title, format='png')
        print >> sys.stderr, title
    else:
      wsGroup = {}
      for searchClass in param.searchClass:
        sensorName = searchClass.split('_')[1]
        wsGroup[sensorName] = batch.filter(class_name=searchClass,
                                           type='measproc.FileWorkSpace',
                                           start=start)

      ObjLoc = {}
      for sensor in wsGroup.keys():
        for entry in wsGroup[sensor]:
          measName = batch.get_entry_attr(entry, "measurement")
          workspace = batch.wake_entry(entry)
          measDict = ObjLoc.setdefault(measName, {})
          sensorDict = measDict.setdefault(sensor, {})
          for key in workspace.workspace.keys():
            if key in ('__header__', '__globals__', '__version__'):
              continue
            sensorDict[key] = workspace.workspace[key].flatten()

      batchLoc = os.path.dirname(batch.dbname)

      for meas in ObjLoc.keys():
        selCoordsAC100 = {'x': {'left': [0.0], 'right': [0.0]}, 'y': {'left': [0.0], 'right': [0.0]}}
        for notableDist in NOTABLE_DISTS_AC100:
          maskAC100 = numpy.logical_and(notableDist-1 <= ObjLoc[meas]['AC100']['range'], ObjLoc[meas]['AC100']['range'] <= notableDist+1)

          if len(ObjLoc[meas]['AC100']['viewangle'][maskAC100]) != 0:
            valueMaxAC100 = numpy.max(ObjLoc[meas]['AC100']['viewangle'][maskAC100])
            tmp = numpy.logical_and(ObjLoc[meas]['AC100']['viewangle']==valueMaxAC100, maskAC100)
            idxMaxAC100 = numpy.where(tmp)[0][0]
            valueMinAC100 = numpy.min(ObjLoc[meas]['AC100']['viewangle'][maskAC100])
            tmp = numpy.logical_and(ObjLoc[meas]['AC100']['viewangle']==valueMinAC100, maskAC100)
            idxMinAC100 = numpy.where(tmp)[0][0]

          selCoordsAC100['x']['left'].append(ObjLoc[meas]['AC100']['x'][idxMinAC100])
          selCoordsAC100['y']['left'].append(ObjLoc[meas]['AC100']['y'][idxMinAC100])
          selCoordsAC100['x']['right'].append(ObjLoc[meas]['AC100']['x'][idxMaxAC100])
          selCoordsAC100['y']['right'].append(ObjLoc[meas]['AC100']['y'][idxMaxAC100])

        selCoordsCVR3 = {'x': {'left': [0.0], 'right': [0.0]}, 'y': {'left': [0.0], 'right': [0.0]}}
        for notableDist in NOTABLE_DISTS_CVR3:
          maskCVR3 = numpy.logical_and(notableDist-1 <= ObjLoc[meas]['CVR3']['range'], ObjLoc[meas]['CVR3']['range'] <= notableDist+1)

          if len(ObjLoc[meas]['CVR3']['viewangle'][maskCVR3]) != 0:
            valueMaxCVR3 = numpy.max(ObjLoc[meas]['CVR3']['viewangle'][maskCVR3])
            tmp = numpy.logical_and(ObjLoc[meas]['CVR3']['viewangle']==valueMaxCVR3, maskCVR3)
            idxMaxCVR3 = numpy.where(tmp)[0][0]
            valueMinCVR3 = numpy.min(ObjLoc[meas]['CVR3']['viewangle'][maskCVR3])
            tmp = numpy.logical_and(ObjLoc[meas]['CVR3']['viewangle']==valueMinCVR3, maskCVR3)
            idxMinCVR3 = numpy.where(tmp)[0][0]

          selCoordsCVR3['x']['left'].append(ObjLoc[meas]['CVR3']['x'][idxMinCVR3])
          selCoordsCVR3['y']['left'].append(ObjLoc[meas]['CVR3']['y'][idxMinCVR3])
          selCoordsCVR3['x']['right'].append(ObjLoc[meas]['CVR3']['x'][idxMaxCVR3])
          selCoordsCVR3['y']['right'].append(ObjLoc[meas]['CVR3']['y'][idxMaxCVR3])

        fig  = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.set_xlim(FIG_X_LIM)
        ax.set_ylim(FIG_Y_LIM)
        title = param.title + '\n' + meas
        filename = param.title + ' - ' + meas
        ax.set_title(title)
        file2save = os.path.join(batchLoc, filename + '.png')
        ax.plot(ObjLoc[meas]['AC100']['y'], ObjLoc[meas]['AC100']['x'], '.', color='red', alpha=0.05)
        ax.plot(ObjLoc[meas]['CVR3']['y'], ObjLoc[meas]['CVR3']['x'], '.', color='blue', alpha=0.05)

        pfitleftAC100 = numpy.polyfit(numpy.array(selCoordsAC100['x']['left']), numpy.array(selCoordsAC100['y']['left']), 2)
        pfitrightAC100 = numpy.polyfit(numpy.array(selCoordsAC100['x']['right']), numpy.array(selCoordsAC100['y']['right']), 2)
        pointsAC100 = numpy.linspace(0.0, numpy.max(numpy.concatenate((selCoordsAC100['x']['left'], selCoordsAC100['x']['right']))), 100)
        p1dleftAC100 = numpy.poly1d(pfitleftAC100)
        p1drightAC100 = numpy.poly1d(pfitrightAC100)
        ax.fill_betweenx(pointsAC100, p1dleftAC100(pointsAC100), p1drightAC100(pointsAC100), color='red', alpha=0.5)

        specifXPointsAC100 = numpy.array(SPECIF_X_AC100)
        specifYPointsAC100 = specifXPointsAC100 * numpy.sin(numpy.array(SPECIF_ANGLE_AC100) * numpy.pi / 180)
        ax.plot(specifYPointsAC100, specifXPointsAC100, color='magenta', linewidth=3.0)
        ax.plot(-specifYPointsAC100, specifXPointsAC100, color='magenta', linewidth=3.0)

        pfitleftCVR3 = numpy.polyfit(numpy.array(selCoordsCVR3['x']['left']), numpy.array(selCoordsCVR3['y']['left']), 2)
        pfitrightCVR3 = numpy.polyfit(numpy.array(selCoordsCVR3['x']['right']), numpy.array(selCoordsCVR3['y']['right']), 2)
        pointsCVR3 = numpy.linspace(0.0, numpy.max(numpy.concatenate((selCoordsCVR3['x']['left'], selCoordsCVR3['x']['right']))), 100)
        p1dleftCVR3 = numpy.poly1d(pfitleftCVR3)
        p1drightCVR3 = numpy.poly1d(pfitrightCVR3)
        ax.fill_betweenx(pointsCVR3, p1dleftCVR3(pointsCVR3), p1drightCVR3(pointsCVR3), color='blue', alpha=0.5)

        specifXPointsCVR3 = numpy.array(SPECIF_X_CVR3)
        specifYPointsCVR3 = specifXPointsCVR3 * numpy.sin(numpy.array(SPECIF_ANGLE_CVR3) * numpy.pi / 180)
        ax.plot(specifYPointsCVR3, specifXPointsCVR3, color='cyan', linewidth=3.0)
        ax.plot(-specifYPointsCVR3, specifXPointsCVR3, color='cyan', linewidth=3.0)

        ax.axhline(160, color='cyan', linewidth=1.0)
        ax.text(0.2, 165.0/FIG_Y_LIM[-1], 'Range limit for CVR3', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        ax.axhline(200, color='magenta', linewidth=1.0)
        ax.text(0.2, 205.0/float(FIG_Y_LIM[-1]), 'Range limit for AC100', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

        ax.legend((Line2D([], [], color='red'), Line2D([], [], color='magenta'), Line2D([], [], color='blue'), Line2D([], [], color='cyan')), ('AC100 FoV', 'specification for AC100', 'CVR3 FoV', 'specification for CVR3'))
        fig.savefig(file2save, format='png')

    return
