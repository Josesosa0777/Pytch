import interface

DefParam = interface.NullParam

SignalGroups = [{},]

class cView(interface.iView):
  channels = "main", "foo"

  def check(self):
    Group = interface.Source.selectSignalGroup(SignalGroups)
    return Group
    
  def fill(self, Group):
    return Group

  def view(self, Param, Group):
    return
