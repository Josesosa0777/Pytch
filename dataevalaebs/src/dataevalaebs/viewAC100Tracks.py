import datavis
import measparser
import interface
import aebs

DefParam = interface.NullParam

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectFilteredSignalGroup(aebs.fill.fillAC100_POS.TrackInfoSignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      Client = datavis.cPlotNavigator(title="track_info", figureNr=None)
      interface.Sync.addClient(Client)
      
      for Alias in Group:
        Time, Value = interface.Source.getSignalFromSignalGroup(Group, Alias)
        Axis = Client.addAxis()
        Client.addSignal2Axis(Axis, Alias, Time, Value)
      pass
    pass



