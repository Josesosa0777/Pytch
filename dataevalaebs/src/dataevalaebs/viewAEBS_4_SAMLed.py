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

SignalGroups = [{"SAMLED1": ("PGNFFB2", "SAMLED1"),
                 "SAMLED2": ("PGNFFB2", "SAMLED2"),
                 "SAMLED3": ("PGNFFB2", "SAMLED3"),
                 "asf.HmiReq_TC.SystemAvailMon.w.BITBE_b2": ("ECU", "asf.HmiReq_TC.SystemAvailMon.w.BITBE_b2"),},]

class cView(interface.iView):
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      ################################################
      #SystemAvailabilityMonitoring (SAM) LED analyze#
      ################################################
      Client = datavis.cPlotNavigator(title="SAM_LED_analyze", figureNr=104) 
      interface.Sync.addClient(Client) 
      Client.addsignal('LED_1 []', interface.Source.getSignalFromSignalGroup(Group, "SAMLED1"),
               'LED_2[]', interface.Source.getSignalFromSignalGroup(Group, "SAMLED2"),
               'LED_3[]', interface.Source.getSignalFromSignalGroup(Group, "SAMLED3"),
               'BITBE[]', interface.Source.getSignalFromSignalGroup(Group, "asf.HmiReq_TC.SystemAvailMon.w.BITBE_b2"))
      return []

