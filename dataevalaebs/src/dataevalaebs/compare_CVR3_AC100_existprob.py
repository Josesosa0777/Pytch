""" Creates histograms of existence probability for CVR3 and credibility for AC100 in the associated objects.
The module analyzes the mdf measurement files in a specified directory (given as command line argument), 
collects all the objects data, merges them and creates the histograms.
"""

import os
import sys
import glob
import time

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import measparser
import aebs.sdf.asso_cvr3_ac100
from viewIntroObstacleClassif import SPEED_LIM_KMPH, MPS_2_KMPH

tstart = time.time()

# control variables
isStationaryRun = True # differentiate between stationary and moving statistics
DX_RANGE = (0.,150.)
EX_PROB_VAR_RANGE = (0.1,1.)
DX_BINS = 15
EX_PROB_BINS = 9

signalGroups = [{'egoSpeed' : ('MRR1plus', 'evi.General_TC.vxvRef')},]

# get signals
sensorName2dataListAsso = {'CVR3' : [], 'AC100' : []}
"""
Collection of measurement data per sensor
{ sensorName<str> : [meas0Obj0<ndarray, shape (2,..)>, meas0Obj1<ndarray, shape (2,..)>, .., meas1Obj0<ndarray, shape (2,..)>, ..] }"""
try:
  path = sys.argv[1]
except IndexError:
  print 'Please provide a measurement directory as command line parameter.'
  exit()
filePaths = glob.glob( os.path.join(path, '*[.][mM][dD][fF]') )
if not filePaths:
  print 'No valid mdf file was found in the given measurement directory: %s' %path
  exit()
for filePath in filePaths:
  print filePath
  if not os.path.isfile(filePath):
    print 'Invalid file path: %s' %filePath
    continue
  try:
    source = measparser.cSignalSource(filePath)
    # parsing
    assoObj = aebs.sdf.asso_cvr3_ac100.AssoCvr3Ac100(source)
    group = source.selectSignalGroup(signalGroups)
  except measparser.signalgroup.SignalGroupError, error:
    print error.message
  else:
    # filter out intervals when ego speed was too low
    egoSpeed = source.getSignalFromSignalGroup(group, 'egoSpeed', ScaleTime=assoObj.scaleTime)[1]
    speedUnit = source.getPhysicalUnitFromSignalGroup(group, 'egoSpeed')
    if speedUnit == 'm/s' or speedUnit == 'mps':
      speedLimit = SPEED_LIM_KMPH / MPS_2_KMPH
    else:
      speedLimit = SPEED_LIM_KMPH
    speedmask = egoSpeed > speedLimit
    # track association
    assoObj.calc()
    # collecting associated data
    mask = np.zeros(assoObj.scaleTime.shape, dtype=np.bool)
    sensorName2dxProbListAsso = {'CVR3' : [], 'AC100' : []}
    for (cvr3objNum, ac100objNum), timeIndices in assoObj.assoData.iteritems():
      mask[:] = False
      mask[timeIndices] = True
      mask &= speedmask
      movingState = assoObj.movingState['CVR3'][cvr3objNum]
      if isStationaryRun:
        mask &= movingState
      else:
        mask &= ~movingState
      for sensorName, objNum in ( ('CVR3',cvr3objNum), ('AC100',ac100objNum) ):
        state, covarMatrix = assoObj.posTracks[sensorName][objNum]
        dx = state[:,0][mask]
        ExProb = assoObj.reliability[sensorName][objNum]
        Prob = ExProb[mask]
        dxProbList = sensorName2dxProbListAsso[sensorName]
        dxProbList.append( (dx,Prob) )
    for sensorName in ('CVR3', 'AC100'):
      dxProbListAsso = sensorName2dxProbListAsso[sensorName]
      measDataAsso = np.hstack(dxProbListAsso)
      dataListAsso = sensorName2dataListAsso[sensorName]
      dataListAsso.append(measDataAsso)
    # save backup and free namespace
    source.save()
    del source, assoObj

