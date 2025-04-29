#!/usr/bin/python

import datavis
import measparser
import interface

DefParam = interface.NullParam

Nr = 5

SignalGroups = []
for DeviceName in 'ECU', 'MRR1plus':
  SignalGroup = {'vxvref':   (DeviceName, 'evi.General_T20.vxvRef'),
                 'psidtopt': (DeviceName, 'evi.General_T20.psiDtOpt'),
                 'FakePO0':  (DeviceName, 'fos_internal_states_pri.FakePO0')}
  for i in xrange(Nr):
    SignalGroup['dxvpo%d'    %i] = DeviceName, 'ats.Po_TC.PO.i%d.dxvFilt' %i
    SignalGroup['Handlepo%d' %i] = DeviceName, 'ats.Po_TC.PO.i%d.Handle'  %i
  SignalGroups.append(SignalGroup)
  
class cATS_SameHandle(interface.iView):
  @classmethod
  def view(cls, Param):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, Error:
      print __file__
      print Error.message
    else:
      PN = datavis.cPlotNavigator()
      interface.Sync.addClient(PN)
      
      for Alias in 'vxvref', 'psidtopt', 'FakePO0':
        Axis = PN.addAxis()
        Time, Value = interface.Source.getSignalFromSignalGroup(Group, Alias)
        PN.addSignal2Axis(Axis, Alias, Time, Value)
      
      for Pattern in 'dxvpo%d', 'Handlepo%d':
        Axis = PN.addAxis()
        for i in xrange(Nr):
          Alias = Pattern %i
          Time, Value = interface.Source.getSignalFromSignalGroup(Group, Alias)
          PN.addSignal2Axis(Axis, Alias, Time, Value)
      pass
