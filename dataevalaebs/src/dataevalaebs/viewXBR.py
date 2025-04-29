import numpy as np
import scipy.interpolate
import scipy.signal
import warnings

import interface
import datavis
import measparser

DefParam = interface.NullParam

SignalGroups = [{"ExtAccelDem_hwc": ("XBRhwc", "ExtAccelDem_hwc"),
                 "FrontAxleSpeed": ("EBC2", "FrontAxleSpeed"),
                 "Velocity_Kmh": ("VBOX_2", "Velocity_Kmh"),
                 "ABSActive": ("EBC1", "ABSActive"),},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      Time1, Value1 = interface.Source.getSignalFromSignalGroup(Group, "ExtAccelDem_hwc")
      Time2, Value2 = interface.Source.getSignalFromSignalGroup(Group, "FrontAxleSpeed")
      Time3, Value3 = interface.Source.getSignalFromSignalGroup(Group, "Velocity_Kmh")
      Time4, Value4 = interface.Source.getSignalFromSignalGroup(Group, "ABSActive")
      
      refAccs, avgAccs, breakpoints = run(Value1, Value2, Value3, Time1, Time2, Time3)
      acc = calcAcceleration(Value2, Time2, cutoffFreq=5)

      Client = datavis.cPlotNavigator(title="Errors in averaged accelerations", figureNr=None)
      interface.Sync.addStaticClient(Client)
      Axis = Client.addAxis()
      ax = Client.fig.gca()
      ax.set_xlabel('Reference acc. [m/s^2]')
      ax.set_ylabel('Acceleration error [m/s^2]')
      xLim = np.array((np.min(refAccs)-1, np.max((-2, np.max(np.where(refAccs<-0.5, refAccs, -np.inf))))))
      Client.addSignal2Axis(Axis, "Zero level", xLim, np.zeros(2), color='g-', unit="m/s^2")
      Client.addSignal2Axis(Axis, "Acceleration error", refAccs, refAccs-avgAccs, color='b.', unit="m/s^2")
      Client.setXlim(*xLim)

      Client = datavis.cPlotNavigator(title="Reference and measured acceleration with ABS activity", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      ax = Client.fig.gca()
      ax.set_xlabel('Time [s]')
      Client.addSignal2Axis(Axis, "ABS Activity", Time4, Value4, color='g-', unit="")
      Client.addSignal2Axis(Axis, "Reference acc. [m/s^2]", Time1, Value1, color='r-', unit="m/s^2")
      Client.addSignal2Axis(Axis, "Measured acc. [m/s^2]", Time2, acc, color='b-', unit="m/s^2")
      # add annotations
      for i in range(len(refAccs)):
        if abs(refAccs[i]) > 0.1: # exclude values without deceleration request
          ax.annotate('%.1f | %.1f' % (refAccs[i], avgAccs[i]), (breakpoints[i]+0.5, refAccs[i]), xytext=(10, -20), xycoords='data', textcoords='offset points', arrowprops=dict(arrowstyle="->"))
      pass
    pass

def correctFrontAxleSpeed(FrontAxleSpeed, Velocity_Kmh, t_EBC2, t_VBOX_2):
    """Corrects FrontAxleSpeed signal based on VBOX measurements."""
    
    # sample Velocity_Kmh at time values in t_EBC2
    f = scipy.interpolate.interp1d(t_VBOX_2.flatten(), Velocity_Kmh.flatten())
    Velocity_Kmh_sampled = f(t_EBC2)
    # select speed values >= 10 km/h
    validIndices = np.where(Velocity_Kmh_sampled >= 10)
    Velocity_Kmh_sampled = Velocity_Kmh_sampled[validIndices]
    FrontAxleSpeed_sel = FrontAxleSpeed[validIndices]
    # calculate correction ratio (least-squares estimate)
    ratio = np.dot(1/(np.dot(FrontAxleSpeed_sel, FrontAxleSpeed_sel)) * FrontAxleSpeed_sel, Velocity_Kmh_sampled)
    return ratio * FrontAxleSpeed # corrected FrontAxleSpeed

def findBreakpoints(signal, time, threshold):
    """Returns the timestamps where the difference in signal exceeds the given threshold."""
    
    sigdiff = signal[1:] - signal[0:-1] # np.diff(signal)
    breakpoints = np.where(np.abs(sigdiff) >= threshold)
    return time[breakpoints]

def getIndexOfMinDiffValue(signal, value):
    """Returns the index of the element in 'signal' with the smallest difference compared to 'value'."""
    
    foo = np.abs(signal - value)
    return np.where(foo == np.min(foo))[0]

def calcRefAccs(time, acc, breakpoints):
    """Calculates average accelerations between breakpoints. Source is reference acceleration."""
    
    breakpointsSize = breakpoints.size
    refAccs = np.empty(breakpointsSize-1)
    for i in range(breakpointsSize-1):
        ind1 = np.where(time == breakpoints[i])[0] + 1
        ind2 = np.where(time == breakpoints[i+1])[0]
        refAccs[i] = (acc[ind1]+acc[ind2]) / 2
    return refAccs

def calcAvgAccs(time, speed, breakpoints, transientDuration=0.3):
    """Calculates average accelerations between breakpoints. Source is speed."""
    
    breakpointsSize = breakpoints.size
    avgAccs = np.empty(breakpointsSize-1)
    validIntervals = 0
    try:
        # calculate accelerations
        for i in range(breakpointsSize-1):
            ind1 = getIndexOfMinDiffValue(time, breakpoints[i]+transientDuration)
            ind2 = getIndexOfMinDiffValue(time, breakpoints[i+1])
            # update ind2 at speed < 10
            foo = np.where(speed[ind1:ind2] < 10)[0]
            if foo.size > 0:
                ind2 = ind1 + foo[0]
            if ind2 > ind1:
                # calculate average acceleration
                avgAccs[i] = (speed[ind2]-speed[ind1]) / 3.6 / (time[ind2]-time[ind1]) # [m/s^2]
            else: # no valid speed values
                avgAccs[i] = 0
            validIntervals += 1
    except IndexError:
        print 'IndexError: Probably caused by an interval containing only transients in speed. No further calculations.'
    return avgAccs[:validIntervals]

def calcAcceleration(FrontAxleSpeed, t_EBC2, cutoffFreq=5):
    """Calculates acceleration signal using a derivative filter with a given cut-off frequency."""
    
    # call lsim() with suppressing its warning (C:\python25\lib\site-packages\scipy\signal\ltisys.py:480: ComplexWarning: Casting complex values to real discards the imaginary part)
    original_filters = warnings.filters[:]
    warnings.simplefilter("ignore")
    try:
        t, y_out, x_out = scipy.signal.lsim(((cutoffFreq, 0), (1, cutoffFreq)), FrontAxleSpeed.flatten(), t_EBC2.flatten())
    finally:
        warnings.filters = original_filters
    
    y_out /= 3.6 # convert into m/s^2
    y_out[0:50] = np.where(abs(y_out[0:50]) < 8, y_out[0:50], 0) # clear errors caused by unknown initial condition
    return y_out

def run(ExtAccelDem_hwc, FrontAxleSpeed, Velocity_Kmh, t_XBRhwc, t_EBC2, t_VBOX_2):
    """Start calculation. Main output is the array of average accelerations."""
    
    FrontAxleSpeed_corr = correctFrontAxleSpeed(FrontAxleSpeed, Velocity_Kmh, t_EBC2, t_VBOX_2)
    breakpoints = findBreakpoints(ExtAccelDem_hwc, t_XBRhwc, threshold=0.3)
    refAccs = calcRefAccs(t_XBRhwc, ExtAccelDem_hwc, breakpoints)
    avgAccs = calcAvgAccs(t_EBC2, FrontAxleSpeed_corr, breakpoints, transientDuration=0.3)
    return refAccs, avgAccs, breakpoints
