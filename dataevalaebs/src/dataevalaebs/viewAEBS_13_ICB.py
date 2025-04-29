"""
:Organization: Knorr-Bremse SfN GmbH T/CES3.2 (BU2) Budapest Schwieberdingen T/CES3.2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import datavis
import measparser
import interface

DefParam = interface.NullParam

SignalGroups = [{"Ext_Acceleration_Demand": ("XBR-8C040B2A", "Ext_Acceleration_Demand"),
                 "asf.pubFlagsASF.b.InCrashBrakingActive_B": ("ECU", "asf.pubFlagsASF.b.InCrashBrakingActive_B"),
                 "padasf_x_par_a.REPaEmergencyBrake": ("ECU", "padasf_x_par_a.REPaEmergencyBrake"),},]

class cView(interface.iView):
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else: 
      ##########################
      #In-Crash Braking analyze#
      ##########################
      Client = datavis.cPlotNavigator(title="In-Crash braking", figureNr=208) 
      interface.Sync.addClient(Client)
      y_limits = [-1,11]
      Client.addsignal('in_Crash_act [bool]', interface.Source.getSignalFromSignalGroup(Group, "asf.pubFlagsASF.b.InCrashBrakingActive_B"),
                       'aEmergency [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "padasf_x_par_a.REPaEmergencyBrake"))
      Client.addsignal('ExtAccelerationDemand[]', interface.Source.getSignalFromSignalGroup(Group, "Ext_Acceleration_Demand"))    
      return []

