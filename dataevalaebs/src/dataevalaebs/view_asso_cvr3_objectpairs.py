# -*- dataeval: call -*-

import numpy as np

import datavis
import interface
from aebs.sdf import asso_cvr3_fus_recalc

class cParameter(interface.iParameter):
  def __init__(self, k):
    self.k = k
    return
# instantiation of module parameters
call_params = dict( ('NEIGHBOUR_%02d' %i, dict(k=i)) for i in xrange(21) )

class cView(interface.iView):
  dep = 'calc_asso_cvr3@aebs.fill',

  def check(self):
    modules = self.get_modules()
    a = modules.fill('calc_asso_cvr3@aebs.fill')
    return a

  def view(cls, par, a):
    Client = datavis.cListNavigator(title="LN")
    # before
    for k in xrange(par.k,0,-1):
      # shift pairs
      left = [[] for i in xrange(k)]
      right = a.objectPairs[:-k]
      left.extend(right)
      assert len(left) == len(a.objectPairs) == a.scaleTime.size
      Client.addsignal("current - %d" %k, (a.scaleTime, left))
      # shift time
      t = np.roll(a.scaleTime,k)
      t[:k] = np.NaN
      Client.addsignal("current - %d" %k, (a.scaleTime, t), groupname='time')
    # actual
    Client.addsignal("current", (a.scaleTime, a.objectPairs), bg='red')
    Client.addsignal("current", (a.scaleTime, a.scaleTime),   bg='red', groupname='time')
    # after
    for k in xrange(1,par.k+1):
      # shift pairs
      left = a.objectPairs[k:]
      right = [[] for i in xrange(k)]
      left.extend(right)
      assert len(left) == len(a.objectPairs)
      Client.addsignal("current + %d" %k, (a.scaleTime, left))
      # shift time
      t = np.roll(a.scaleTime,-k)
      t[-k:] = np.NaN
      Client.addsignal("current + %d" %k, (a.scaleTime, t), groupname='time')
    # register client
    interface.Sync.addClient(Client)
    return
