"""
:Organization: Knorr-Bremse SfN GmbH T/CES3.2 (BU2) Budapest Schwieberdingen T/CES3.2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

import interface
import measparser

DefParam = interface.NullParam

SignalGroups = [{"fus.ObjData_TC.FusObj.i0.vxv": ("ECU", "fus.ObjData_TC.FusObj.i0.vxv"),
                 "fus.ObjData_TC.FusObj.i1.vxv": ("ECU", "fus.ObjData_TC.FusObj.i1.vxv"),
                 "fus.ObjData_TC.FusObj.i10.vxv": ("ECU", "fus.ObjData_TC.FusObj.i10.vxv"),
                 "fus.ObjData_TC.FusObj.i11.vxv": ("ECU", "fus.ObjData_TC.FusObj.i11.vxv"),
                 "fus.ObjData_TC.FusObj.i12.vxv": ("ECU", "fus.ObjData_TC.FusObj.i12.vxv"),
                 "fus.ObjData_TC.FusObj.i13.vxv": ("ECU", "fus.ObjData_TC.FusObj.i13.vxv"),
                 "fus.ObjData_TC.FusObj.i14.vxv": ("ECU", "fus.ObjData_TC.FusObj.i14.vxv"),
                 "fus.ObjData_TC.FusObj.i15.vxv": ("ECU", "fus.ObjData_TC.FusObj.i15.vxv"),
                 "fus.ObjData_TC.FusObj.i16.vxv": ("ECU", "fus.ObjData_TC.FusObj.i16.vxv"),
                 "fus.ObjData_TC.FusObj.i17.vxv": ("ECU", "fus.ObjData_TC.FusObj.i17.vxv"),
                 "fus.ObjData_TC.FusObj.i18.vxv": ("ECU", "fus.ObjData_TC.FusObj.i18.vxv"),
                 "fus.ObjData_TC.FusObj.i19.vxv": ("ECU", "fus.ObjData_TC.FusObj.i19.vxv"),
                 "fus.ObjData_TC.FusObj.i2.vxv": ("ECU", "fus.ObjData_TC.FusObj.i2.vxv"),
                 "fus.ObjData_TC.FusObj.i20.vxv": ("ECU", "fus.ObjData_TC.FusObj.i20.vxv"),
                 "fus.ObjData_TC.FusObj.i21.vxv": ("ECU", "fus.ObjData_TC.FusObj.i21.vxv"),
                 "fus.ObjData_TC.FusObj.i22.vxv": ("ECU", "fus.ObjData_TC.FusObj.i22.vxv"),
                 "fus.ObjData_TC.FusObj.i23.vxv": ("ECU", "fus.ObjData_TC.FusObj.i23.vxv"),
                 "fus.ObjData_TC.FusObj.i24.vxv": ("ECU", "fus.ObjData_TC.FusObj.i24.vxv"),
                 "fus.ObjData_TC.FusObj.i25.vxv": ("ECU", "fus.ObjData_TC.FusObj.i25.vxv"),
                 "fus.ObjData_TC.FusObj.i26.vxv": ("ECU", "fus.ObjData_TC.FusObj.i26.vxv"),
                 "fus.ObjData_TC.FusObj.i27.vxv": ("ECU", "fus.ObjData_TC.FusObj.i27.vxv"),
                 "fus.ObjData_TC.FusObj.i28.vxv": ("ECU", "fus.ObjData_TC.FusObj.i28.vxv"),
                 "fus.ObjData_TC.FusObj.i29.vxv": ("ECU", "fus.ObjData_TC.FusObj.i29.vxv"),
                 "fus.ObjData_TC.FusObj.i3.vxv": ("ECU", "fus.ObjData_TC.FusObj.i3.vxv"),
                 "fus.ObjData_TC.FusObj.i30.vxv": ("ECU", "fus.ObjData_TC.FusObj.i30.vxv"),
                 "fus.ObjData_TC.FusObj.i31.vxv": ("ECU", "fus.ObjData_TC.FusObj.i31.vxv"),
                 "fus.ObjData_TC.FusObj.i32.vxv": ("ECU", "fus.ObjData_TC.FusObj.i32.vxv"),
                 "fus.ObjData_TC.FusObj.i4.vxv": ("ECU", "fus.ObjData_TC.FusObj.i4.vxv"),
                 "fus.ObjData_TC.FusObj.i5.vxv": ("ECU", "fus.ObjData_TC.FusObj.i5.vxv"),
                 "fus.ObjData_TC.FusObj.i6.vxv": ("ECU", "fus.ObjData_TC.FusObj.i6.vxv"),
                 "fus.ObjData_TC.FusObj.i7.vxv": ("ECU", "fus.ObjData_TC.FusObj.i7.vxv"),
                 "fus.ObjData_TC.FusObj.i8.vxv": ("ECU", "fus.ObjData_TC.FusObj.i8.vxv"),
                 "fus.ObjData_TC.FusObj.i9.vxv": ("ECU", "fus.ObjData_TC.FusObj.i9.vxv"),},]

class cView(interface.iView):
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      ###################
      #FUS objects - vxv#
      ###################
      Client = datavis.cPlotNavigator(title="FUS_objects_vxv", figureNr=303)
      interface.Sync.addClient(Client)
      signals=[] #Erstellen einer leeren Liste
      for i in xrange(0,33,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
        signals.append("FUS_vxv_%d"%i) #Name der Signalbezeichnung
        signals.append(interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%d.vxv"%i)) # Angabe des Geraetes und des Signalnamens
      Client.addsignal(*signals) #entpacken der liste
      return []

