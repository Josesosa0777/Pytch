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

SignalGroups = [{"Mrf._.PssObjectDebugInfo.Index": ("ECU", "Mrf._.PssObjectDebugInfo.Index"),
                 "Mrf._.PssObjectDebugInfo.dxv": ("ECU", "Mrf._.PssObjectDebugInfo.dxv"),
                 "Mrf._.PssObjectDebugInfo.dyv": ("ECU", "Mrf._.PssObjectDebugInfo.dyv"),
                 "Mrf._.PssObjectDebugInfo.vxv": ("ECU", "Mrf._.PssObjectDebugInfo.vxv"),
                 "Mrf._.PssObjectDebugInfo.wExistProb": ("ECU", "Mrf._.PssObjectDebugInfo.wExistProb"),
                 "Mrf._.PssObjectDebugInfo.wObstacle": ("ECU", "Mrf._.PssObjectDebugInfo.wObstacle"),
                 "csi.VelocityData_TC.vDis": ("ECU", "csi.VelocityData_TC.vDis"),
                 "sit.IntroFinder_TC.Intro.i0.Id": ("ECU", "sit.IntroFinder_TC.Intro.i0.Id"),},]

class cView(interface.iView):
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      ########################
      #Mrf object information#
      ########################
      Client = datavis.cPlotNavigator(title="Mrf_object_info", figureNr=203)
      interface.Sync.addClient(Client)
      Client.addsignal('TC.vDis [km/h]', interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_TC.vDis"),
              factor=[3.6])
      Client.addsignal('Mrf_dxv [m]', interface.Source.getSignalFromSignalGroup(Group, "Mrf._.PssObjectDebugInfo.dxv"),
                       'Mrf_dyv [m]', interface.Source.getSignalFromSignalGroup(Group, "Mrf._.PssObjectDebugInfo.dyv"))
      Client.addsignal('Mrf_vxv [m/s]', interface.Source.getSignalFromSignalGroup(Group, "Mrf._.PssObjectDebugInfo.vxv"))
      Client.addsignal('Mrf_wExistProb', interface.Source.getSignalFromSignalGroup(Group, "Mrf._.PssObjectDebugInfo.wExistProb"),
                       'Mrf_wObstacle', interface.Source.getSignalFromSignalGroup(Group, "Mrf._.PssObjectDebugInfo.wObstacle"),
                       'TC.Intro.i0.Id', interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.Intro.i0.Id"))
      Client.addsignal('ObjectIndex', interface.Source.getSignalFromSignalGroup(Group, "Mrf._.PssObjectDebugInfo.Index")) 
      return []

