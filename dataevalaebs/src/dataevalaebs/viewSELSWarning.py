import os

import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"repprew.__b_Rep.__b_RepBase.status": ("RadarFC", "repprew.__b_Rep.__b_RepBase.status"),},]

class cView(interface.iView):
  channels = "main", "sels"
  def check(self):
    Source = self.get_source("sels") 
    Group = Source.selectSignalGroup(SignalGroups)
    return Group
    
  def fill(self, Group):
    return Group

  def view(self, Param, Group):
    Source = self.get_source("sels") 
    Client = datavis.cPlotNavigator(title="PN", figureNr=None)
    Client.setUserWindowTitle(os.path.basename(Source.FileName))
    interface.Sync.addClient(Client)
    Axis = Client.addAxis()
    Time, Value = Source.getSignalFromSignalGroup(Group, "repprew.__b_Rep.__b_RepBase.status")
    Client.addSignal2Axis(Axis, "repprew.__b_Rep.__b_RepBase.status", Time, Value, unit="")
    return

