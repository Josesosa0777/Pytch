# -*- dataeval: init -*-

import numpy as np
import scipy.signal

from interface import iSearch
from measproc.report2 import Report
from measproc.workspace import DinWorkSpace
from measproc.IntervalList import cIntervalList, maskToIntervals

N_INTMED_CLASSES = 3  # number of intermediate classes, besides the classes for min and max values

init_params = {
  "flr20_targets": dict(
    sgs=[{'num': ("General_radar_status", "number_of_targets")}], max_num=26),
  "flr20_tracks":  dict(
    sgs=[{'num': ("General_radar_status", "number_of_tracks")}],  max_num=20),
  "flc20_objects": dict(
    sgs=[{'num': ("Video_Object_Header",  "Number_Of_Objects")}], max_num=10),
}

### Copied from viewAEBS_1_accelerations
### TODO: rm
def _LPF_butter_4o(t, input_signal):
# input:  t             time [sec] signal as np array
#         input_signal  input signal as np array 
# return: filtered signal as np array 

  # parameters
  n_order  = 4                      # filter order of butterworth filter
  f0 = 1.0                          # -3dB corner frequency [Hz] of butterworth filter
  
  fs = 1.0/np.mean(np.diff(t))      # sampling frequency (assumption: constant sampling interval)
  f_nyq = fs/2.0                    # Nyquist frequency (= 1/2 sampling frequency)
  Wn = f0/f_nyq                     # normalized corner frequency  (related to Nyquist frequency)
  
  # calculate filter coefficients
  B,A = scipy.signal.butter(n_order, Wn)
  
  # calculate filter 
  out_signal = scipy.signal.lfilter(B,A,input_signal)
  
  return out_signal
###

class Search(iSearch):
  optdep = 'set_ego_speed',
  
  def init(self, sgs, max_num):
    self.sgs = sgs
    self.max_num = max_num
    return
  
  def check(self):
    group = self.source.selectSignalGroup(self.sgs)
    return group
  
  def fill(self, group):
    # load signals
    time, num = group.get_signal('num')
    assert np.all(num <= self.max_num), "maximum number of objects exceeded"
    
    # calculate histogram
    hist, bin_edges = np.histogram(num, self.max_num+1, (0, self.max_num+1))
    ws = DinWorkSpace('quantity_histogram')
    ws.add(hist=hist, bin_edges=bin_edges)
    
    # create intervals
    votes = self.batch.get_labelgroups('general')
    report = Report(cIntervalList(time), "Quantities", votes=votes)
    bounds = np.linspace(1, self.max_num, N_INTMED_CLASSES+1)
    bounds = np.hstack((0.0, bounds, np.inf))
    num_filt = np.round(_LPF_butter_4o(time, num))  # smooth
    for i in xrange(bounds.size-1):
      mask = (num_filt >= bounds[i]) & (num_filt < bounds[i+1])
      intvals = maskToIntervals(mask)
      for st, end in intvals:
        index = report.addInterval([st, end])
        report.vote(index, 'general', 'class-%d' % i)
    # add ego speed if available
    if 'set_ego_speed' in self.passed_optdep:
      self.modules.get_module('set_ego_speed')(report)
    else:
      self.logger.warning("Ego speed could not be set.")
    
    return ws, report
  
  def search(self, ws, report):
    # store workspace
    self.batch.add_entry(ws)
    # store report
    result = self.FAILED if report.isEmpty() else self.PASSED
    self.batch.add_entry(report, result=result)
    
    return
