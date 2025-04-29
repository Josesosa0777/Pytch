import datavis
import interface

DefParam = interface.NullParam

signalgroups =   [{'vx_ego': (dev_name, 'evi.General_TC.vxvRef')}
                  for dev_name  in 'ECU', 'MRR1plus', 'RadarFC']

class cView(interface.iView):
  def check(self):
    group = interface.Source.selectSignalGroup(signalgroups)
    return group
    
  def fill(self, group):
    return group

  def view(cls, param, group):
    client = datavis.cPlotNavigator(title="PN", figureNr=None)
    interface.Sync.addClient(client)
    axis = client.addAxis()
    time, value = interface.Source.getSignalFromSignalGroup(group, "vx_ego")
    client.addSignal2Axis(axis, "vx_ego", time, value, unit="m/s")
    return

