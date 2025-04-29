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

SignalGroups = [{"fus.ObjData_TC.FusObj.i0.dxv": ("ECU", "fus.ObjData_TC.FusObj.i0.dxv"),
                 "fus.ObjData_TC.FusObj.i1.dxv": ("ECU", "fus.ObjData_TC.FusObj.i1.dxv"),
                 "fus.ObjData_TC.FusObj.i10.dxv": ("ECU", "fus.ObjData_TC.FusObj.i10.dxv"),
                 "fus.ObjData_TC.FusObj.i11.dxv": ("ECU", "fus.ObjData_TC.FusObj.i11.dxv"),
                 "fus.ObjData_TC.FusObj.i12.dxv": ("ECU", "fus.ObjData_TC.FusObj.i12.dxv"),
                 "fus.ObjData_TC.FusObj.i13.dxv": ("ECU", "fus.ObjData_TC.FusObj.i13.dxv"),
                 "fus.ObjData_TC.FusObj.i14.dxv": ("ECU", "fus.ObjData_TC.FusObj.i14.dxv"),
                 "fus.ObjData_TC.FusObj.i15.dxv": ("ECU", "fus.ObjData_TC.FusObj.i15.dxv"),
                 "fus.ObjData_TC.FusObj.i16.dxv": ("ECU", "fus.ObjData_TC.FusObj.i16.dxv"),
                 "fus.ObjData_TC.FusObj.i17.dxv": ("ECU", "fus.ObjData_TC.FusObj.i17.dxv"),
                 "fus.ObjData_TC.FusObj.i18.dxv": ("ECU", "fus.ObjData_TC.FusObj.i18.dxv"),
                 "fus.ObjData_TC.FusObj.i19.dxv": ("ECU", "fus.ObjData_TC.FusObj.i19.dxv"),
                 "fus.ObjData_TC.FusObj.i2.dxv": ("ECU", "fus.ObjData_TC.FusObj.i2.dxv"),
                 "fus.ObjData_TC.FusObj.i20.dxv": ("ECU", "fus.ObjData_TC.FusObj.i20.dxv"),
                 "fus.ObjData_TC.FusObj.i21.dxv": ("ECU", "fus.ObjData_TC.FusObj.i21.dxv"),
                 "fus.ObjData_TC.FusObj.i22.dxv": ("ECU", "fus.ObjData_TC.FusObj.i22.dxv"),
                 "fus.ObjData_TC.FusObj.i23.dxv": ("ECU", "fus.ObjData_TC.FusObj.i23.dxv"),
                 "fus.ObjData_TC.FusObj.i24.dxv": ("ECU", "fus.ObjData_TC.FusObj.i24.dxv"),
                 "fus.ObjData_TC.FusObj.i25.dxv": ("ECU", "fus.ObjData_TC.FusObj.i25.dxv"),
                 "fus.ObjData_TC.FusObj.i26.dxv": ("ECU", "fus.ObjData_TC.FusObj.i26.dxv"),
                 "fus.ObjData_TC.FusObj.i27.dxv": ("ECU", "fus.ObjData_TC.FusObj.i27.dxv"),
                 "fus.ObjData_TC.FusObj.i28.dxv": ("ECU", "fus.ObjData_TC.FusObj.i28.dxv"),
                 "fus.ObjData_TC.FusObj.i29.dxv": ("ECU", "fus.ObjData_TC.FusObj.i29.dxv"),
                 "fus.ObjData_TC.FusObj.i3.dxv": ("ECU", "fus.ObjData_TC.FusObj.i3.dxv"),
                 "fus.ObjData_TC.FusObj.i30.dxv": ("ECU", "fus.ObjData_TC.FusObj.i30.dxv"),
                 "fus.ObjData_TC.FusObj.i31.dxv": ("ECU", "fus.ObjData_TC.FusObj.i31.dxv"),
                 "fus.ObjData_TC.FusObj.i32.dxv": ("ECU", "fus.ObjData_TC.FusObj.i32.dxv"),
                 "fus.ObjData_TC.FusObj.i4.dxv": ("ECU", "fus.ObjData_TC.FusObj.i4.dxv"),
                 "fus.ObjData_TC.FusObj.i5.dxv": ("ECU", "fus.ObjData_TC.FusObj.i5.dxv"),
                 "fus.ObjData_TC.FusObj.i6.dxv": ("ECU", "fus.ObjData_TC.FusObj.i6.dxv"),
                 "fus.ObjData_TC.FusObj.i7.dxv": ("ECU", "fus.ObjData_TC.FusObj.i7.dxv"),
                 "fus.ObjData_TC.FusObj.i8.dxv": ("ECU", "fus.ObjData_TC.FusObj.i8.dxv"),
                 "fus.ObjData_TC.FusObj.i9.dxv": ("ECU", "fus.ObjData_TC.FusObj.i9.dxv"),},]

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
      #FUS objects - dx#
      ##################
      Client = datavis.cPlotNavigator(title="FUS_objects_dx", figureNr=301)
      interface.Sync.addClient(Client)
      signals=[] #Erstellen einer leeren Liste
      for i in xrange(0,33,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
        signals.append("FUS_dx_%d"%i) #Name der Signalbezeichnung
        signals.append(interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%d.dxv"%i)) # Angabe des Geraetes und des Signalnamens
      Client.addsignal(*signals) #entpacken der liste 
      return []

