import datavis
import interface

DefParam = interface.NullParam

class cLRR3_ATS_CutIn(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    if interface.Source.checkStatus("LRR3_FUS"):
      DeviceName = 'ECU_0_0'
    else:
      Decivename = 'MRR1plus_0_0'
    PN = datavis.cPlotNavigator()
    time2, value = interface.Source.getSignal(DeviceName,'evi.General_T20.vxvRef')
    PN.addsignal('vxvref',(time2, value))
    time2, value = interface.Source.getSignal(DeviceName,'evi.General_T20.psiDtOpt')
    PN.addsignal('psidtopt',(time2, value))
    signal = []
    for x in xrange(4):
        time2, value = interface.Source.getSignal(DeviceName,'ats.Po_T20.PO.i%d.dxvFilt'%x)
        signal.append('dxvpo%d'%x)
        signal.append((time2, value))
    PN.addsignal(*signal)
    interface.Sync.addClient(PN)
