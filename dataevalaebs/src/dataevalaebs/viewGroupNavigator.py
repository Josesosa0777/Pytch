import datavis
import interface

DefParam = interface.NullParam

class cView(interface.iView):
  @classmethod
  def view(cls, Param = DefParam):
    GN = datavis.cGroupNavigator()
    interface.Sync.addClient(GN)    
    GN.addGroups(interface.Groups)
    return [GN]