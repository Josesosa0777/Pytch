import numpy as np

import datavis
import interface
import measparser
from aebs.fill.fillAC100 import N_AC100_TR
from aebs.sdf.asso_cvr3_ac100 import TRACK_IS_EMPTY

INVALID_INT_VALUE = -1

# bitvalue dictionaries
tracking_status_dict = {
  0 : 'TRACK_IS_EMPTY',
  1 : 'TRACK_IS_INIT',
  2 : 'TRACK_IS_ESTABLISHED',
  3 : 'TRACK_IS_SLEEPING',
}
acc_track_info_dict = {
  0 : 'normal track',
  1 : 'ACC-track',
  2 : 'IIV-Track',
  3 : 'NIV-Track',
}

# signal templates (assumption: all signal starts with 'tr%d_')
TrackSignalTemplates = {
#  signal template                    axisNum  bitvalue dict
  'tr%d_range'                     : (0,       None                 ),
  'tr%d_corrected_lateral_distance': (0,       None                 ),
  'tr%d_relative_velocitiy'        : (0,       None                 ),
# 'tr%d_acceleration_over_ground'  : (0,       None                 ), # non ASCII character coding of physical unit
  'tr%d_credibility'               : (1,       None                 ),
  'tr%d_acc_track_info'            : (2,       acc_track_info_dict  ),
  'tr%d_CW_track'                  : (3,       None                 ),
  'tr%d_secondary'                 : (3,       None                 ),
  'tr%d_forbidden'                 : (3,       None                 ),
  'tr%d_power'                     : (4,       None                 ),
  'tr%d_tracking_status'           : (5,       tracking_status_dict ),
  'tr%d_asso_target_index'         : (6,       None                 ),
}
TrackSignalGroup = {}
for k in xrange(N_AC100_TR):
  TrackSignalGroup['tr%d_internal_track_index' %k] = ('Tracks', 'tr%d_internal_track_index' %k)
  for SignalTemplate in TrackSignalTemplates.iterkeys():
    SignalName = SignalTemplate %k
    TrackSignalGroup[SignalName] = ('Tracks', SignalName)
TrackSignalGroups = [TrackSignalGroup, ]

class cParameter(interface.iParameter):
  def __init__(self, objIndex):
    self.objIndex = objIndex
    self.genKeys()
    pass
# instantiation of module parameters
AC100_OBJ_00 = cParameter(0)
AC100_OBJ_01 = cParameter(1)
AC100_OBJ_02 = cParameter(2)
AC100_OBJ_03 = cParameter(3)
AC100_OBJ_04 = cParameter(4)
AC100_OBJ_05 = cParameter(5)
AC100_OBJ_06 = cParameter(6)
AC100_OBJ_07 = cParameter(7)
AC100_OBJ_08 = cParameter(8)
AC100_OBJ_09 = cParameter(9)
AC100_OBJ_10 = cParameter(10)
AC100_OBJ_11 = cParameter(11)
AC100_OBJ_12 = cParameter(12)
AC100_OBJ_13 = cParameter(13)
AC100_OBJ_14 = cParameter(14)
AC100_OBJ_15 = cParameter(15)
AC100_OBJ_16 = cParameter(16)
AC100_OBJ_17 = cParameter(17)
AC100_OBJ_18 = cParameter(18)
AC100_OBJ_19 = cParameter(19)

class cView(interface.iView):
  def check(self):
    if not hasattr(interface.Objects, 'ScaleTime'):
      raise measparser.signalgroup.SignalGroupError('Error: scale time is needed (probably no status is selected)!')
    return

  def view(self, Param):
    scaleTime = interface.Objects.ScaleTime
    kwargs = dict(ScaleTime=scaleTime)
    Filtered, = interface.Source.filterSignalGroups(TrackSignalGroups)
    trackNum2mask = {}
    """:type: dict
    Store mask for each track (message) where object is present { trackNum<int> : mask<ndarray> }"""
    
    # loop through all tracks
    for k in xrange(N_AC100_TR):
      # skip track if its signals are not present
      for SignalTemplate in TrackSignalTemplates.iterkeys():
        if (SignalTemplate %k) not in Filtered:
          break
      else:
        TrackIndex = interface.Source.getSignalFromSignalGroup(Filtered, 'tr%d_internal_track_index' %k, **kwargs)[1]
        TrackingStatus = interface.Source.getSignalFromSignalGroup(Filtered, 'tr%d_tracking_status' %k, **kwargs)[1]
        mask = np.logical_and(TrackIndex==Param.objIndex, TrackingStatus != TRACK_IS_EMPTY)
        if np.any(mask):
          trackNum2mask[k] = mask
    # return if object was not found in any messages
    if len(trackNum2mask) == 0:
      print 'Warning: AC100 object #%d was never transmitted!' %Param.objIndex
      return
    
    # collect object attributes
    object = {}
    """:type: dict
    { SignalTemplate<str> : (signal<ndarray>, physUnit<str>) }"""
    for k, mask in trackNum2mask.iteritems():
      for SignalTemplate in TrackSignalTemplates.iterkeys():
        signalName = (SignalTemplate %k)
        signal_k   = interface.Source.getSignalFromSignalGroup(Filtered, signalName, **kwargs)[1]
        # set default array props
        if SignalTemplate not in object:
          signal = np.zeros_like(signal_k)
          # fill with invalid values
          if np.issubdtype(signal.dtype, np.int):
            signal += INVALID_INT_VALUE
          else:
            signal += np.NaN
          physUnit = interface.Source.getPhysicalUnitFromSignalGroup(Filtered, signalName)
          object[SignalTemplate] = signal, physUnit
        else:
          signal = object[SignalTemplate][0]
        signal[mask] = signal_k[mask]
    
    # plotting
    PN = datavis.cPlotNavigator(title='AC100 internal track #%d' %Param.objIndex)
    axes = {}
    for SignalTemplate, (signal, physUnit) in object.iteritems():
      axisNum, bitvalueDict = TrackSignalTemplates[SignalTemplate]
      signalName = SignalTemplate[5:] # strip does not work as expected
      # create axis if not exists
      if axisNum not in axes:
        yLabel = signalName if bitvalueDict is not None else None
        ax = PN.addAxis(ylabel=yLabel)
        axes[axisNum] = ax
      else:
        ax = axes[axisNum]
      # handle bitvalues
      if bitvalueDict is None:
        PN.addSignal2Axis(ax, '%s [%s]' %(signalName, physUnit), scaleTime, signal)
      else:
        for bitvalue, description in bitvalueDict.iteritems():
          bitSignal = signal==bitvalue
          PN.addSignal2Axis(ax, '%s [%s]' %(description, physUnit), scaleTime, bitSignal)
    interface.Sync.addClient(PN)
    pass
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