# merge all measurement data and create histogram data
sensorName2data = {} # { sensorName<str> : (hist<ndarray>, dxEdges<ndarray>, ProbEdges<ndarray>) }
for sensorName, dataList in sensorName2dataListAsso.iteritems():
  data = np.hstack(dataList) # dx in first row, ExProb in second
  hist, dxEdges, ExProbEdges = np.histogram2d(data[0], data[1], 
                                             bins=[DX_BINS, EX_PROB_BINS], 
                                             range=[DX_RANGE,EX_PROB_VAR_RANGE],
                                             normed=True)
  # normalize densities along dx
  sum = np.sum(hist, axis=1)
  hist /= sum[:,np.newaxis]
  hist = hist.T # for plotting reasons, see numpy.histogram2d docstring
  # store histogram data
  sensorName2data[sensorName] = hist, dxEdges, ExProbEdges
  print '%s data size: %d' %(sensorName, data.shape[1])

print 'Time elapsed: %.2f s' %(time.time()-tstart)

#
# plotting
#
colors = {'CVR3' : 'b', 'AC100' : 'r'}
# prepare plot params
_,xedges,yedges = sensorName2data['CVR3'] # edges are the same for both sensor histogram data
elements = (xedges.size - 1) * (yedges.size - 1)
ones = np.ones(elements)
# bar dimensions
dx = (DX_RANGE[1]-DX_RANGE[0])         / float(DX_BINS)
dy = (EX_PROB_VAR_RANGE[1]-EX_PROB_VAR_RANGE[0]) / float(EX_PROB_BINS)
# bar positions
xpos, ypos = np.meshgrid(xedges[:-1]+dx/4., yedges[:-1]+dy/4.)
x = xpos.flatten()
y = ypos.flatten()
z = np.zeros(elements)
# plotting: sensor dy variance densities
fig = plt.figure()
fig.canvas.set_window_title(os.path.join(path, '*.mdf'))
if isStationaryRun:
  movState = 'stationary'
else:
  movState = 'moving/stopped'
fig.suptitle("Associated %s objects' existence probability densities over distance" %movState)
for i, (sensorName, (hist, _, __)) in enumerate(sensorName2data.iteritems()):
  color = colors[sensorName]
  # create axis
  ax = fig.add_subplot(1,2,i+1, projection='3d')
  ax.set_xlabel('dx [m]')
  ax.set_ylabel('existence probability [-]')
  ax.set_yticks(yedges)
  dz = hist.flatten()
  # create histogram
  ax.bar3d(x, y, z, dx/2., dy/2., dz, color=color, zsort='average')
  # rotate 3d plot
  ax.view_init(elev=15., azim=150.)
  # legend stuff
  proxy = plt.Rectangle((0, 0), 1, 1, fc=color)
  ax.legend([proxy,], [sensorName,])
# plotting: density difference
fig2 = plt.figure()
fig2.canvas.set_window_title(os.path.join(path, '*.mdf'))
fig2.suptitle("Density differences")
ax2 = fig2.add_subplot(111, projection='3d')
ax2.set_xlabel('dx [m]')
ax2.set_ylabel('existence probability [-]')
ax2.set_zlabel('difference')
ax2.set_yticks(yedges)
# prepare plot params
histCvr3,_,__ = sensorName2data['CVR3']
histAc100,_,__ = sensorName2data['AC100']
dz = np.abs(histCvr3-histAc100).flatten()
color = np.where(histCvr3>histAc100, colors['CVR3'], colors['AC100'])
color = color.flatten()
# create histogram
ax2.bar3d(x, y, z, dx/2., dy/2., dz, color=color, zsort='average')
# rotate 3d plot
ax2.view_init(elev=20., azim=150.)
# legend stuff
proxy1 = plt.Rectangle((0, 0), 1, 1, fc='b')
proxy2 = plt.Rectangle((0, 0), 1, 1, fc='r')
ax2.legend([proxy1,proxy2], ['CVR3', 'AC100'])

fig.show()
fig2.show()

raw_input('Press Enter to exit...')
