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

SignalGroups = [{"ats.Po_TC.PO.i0.dxvFilt": ("ECU", "ats.Po_TC.PO.i0.dxvFilt"),
                 "ats.Po_TC.PO.i0.dyv": ("ECU", "ats.Po_TC.PO.i0.dyv"),
                 "ats.Po_TC.PO.i1.dxvFilt": ("ECU", "ats.Po_TC.PO.i1.dxvFilt"),
                 "ats.Po_TC.PO.i1.dyv": ("ECU", "ats.Po_TC.PO.i1.dyv"),
                 "ats.Po_TC.PO.i2.dxvFilt": ("ECU", "ats.Po_TC.PO.i2.dxvFilt"),
                 "ats.Po_TC.PO.i2.dyv": ("ECU", "ats.Po_TC.PO.i2.dyv"),
                 "ats.Po_TC.PO.i3.dxvFilt": ("ECU", "ats.Po_TC.PO.i3.dxvFilt"),
                 "ats.Po_TC.PO.i3.dyv": ("ECU", "ats.Po_TC.PO.i3.dyv"),
                 "ats.Po_TC.PO.i4.dxvFilt": ("ECU", "ats.Po_TC.PO.i4.dxvFilt"),
                 "ats.Po_TC.PO.i4.dyv": ("ECU", "ats.Po_TC.PO.i4.dyv"),},]

class cView(interface.iView):
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      #####################
      #ATS objects - dx,dy#
      #####################
      Client = datavis.cPlotNavigator(title="ATS objects - dx,dy", figureNr=601)
      interface.Sync.addClient(Client)
      signals=[] #Erstellen einer leeren Liste
      for i in xrange(0,5,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
        signals.append("ats_dx_i%d"%i) #Name der Signalbezeichnung
        signals.append(interface.Source.getSignalFromSignalGroup(Group, "ats.Po_TC.PO.i%d.dxvFilt"%i)) # Angabe des Geraetes und des Signalnamens
      Client.addsignal(*signals)  
      signals=[] #Erstellen einer leeren Liste
      for i in xrange(0,5,1):
        signals.append("ats_dy_i%d"%i) #Name der Signalbezeichnung
        signals.append(interface.Source.getSignalFromSignalGroup(Group, "ats.Po_TC.PO.i%d.dyv"%i))
      Client.addsignal(*signals) #entpacken der liste
      return []

