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

SignalGroups = [{"repacuw.__b_Rep.__b_RepBase.ExecutionStatus": ("ECU", "repacuw.__b_Rep.__b_RepBase.ExecutionStatus"),
                 "repacuw.__b_Rep.__b_RepBase.status": ("ECU", "repacuw.__b_Rep.__b_RepBase.status"),
                 "repaubr.__b_Rep.__b_RepBase.ExecutionStatus": ("ECU", "repaubr.__b_Rep.__b_RepBase.ExecutionStatus"),
                 "repaubr.__b_Rep.__b_RepBase.status": ("ECU", "repaubr.__b_Rep.__b_RepBase.status"),
                 "repbrph.__b_Rep.__b_RepBase.ExecutionStatus": ("ECU", "repbrph.__b_Rep.__b_RepBase.ExecutionStatus"),
                 "repbrph.__b_Rep.__b_RepBase.status": ("ECU", "repbrph.__b_Rep.__b_RepBase.status"),
                 "repbrpp.__b_Rep.__b_RepBase.ExecutionStatus": ("ECU", "repbrpp.__b_Rep.__b_RepBase.ExecutionStatus"),
                 "repbrpp.__b_Rep.__b_RepBase.status": ("ECU", "repbrpp.__b_Rep.__b_RepBase.status"),
                 "repdesu.__b_Rep.__b_RepBase.ExecutionStatus": ("ECU", "repdesu.__b_Rep.__b_RepBase.ExecutionStatus"),
                 "repdesu.__b_Rep.__b_RepBase.status": ("ECU", "repdesu.__b_Rep.__b_RepBase.status"),
                 "repinfo.__b_Rep.__b_RepBase.ExecutionStatus": ("ECU", "repinfo.__b_Rep.__b_RepBase.ExecutionStatus"),
                 "repinfo.__b_Rep.__b_RepBase.status": ("ECU", "repinfo.__b_Rep.__b_RepBase.status"),
                 "repladi.__b_Rep.__b_RepBase.ExecutionStatus": ("ECU", "repladi.__b_Rep.__b_RepBase.ExecutionStatus"),
                 "repladi.__b_Rep.__b_RepBase.status": ("ECU", "repladi.__b_Rep.__b_RepBase.status"),
                 "repprew.__b_Rep.__b_RepBase.ExecutionStatus": ("ECU", "repprew.__b_Rep.__b_RepBase.ExecutionStatus"),
                 "repprew.__b_Rep.__b_RepBase.status": ("ECU", "repprew.__b_Rep.__b_RepBase.status"),
                 "repretg.__b_Rep.__b_RepBase.ExecutionStatus": ("ECU", "repretg.__b_Rep.__b_RepBase.ExecutionStatus"),
                 "repretg.__b_Rep.__b_RepBase.status": ("ECU", "repretg.__b_Rep.__b_RepBase.status"),},]

class cView(interface.iView):
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      ##################
      #Reaction pattern#
      ##################
      Client = datavis.cPlotNavigator(title="Reaction pattern", figureNr=207)
      interface.Sync.addClient(Client)
      Client.addsignal('repacuw.stat', interface.Source.getSignalFromSignalGroup(Group, "repacuw.__b_Rep.__b_RepBase.status"),
                       'repaubr.stat', interface.Source.getSignalFromSignalGroup(Group, "repaubr.__b_Rep.__b_RepBase.status"),
                       'repbrph.stat', interface.Source.getSignalFromSignalGroup(Group, "repbrph.__b_Rep.__b_RepBase.status"),
                       'repbrpp.stat', interface.Source.getSignalFromSignalGroup(Group, "repbrpp.__b_Rep.__b_RepBase.status"),
                       'repdesu.stat', interface.Source.getSignalFromSignalGroup(Group, "repdesu.__b_Rep.__b_RepBase.status"),
                       'repinfo.stat', interface.Source.getSignalFromSignalGroup(Group, "repinfo.__b_Rep.__b_RepBase.status"),
                       'repladi.stat', interface.Source.getSignalFromSignalGroup(Group, "repladi.__b_Rep.__b_RepBase.status"),
                       'repprew.stat', interface.Source.getSignalFromSignalGroup(Group, "repprew.__b_Rep.__b_RepBase.status"),
                       'repretg.stat', interface.Source.getSignalFromSignalGroup(Group, "repretg.__b_Rep.__b_RepBase.status"))
      Client.addsignal('repacuw.Execution', interface.Source.getSignalFromSignalGroup(Group, "repacuw.__b_Rep.__b_RepBase.ExecutionStatus"),
                       'repaubr.Execution', interface.Source.getSignalFromSignalGroup(Group, "repaubr.__b_Rep.__b_RepBase.ExecutionStatus"),
                       'repbrph.Execution', interface.Source.getSignalFromSignalGroup(Group, "repbrph.__b_Rep.__b_RepBase.ExecutionStatus"),
                       'repbrpp.Execution', interface.Source.getSignalFromSignalGroup(Group, "repbrpp.__b_Rep.__b_RepBase.ExecutionStatus"),
                       'repdesu.Execution', interface.Source.getSignalFromSignalGroup(Group, "repdesu.__b_Rep.__b_RepBase.ExecutionStatus"),
                       'repinfo.Execution', interface.Source.getSignalFromSignalGroup(Group, "repinfo.__b_Rep.__b_RepBase.ExecutionStatus"),
                       'repladi.Execution', interface.Source.getSignalFromSignalGroup(Group, "repladi.__b_Rep.__b_RepBase.ExecutionStatus"),
                       'repprew.Execution', interface.Source.getSignalFromSignalGroup(Group, "repprew.__b_Rep.__b_RepBase.ExecutionStatus"),
                       'repretg.Execution', interface.Source.getSignalFromSignalGroup(Group, "repretg.__b_Rep.__b_RepBase.ExecutionStatus"))
      return []

