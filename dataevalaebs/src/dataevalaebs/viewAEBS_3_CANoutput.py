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

SignalGroups = [{"Buzzer": ("PGNFFB2", "Buzzer"),
                 "FlashingLights": ("PGNFFB2", "FlashingLights"),
                 "HazardLights": ("PGNFFB2", "HazardLights"),
                 "SourceAddressOfControllingDeviceForBrakeControl": ("EBC1", "SourceAddressOfControllingDeviceForBrakeControl"),},]

class cView(interface.iView):
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      ####################
      #CAN output signals#
      ####################
      Client = datavis.cPlotNavigator(title="CAN_output", figureNr=103)
      interface.Sync.addClient(Client)
      Client.addsignal('Buzzer[bool]', interface.Source.getSignalFromSignalGroup(Group, "Buzzer"),
                       'Flash[bool]', interface.Source.getSignalFromSignalGroup(Group, "FlashingLights"),
                       'hazard[bool]', interface.Source.getSignalFromSignalGroup(Group, "HazardLights"),
                       'SAoCD[dec]', interface.Source.getSignalFromSignalGroup(Group, "SourceAddressOfControllingDeviceForBrakeControl")) 
      return []

