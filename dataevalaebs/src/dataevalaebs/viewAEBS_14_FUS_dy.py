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

SignalGroups = [{"fus.ObjData_TC.FusObj.i0.dyv": ("ECU", "fus.ObjData_TC.FusObj.i0.dyv"),
                 "fus.ObjData_TC.FusObj.i1.dyv": ("ECU", "fus.ObjData_TC.FusObj.i1.dyv"),
                 "fus.ObjData_TC.FusObj.i10.dyv": ("ECU", "fus.ObjData_TC.FusObj.i10.dyv"),
                 "fus.ObjData_TC.FusObj.i11.dyv": ("ECU", "fus.ObjData_TC.FusObj.i11.dyv"),
                 "fus.ObjData_TC.FusObj.i12.dyv": ("ECU", "fus.ObjData_TC.FusObj.i12.dyv"),
                 "fus.ObjData_TC.FusObj.i13.dyv": ("ECU", "fus.ObjData_TC.FusObj.i13.dyv"),
                 "fus.ObjData_TC.FusObj.i14.dyv": ("ECU", "fus.ObjData_TC.FusObj.i14.dyv"),
                 "fus.ObjData_TC.FusObj.i15.dyv": ("ECU", "fus.ObjData_TC.FusObj.i15.dyv"),
                 "fus.ObjData_TC.FusObj.i16.dyv": ("ECU", "fus.ObjData_TC.FusObj.i16.dyv"),
                 "fus.ObjData_TC.FusObj.i17.dyv": ("ECU", "fus.ObjData_TC.FusObj.i17.dyv"),
                 "fus.ObjData_TC.FusObj.i18.dyv": ("ECU", "fus.ObjData_TC.FusObj.i18.dyv"),
                 "fus.ObjData_TC.FusObj.i19.dyv": ("ECU", "fus.ObjData_TC.FusObj.i19.dyv"),
                 "fus.ObjData_TC.FusObj.i2.dyv": ("ECU", "fus.ObjData_TC.FusObj.i2.dyv"),
                 "fus.ObjData_TC.FusObj.i20.dyv": ("ECU", "fus.ObjData_TC.FusObj.i20.dyv"),
                 "fus.ObjData_TC.FusObj.i21.dyv": ("ECU", "fus.ObjData_TC.FusObj.i21.dyv"),
                 "fus.ObjData_TC.FusObj.i22.dyv": ("ECU", "fus.ObjData_TC.FusObj.i22.dyv"),
                 "fus.ObjData_TC.FusObj.i23.dyv": ("ECU", "fus.ObjData_TC.FusObj.i23.dyv"),
                 "fus.ObjData_TC.FusObj.i24.dyv": ("ECU", "fus.ObjData_TC.FusObj.i24.dyv"),
                 "fus.ObjData_TC.FusObj.i25.dyv": ("ECU", "fus.ObjData_TC.FusObj.i25.dyv"),
                 "fus.ObjData_TC.FusObj.i26.dyv": ("ECU", "fus.ObjData_TC.FusObj.i26.dyv"),
                 "fus.ObjData_TC.FusObj.i27.dyv": ("ECU", "fus.ObjData_TC.FusObj.i27.dyv"),
                 "fus.ObjData_TC.FusObj.i28.dyv": ("ECU", "fus.ObjData_TC.FusObj.i28.dyv"),
                 "fus.ObjData_TC.FusObj.i29.dyv": ("ECU", "fus.ObjData_TC.FusObj.i29.dyv"),
                 "fus.ObjData_TC.FusObj.i3.dyv": ("ECU", "fus.ObjData_TC.FusObj.i3.dyv"),
                 "fus.ObjData_TC.FusObj.i30.dyv": ("ECU", "fus.ObjData_TC.FusObj.i30.dyv"),
                 "fus.ObjData_TC.FusObj.i31.dyv": ("ECU", "fus.ObjData_TC.FusObj.i31.dyv"),
                 "fus.ObjData_TC.FusObj.i32.dyv": ("ECU", "fus.ObjData_TC.FusObj.i32.dyv"),
                 "fus.ObjData_TC.FusObj.i4.dyv": ("ECU", "fus.ObjData_TC.FusObj.i4.dyv"),
                 "fus.ObjData_TC.FusObj.i5.dyv": ("ECU", "fus.ObjData_TC.FusObj.i5.dyv"),
                 "fus.ObjData_TC.FusObj.i6.dyv": ("ECU", "fus.ObjData_TC.FusObj.i6.dyv"),
                 "fus.ObjData_TC.FusObj.i7.dyv": ("ECU", "fus.ObjData_TC.FusObj.i7.dyv"),
                 "fus.ObjData_TC.FusObj.i8.dyv": ("ECU", "fus.ObjData_TC.FusObj.i8.dyv"),
                 "fus.ObjData_TC.FusObj.i9.dyv": ("ECU", "fus.ObjData_TC.FusObj.i9.dyv"),},]

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
      #FUS objects - dy#
      ##################
      Client = datavis.cPlotNavigator(title="FUS_objects_dy", figureNr=302)
      interface.Sync.addClient(Client)
      signals=[] #Erstellen einer leeren Liste
      for i in xrange(0,33,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
        signals.append("FUS_dy_%d"%i) #Name der Signalbezeichnung
        signals.append(interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%d.dyv"%i)) # Angabe des Geraetes und des Signalnamens
      Client.addsignal(*signals) #entpacken der liste 
      return []

