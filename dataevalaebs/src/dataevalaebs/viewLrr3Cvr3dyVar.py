""" Creates histograms of lateral position uncertainties (dy variances) of 'reliable' LRR3 and CVR3 OHL objects.
"""

import numpy as np
import matplotlib.pyplot as plt

import interface
from aebs.sdf.assoOHL import AssoOHL

DefParam = interface.NullParam

class ViewLrr3Cvr3dyVar(interface.iView):
  @classmethod
  def view(cls, viewParam):
    if hasattr(interface, 'assoObj'):
      assoObj = interface.assoObj
      if not isinstance(assoObj, AssoOHL):
        print 'Error: another association object has already been created: %s' %assoObj
        return
    else:
      scaletime = None if hasattr(interface.Objects, 'ScaleTime') else interface.Objects.ScaleTime
      try: assoObj = AssoOHL(interface.Source, scaleTime=scaletime)
      except measparser.signalgroup.SignalGroupError, error:
        print error.message
        return
    sensorName2DyVar = {}
    for sensorName, objDict in assoObj.posTracks.iteritems():
      dyVarList = [] # [ dyVarObj0<ndarray>, dyVarObj1<ndarray>, ... ]
      for objNum, (state, covarMatrix) in objDict.iteritems():
        mask = assoObj.masks[sensorName][objNum]
        dyVar = covarMatrix[:,1,1][mask]
        dyVarList.append(dyVar)
      sensorName2DyVar[sensorName] = dyVarList
    dataList = []
    labels = []
    for sensorName, dyVarList in sensorName2DyVar.iteritems():
      dataList.append( np.concatenate(dyVarList) )
      labels.append(sensorName)
    # plotting
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(dataList, bins=np.linspace(0.,5.,20), normed=True, histtype='bar', label=labels)
    ax.set_xlabel('dy variance [m^2]')
    ax.legend()
    fig.show()
    pass
