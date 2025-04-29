import numpy as np

import datavis
import interface
from asso.interface import INVALID_COST_COEFF

class cParameter(interface.iParameter):
  def __init__(self, title, i, j):
    self.title = title
    self.i = i
    self.j = j
    self.genKeys()
    return
# instantiation of module parameters
associated = cParameter('associated',  1, 42)
required   = cParameter('required'  , 22, 42)

class cView(interface.iView):

  def view(cls, param):
    try:
      assoObj = interface.assoObj
    except AttributeError:
      print 'No association object loaded!'
    else:      
      i = param.i
      j = param.j
      xi,Pi = assoObj.tracks['CVR3'][i]
      xj,Pj = assoObj.tracks['S-Cam'][j]
      maski = assoObj.masks['CVR3'][i]
      maskj = assoObj.masks['S-Cam'][j]
      gate = np.ones_like(assoObj.scaleTime)
      gate *= assoObj.invalidAssoCost / INVALID_COST_COEFF
      
      LN = datavis.cListNavigator(title=param.title)
      interface.Sync.addClient(LN)
      
      ones = np.ones_like(assoObj.scaleTime, dtype=np.int)
      
      LN.addsignal("k",     (assoObj.scaleTime, np.arange(assoObj.scaleTime.size)))
      LN.addsignal("i",     (assoObj.scaleTime, i*ones))
      LN.addsignal("j",     (assoObj.scaleTime, j*ones))
      LN.addsignal("maski", (assoObj.scaleTime, maski))
      LN.addsignal("maskj", (assoObj.scaleTime, maskj))
      LN.addsignal("xi",    (assoObj.scaleTime, xi))
      LN.addsignal("xj",    (assoObj.scaleTime, xj))
      LN.addsignal("Pi",    (assoObj.scaleTime, Pi.diagonal(axis1=1, axis2=2)))
      LN.addsignal("Pj",    (assoObj.scaleTime, Pj.diagonal(axis1=1, axis2=2)))
      if hasattr(assoObj, 'c'): # debug variable
        LN.addsignal("d2ij",  (assoObj.scaleTime, assoObj.c[:,i,j]))
      LN.addsignal("gate",  (assoObj.scaleTime, gate))
      LN.addsignal("C",     (assoObj.scaleTime, assoObj.C[:,i,j]))
    return

